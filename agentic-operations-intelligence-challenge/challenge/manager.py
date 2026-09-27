from __future__ import annotations

import json
from typing import Any

from dotenv import load_dotenv
from pydantic_ai import Agent

from .config import student_path
from .data_api import get_data_client
from .llm_config import resolve_manager_model
from .model_registry import StudentModelRegistry
from .rag import RagIndex
from .runtime import RuntimeDeps
from .schemas import MonthlyOperationsPlan
from .skills import SkillLibrary
from .tools import ALL_TOOLS

load_dotenv()


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
    bootstrap = get_data_client().bootstrap(team_id)
    return RuntimeDeps(
        team_id=team_id,
        case=bootstrap["case"],
        scenario=scenario,
        rag=RagIndex(bootstrap["knowledge"], workspace / "rag" / "config.yaml"),
        skills=SkillLibrary(workspace / "skills"),
        models=StudentModelRegistry(workspace / "models", bootstrap["model_spec"]),
    )


def build_agent(model_id: str | None = None) -> Agent:
    model, model_settings = resolve_manager_model(model_id)
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
    deps = build_runtime(team_id, scenario)
    agent = build_agent(model_id)
    result = await agent.run(manager_prompt(deps), deps=deps)
    plan = result.output
    plan.team_id = team_id
    plan.scenario_id = scenario["id"]
    return plan, deps
