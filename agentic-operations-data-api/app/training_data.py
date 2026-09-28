from __future__ import annotations

import math
import logging
import random

from .store import load_model_spec
from .observability import log_event

logger = logging.getLogger(__name__)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _demand_row(rng: random.Random) -> tuple[dict[str, float], float]:
    """Internal Case 0 reference-data generator.

    Student teams do not receive generated training rows from this service.
    """
    mean = rng.uniform(700, 1600)
    std = rng.uniform(40, 220)
    trend = rng.uniform(-0.10, 0.12)
    promo = 1.0 if rng.random() < 0.10 else 0.0
    price_index = rng.uniform(0.92, 1.08)
    confirmed = mean * rng.uniform(0.75, 1.20)
    seasonal = rng.uniform(0.90, 1.15)
    row = {
        "last4_mean": mean,
        "last4_std": std,
        "trend": trend,
        "promotion": promo,
        "price_index": price_index,
        "confirmed_orders": confirmed,
        "seasonal_index": seasonal,
    }
    return row, 0.30


def _supplier_row(rng: random.Random) -> dict[str, float]:
    return {
        "reliability": rng.uniform(0.60, 0.99),
        "recent_late_rate": rng.uniform(0.0, 0.50),
        "lead_time_days": rng.uniform(1.0, 20.0),
        "order_qty_ratio": rng.uniform(0.25, 2.0),
        "urgency": rng.uniform(0.0, 1.0),
        "season_risk": rng.uniform(0.0, 0.8),
    }


def generate_training_rows(
    team_id: str,
    model_key: str,
    rows: int = 1000,
    seed: int = 42,
) -> list[dict[str, float]]:
    """Generate data only for the instructor's solved Case 0 reference models.

    Teams 1-5 must build supervised datasets locally from the raw historical
    case files distributed in their student workspace. There is intentionally
    no student training-data API.
    """
    if team_id != "team_0":
        raise PermissionError(
            "Generated training rows are not available for student teams. "
            "Use the local raw_case_history.csv and CASE_TRAINING.md supplied with the case."
        )

    spec = load_model_spec(team_id)
    model = spec["models"][model_key]
    task = model["task"]
    rng = random.Random(seed + sum(ord(c) for c in team_id + model_key))
    data: list[dict[str, float]] = []

    log_event(
        logger,
        "case0.training_data.generation.started",
        level=logging.DEBUG,
        team_id=team_id,
        model_key=model_key,
        rows=rows,
        seed=seed,
        task=task,
    )

    for _ in range(rows):
        row: dict[str, float] = {}

        if task == "demand_forecast":
            row, noise_scale = _demand_row(rng)
            base = max(
                50.0,
                row["last4_mean"]
                * (1 + row["trend"])
                * row["seasonal_index"]
                * (1 + 0.35 * row["promotion"])
                / row["price_index"],
            )
            for week in range(1, 5):
                row[f"target_w{week}"] = max(
                    0.0,
                    base * (1 + 0.02 * week)
                    + rng.gauss(0, row["last4_std"] * noise_scale),
                )

        elif task == "supplier_delay":
            row.update(_supplier_row(rng))
            p = _sigmoid(
                -2.5
                + 4.0 * (1 - row["reliability"])
                + 3.2 * row["recent_late_rate"]
                + 0.55 * row["order_qty_ratio"]
                + 1.2 * row["season_risk"]
                + 0.35 * row["urgency"]
            )
            row["target_delay"] = 1.0 if rng.random() < p else 0.0

        else:
            raise KeyError(f"Unsupported Case 0 task: {task}")

        data.append(row)

    log_event(
        logger,
        "case0.training_data.generation.completed",
        level=logging.DEBUG,
        team_id=team_id,
        model_key=model_key,
        task=task,
        rows=len(data),
        columns=sorted(data[0]) if data else [],
    )
    return data
