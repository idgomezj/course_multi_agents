from __future__ import annotations

import copy
import math
from pathlib import Path

import pandas as pd
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[4]
TEAM = ROOT / "agentic-operations-intelligence-challenge" / "student" / "team_1"
TRAINING = TEAM / "training"
MODELS = TEAM / "models"

FEATURES_A = [
    "last4_mean",
    "last4_std",
    "trend",
    "promotion",
    "price_index",
    "confirmed_orders",
    "seasonal_index",
]
TARGETS_A = ["target_w1", "target_w2", "target_w3", "target_w4"]
FEATURES_B = [
    "last4_std",
    "promotion",
    "trend_abs",
    "forecast_disagreement",
    "confirmed_ratio",
]
TARGETS_B = ["target_uncertainty"]


class ForecastNet(nn.Module):
    def __init__(self, mean: torch.Tensor, std: torch.Tensor):
        super().__init__()
        self.register_buffer("x_mean", mean)
        self.register_buffer("x_std", torch.where(std < 1e-6, torch.ones_like(std), std))
        self.network = nn.Sequential(
            nn.Linear(7, 48),
            nn.SiLU(),
            nn.Linear(48, 48),
            nn.SiLU(),
            nn.Linear(48, 4),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = (x - self.x_mean) / self.x_std
        # Bounded demand ratio keeps hidden-scenario extrapolation sane.
        ratio = 0.55 + 1.25 * torch.sigmoid(self.network(z))
        base = 0.65 * x[:, 0:1] + 0.35 * x[:, 5:6]
        return torch.clamp(base * ratio, min=0.0)


class UncertaintyNet(nn.Module):
    def __init__(self, mean: torch.Tensor, std: torch.Tensor):
        super().__init__()
        self.register_buffer("x_mean", mean)
        self.register_buffer("x_std", torch.where(std < 1e-6, torch.ones_like(std), std))
        self.network = nn.Sequential(
            nn.Linear(5, 12),
            nn.SiLU(),
            nn.Linear(12, 12),
            nn.SiLU(),
            nn.Linear(12, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = (x - self.x_mean) / self.x_std
        return torch.sigmoid(self.network(z))


def split(frame: pd.DataFrame, features: list[str], targets: list[str]):
    cut = int(len(frame) * 0.8)
    train = frame.iloc[:cut]
    val = frame.iloc[cut:]
    return (
        torch.tensor(train[features].values, dtype=torch.float32),
        torch.tensor(train[targets].values, dtype=torch.float32),
        torch.tensor(val[features].values, dtype=torch.float32),
        torch.tensor(val[targets].values, dtype=torch.float32),
    )


def export(model: nn.Module, input_dim: int, path: Path) -> None:
    model.eval()
    program = torch.export.export(
        model, (torch.zeros((1, input_dim), dtype=torch.float32),)
    )
    torch.export.save(program, str(path))
    # Validate using the exact runtime loading mechanism.
    loaded = torch.export.load(str(path)).module()
    with torch.inference_mode():
        out = loaded(torch.zeros((1, input_dim), dtype=torch.float32))
    if not torch.isfinite(out).all():
        raise RuntimeError(f"Non-finite values from exported artifact {path}")


def train_forecast(frame: pd.DataFrame):
    torch.manual_seed(123)
    x_train, y_train, x_val, y_val = split(frame, FEATURES_A, TARGETS_A)
    model = ForecastNet(x_train.mean(0), x_train.std(0))
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)

    best_score = math.inf
    best_state = None
    for epoch in range(1000):
        pred = model(x_train)
        scale = torch.clamp(y_train.mean(dim=1, keepdim=True), min=100.0)
        loss = nn.functional.smooth_l1_loss(pred / scale, y_train / scale, beta=0.1)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0 or epoch == 999:
            with torch.inference_mode():
                val_pred = model(x_val)
                mape = torch.mean(
                    torch.abs(val_pred - y_val) / torch.clamp(y_val, min=1.0)
                ).item()
            if mape < best_score:
                best_score = mape
                best_state = copy.deepcopy(model.state_dict())

    model.load_state_dict(best_state)
    with torch.inference_mode():
        pred = model(x_val)
        mape = torch.mean(torch.abs(pred - y_val) / torch.clamp(y_val, min=1.0)).item()
        mae = torch.mean(torch.abs(pred - y_val)).item()
        rmse = torch.sqrt(torch.mean((pred - y_val) ** 2)).item()

        moving_average = x_val[:, 0:1].repeat(1, 4)
        baseline_mape = torch.mean(
            torch.abs(moving_average - y_val) / torch.clamp(y_val, min=1.0)
        ).item()

    return model, {
        "validation_mape": mape,
        "validation_mae": mae,
        "validation_rmse": rmse,
        "moving_average_mape": baseline_mape,
    }


def train_uncertainty(frame: pd.DataFrame):
    torch.manual_seed(42)
    x_train, y_train, x_val, y_val = split(frame, FEATURES_B, TARGETS_B)
    model = UncertaintyNet(x_train.mean(0), x_train.std(0))
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)

    best_score = math.inf
    best_state = None
    for epoch in range(800):
        pred = model(x_train)
        loss = nn.functional.smooth_l1_loss(pred, y_train, beta=0.05)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0 or epoch == 799:
            with torch.inference_mode():
                mae = torch.mean(torch.abs(model(x_val) - y_val)).item()
            if mae < best_score:
                best_score = mae
                best_state = copy.deepcopy(model.state_dict())

    model.load_state_dict(best_state)
    with torch.inference_mode():
        pred = model(x_val)
        mae = torch.mean(torch.abs(pred - y_val)).item()
        rmse = torch.sqrt(torch.mean((pred - y_val) ** 2)).item()
    return model, {"validation_mae": mae, "validation_rmse": rmse}


def main() -> None:
    a = pd.read_csv(TRAINING / "model_a_training.csv")
    b = pd.read_csv(TRAINING / "model_b_training.csv")
    MODELS.mkdir(parents=True, exist_ok=True)

    model_a, metrics_a = train_forecast(a)
    model_b, metrics_b = train_uncertainty(b)

    export(model_a, len(FEATURES_A), MODELS / "model_a.pt2")
    export(model_b, len(FEATURES_B), MODELS / "model_b.pt2")

    print("model_a", metrics_a)
    print("model_b", metrics_b)
    print("saved", MODELS / "model_a.pt2")
    print("saved", MODELS / "model_b.pt2")


if __name__ == "__main__":
    main()
