from pathlib import Path

import pytest

from challenge.api import app
from challenge.training_data import (
    load_model_spec,
    load_raw_case_history,
    load_training_frame,
)


@pytest.mark.parametrize("team_id", [f"team_{i}" for i in range(1, 6)])
def test_training_assets_are_local_and_readable(team_id):
    spec = load_model_spec(team_id)
    assert set(spec["models"]) == {"model_a", "model_b"}

    raw = load_raw_case_history(team_id)
    assert len(raw) >= 50
    assert len(raw.columns) >= 5


def test_platform_does_not_build_supervised_training_rows(tmp_path: Path):
    missing = tmp_path / "model_a_training.csv"
    with pytest.raises(FileNotFoundError, match="Build it yourself"):
        load_training_frame("team_1", "model_a", missing)


def test_training_http_endpoint_is_not_exposed():
    paths = {getattr(route, "path", None) for route in app.routes}
    assert not any(path and "training-data" in path for path in paths)
