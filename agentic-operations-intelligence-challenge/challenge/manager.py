from __future__ import annotations

import json
import os
import logging
from time import perf_counter
from typing import Any

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import PrepareTools
from pydantic_ai.output import ToolOutput
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.usage import UsageLimits

from .config import student_path
from .data_api import get_data_client
from .llm_config import resolve_manager_model
from .model_registry import StudentModelRegistry
from .observability import current_trace_id, log_event, set_trace_context, reset_trace_context, log_exception
from .rag import RagIndex
from .runtime import RuntimeDeps
from .schemas import MonthlyOperationsPlan
from .skills import SkillLibrary
from .student_config import load_runtime_config
from .tools import ALL_TOOLS
from .training_data import load_model_spec

load_dotenv()
logger = logging.getLogger(__name__)


def _manager_tool_retry_limit() -> int:
    raw = os.getenv("MANAGER_TOOL_RETRY_LIMIT", "3").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 3
    return max(1, min(value, 8))


def _manager_request_limit() -> int:
    raw = os.getenv("MANAGER_REQUEST_LIMIT", "75").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 75
    return max(10, min(value, 150))


def _manager_research_step_limit() -> int:
    """Maximum model steps that may still expose normal function tools."""
    raw = os.getenv("MANAGER_RESEARCH_STEP_LIMIT", "12").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 12
    return max(4, min(value, 24))


def _manager_output_retry_limit() -> int:
    raw = os.getenv("MANAGER_OUTPUT_RETRY_LIMIT", "2").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 2
    return max(1, min(value, 4))


def _prepare_manager_tools(
    ctx: RunContext[RuntimeDeps],
    tool_defs: list[ToolDefinition],
) -> list[ToolDefinition]:
    """Stop research loops by switching to an output-only finalization phase."""
    limit = _manager_research_step_limit()
    if ctx.run_step >= limit:
        log_event(
            logger,
            "manager.finalization_phase",
            team_id=ctx.deps.team_id,
            scenario_id=ctx.deps.scenario.get("id"),
            run_step=ctx.run_step,
            research_step_limit=limit,
            hidden_function_tools=len(tool_defs),
        )
        return []
    return tool_defs


BASE_INSTRUCTIONS = """
You are the Operations Manager Agent for a manufacturing planning challenge.

Your job is to create a four-week integrated production and procurement plan.
The students teach you the business through PyTorch specialist models, RAG,
procedural Skills, and student-editable decision configuration.

Rules:
1. Never invent inventory, BOM, supplier, capacity, policy, budget or cost data; use tools/RAG.
2. Inspect relevant Skills and retrieve policy evidence before sensitive decisions.
3. Hard business constraints from the case are authoritative. Student preferences may guide trade-offs but can never relax a hard constraint.
4. When model, statistical and confirmed-order signals disagree, investigate the disagreement instead of blindly trusting one signal.
5. Check existing POs before placing new purchase orders.
6. Lowest unit price is not necessarily lowest total cost; compare feasible alternatives.
7. Respect capacity, authorized suppliers, MOQ, approvals, budget, inventory and service constraints.
8. Follow student tool-policy guidance when reasonable, but never skip required cost/validation discipline.
9. Before finalizing, calculate candidate cost, validate the plan and revise critical violations.
10. Do not repeat an identical tool call unless its inputs or the underlying evidence changed.
11. Once validate_plan is feasible, or additional research is unlikely to materially improve the plan, immediately call submit_monthly_operations_plan.
12. The investigation phase is bounded; if normal tools disappear, finalize the best evidence-backed plan immediately.
13. Return only a plan matching the structured output schema.
"""


def build_runtime(team_id: str, scenario: dict[str, Any]) -> RuntimeDeps:
    workspace = student_path(team_id)
    log_event(logger, "manager.runtime.build.started", team_id=team_id, scenario_id=scenario.get("id"), workspace=str(workspace))
    start_context = get_data_client().start_context(team_id)
    student_config = load_runtime_config(team_id)
    model_spec = load_model_spec(team_id)
    models = StudentModelRegistry(workspace / "models", model_spec, feature_config=student_config.get("feature_config"))
    model_status = models.warmup()
    manager_cfg = student_config.get("manager_llm", {})
    runtime = RuntimeDeps(
        team_id=team_id,
        case=start_context["case"],
        scenario=scenario,
        rag=RagIndex(
            start_context["knowledge"],
            workspace / "rag" / "config.yaml",
            document_priorities=student_config.get("document_priorities"),
            max_top_k=int(manager_cfg.get("max_rag_documents", 5)),
        ),
        skills=SkillLibrary(workspace / "skills"),
        models=models,
        student_config=student_config,
    )
    log_event(
        logger,
        "manager.runtime.build.completed",
        team_id=team_id,
        scenario_id=scenario.get("id"),
        knowledge_documents=len(start_context.get("knowledge", [])),
        skill_directory=str(workspace / "skills"),
        model_keys=sorted(model_spec.get("models", {})),
        model_contract=str(workspace / "training" / "model_contract.json"),
        model_warmup=model_status,
        student_config=student_config,
    )
    return runtime


def _student_model_settings(student_config: dict[str, Any], base: Any | None) -> dict[str, Any] | None:
    settings = dict(base or {})
    llm = student_config.get("manager_llm", {})
    settings["temperature"] = float(llm.get("temperature", 0.20))
    settings["max_tokens"] = int(llm.get("max_tokens", 3000))
    return settings or None


