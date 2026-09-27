from __future__ import annotations

import math
import random

import pandas as pd

from .config import student_path


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def generate_training_frame(team_id: str, model_key: str, rows: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate the public training set.

    This is intentionally only the *public* data generator. The final holdout and
    hidden scenario generators must live in private instructor infrastructure.
    """
    import json

    spec = json.loads((student_path(team_id) / "models" / "spec.json").read_text(encoding="utf-8"))
    model = spec["models"][model_key]
    task = model["task"]
    rng = random.Random(seed + sum(ord(c) for c in team_id + model_key))
    data: list[dict[str, float]] = []

    for _ in range(rows):
        row: dict[str, float] = {}
        if task == "demand_forecast":
            mean = rng.uniform(700, 1800)
            std = rng.uniform(20, 450)
            trend = rng.uniform(-0.20, 0.25)
            promo = rng.choice([0.0, 0.0, 0.0, 1.0])
            price_index = rng.uniform(0.88, 1.12)
            confirmed = mean * rng.uniform(0.55, 1.15)
            seasonal = rng.uniform(0.80, 1.30)
            row.update(last4_mean=mean, last4_std=std, trend=trend, promotion=promo,
                       price_index=price_index, confirmed_orders=confirmed, seasonal_index=seasonal)
            base = max(50.0, mean * (1 + trend) * seasonal * (1 + 0.35 * promo) / price_index)
            for week in range(1, 5):
                row[f"target_w{week}"] = max(0.0, base * (1 + 0.02 * week) + rng.gauss(0, std * 0.35))
        elif task == "demand_uncertainty":
            row.update(
                last4_std=rng.uniform(20, 500),
                promotion=rng.choice([0.0, 1.0]),
                trend_abs=rng.uniform(0, 0.35),
                forecast_disagreement=rng.uniform(0, 0.5),
                confirmed_ratio=rng.uniform(0.3, 1.2),
            )
            row["target_uncertainty"] = min(
                1.0,
                0.08 + row["last4_std"] / 900 + 0.18 * row["promotion"]
                + 0.55 * row["forecast_disagreement"] + 0.25 * row["trend_abs"]
                + rng.gauss(0, 0.04),
            )
        elif task == "excess_inventory_risk":
            row.update(
                on_hand=rng.uniform(300, 5000),
                incoming=rng.uniform(0, 3000),
                forecast_total=rng.uniform(1000, 7000),
                holding_cost=rng.uniform(0.5, 8.0),
                trend=rng.uniform(-0.25, 0.15),
            )
            score = (row["on_hand"] + row["incoming"] - row["forecast_total"]) / 1800 + row["holding_cost"] / 8 - 1.4 * row["trend"]
            row["target_risk"] = 1.0 if rng.random() < _sigmoid(score) else 0.0
        elif task in {"supplier_delay", "arrival_time"}:
            row.update(
                reliability=rng.uniform(0.55, 0.99),
                recent_late_rate=rng.uniform(0, 0.6),
                lead_time_days=rng.uniform(1, 30),
                order_qty_ratio=rng.uniform(0.2, 2.2),
                urgency=rng.uniform(0, 1),
                season_risk=rng.uniform(0, 1),
            )
            p = _sigmoid(-3.0 + 4.2 * (1 - row["reliability"]) + 3.2 * row["recent_late_rate"]
                         + 0.65 * row["order_qty_ratio"] + 1.1 * row["season_risk"] + 0.5 * row["urgency"])
            if task == "supplier_delay":
                row["target_delay"] = 1.0 if rng.random() < p else 0.0
            else:
                row["target_days"] = max(0.5, row["lead_time_days"] * (1 + 0.9 * p) + rng.gauss(0, 1.0))
        elif task == "supplier_quality":
            row.update(
                quality_score=rng.uniform(0.65, 0.995),
                recent_reject_rate=rng.uniform(0, 0.25),
                order_qty_ratio=rng.uniform(0.2, 2.2),
                criticality=rng.uniform(0, 1),
                process_change=rng.choice([0.0, 0.0, 1.0]),
            )
            p = _sigmoid(-4 + 5 * (1 - row["quality_score"]) + 6 * row["recent_reject_rate"]
                         + 0.5 * row["order_qty_ratio"] + 0.8 * row["process_change"])
            row["target_quality_failure"] = 1.0 if rng.random() < p else 0.0
        elif task == "downtime_risk":
            row.update(
                recent_downtime=rng.uniform(0, 30),
                maintenance_age_days=rng.uniform(1, 180),
                utilization=rng.uniform(0.45, 1.05),
                runtime_hours=rng.uniform(20, 190),
                overload=rng.uniform(0, 0.35),
            )
            p = _sigmoid(-4 + row["recent_downtime"] / 12 + row["maintenance_age_days"] / 100
                         + 2.5 * max(0, row["utilization"] - 0.75) + 3 * row["overload"])
            row["target_downtime"] = 1.0 if rng.random() < p else 0.0
        elif task == "production_feasibility":
            row.update(
                required_hours_ratio=rng.uniform(0.35, 1.35),
                downtime_risk=rng.uniform(0, 1),
                changeovers=rng.uniform(0, 6),
                overtime_available=rng.uniform(0, 20),
                labor_ratio=rng.uniform(0.65, 1.05),
            )
            score = 4.2 - 4.0 * row["required_hours_ratio"] - 1.8 * row["downtime_risk"] - 0.14 * row["changeovers"] + 0.05 * row["overtime_available"] + 1.3 * (row["labor_ratio"] - 0.8)
            row["target_feasible"] = 1.0 if rng.random() < _sigmoid(score) else 0.0
        else:
            raise ValueError(f"Unsupported public training task: {task}")
        data.append(row)

    return pd.DataFrame(data)
