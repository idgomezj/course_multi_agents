"""Transient end-to-end runtime smoke validation for every configured scenario.

This intentionally does not solve or persist Team 1-5 plans. It builds the real runtime,
runs the real Pydantic-AI tool/output pipeline with TestModel, and discards outputs.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COURSE_DIR = ROOT / "course-agentic-api"
CHALLENGE_DIR = ROOT / "agentic-operations-intelligence-challenge"
sys.path.insert(0, str(COURSE_DIR))
sys.path.insert(0, str(CHALLENGE_DIR))

# Let production DeepSeek agent construction run without making a provider request.
os.environ.setdefault("DEEPSEEK_API_KEY", "offline-validation-key")

from pydantic_ai.models.test import TestModel
from pydantic_ai.usage import UsageLimits

from app.store import case_without_scenarios, hidden_scenarios, load_knowledge, public_scenarios
from demo_app.manager import (
    build_agent as build_demo_agent,
    build_runtime as build_demo_runtime,
    manager_prompt as demo_manager_prompt,
)
from demo_app.schemas import MonthlyOperationsPlan as DemoPlan
from challenge import manager as challenge_manager
from challenge.schemas import MonthlyOperationsPlan as ChallengePlan


TOOLS_TO_EXERCISE = ["get_business_constraints", "get_inventory", "list_skills"]


class LocalDataClient:
    """In-process Data API adapter used only by this validation script."""

    def start_context(self, team_id: str) -> dict:
        return {
            "case": case_without_scenarios(team_id),
            "knowledge": list(load_knowledge(team_id)),
        }


async def _run_demo_scenario(scenario: dict) -> None:
    deps = build_demo_runtime(scenario)
    agent = build_demo_agent("deepseek", deps.student_config)
    with agent.override(model=TestModel(call_tools=TOOLS_TO_EXERCISE)):
        result = await agent.run(
            demo_manager_prompt(deps),
            deps=deps,
            usage_limits=UsageLimits(request_limit=10),
        )
    assert isinstance(result.output, DemoPlan)
    assert TOOLS_TO_EXERCISE == [name for name in TOOLS_TO_EXERCISE if name in {x["tool"] for x in deps.trace}]
    result.output.team_id = "team_0"
    result.output.scenario_id = scenario["id"]


async def _run_student_scenario(team_id: str, scenario: dict) -> None:
    deps = challenge_manager.build_runtime(team_id, scenario)
    agent = challenge_manager.build_agent("deepseek", deps.student_config)
    with agent.override(model=TestModel(call_tools=TOOLS_TO_EXERCISE)):
        result = await agent.run(
            challenge_manager.manager_prompt(deps),
            deps=deps,
            usage_limits=UsageLimits(request_limit=10),
        )
    assert isinstance(result.output, ChallengePlan)
    called = {entry["tool"] for entry in deps.trace}
    assert set(TOOLS_TO_EXERCISE).issubset(called)
    # Keep this transient: assign identifiers in memory only and never write the plan.
    result.output.team_id = team_id
    result.output.scenario_id = scenario["id"]


async def main() -> None:
    # The challenge normally calls the deployed Data API. For CI, use the exact same
    # local case/knowledge data so hidden/public scenarios can be exercised safely.
    challenge_manager.get_data_client = lambda: LocalDataClient()

    demo_scenarios = public_scenarios("team_0")
    assert {s["id"] for s in demo_scenarios} == {"T0-P01", "T0-P02", "T0-P03"}
    for scenario in demo_scenarios:
        await _run_demo_scenario(scenario)

    tested = len(demo_scenarios)
    for team_id in [f"team_{i}" for i in range(1, 6)]:
        scenarios = [*public_scenarios(team_id), *hidden_scenarios(team_id)]
        assert scenarios, f"No scenarios found for {team_id}"
        for scenario in scenarios:
            await _run_student_scenario(team_id, scenario)
            tested += 1

    print(f"Validated {tested} scenarios transiently; no Team 1-5 solution was persisted.")


if __name__ == "__main__":
    asyncio.run(main())