def build_agent(model_id: str | None = None, student_config: dict[str, Any] | None = None) -> Agent:
    student_config = student_config or {}
    llm_cfg = student_config.get("manager_llm", {})
    requested_model_id = model_id or llm_cfg.get("provider")
    model, base_settings = resolve_manager_model(requested_model_id)
    model_settings = _student_model_settings(student_config, base_settings)
    log_event(
        logger,
        "manager.agent.build",
        requested_model_id=model_id,
        student_preferred_provider=llm_cfg.get("provider"),
        resolved_model=model,
        model_settings=model_settings,
        tool_count=len(ALL_TOOLS),
        research_step_limit=_manager_research_step_limit(),
        output_retry_limit=_manager_output_retry_limit(),
        end_strategy="early",
    )
    kwargs = {
        "deps_type": RuntimeDeps,
        "output_type": ToolOutput(
            MonthlyOperationsPlan,
            name="submit_monthly_operations_plan",
            description=(
                "Submit the final four-week production and procurement plan. "
                "Use this as soon as the candidate plan is sufficiently investigated and validated; "
                "calling it ends the Manager run."
            ),
            max_retries=_manager_output_retry_limit(),
        ),
        "tools": ALL_TOOLS,
        "instructions": BASE_INSTRUCTIONS,
        "retries": {
            "tools": _manager_tool_retry_limit(),
            "output": _manager_output_retry_limit(),
        },
        "capabilities": [PrepareTools(_prepare_manager_tools)],
        "end_strategy": "early",
    }
    if model_settings is not None:
        kwargs["model_settings"] = model_settings
    return Agent(model, **kwargs)


def manager_prompt(deps: RuntimeDeps) -> str:
    visible = deps.scenario.get("visible", {})
    llm_cfg = deps.student_config.get("manager_llm", {})
    business = {
        "team_id": deps.team_id,
        "business_name": deps.case.get("name"),
        "operating_context": deps.case.get("description"),
        "company_profile": deps.case.get("company_profile"),
        "objective": deps.case.get("objective"),
        "cost_priorities": deps.case.get("cost_priorities", []),
        "hard_policies": deps.case.get("policies", {}),
        "hard_constraints": deps.case.get("constraints", {}),
        "customer_priorities": deps.case.get("customer_priorities", {}),
        "scenario_id": deps.scenario["id"],
        "scenario_title": deps.scenario["title"],
        "visible_information": visible,
        "student_decision_configuration": {
            "forecast_policy": deps.student_config.get("forecast_policy", {}),
            "risk_policy": deps.student_config.get("risk_policy", {}),
            "planning_objectives": deps.student_config.get("planning_objectives", {}),
            "tool_policy": deps.student_config.get("tool_policy", {}),
            "business_assumptions": deps.student_config.get("business_assumptions", {}),
            "manager_context_preferences": {
                "reasoning_mode": llm_cfg.get("reasoning_mode"),
                "include_model_diagnostics": llm_cfg.get("include_model_diagnostics"),
                "include_cost_breakdown": llm_cfg.get("include_cost_breakdown"),
                "include_previous_plan": llm_cfg.get("include_previous_plan"),
            },
        },
    }
    return (
        "Prepare the integrated four-week production and procurement plan for this scenario. "
        "Optimize total operational cost subject to the authoritative business constraints. "
        "Use the student configuration as decision guidance, not as permission to override the case. "
        "When signals disagree, investigate why and apply the configured risk/forecast policy.\n\n"
        + json.dumps(business, indent=2)
    )


async def run_manager(team_id: str, scenario: dict[str, Any], model_id: str | None = None) -> tuple[MonthlyOperationsPlan, RuntimeDeps]:
    owns_trace = current_trace_id() == "-"
    tokens = set_trace_context() if owns_trace else None
    started = perf_counter()
    try:
        deps = build_runtime(team_id, scenario)
        prompt = manager_prompt(deps)
        effective_model_id = model_id or deps.student_config.get("manager_llm", {}).get("provider")
        resolved_model, _ = resolve_manager_model(effective_model_id)
        agent = build_agent(model_id, deps.student_config)
        log_event(
            logger,
            "manager.run.started",
            team_id=team_id,
            scenario_id=scenario.get("id"),
            requested_model_id=model_id,
            resolved_model=resolved_model,
            prompt=prompt,
            visible_information=scenario.get("visible", {}),
        )
        request_limit = _manager_request_limit()
        log_event(
            logger,
            "manager.usage_limits",
            request_limit=request_limit,
            research_step_limit=_manager_research_step_limit(),
            tool_retry_limit=_manager_tool_retry_limit(),
            output_retry_limit=_manager_output_retry_limit(),
        )
        result = await agent.run(prompt, deps=deps, usage_limits=UsageLimits(request_limit=request_limit))
        plan = result.output
        plan.team_id = team_id
        plan.scenario_id = scenario["id"]
        log_event(
            logger,
            "manager.run.completed",
            team_id=team_id,
            scenario_id=scenario.get("id"),
            duration_ms=round((perf_counter() - started) * 1000, 2),
            tool_calls=len(deps.trace),
            rag_sources=sorted(deps.rag_hits),
            production_orders=len(plan.production_plan),
            purchase_orders=len(plan.purchase_orders),
            actions=[a.model_dump() for a in plan.actions],
            plan=plan.model_dump(),
        )
        return plan, deps
    except Exception as exc:
        log_exception(
            logger,
            "manager.run.failed",
            team_id=team_id,
            scenario_id=scenario.get("id"),
            duration_ms=round((perf_counter() - started) * 1000, 2),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        raise
    finally:
        if tokens is not None:
            reset_trace_context(tokens)
