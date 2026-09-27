from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any

from dotenv import load_dotenv
from pydantic_ai import Agent

from app.store import load_case, load_knowledge, load_model_spec
from app.observability import current_trace_id, log_event, reset_trace_context, set_trace_context
from .config import DEMO_MODELS_DIR, DEMO_RAG_CONFIG, DEMO_SKILLS_DIR
from .llm_config import resolve_manager_model
from .model_registry import StudentModelRegistry
from .rag import RagIndex
from .runtime import RuntimeDeps
from .schemas import MonthlyOperationsPlan
from .skills import SkillLibrary
from .tools import ALL_TOOLS

load_dotenv()

logger = logging.getLogger(__name__)

TEAM_ID = "team_0"

BASE_INSTRUCTIONS = """
You are the Operations Manager Agent for the fully solved Case 0 manufacturing planning demo.

Your job is to create a four-week integrated production and procurement plan that meets
service and policy requirements while minimizing total operational cost.

This is a worked teaching example. Use the supplied RAG documents, Skills, specialist
PyTorch models, deterministic calculations, cost tools and validation tools.

Rules:
1. Never invent inventory, BOM, supplier, capacity, policy or cost data.
2. Inspect the available Skills and retrieve relevant company evidence.
3. Forecast demand with the trained PyTorch model when appropriate.
4. Check inventory and existing POs before recommending new purchases.
5. Use supplier-delay prediction when delivery timing matters.
6. Compare total operational cost, not only unit purchase price.
7. Respect capacity, supplier authorization, MOQ, approvals and the service target.
8. Run validate_plan before finalizing; revise if critical violations remain.
9. Return a plan matching the structured output schema.
"""


def build_runtime(scenario: dict[str, Any]) -> RuntimeDeps:
    log_event(logger, "manager.runtime.build.started", team_id=TEAM_ID, scenario_id=scenario.get("id"))
    case = load_case(TEAM_ID)
    knowledge = list(load_knowledge(TEAM_ID))
    models = StudentModelRegistry(DEMO_MODELS_DIR, load_model_spec(TEAM_ID))
    model_status = models.warmup()
    runtime = RuntimeDeps(
        team_id=TEAM_ID,
        case=case,
        scenario=scenario,
        rag=RagIndex(knowledge, DEMO_RAG_CONFIG),
        skills=SkillLibrary(DEMO_SKILLS_DIR),
        models=models,
    )
    log_event(logger, "manager.runtime.build.completed", team_id=TEAM_ID, scenario_id=scenario.get("id"), knowledge_documents=len(knowledge), skill_directory=str(DEMO_SKILLS_DIR), model_directory=str(DEMO_MODELS_DIR), model_warmup=model_status)
    return runtime


def build_agent(model_id: str | None = None) -> Agent:
    model, model_settings = resolve_manager_model(model_id)
    log_event(logger, "manager.agent.build", requested_model_id=model_id, resolved_model=model, has_custom_model_settings=model_settings is not None, tool_count=len(ALL_TOOLS))
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
        "team_id": TEAM_ID,
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
        "Prepare the integrated four-week production and procurement plan for Case 0. "
        "Use the worked-example Skills and company knowledge, but solve the selected scenario "
        "through the normal agent/tool pipeline. Optimize total operational cost subject to constraints.\n\n"
        + json.dumps(business, indent=2)
    )


async def run_manager(scenario: dict[str, Any], model_id: str | None = None):
    owns_trace = current_trace_id() == "-"
    tokens = set_trace_context() if owns_trace else None
    started = perf_counter()
    try:
        deps = build_runtime(scenario)
        prompt = manager_prompt(deps)
        agent = build_agent(model_id)
        log_event(logger, "manager.run.started", team_id=TEAM_ID, scenario_id=scenario.get("id"), requested_model_id=model_id, prompt=prompt, visible_information=scenario.get("visible", {}))
        result = await agent.run(prompt, deps=deps)
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
        log_event(logger, "manager.run.failed", level=logging.ERROR, team_id=TEAM_ID, scenario_id=scenario.get("id"), duration_ms=round((perf_counter()-started)*1000, 2), error=str(exc))
        raise
    finally:
        if tokens is not None:
            reset_trace_context(tokens)
