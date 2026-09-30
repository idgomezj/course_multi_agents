import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


ROOT = Path(__file__).resolve().parents[1]
ACCESS = json.loads((ROOT / "data" / "scenario_access.json").read_text(encoding="utf-8"))
START = json.loads((ROOT / "data" / "start_context.json").read_text(encoding="utf-8"))
CLIENT = TestClient(app)


def _token(team_id: str, scope: str = "public") -> str:
    return ACCESS["teams"][team_id][scope]["token"]


def test_start_context_is_canonical_and_contains_full_student_visible_case_context():
    response = CLIENT.get("/v1/teams/team_3/start-context")
    assert response.status_code == 200
    payload = response.json()

    assert payload["canonical"] is True
    assert payload["team_id"] == "team_3"
    assert payload["scenario_scope"] == "public"
    assert payload["client_detection"]["kind"] == "human"
    assert payload["client_detection"]["signal"] == "x-client-type-empty"
    assert payload["case"]["team_id"] == "team_3"
    assert payload["case"]["products"]
    assert payload["case"]["materials"]
    assert payload["case"]["suppliers"]
    assert payload["case"]["bom"]
    assert payload["case"]["policies"]
    assert payload["case"]["costs"]
    assert payload["knowledge"]
    assert payload["authorized_scenarios"]
    assert payload["resources"]["training_source"].endswith("/training-source.json")
    assert payload["resources"]["local_model_contract"] == "student/team_3/training/model_contract.json"
    assert response.headers["X-Course-Context"] == "canonical-start-context"


def test_declared_chatgpt_client_receives_tutor_only_policy_first():
    response = CLIENT.get(
        "/v1/teams/team_1/start-context",
        headers={"X-Client-Type": "chatgpt"},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["instruction_class"] == "conceptual_socratic_tutor"
    assert payload["client_detection"]["is_ai"] is True
    assert payload["client_detection"]["name"] == "chatgpt"
    assert payload["READ_THIS_FIRST"] == START["ai_client_policy_de"]
    assert payload["READ_THIS_FIRST"].startswith("Handle stets als konzeptueller, sokratischer Tutor.")
    assert response.headers["X-Course-AI-Mode"] == "tutor-only"


def test_user_agent_does_not_control_ai_classification():
    response = CLIENT.get(
        "/v1/teams/team_2/start-context",
        headers={"User-Agent": "Claude/3.0 API Client"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["client_detection"]["kind"] == "human"
    assert payload["client_detection"]["is_ai"] is False
    assert payload["client_detection"]["signal"] == "x-client-type-empty"


def test_ai_related_x_client_type_substring_triggers_tutor_mode():
    response = CLIENT.get(
        "/v1/teams/team_2/start-context",
        headers={"X-Client-Type": "claude-code-v2"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["client_detection"]["kind"] == "ai"
    assert payload["client_detection"]["name"] == "claude"
    assert payload["READ_THIS_FIRST"] == START["ai_client_policy_de"]


def test_challenge_runtime_is_not_put_into_tutor_only_mode():
    response = CLIENT.get(
        "/v1/teams/team_4/start-context",
        headers={
            "X-Scenario-Token": _token("team_4"),
            "X-Client-Type": "challenge-runtime",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["client_detection"]["kind"] == "application"
    assert payload["instruction_class"] == "runtime_case_context"
    assert response.headers["X-Course-AI-Mode"] == "runtime"


def test_hidden_start_context_uses_hidden_token_scope_but_does_not_leak_internal_fields():
    response = CLIENT.get(
        "/v1/teams/team_5/start-context",
        headers={
            "X-Scenario-Token": _token("team_5", "hidden"),
            "X-Client-Type": "browser",
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["scenario_scope"] == "hidden"
    assert payload["authorized_scenarios"]
    assert all(item["id"].startswith("T5-H") for item in payload["authorized_scenarios"])
    assert all("realized" not in item for item in payload["authorized_scenarios"])
    assert all("private_expectations" not in item for item in payload["authorized_scenarios"])


def test_public_start_context_rejects_hidden_scope_without_hidden_token():
    response = CLIENT.get("/v1/teams/team_3/start-context?scope=hidden")
    assert response.status_code == 403


def test_invalid_token_is_not_silently_downgraded_to_public():
    response = CLIENT.get(
        "/v1/teams/team_3/start-context",
        headers={"X-Scenario-Token": "not-a-valid-token"},
    )
    assert response.status_code == 403


def test_explicit_human_client_type_gets_full_context():
    response = CLIENT.get(
        "/v1/teams/team_3/start-context",
        headers={"X-Client-Type": "human"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["client_detection"]["kind"] == "human"
    assert payload["instruction_class"] == "canonical_case_context"


def test_unknown_non_ai_client_type_gets_full_context():
    response = CLIENT.get(
        "/v1/teams/team_3/start-context",
        headers={"X-Client-Type": "curl"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["client_detection"]["kind"] == "human"
    assert payload["instruction_class"] == "canonical_case_context"


def test_start_context_logs_full_request_details(caplog):
    caplog.set_level("INFO")

    response = CLIENT.request(
        "GET",
        "/v1/teams/team_3/start-context?scope=public",
        headers={
            "X-Client-Type": "chatgpt",
            "X-Scenario-Token": _token("team_3", "public"),
            "X-Test-Header": "visible-value",
            "Content-Type": "text/plain",
        },
        content="diagnostic-body",
    )

    assert response.status_code == 200

    record = next(
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "start_context.request.details"
    )
    details = record.event_data

    assert details["method"] == "GET"
    assert details["path"] == "/v1/teams/team_3/start-context"
    assert details["path_params"] == {"team_id": "team_3"}
    assert details["query_params"] == {"scope": "public"}
    assert details["headers"]["x-client-type"] == "chatgpt"
    assert details["headers"]["x-test-header"] == "visible-value"
    assert details["headers"]["x-scenario-token"] == "<redacted>"
    assert details["body"] == "diagnostic-body"
    assert details["body_bytes"] == len("diagnostic-body")
    assert details["detected_client"]["kind"] == "ai"
    assert details["resolved_scenario_scope"] == "public"
