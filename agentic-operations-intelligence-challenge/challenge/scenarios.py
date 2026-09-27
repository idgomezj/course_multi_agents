from __future__ import annotations

from copy import deepcopy
from typing import Any

from .config import load_case


def list_public_scenarios(team_id: str) -> list[dict[str, Any]]:
    case = load_case(team_id)
    return deepcopy(case.get("public_scenarios", []))


def get_public_scenario(team_id: str, scenario_id: str) -> dict[str, Any]:
    for scenario in list_public_scenarios(team_id):
        if scenario["id"] == scenario_id:
            return scenario
    raise ValueError(f"Unknown public scenario {scenario_id} for {team_id}")


def student_visible_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": scenario["id"],
        "title": scenario["title"],
        "description": scenario.get("description", ""),
        "visible": scenario.get("visible", {}),
    }
