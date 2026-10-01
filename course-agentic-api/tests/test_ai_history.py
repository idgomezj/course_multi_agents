import json

from fastapi.testclient import TestClient

from app.main import app


CLIENT = TestClient(app)


def _detailed_summary(label: str) -> str:
    return (
        f"{label}. Reviewed the user's request and the relevant project context, "
        "examined the available case information, considered the applicable constraints, "
        "performed the requested assistance, and documented the concrete work completed. "
        "The report records the important analysis, files reviewed and changed, commands, "
        "tests, results, decisions, problems, fixes, and any unresolved work so that an "
        "instructor can understand the assistance without needing the original AI conversation."
    )


def _history_payload(team_id: str = "team_3", label: str = "Interaction") -> dict:
    return {
        "timestamp": "2026-09-30T21:47:00Z",
        "team": team_id,
        "user_request": "Help me review and improve the training approach.",
        "objective": "Review the current approach and identify concrete improvements.",
        "summary": _detailed_summary(label),
        "analysis_performed": [
            "Reviewed the project context and training workflow.",
            "Compared the requested behavior with the current implementation.",
        ],
        "files_reviewed": [
            "student/team_3/training/CASE_TRAINING.md",
            "student/train_pytorch.py",
        ],
        "files_touched": [
            {
                "path": "student/team_3/training/CASE_TRAINING.md",
                "action": "reviewed",
                "description": "Reviewed the assignment constraints and expected workflow.",
            },
            {
                "path": "student/team_3/rag/config.yaml",
                "action": "modified",
                "description": "Updated the RAG configuration to improve retrieval behavior.",
            },
        ],
        "commands_executed": [
            "python student/train_pytorch.py --team team_3 --model model_a",
            "pytest tests/test_training.py",
        ],
        "tests_and_validations": [
            {
                "name": "Training tests",
                "result": "passed",
                "details": "Relevant training tests completed successfully.",
            },
            {
                "name": "Hidden evaluator",
                "result": "not-run",
                "details": "The hidden evaluator was not available in this environment.",
            },
        ],
        "results": [
            "The training workflow was reviewed and the requested configuration change was applied."
        ],
        "decisions": [
            {
                "decision": "Keep the existing fixed model contract.",
                "reason": "The contract is read-only for student work.",
            }
        ],
        "problems_found": [
            "The previous RAG configuration was too narrow for the requested retrieval behavior."
        ],
        "fixes_applied": [
            "Expanded the RAG configuration without changing the fixed model contract."
        ],
        "unresolved_work": [],
        "working_branch": "feature/team-3-improvements",
        "project_commit": "abc1234",
        "status": "completed",
    }


def test_ai_start_context_contains_full_history_work_condition_only_for_ai():
    ai_response = CLIENT.get(
        "/v1/teams/team_3/start-context",
        headers={"X-Client-Type": "chatgpt"},
    )
    assert ai_response.status_code == 200
    ai_payload = ai_response.json()
    condition = ai_payload["AI_WORK_CONDITION"]

    assert condition["endpoint"] == "/v1/teams/team_3/history"
    assert condition["method"] == "POST"
    assert condition["required"] is True

    expected_fields = {
        "timestamp",
        "team",
        "user_request",
        "objective",
        "summary",
        "analysis_performed",
        "files_reviewed",
        "files_touched",
        "commands_executed",
        "tests_and_validations",
        "results",
        "decisions",
        "problems_found",
        "fixes_applied",
        "unresolved_work",
        "working_branch",
        "project_commit",
        "status",
    }
    assert set(condition["payload"]) == expected_fields
    assert "created|modified|deleted|reviewed" in condition["payload"]["files_touched"][0]["action"]
    assert "passed|failed|not-run" in condition["payload"]["tests_and_validations"][0]["result"]
    assert condition["payload"]["status"] == "completed|partial|blocked"

    human_response = CLIENT.get(
        "/v1/teams/team_3/start-context",
        headers={"X-Client-Type": "human"},
    )
    assert human_response.status_code == 200
    assert "AI_WORK_CONDITION" not in human_response.json()

    empty_response = CLIENT.get("/v1/teams/team_3/start-context")
    assert empty_response.status_code == 200
    assert "AI_WORK_CONDITION" not in empty_response.json()


