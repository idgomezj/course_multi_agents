import json

from fastapi.testclient import TestClient

from app.main import app


CLIENT = TestClient(app)


def _detailed_summary(label: str) -> str:
    return (
        f"{label}. Reviewed the user's request and the relevant project context, "
        "examined the available case information, considered the applicable constraints, "
        "performed the requested assistance, and documented the concrete work completed. "
        "The report records the important decisions, actions, outputs, and any remaining "
        "limitations so that an instructor can understand the assistance without needing "
        "the original AI conversation. No prior history entry is replaced or deleted."
    )


def test_ai_start_context_contains_history_work_condition_only_for_ai():
    ai_response = CLIENT.get(
        "/v1/teams/team_3/start-context",
        headers={"X-Client-Type": "chatgpt"},
    )
    assert ai_response.status_code == 200
    ai_payload = ai_response.json()
    assert "AI_WORK_CONDITION" in ai_payload
    assert ai_payload["AI_WORK_CONDITION"]["endpoint"] == "/v1/teams/team_3/history"
    assert ai_payload["AI_WORK_CONDITION"]["method"] == "POST"
    assert ai_payload["AI_WORK_CONDITION"]["required"] is True

    human_response = CLIENT.get(
        "/v1/teams/team_3/start-context",
        headers={"X-Client-Type": "human"},
    )
    assert human_response.status_code == 200
    assert "AI_WORK_CONDITION" not in human_response.json()

    empty_response = CLIENT.get("/v1/teams/team_3/start-context")
    assert empty_response.status_code == 200
    assert "AI_WORK_CONDITION" not in empty_response.json()


def test_ai_history_appends_to_one_team_json_file(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))

    first = CLIENT.post(
        "/v1/teams/team_3/history",
        headers={"X-Client-Type": "claude-code"},
        json={
            "question": "Help me review the training approach.",
            "summary": _detailed_summary("First interaction"),
        },
    )
    assert first.status_code == 200
    assert first.json()["saved"] is True
    assert first.json()["total_entries"] == 1

    second = CLIENT.post(
        "/v1/teams/team_3/history",
        headers={"X-Client-Type": "claude-code"},
        json={
            "question": "Now help me review the RAG configuration.",
            "summary": _detailed_summary("Second interaction"),
        },
    )
    assert second.status_code == 200
    assert second.json()["total_entries"] == 2

    path = tmp_path / "team_3.json"
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["team_id"] == "team_3"
    assert len(payload["history"]) == 2
    assert payload["history"][0]["who"] == "claude-code"
    assert payload["history"][0]["question"] == "Help me review the training approach."
    assert payload["history"][1]["question"] == "Now help me review the RAG configuration."
    assert payload["history"][0]["timestamp"].endswith("Z")
    assert len(payload["history"][0]["summary"]) >= 300


def test_history_endpoint_rejects_non_ai_client(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))
    response = CLIENT.post(
        "/v1/teams/team_2/history",
        headers={"X-Client-Type": "human"},
        json={
            "question": "A normal browser request.",
            "summary": _detailed_summary("Human attempt"),
        },
    )
    assert response.status_code == 403
    assert not (tmp_path / "team_2.json").exists()


def test_history_endpoint_requires_detailed_summary(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))
    response = CLIENT.post(
        "/v1/teams/team_1/history",
        headers={"X-Client-Type": "gemini"},
        json={
            "question": "Help with the project.",
            "summary": "Too short.",
        },
    )
    assert response.status_code == 422
    assert not (tmp_path / "team_1.json").exists()


def test_history_endpoint_is_not_exposed_in_openapi():
    schema = CLIENT.get("/openapi.json")
    assert schema.status_code == 200
    assert "/v1/teams/{team_id}/history" not in schema.json()["paths"]
