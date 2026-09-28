from __future__ import annotations

import json
import os
import logging
from time import perf_counter
from typing import Any

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits

from .config import student_path
from .data_api import get_data_client
from .llm_config import resolve_manager_model
from .model_registry import StudentModelRegistry
from .observability import current_trace_id, log_event, set_trace_context, reset_trace_context
from .rag import RagIndex
from .runtime import RuntimeDeps
from .schemas import MonthlyOperationsPlan
from .skills import SkillLibrary
from .tools import ALL_TOOLS
from .training_data import load_model_spec

load_dotenv()

logger = logging.getLogger(__name__)


def _manager_request_limit() -> int:
    raw = os.getenv("MANAGER_REQUEST_LIMIT", "75").strip()
    try:
        value = int(raw)
    except ValueError:
        value = 75
    # Keep a finite guardrail: enough room for a complex tool-using run without
    # allowing an accidental unbounded agent loop.
    return max(10, min(value, 150))




BASE_INSTRUCTIONS = """
You are the Operations Manager Agent for a manufacturing planning challenge.

Your job is to create a four-week integrated production and procurement plan.
You have many tools, but not every tool is appropriate for every business.
The students teach you the business through PyTorch specialist models, RAG configuration,
and procedural Skills.

Rules:
1. Never invent inventory, BOM, supplier, capacity, policy or cost data; use tools/RAG.
2. Inspect relevant Skills and retrieve policy evidence before sensitive decisions.
3. Choose forecasting/risk tools that fit this team's operating context.
4. Check existing POs before placing new purchase orders.
5. Use the cost tools to compare feasible alternatives; lowest unit price is not the same as lowest total cost.
6. Respect capacity, authorized suppliers, MOQ, approvals and service targets.
7. Before finalizing, validate your candidate plan and revise if critical violations remain.
8. Return only a plan matching the structured output schema.
"""


def build_runtime(team_id: str, scenario: dict[str, Any]) -> RuntimeDeps:
    workspace = student_path(team_id)
    log_event(logger, "manager.runtime.build.started", team_id=team_id, scenario_id=scenario.get("id"), workspace=str(workspace))
    start_context = get_data_client().start_context(team_id)
    model_spec = load_model_spec(team_id)
    models = StudentModelRegistry(workspace / "models", model_spec)
    model_status = models.warmup()
    runtime = RuntimeDeps(
        team_id=team_id,
        case=start_context["case"],
        scenario=scenario,
        rag=RagIndex(start_context["knowledge"], workspace / "rag" / "config.yaml"),
        skills=SkillLibrary(workspace / "skills"),
        models=models,
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
    )
    return runtime


def build_agent(model_id: str | None = None) -> Agent:
    model, model_settings = resolve_manager_model(model_id)
    log_event(
        logger,
        "manager.agent.build",
        requested_model_id=model_id,
        resolved_model=model,
        has_custom_model_settings=model_settings is not None,
        tool_count=len(ALL_TOOLS),
    )
    kwargs = {
        "deps_type": RuntimeDeps,
        "output_type": MonthlyOperationsPlan,
        "tools": ALL_TOOLS,
        "instructions": BASE_INSTRUCTIONS,
    }
    if model_settings is not None:
        kwargs["model_settings"] = model_settings
    return Agent(model, **kwargs)


def manager_prompt(deps: RuntimeDeps) -> str:
    visible = deps.scenario.get("visible", {})
    business = {
        "team_id": deps.team_id,
        "business_name": deps.case["name"],
        "operating_context": deps.case["description"],
        "objective": deps.case["objective"],
        "cost_priorities": deps.case.get("cost_priorities", []),
        "service_level_target": deps.case.get("policies", {}).get("service_level_target"),
        "scenario_id": deps.scenario["id"],
        "scenario_title": deps.scenario["title"],
        "visible_information": visible,
    }
    return (
        "Prepare the integrated four-week production and procurement plan for this scenario. "
        "Optimize total operational cost subject to the business constraints.\n\n"
        + json.dumps(business, indent=2)
    )


async def run_manager(
    team_id: str,
    scenario: dict[str, Any],
    model_id: str | None = None,
) -> tuple[MonthlyOperationsPlan, RuntimeDeps]:
    owns_trace = current_trace_id() == "-"
    tokens = set_trace_context() if owns_trace else None
    started = perf_counter()
    try:
        deps = build_runtime(team_id, scenario)
        prompt = manager_prompt(deps)
        agent = build_agent(model_id)
        log_event(
            logger,
            "manager.run.started",
            team_id=team_id,
            scenario_id=scenario.get("id"),
            requested_model_id=model_id,
            prompt=prompt,
            visible_information=scenario.get("visible", {}),
        )
        request_limit = _manager_request_limit()
        log_event(
            logger,
            "manager.usage_limits",
            request_limit=request_limit,
        )
        result = await agent.run(
            prompt,
            deps=deps,
            usage_limits=UsageLimits(request_limit=request_limit),
        )
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
        log_event(
            logger,
            "manager.run.failed",
            level=logging.ERROR,
            team_id=team_id,
            scenario_id=scenario.get("id"),
            duration_ms=round((perf_counter() - started) * 1000, 2),
            error=str(exc),
        )
        raise
    finally:
        if tokens is not None:
            reset_trace_context(tokens)