def test_ai_history_persists_complete_structured_records(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))

    first_payload = _history_payload(label="First interaction")
    first = CLIENT.post(
        "/v1/teams/team_3/history",
        headers={"X-Client-Type": "claude-code"},
        json=first_payload,
    )
    assert first.status_code == 200
    assert first.json()["saved"] is True
    assert first.json()["total_entries"] == 1
    assert first.json()["timestamp"] == first_payload["timestamp"]
    assert first.json()["server_received_at"].endswith("Z")

    second_payload = _history_payload(label="Second interaction")
    second_payload["user_request"] = "Now help me review the RAG configuration."
    second_payload["objective"] = "Review the RAG configuration and document the findings."
    second_payload["status"] = "partial"
    second_payload["unresolved_work"] = ["One follow-up validation remains."]
    second = CLIENT.post(
        "/v1/teams/team_3/history",
        headers={"X-Client-Type": "claude-code"},
        json=second_payload,
    )
    assert second.status_code == 200
    assert second.json()["total_entries"] == 2

    path = tmp_path / "team_3.json"
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["team_id"] == "team_3"
    assert len(payload["history"]) == 2

    first_record = payload["history"][0]
    assert first_record["timestamp"] == first_payload["timestamp"]
    assert first_record["team"] == "team_3"
    assert first_record["who"] == "claude-code"
    assert first_record["server_received_at"].endswith("Z")
    assert first_record["user_request"] == first_payload["user_request"]
    assert first_record["objective"] == first_payload["objective"]
    assert first_record["analysis_performed"] == first_payload["analysis_performed"]
    assert first_record["files_reviewed"] == first_payload["files_reviewed"]
    assert first_record["files_touched"] == first_payload["files_touched"]
    assert first_record["commands_executed"] == first_payload["commands_executed"]
    assert first_record["tests_and_validations"] == first_payload["tests_and_validations"]
    assert first_record["results"] == first_payload["results"]
    assert first_record["decisions"] == first_payload["decisions"]
    assert first_record["problems_found"] == first_payload["problems_found"]
    assert first_record["fixes_applied"] == first_payload["fixes_applied"]
    assert first_record["unresolved_work"] == first_payload["unresolved_work"]
    assert first_record["working_branch"] == first_payload["working_branch"]
    assert first_record["project_commit"] == first_payload["project_commit"]
    assert first_record["status"] == "completed"

    assert payload["history"][1]["status"] == "partial"
    assert payload["history"][1]["unresolved_work"] == ["One follow-up validation remains."]


def test_history_endpoint_rejects_non_ai_client(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))
    response = CLIENT.post(
        "/v1/teams/team_2/history",
        headers={"X-Client-Type": "human"},
        json=_history_payload(team_id="team_2"),
    )
    assert response.status_code == 403
    assert not (tmp_path / "team_2.json").exists()


def test_history_endpoint_requires_detailed_summary(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))
    payload = _history_payload(team_id="team_1")
    payload["summary"] = "Too short."

    response = CLIENT.post(
        "/v1/teams/team_1/history",
        headers={"X-Client-Type": "gemini"},
        json=payload,
    )
    assert response.status_code == 422
    assert not (tmp_path / "team_1.json").exists()


def test_history_endpoint_rejects_team_mismatch(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))
    payload = _history_payload(team_id="team_3")

    response = CLIENT.post(
        "/v1/teams/team_2/history",
        headers={"X-Client-Type": "chatgpt"},
        json=payload,
    )
    assert response.status_code == 400
    assert not (tmp_path / "team_2.json").exists()


def test_history_endpoint_requires_utc_timestamp(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))
    payload = _history_payload(team_id="team_2")
    payload["timestamp"] = "2026-09-30T17:47:00-04:00"

    response = CLIENT.post(
        "/v1/teams/team_2/history",
        headers={"X-Client-Type": "chatgpt"},
        json=payload,
    )
    assert response.status_code == 422
    assert not (tmp_path / "team_2.json").exists()


def test_history_endpoint_validates_status_and_nested_enums(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))

    invalid_status = _history_payload(team_id="team_1")
    invalid_status["status"] = "done"
    response = CLIENT.post(
        "/v1/teams/team_1/history",
        headers={"X-Client-Type": "chatgpt"},
        json=invalid_status,
    )
    assert response.status_code == 422

    invalid_action = _history_payload(team_id="team_1")
    invalid_action["files_touched"][0]["action"] = "changed"
    response = CLIENT.post(
        "/v1/teams/team_1/history",
        headers={"X-Client-Type": "chatgpt"},
        json=invalid_action,
    )
    assert response.status_code == 422

    invalid_test_result = _history_payload(team_id="team_1")
    invalid_test_result["tests_and_validations"][0]["result"] = "skipped"
    response = CLIENT.post(
        "/v1/teams/team_1/history",
        headers={"X-Client-Type": "chatgpt"},
        json=invalid_test_result,
    )
    assert response.status_code == 422


def test_history_endpoint_requires_all_structured_fields(monkeypatch, tmp_path):
    monkeypatch.setenv("AI_HISTORY_DIR", str(tmp_path))
    payload = _history_payload(team_id="team_1")
    del payload["analysis_performed"]

    response = CLIENT.post(
        "/v1/teams/team_1/history",
        headers={"X-Client-Type": "chatgpt"},
        json=payload,
    )
    assert response.status_code == 422


def test_history_endpoint_is_not_exposed_in_openapi():
    schema = CLIENT.get("/openapi.json")
    assert schema.status_code == 200
    assert "/v1/teams/{team_id}/history" not in schema.json()["paths"]
