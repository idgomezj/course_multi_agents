from pathlib import Path

import pytest

from challenge.api import app
from challenge.training_data import (
    load_model_spec,
    load_training_frame,
    training_source_url,
)


@pytest.mark.parametrize("team_id", [f"team_{i}" for i in range(1, 6)])
def test_model_contract_is_local_and_training_source_is_api_json(team_id):
    spec = load_model_spec(team_id)
    assert set(spec["models"]) == {"model_a", "model_b"}
    assert training_source_url(team_id).endswith(
        f"/v1/teams/{team_id}/training-source.json"
    )


def test_platform_does_not_build_supervised_training_rows(tmp_path: Path):
    missing = tmp_path / "model_a_training.csv"
    with pytest.raises(FileNotFoundError, match="raw JSON"):
        load_training_frame("team_1", "model_a", missing)


def test_challenge_app_does_not_proxy_training_rows():
    paths = {getattr(route, "path", None) for route in app.routes}
    assert not any(path and "training-data" in path for path in paths)
