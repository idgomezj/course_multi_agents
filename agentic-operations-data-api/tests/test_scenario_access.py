import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


ROOT = Path(__file__).resolve().parents[1]
ACCESS = json.loads((ROOT / "data" / "scenario_access.json").read_text(encoding="utf-8"))
CLIENT = TestClient(app)


def _token(team_id: str, scope: str) -> str:
    return ACCESS["teams"][team_id][scope]["token"]


def test_public_token_lists_only_public_scenarios_and_safe_fields():
    response = CLIENT.get(
        "/v1/teams/team_1/scenarios",
        headers={"X-Scenario-Token": _token("team_1", "public")},
    )
    assert response.status_code == 200
    scenarios = response.json()
    assert scenarios
    assert all(item["id"].startswith("T1-P") for item in scenarios)
    assert all("realized" not in item for item in scenarios)
    assert all("benchmark_cost" in item for item in scenarios)
    assert all(isinstance(item["benchmark_cost"], (int, float)) for item in scenarios)
    assert all("public_expectations" not in item for item in scenarios)


def test_hidden_token_lists_only_hidden_scenarios_and_hides_visible_until_detail():
    token = _token("team_1", "hidden")
    response = CLIENT.get(
        "/v1/teams/team_1/scenarios",
        headers={"X-Scenario-Token": token},
    )
    assert response.status_code == 200
    scenarios = response.json()
    assert scenarios
    assert all(item["id"].startswith("T1-H") for item in scenarios)
    assert all("visible" not in item for item in scenarios)

    scenario_id = scenarios[0]["id"]
    detail = CLIENT.get(
        f"/v1/teams/team_1/scenarios/{scenario_id}",
        headers={"X-Scenario-Token": token},
    )
    assert detail.status_code == 200
    payload = detail.json()
    assert "visible" in payload
    assert "realized" not in payload
    assert "benchmark_cost" not in payload
    assert "private_expectations" not in payload


def test_public_and_hidden_tokens_are_not_interchangeable_on_explicit_routes():
    public = CLIENT.get(
        "/v1/teams/team_1/scenarios/hidden",
        headers={"X-Scenario-Token": _token("team_1", "public")},
    )
    hidden = CLIENT.get(
        "/v1/teams/team_1/scenarios/public",
        headers={"X-Scenario-Token": _token("team_1", "hidden")},
    )
    assert public.status_code == 403
    assert hidden.status_code == 403


def test_team_token_cannot_cross_team_boundary():
    response = CLIENT.get(
        "/v1/teams/team_2/scenarios",
        headers={"X-Scenario-Token": _token("team_1", "public")},
    )
    assert response.status_code == 403


def test_bootstrap_does_not_leak_scenarios():
    response = CLIENT.get(
        "/v1/teams/team_1/bootstrap",
        headers={"X-Scenario-Token": _token("team_1", "public")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "public_scenarios" not in payload
    assert "hidden_scenarios" not in payload
