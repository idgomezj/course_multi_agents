from __future__ import annotations

import csv
import logging
from pathlib import Path

from .observability import log_event

logger = logging.getLogger(__name__)

_CASE0_TRAINING_DIR = (
    Path(__file__).resolve().parents[1]
    / "demo_case_0_solution"
    / "training"
)


def generate_training_rows(
    team_id: str,
    model_key: str,
    rows: int = 1000,
    seed: int = 42,
) -> list[dict[str, float]]:
    """Compatibility loader for the committed clean Case 0 datasets.

    Despite the historical function name, this function no longer synthesizes
    training examples. Case 0 uses deterministic, committed, model-ready CSV
    files so the instructor can validate the complete training/export/inference
    pipeline against stable inputs.

    Teams 1-5 receive raw historical JSON through the team-scoped Data API and
    must build their own supervised training datasets.
    """
    if team_id != "team_0":
        raise PermissionError(
            "Ready-made training rows exist only for the solved Case 0 validation case. "
            "Student teams must build supervised datasets from their raw JSON source."
        )
    if model_key not in {"model_a", "model_b"}:
        raise KeyError(model_key)

    path = _CASE0_TRAINING_DIR / f"{model_key}_training.csv"
    if not path.exists():
        raise FileNotFoundError(f"Case 0 training dataset not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as fh:
        source = [
            {key: float(value) for key, value in row.items()}
            for row in csv.DictReader(fh)
        ]

    if not source:
        raise ValueError(f"Case 0 training dataset is empty: {path}")

    # Keep legacy callers deterministic without synthesizing new examples.
    # seed only controls the starting offset when fewer than all rows are requested.
    count = max(1, min(int(rows), len(source)))
    start = int(seed) % len(source)
    selected = [source[(start + i) % len(source)] for i in range(count)]

    log_event(
        logger,
        "case0.training_data.loaded",
        team_id=team_id,
        model_key=model_key,
        path=str(path),
        requested_rows=rows,
        returned_rows=len(selected),
        source_rows=len(source),
    )
    return selected
