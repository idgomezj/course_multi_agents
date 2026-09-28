from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .config import student_path


def model_contract_path(team_id: str) -> Path:
    return student_path(team_id) / "training" / "model_contract.json"


def raw_case_history_path(team_id: str) -> Path:
    return student_path(team_id) / "training" / "raw_case_history.csv"


def processed_training_path(team_id: str, model_key: str) -> Path:
    return student_path(team_id) / "training" / f"{model_key}_training.csv"


def load_model_spec(team_id: str) -> dict[str, Any]:
    """Load the fixed model I/O contract distributed with the student's case."""
    path = model_contract_path(team_id)
    if not path.exists():
        raise FileNotFoundError(
            f"Local model contract not found: {path}. "
            "The model contract is part of the assigned case package, not the Data API."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw_case_history(team_id: str) -> pd.DataFrame:
    """Load readable raw historical evidence supplied with the case."""
    path = raw_case_history_path(team_id)
    if not path.exists():
        raise FileNotFoundError(f"Raw case history not found: {path}")
    return pd.read_csv(path)


def load_training_frame(
    team_id: str,
    model_key: str,
    dataset_path: str | Path | None = None,
) -> pd.DataFrame:
    """Load a supervised dataset BUILT BY THE STUDENT from the raw case history.

    The platform intentionally does not generate features or labels. Students must
    create model_a_training.csv/model_b_training.csv from raw_case_history.csv and
    the business case description.
    """
    spec = load_model_spec(team_id)
    if model_key not in spec.get("models", {}):
        raise KeyError(f"Unknown model key {model_key}")

    path = Path(dataset_path) if dataset_path else processed_training_path(team_id, model_key)
    if not path.exists():
        raw = raw_case_history_path(team_id)
        brief = student_path(team_id) / "training" / "CASE_TRAINING.md"
        raise FileNotFoundError(
            f"Training dataset not found: {path}\n"
            f"Build it yourself from {raw} using the assignment guidance in {brief}.\n"
            f"The Data API does not provide training rows."
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
            f"{path} has only {len(frame)} rows. Build a defensible training dataset "
            "from the supplied history before training."
        )
    return frame
