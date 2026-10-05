from __future__ import annotations

import json
import os
import logging
from time import perf_counter
from typing import Any

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits

from app.store import load_case, load_knowledge, load_model_spec
from app.observability import current_trace_id, log_event, reset_trace_context, set_trace_context, log_exception
from .config import DEMO_MODELS_DIR, DEMO_RAG_CONFIG, DEMO_SKILLS_DIR
from .llm_config import resolve_manager_model
from .model_registry import StudentModelRegistry
from .rag import RagIndex
from .runtime import RuntimeDeps
from .schemas import MonthlyOperationsPlan
from .skills import SkillLibrary
from .student_config import load_runtime_config
from .tools import ALL_TOOLS

load_dotenv()
logger = logging.getLogger(__name__)
TEAM_ID = "team_0"


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


BASE_INSTRUCTIONS = """
You are the Operations Manager Agent for the fully solved Case 0 manufacturing planning demo.

Your job is to create a four-week integrated production and procurement plan that meets
service and policy requirements while minimizing total operational cost.

This is a worked teaching example. Use the supplied RAG documents, Skills, specialist
PyTorch models, student decision configuration, deterministic calculations, cost tools
and validation tools.

Rules:
1. Never invent inventory, BOM, supplier, capacity, policy, budget or cost data.
2. Hard company constraints are authoritative; solved preferences can guide trade-offs but cannot weaken them.
3. Inspect relevant Skills and retrieve current company evidence before high-impact decisions.
4. When model, statistical and confirmed-order signals disagree, investigate the disagreement rather than blindly trusting one source.
5. Check inventory and existing POs before recommending new purchases.
6. Use supplier-delay prediction when delivery timing matters.
7. Compare total operational cost, not only unit purchase price.
8. Respect capacity, supplier authorization, MOQ, approvals, budget, inventory and service constraints.
9. Follow the solved tool policy and retain cost/validation discipline.
10. Run validate_plan before finalizing; revise if critical violations remain.
11. Return a plan matching the structured output schema.
"""


def build_runtime(scenario: dict[str, Any]) -> RuntimeDeps:
    log_event(logger, "manager.runtime.build.started", team_id=TEAM_ID, scenario_id=scenario.get("id"))
    case = load_case(TEAM_ID)
    knowledge = list(load_knowledge(TEAM_ID))
    student_config = load_runtime_config()
    models = StudentModelRegistry(
        DEMO_MODELS_DIR,
        load_model_spec(TEAM_ID),
        feature_config=student_config.get("feature_config"),
    )
    model_status = models.warmup()
    manager_cfg = student_config.get("manager_llm", {})
    runtime = RuntimeDeps(
        team_id=TEAM_ID,
        case=case,
        scenario=scenario,
        rag=RagIndex(
            knowledge,
            DEMO_RAG_CONFIG,
            document_priorities=student_config.get("document_priorities"),
            max_top_k=int(manager_cfg.get("max_rag_documents", 5)),
        ),
        skills=SkillLibrary(DEMO_SKILLS_DIR),
        models=models,
        student_config=student_config,
    )
    log_event(
        logger,
        "manager.runtime.build.completed",
        team_id=TEAM_ID,
        scenario_id=scenario.get("id"),
        knowledge_documents=len(knowledge),
        skill_directory=str(DEMO_SKILLS_DIR),
        model_directory=str(DEMO_MODELS_DIR),
        model_warmup=model_status,
        solved_config=student_config,
    )
    return runtime


def _resolved_settings(student_config: dict[str, Any], base: Any | None) -> dict[str, Any]:
    settings = dict(base or {})
    llm = student_config.get("manager_llm", {})
    settings["temperature"] = float(llm.get("temperature", 0.10))
    settings["max_tokens"] = int(llm.get("max_tokens", 3500))
    return settings


