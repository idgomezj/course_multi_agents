from __future__ import annotations

import math
import logging
import random

from .store import load_model_spec
from .observability import log_event

logger = logging.getLogger(__name__)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _demand_row(team_id: str, rng: random.Random) -> tuple[dict[str, float], float]:
    if team_id == "team_1":
        mean = rng.uniform(700, 1800)
        std = rng.uniform(160, 520)
        trend = rng.uniform(-0.22, 0.28)
        promo = rng.choice([0.0, 0.0, 1.0, 1.0])
        price_index = rng.uniform(0.86, 1.16)
        confirmed = mean * rng.uniform(0.45, 1.35)
        seasonal = rng.uniform(0.78, 1.35)
        noise_scale = 0.50
    elif team_id == "team_2":
        mean = rng.uniform(850, 1450)
        std = rng.uniform(8, 65)
        trend = rng.uniform(-0.045, 0.045)
        promo = 1.0 if rng.random() < 0.03 else 0.0
        price_index = rng.uniform(0.97, 1.03)
        confirmed = mean * rng.uniform(0.90, 1.08)
        seasonal = rng.uniform(0.96, 1.04)
        noise_scale = 0.18
    else:
        mean = rng.uniform(700, 1600)
        std = rng.uniform(40, 220)
        trend = rng.uniform(-0.10, 0.12)
        promo = 1.0 if rng.random() < 0.10 else 0.0
        price_index = rng.uniform(0.92, 1.08)
        confirmed = mean * rng.uniform(0.75, 1.20)
        seasonal = rng.uniform(0.90, 1.15)
        noise_scale = 0.30

    row = {
        "last4_mean": mean,
        "last4_std": std,
        "trend": trend,
        "promotion": promo,
        "price_index": price_index,
        "confirmed_orders": confirmed,
        "seasonal_index": seasonal,
    }
    return row, noise_scale


