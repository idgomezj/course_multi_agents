from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from .config import student_path


def model_contract_path(team_id: str) -> Path:
    return student_path(team_id) / "training" / "model_contract.json"


def processed_training_path(team_id: str, model_key: str) -> Path:
    return student_path(team_id) / "training" / f"{model_key}_training.csv"


def downloaded_raw_source_path(team_id: str) -> Path:
    """Suggested location for the raw JSON a student downloads from the Data API."""
    return student_path(team_id) / "training" / "raw_source.json"


def training_source_url(team_id: str) -> str:
    base = os.getenv("DATA_API_URL", "http://localhost:8100").rstrip("/")
    return f"{base}/v1/teams/{team_id}/training-source.json"


def load_model_spec(team_id: str) -> dict[str, Any]:
    """Load the fixed model I/O contract distributed with the student's case."""
    path = model_contract_path(team_id)
    if not path.exists():
        raise FileNotFoundError(
            f"Local model contract not found: {path}. "
            "The model contract is part of the assigned case package."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_training_frame(
    team_id: str,
    model_key: str,
    dataset_path: str | Path | None = None,
) -> pd.DataFrame:
    """Load a supervised dataset built by the student from the raw JSON source.

    The platform intentionally does not fetch, clean, filter, engineer or label
    model-training rows. Students must retrieve the raw JSON source from the
    team-scoped Data API and create model_a_training.csv/model_b_training.csv.
    """
    spec = load_model_spec(team_id)
    if model_key not in spec.get("models", {}):
        raise KeyError(f"Unknown model key {model_key}")

    path = Path(dataset_path) if dataset_path else processed_training_path(team_id, model_key)
    if not path.exists():
        brief = student_path(team_id) / "training" / "CASE_TRAINING.md"
        raw_target = downloaded_raw_source_path(team_id)
        raise FileNotFoundError(
            f"Training dataset not found: {path}\n"
            f"Retrieve the raw JSON from {training_source_url(team_id)} and save/inspect it "
            f"(suggested path: {raw_target}).\n"
            f"Then build {path.name} yourself using the business guidance in {brief}. "
            "The API intentionally does not return a cleaned or model-ready training table."
        )

    frame = pd.read_csv(path)
    model = spec["models"][model_key]
    required = list(model["features"]) + list(model["targets"])
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(
            f"{path} is missing required columns for {model_key}: {missing}. "
            f"Required contract columns: {required}"
        )
    if len(frame) < 20:
        raise ValueError(
            f"{path} has only {len(frame)} rows. Build a defensible supervised dataset "
            "from the raw JSON source before training."
        )
    return frame