def build_agent(model_id: str | None = None, student_config: dict[str, Any] | None = None) -> Agent:
    student_config = student_config or load_runtime_config()
    preferred = student_config.get("manager_llm", {}).get("provider")
    effective_id = model_id or preferred
    model, base_settings = resolve_manager_model(effective_id)
    model_settings = _resolved_settings(student_config, base_settings)
    log_event(
        logger,
        "manager.agent.build",
        requested_model_id=model_id,
        solved_preferred_provider=preferred,
        resolved_model=model,
        model_settings=model_settings,
        tool_count=len(ALL_TOOLS),
    )
    return Agent(
        model,
        deps_type=RuntimeDeps,
        output_type=MonthlyOperationsPlan,
        tools=ALL_TOOLS,
        instructions=BASE_INSTRUCTIONS,
        retries={"tools": _manager_tool_retry_limit()},
        model_settings=model_settings,
    )


def manager_prompt(deps: RuntimeDeps) -> str:
    visible = deps.scenario.get("visible", {})
    business = {
        "team_id": TEAM_ID,
        "business_name": deps.case.get("name"),
        "company_profile": deps.case.get("company_profile"),
        "operating_context": deps.case.get("description"),
        "objective": deps.case.get("objective"),
        "cost_priorities": deps.case.get("cost_priorities", []),
        "hard_policies": deps.case.get("policies", {}),
        "hard_constraints": deps.case.get("constraints", {}),
        "customer_priorities": deps.case.get("customer_priorities", {}),
        "decision_signal_guidance": deps.case.get("decision_signals", {}),
        "scenario_id": deps.scenario["id"],
        "scenario_title": deps.scenario["title"],
        "visible_information": visible,
        "solved_student_configuration": {
            "forecast_policy": deps.student_config.get("forecast_policy", {}),
            "risk_policy": deps.student_config.get("risk_policy", {}),
            "planning_objectives": deps.student_config.get("planning_objectives", {}),
            "tool_policy": deps.student_config.get("tool_policy", {}),
            "business_assumptions": deps.student_config.get("business_assumptions", {}),
        },
    }
    return (
        "Prepare the integrated four-week production and procurement plan for Case 0. "
        "This is the solved reference configuration: apply it while independently solving "
        "the selected scenario through the normal agent/tool pipeline. "
        "Hard company constraints override preferences.\n\n"
        + json.dumps(business, indent=2)
    )


async def run_manager(scenario: dict[str, Any], model_id: str | None = None):
    owns_trace = current_trace_id() == "-"
    tokens = set_trace_context() if owns_trace else None
    started = perf_counter()
    try:
        deps = build_runtime(scenario)
        prompt = manager_prompt(deps)
        agent = build_agent(model_id, deps.student_config)
        effective_id = model_id or deps.student_config.get("manager_llm", {}).get("provider")
        resolved_model, _ = resolve_manager_model(effective_id)
        log_event(
            logger,
            "manager.run.started",
            team_id=TEAM_ID,
            scenario_id=scenario.get("id"),
            requested_model_id=model_id,
            resolved_model=resolved_model,
            prompt=prompt,
            visible_information=scenario.get("visible", {}),
        )
        request_limit = _manager_request_limit()
        log_event(logger, "manager.usage_limits", request_limit=request_limit, tool_retry_limit=_manager_tool_retry_limit())
        result = await agent.run(prompt, deps=deps, usage_limits=UsageLimits(request_limit=request_limit))
        plan = result.output
        plan.team_id = TEAM_ID
        plan.scenario_id = scenario["id"]
        log_event(
            logger,
            "manager.run.completed",
            team_id=TEAM_ID,
            scenario_id=scenario.get("id"),
            duration_ms=round((perf_counter()-started)*1000, 2),
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
            team_id=TEAM_ID,
            scenario_id=scenario.get("id"),
            duration_ms=round((perf_counter()-started)*1000, 2),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        raise
    finally:
        if tokens is not None:
            reset_trace_context(tokens)
