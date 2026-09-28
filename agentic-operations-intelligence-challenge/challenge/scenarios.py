from __future__ import annotations

from copy import deepcopy
from typing import Any

from .data_api import get_data_client


def list_public_scenarios(team_id: str) -> list[dict[str, Any]]:
    return deepcopy(get_data_client().get_public_scenarios(team_id))


def get_public_scenario(team_id: str, scenario_id: str) -> dict[str, Any]:
    return deepcopy(get_data_client().get_public_scenario(team_id, scenario_id))


def student_visible_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": scenario["id"],
        "title": scenario["title"],
        "description": scenario.get("description", ""),
        "visible": scenario.get("visible", {}),
    }
