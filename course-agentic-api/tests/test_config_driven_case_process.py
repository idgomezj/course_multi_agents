from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import available_teams, case_without_scenarios, load_knowledge, load_training_source
from demo_app.rag import RagIndex
from demo_app.student_config import config_status, load_runtime_config, load_training_config


CLIENT = TestClient(app)


def test_every_case_exposes_richer_company_reasoning_context():
    for team_id in available_teams():
        case = case_without_scenarios(team_id)
        assert case["company_profile"]["legal_name"]
        assert case["customer_priorities"]
        assert case["constraints"]["monthly_operating_budget"] > 0
        assert case["constraints"]["max_monthly_overtime_hours"] >= 0
        assert case["constraints"]["max_expedited_units"] >= 0
        assert case["constraints"]["max_finished_goods_inventory_units"] > 0
        assert case["data_quality_context"]["raw_history_is_imperfect"] is True
        assert case["decision_signals"]["may_disagree"]


def test_each_case_knowledge_contains_current_obsolete_draft_and_irrelevant_sources():
    for team_id in available_teams():
        names = {doc["name"] for doc in load_knowledge(team_id)}
        assert "operations_policy.md" in names
        assert "supplier_contracts.md" in names
        assert "legacy_policy_2024.md" in names
        assert "planning_draft.md" in names
        assert "travel_reimbursement_policy.md" in names
        assert "office_parking_rules.md" in names


def test_team_training_sources_describe_imperfections():
    for team_id in available_teams():
        payload = load_training_source(team_id)
        assert payload["record_count"] == len(payload["records"])
        assert payload["data_quality_notes"]["raw_source"] is True
        assert payload["data_quality_notes"]["not_training_ready"] is True
        assert payload["data_quality_notes"]["expected_issues"]
        assert payload.get("analysis_expectations")


def test_case0_raw_training_sample_contains_worked_data_quality_problems():
    payload = load_training_source("team_0")
    assert payload["dataset"] == "case0_worked_raw_training_sample"
    records = payload["records"]
    assert any(row.get("record_id", "").endswith("-DUP") for row in records)
    assert any(any(value is None for value in row.values()) for row in records)
    assert any(str(row.get("supplier_id", "")).strip() != str(row.get("supplier_id", "")) for row in records if "supplier_id" in row)


def test_case0_solved_configuration_is_complete_and_loaded():
    status = config_status()
    assert status
    assert all(status.values())

    runtime = load_runtime_config()
    assert pytest.approx(sum(runtime["forecast_policy"]["weights"].values()), abs=1e-9) == 1.0
    assert runtime["risk_policy"]["high_threshold"] > runtime["risk_policy"]["medium_threshold"]
    assert pytest.approx(sum(runtime["planning_objectives"]["priorities"].values()), abs=1e-9) == 1.0

    training = load_training_config()
    assert set(training["models"]) == {"model_a", "model_b"}
    assert training["validation"]["method"] == "chronological"


def test_case0_demo_config_endpoint_exposes_reference_settings():
    response = CLIENT.get("/demo/api/config")
    assert response.status_code == 200
    payload = response.json()
    assert payload["team_id"] == "team_0"
    assert all(payload["config_files"].values())
    assert payload["runtime"]["forecast_policy"]["weights"]["model_a"] > 0
    assert payload["runtime"]["document_priorities"]["documents"]["legacy_policy_2024.md"]["authority"] == "obsolete"


def test_case0_document_authority_can_outrank_legacy_noise(tmp_path: Path):
    config = tmp_path / "config.yaml"
    config.write_text("chunk_size: 80\noverlap: 10\ntop_k: 2\nmin_score: 0.0\nngram_max: 2\n", encoding="utf-8")
    documents = [
        {"name": "operations_policy.md", "content": "Current official policy says protect service while controlling inventory and total operational cost."},
        {"name": "legacy_policy_2024.md", "content": "Old inventory policy says protect service while holding much more inventory and choosing low unit cost."},
    ]
    priorities = {
        "default_weight": 1.0,
        "authority_weights": {"official": 1.2, "obsolete": 0.3},
        "documents": {
            "operations_policy.md": {"authority": "official", "weight": 1.2},
            "legacy_policy_2024.md": {"authority": "obsolete", "weight": 0.5},
        },
    }
    index = RagIndex(documents, config, document_priorities=priorities)
    results = index.search("service inventory operational cost", top_k=2)
    assert results
    assert results[0]["source"] == "operations_policy.md"
    assert results[0]["authority"] == "official"
