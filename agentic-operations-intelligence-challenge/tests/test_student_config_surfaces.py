from pathlib import Path

import pytest

from challenge.rag import RagIndex
from challenge.student_config import (
    config_file_status,
    load_feature_config,
    load_runtime_config,
    load_training_config,
)


@pytest.mark.parametrize("team_id", [f"team_{i}" for i in range(1, 6)])
def test_every_team_has_complete_student_config_surface(team_id):
    status = config_file_status(team_id)
    assert status
    assert all(status.values()), status

    runtime = load_runtime_config(team_id)
    assert pytest.approx(sum(runtime["forecast_policy"]["weights"].values()), abs=1e-9) == 1.0
    assert pytest.approx(sum(runtime["planning_objectives"]["priorities"].values()), abs=1e-9) == 1.0
    assert runtime["risk_policy"]["high_threshold"] > runtime["risk_policy"]["medium_threshold"]
    assert runtime["tool_policy"]["required_before_finalize"]
    assert 1 <= runtime["manager_llm"]["max_rag_documents"] <= 12

    training = load_training_config(team_id)
    assert set(training["models"]) == {"model_a", "model_b"}
    assert training["validation"]["method"] in {"chronological", "random"}


@pytest.mark.parametrize("team_id", [f"team_{i}" for i in range(1, 6)])
def test_feature_config_preserves_fixed_contract_names(team_id):
    feature_cfg = load_feature_config(team_id)
    assert set(feature_cfg["models"]) == {"model_a", "model_b"}
    for model in feature_cfg["models"].values():
        assert model["enabled_features"]
        assert not set(model["enabled_features"]) & set(model["disabled_features"])


def test_rag_document_authority_changes_ranking_without_editing_source(tmp_path: Path):
    config = tmp_path / "config.yaml"
    config.write_text(
        "chunk_size: 80\noverlap: 10\ntop_k: 2\nmin_score: 0.0\nngram_max: 2\n",
        encoding="utf-8",
    )
    documents = [
        {
            "name": "current_policy.md",
            "content": "Current policy requires service protection, inventory control and total cost review.",
        },
        {
            "name": "legacy_policy.md",
            "content": "Legacy policy requires service protection, inventory control and total cost review.",
        },
    ]
    priorities = {
        "default_weight": 1.0,
        "authority_weights": {"official": 1.2, "obsolete": 0.3},
        "documents": {
            "current_policy.md": {"authority": "official", "weight": 1.2},
            "legacy_policy.md": {"authority": "obsolete", "weight": 0.5},
        },
    }

    index = RagIndex(documents, config, document_priorities=priorities)
    results = index.search("service inventory total cost", top_k=2)

    assert results[0]["source"] == "current_policy.md"
    assert results[0]["authority"] == "official"
    assert "Legacy policy" in documents[1]["content"]  # source content was not rewritten