def _supplier_row(team_id: str, rng: random.Random) -> dict[str, float]:
    if team_id == "team_3":
        return {
            "reliability": rng.uniform(0.78, 0.995),
            "recent_late_rate": rng.uniform(0.0, 0.38),
            "lead_time_days": rng.uniform(1.0, 8.0),
            "order_qty_ratio": rng.uniform(0.35, 1.65),
            "urgency": rng.uniform(0.35, 1.0),
            "season_risk": rng.uniform(0.0, 0.55),
        }
    if team_id == "team_4":
        return {
            "reliability": rng.uniform(0.50, 0.96),
            "recent_late_rate": rng.uniform(0.0, 0.68),
            "lead_time_days": rng.uniform(4.0, 30.0),
            "order_qty_ratio": rng.uniform(0.25, 2.40),
            "urgency": rng.uniform(0.0, 1.0),
            "season_risk": rng.uniform(0.10, 1.0),
        }
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
    """Generate public training data with a distribution specific to each team case."""
    spec = load_model_spec(team_id)
    model = spec["models"][model_key]
    log_event(
        logger,
        "training_data.generation.started",
        level=logging.DEBUG,
        team_id=team_id,
        model_key=model_key,
        rows=rows,
        seed=seed,
        task=model.get("task"),
    )
    task = model["task"]
    rng = random.Random(seed + sum(ord(c) for c in team_id + model_key))
    data: list[dict[str, float]] = []

    for _ in range(rows):
        row: dict[str, float] = {}

        if task == "demand_forecast":
            row, noise_scale = _demand_row(team_id, rng)
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

        elif task == "demand_uncertainty":
            row.update(
                last4_std=rng.uniform(120, 560),
                promotion=rng.choice([0.0, 0.0, 1.0, 1.0]),
                trend_abs=rng.uniform(0.02, 0.35),
                forecast_disagreement=rng.uniform(0.05, 0.60),
                confirmed_ratio=rng.uniform(0.35, 1.35),
            )
            row["target_uncertainty"] = max(
                0.0,
                min(
                    1.0,
                    0.06
                    + row["last4_std"] / 850
                    + 0.20 * row["promotion"]
                    + 0.55 * row["forecast_disagreement"]
                    + 0.25 * row["trend_abs"]
                    + rng.gauss(0, 0.035),
                ),
            )

        elif task == "excess_inventory_risk":
            row.update(
                on_hand=rng.uniform(700, 6200),
                incoming=rng.uniform(0, 3600),
                forecast_total=rng.uniform(2800, 6200),
                holding_cost=rng.uniform(2.0, 8.5),
                trend=rng.uniform(-0.18, 0.05),
            )
            score = (
                (row["on_hand"] + row["incoming"] - row["forecast_total"]) / 1300
                + row["holding_cost"] / 6
                - 2.0 * row["trend"]
                - 0.7
            )
            row["target_risk"] = 1.0 if rng.random() < _sigmoid(score) else 0.0

        elif task in {"supplier_delay", "arrival_time"}:
            row.update(_supplier_row(team_id, rng))
            if team_id == "team_3":
                p = _sigmoid(
                    -3.7
                    + 5.2 * (1 - row["reliability"])
                    + 4.0 * row["recent_late_rate"]
                    + 0.75 * row["order_qty_ratio"]
                    + 1.45 * row["urgency"]
                    + 1.15 * row["season_risk"]
                )
            else:
                p = _sigmoid(
                    -2.5
                    + 4.0 * (1 - row["reliability"])
                    + 3.2 * row["recent_late_rate"]
                    + 0.55 * row["order_qty_ratio"]
                    + 1.2 * row["season_risk"]
                    + 0.35 * row["urgency"]
                )

            if task == "supplier_delay":
                row["target_delay"] = 1.0 if rng.random() < p else 0.0
            else:
                jitter = 0.35 if team_id == "team_3" else 1.0
                row["target_days"] = max(
                    0.5,
                    row["lead_time_days"] * (1 + 0.85 * p) + rng.gauss(0, jitter),
                )

        elif task == "supplier_quality":
            row.update(
                quality_score=rng.uniform(0.62, 0.995),
                recent_reject_rate=rng.uniform(0.0, 0.32),
                order_qty_ratio=rng.uniform(0.2, 2.4),
                criticality=rng.uniform(0.2, 1.0),
                process_change=1.0 if rng.random() < 0.22 else 0.0,
            )
            p = _sigmoid(
                -3.8
                + 5.4 * (1 - row["quality_score"])
                + 6.5 * row["recent_reject_rate"]
                + 0.45 * row["order_qty_ratio"]
                + 1.0 * row["process_change"]
                + 0.35 * row["criticality"]
            )
            row["target_quality_failure"] = 1.0 if rng.random() < p else 0.0

        elif task == "downtime_risk":
            row.update(
                recent_downtime=rng.uniform(2, 36),
                maintenance_age_days=rng.uniform(20, 200),
                utilization=rng.uniform(0.72, 1.08),
                runtime_hours=rng.uniform(80, 175),
                overload=rng.uniform(0.0, 0.42),
            )
            p = _sigmoid(
                -5.0
                + row["recent_downtime"] / 10
                + row["maintenance_age_days"] / 90
                + 3.2 * max(0, row["utilization"] - 0.78)
                + 3.5 * row["overload"]
            )
            row["target_downtime"] = 1.0 if rng.random() < p else 0.0

        elif task == "production_feasibility":
            row.update(
                required_hours_ratio=rng.uniform(0.65, 1.45),
                downtime_risk=rng.uniform(0.05, 0.95),
                changeovers=rng.uniform(0, 7),
                overtime_available=rng.uniform(0, 16),
                labor_ratio=rng.uniform(0.65, 1.02),
            )
            score = (
                4.6
                - 4.3 * row["required_hours_ratio"]
                - 2.0 * row["downtime_risk"]
                - 0.16 * row["changeovers"]
                + 0.055 * row["overtime_available"]
                + 1.5 * (row["labor_ratio"] - 0.8)
            )
            row["target_feasible"] = 1.0 if rng.random() < _sigmoid(score) else 0.0

        else:
            raise KeyError(f"Unsupported task: {task}")

        data.append(row)

    log_event(
        logger,
        "training_data.generation.completed",
        level=logging.DEBUG,
        team_id=team_id,
        model_key=model_key,
        task=task,
        rows=len(data),
        columns=sorted(data[0]) if data else [],
    )
    return data
