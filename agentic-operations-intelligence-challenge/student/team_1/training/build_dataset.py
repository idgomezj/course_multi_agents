from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

NUMERIC_COLUMNS = [
    "week",
    "actual_demand",
    "promotion",
    "price_index",
    "confirmed_orders",
    "seasonal_index",
]


def _records(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        rows = payload.get("records")
        if isinstance(rows, list):
            return [x for x in rows if isinstance(x, dict)]
    raise ValueError("Expected a JSON list or an object containing a records list")


def clean_history(payload: object) -> pd.DataFrame:
    frame = pd.DataFrame(_records(payload)).copy()
    required = {"week", "product_id", "actual_demand", "promotion", "price_index",
                "confirmed_orders", "seasonal_index"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Raw source missing required fields: {sorted(missing)}")

    frame["product_id"] = frame["product_id"].astype(str).str.strip().str.upper()
    for col in NUMERIC_COLUMNS:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")

    frame = frame[frame["product_id"].ne("") & frame["week"].notna()].copy()
    frame["week"] = frame["week"].astype(int)

    # Collapse duplicate product/week uploads deterministically. Median is robust
    # to an accidental duplicate with one corrupted numeric value.
    agg = {
        "actual_demand": "median",
        "promotion": "max",
        "price_index": "median",
        "confirmed_orders": "median",
        "seasonal_index": "median",
    }
    frame = (
        frame.groupby(["product_id", "week"], as_index=False)
        .agg(agg)
        .sort_values(["product_id", "week"])
        .reset_index(drop=True)
    )

    cleaned = []
    for product_id, group in frame.groupby("product_id", sort=True):
        g = group.sort_values("week").copy()

        # Preserve whether realized demand was actually observed. Windows touching
        # an imputed realized-demand value are excluded later to avoid label leakage/noise.
        g["_demand_was_missing"] = g["actual_demand"].isna()

        # Exogenous planning signals can be interpolated because they are inputs,
        # never labels. Fall back to the product median, then a safe neutral value.
        for col, fallback in [
            ("price_index", 1.0),
            ("confirmed_orders", np.nan),
            ("seasonal_index", 1.0),
        ]:
            g[col] = g[col].interpolate(limit_direction="both")
            med = g[col].median()
            if pd.isna(med):
                med = fallback

            if col == "confirmed_orders" and pd.isna(med):
                med = g["actual_demand"].median()
            g[col] = g[col].fillna(med)

        g["promotion"] = g["promotion"].fillna(0).clip(0, 1)

        # Fill missing realized demand only to keep the time series contiguous;
        # windows that use those values are excluded below.
        g["actual_demand"] = g["actual_demand"].interpolate(limit_direction="both")

        # Detect gross data-entry spikes conservatively. Promotion weeks are left
        # untouched. A record must be both >2x its local median and poorly supported
        # by confirmed orders before replacement with the local median.
        local_med = g["actual_demand"].rolling(5, center=True, min_periods=3).median()
        unsupported = g["confirmed_orders"] / g["actual_demand"].clip(lower=1)
        bad_spike = (
            (g["promotion"] < 0.5)
            & (g["actual_demand"] > 2.0 * local_med)
            & (unsupported < 0.45)
        )
        g.loc[bad_spike, "actual_demand"] = local_med[bad_spike]
        cleaned.append(g)

    return pd.concat(cleaned, ignore_index=True).sort_values(["product_id", "week"])


def build_datasets(clean: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows_a: list[dict] = []
    rows_b: list[dict] = []

    for product_id, group in clean.groupby("product_id", sort=True):
        g = group.sort_values("week").reset_index(drop=True)
        demand = g["actual_demand"].astype(float).to_numpy()

        for i in range(3, len(g) - 4):
            # History is available through anchor i. Targets are strictly future.
            hist_rows = g.iloc[i - 3 : i + 1]
            future_rows = g.iloc[i + 1 : i + 5]
            if hist_rows["_demand_was_missing"].any() or future_rows["_demand_was_missing"].any():
                continue

            hist = demand[i - 3 : i + 1]
            future = demand[i + 1 : i + 5]
            next_row = g.iloc[i + 1]

            last4_mean = float(hist.mean())
            last4_std = float(hist.std(ddof=0))
            trend = float((hist[-1] - hist[0]) / max(1.0, hist[0]))

            # Forecast disagreement proxy available at the prediction date.
            alpha = 0.35
            level = float(demand[0])
            for value in demand[1 : i + 1]:
                level = alpha * float(value) + (1.0 - alpha) * level
            seasonal_w1 = last4_mean * float(next_row["seasonal_index"])
            candidates = np.asarray([last4_mean, level, seasonal_w1], dtype=float)
            disagreement = float(candidates.std() / max(1.0, candidates.mean()))

            confirmed_ratio = float(next_row["confirmed_orders"]) / max(1.0, last4_mean)

            # Uncertainty target: realized four-week MAPE of a forecast that was
            # available at the anchor date. It uses only past demand plus known
            # first-week commercial signal and seasonal indices.
            future_season = future_rows["seasonal_index"].astype(float).to_numpy()
            confirmed_level = (
                float(next_row["confirmed_orders"])
                / max(0.5, float(next_row["seasonal_index"]))
            )
            available_forecast = (
                0.65 * last4_mean * future_season
                + 0.35 * confirmed_level * future_season
            )
            target_uncertainty = float(
                np.clip(
                    np.mean(np.abs(future - available_forecast) / np.maximum(future, 1.0)),
                    0.0,
                    1.0,
                )
            )

            rows_a.append(
                {
                    "anchor_week": int(g.iloc[i]["week"]),
                    "product_id": product_id,
                    "last4_mean": last4_mean,
                    "last4_std": last4_std,
                    "trend": trend,
                    "promotion": float(next_row["promotion"]),
                    "price_index": float(next_row["price_index"]),
                    "confirmed_orders": float(next_row["confirmed_orders"]),
                    "seasonal_index": float(next_row["seasonal_index"]),
                    "target_w1": float(future[0]),
                    "target_w2": float(future[1]),
                    "target_w3": float(future[2]),
                    "target_w4": float(future[3]),
                }
            )
            rows_b.append(
                {
                    "anchor_week": int(g.iloc[i]["week"]),
                    "product_id": product_id,
                    "last4_std": last4_std,
                    "promotion": float(next_row["promotion"]),
                    "trend_abs": abs(trend),
                    "forecast_disagreement": disagreement,
                    "confirmed_ratio": confirmed_ratio,
                    "target_uncertainty": target_uncertainty,
                }
            )

    model_a = pd.DataFrame(rows_a).sort_values(["anchor_week", "product_id"]).reset_index(drop=True)
    model_b = pd.DataFrame(rows_b).sort_values(["anchor_week", "product_id"]).reset_index(drop=True)
    if len(model_a) < 20 or len(model_b) < 20:
        raise ValueError("Not enough leakage-safe supervised rows after cleaning")
    return model_a, model_b


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="student/team_1/training/raw_source.json")
    parser.add_argument("--out-dir", default="student/team_1/training")
    args = parser.parse_args()

    payload = json.loads(Path(args.raw).read_text(encoding="utf-8"))
    clean = clean_history(payload)
    model_a, model_b = build_datasets(clean)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    model_a.to_csv(out / "model_a_training.csv", index=False)
    model_b.to_csv(out / "model_b_training.csv", index=False)

    print(
        f"clean_rows={len(clean)} model_a_rows={len(model_a)} "
        f"model_b_rows={len(model_b)}"
    )


if __name__ == "__main__":
    main()
