from __future__ import annotations

import csv
import math
import zipfile
from pathlib import Path

import torch
from torch import nn

TEAM_DIR = Path(__file__).resolve().parents[1]
TRAINING_DIR = TEAM_DIR / "training"
MODELS_DIR = TEAM_DIR / "models"


def read_csv(path: Path, columns: list[str]) -> torch.Tensor:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return torch.tensor([[float(row[c]) for c in columns] for row in rows], dtype=torch.float64)


def basis_a(x: torch.Tensor) -> torch.Tensor:
    m, s, trend, promo, price, confirmed, season = [x[:, i] for i in range(7)]
    return torch.stack(
        [
            torch.ones_like(m),
            m,
            s,
            trend * m,
            promo * m,
            (price - 1.0) * m,
            confirmed,
            (season - 1.0) * m,
            promo * confirmed,
            promo * s,
        ],
        dim=1,
    )


def basis_b(x: torch.Tensor) -> torch.Tensor:
    s, promo, trend_abs, disagreement, confirmed_ratio = [x[:, i] for i in range(5)]
    return torch.stack(
        [
            torch.ones_like(s),
            s,
            promo,
            trend_abs,
            disagreement,
            confirmed_ratio,
            promo * disagreement,
            promo * s,
            disagreement * confirmed_ratio,
            trend_abs * s,
        ],
        dim=1,
    )


def fit_ridge(
    x: torch.Tensor,
    y: torch.Tensor,
    basis_fn,
    ridge_lambda: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict[str, list[float]]]:
    n_train = max(1, int(len(x) * 0.80))
    train_x, train_y = x[:n_train], y[:n_train]
    val_x, val_y = x[n_train:], y[n_train:]

    train_basis = basis_fn(train_x)
    mu = train_basis.mean(dim=0)
    std = train_basis.std(dim=0, unbiased=False).clamp_min(1e-9)
    mu[0] = 0.0
    std[0] = 1.0

    z = (train_basis - mu) / std
    z[:, 0] = 1.0

    eye = torch.eye(z.shape[1], dtype=z.dtype)
    eye[0, 0] = 0.0
    beta = torch.linalg.solve(z.T @ z + ridge_lambda * eye, z.T @ train_y)

    metrics: dict[str, list[float]] = {}
    if len(val_x):
        val_z = (basis_fn(val_x) - mu) / std
        val_z[:, 0] = 1.0
        pred = val_z @ beta
        err = pred - val_y
        metrics = {
            "mae": err.abs().mean(dim=0).tolist(),
            "rmse": torch.sqrt((err**2).mean(dim=0)).tolist(),
        }

    return mu.float(), std.float(), beta.T.float(), metrics


class ForecastModel(nn.Module):
    def __init__(self, mu: torch.Tensor, std: torch.Tensor, beta: torch.Tensor):
        super().__init__()
        self.register_buffer("mu", mu)
        self.register_buffer("std", std)
        self.register_buffer("beta", beta)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        m, s, trend, promo, price, confirmed, season = [x[:, i] for i in range(7)]
        one = torch.ones_like(m)
        b = torch.stack(
            [
                one,
                m,
                s,
                trend * m,
                promo * m,
                (price - 1.0) * m,
                confirmed,
                (season - 1.0) * m,
                promo * confirmed,
                promo * s,
            ],
            dim=1,
        )
        z = (b - self.mu) / self.std
        z[:, 0] = 1.0
        return torch.clamp(z @ self.beta.T, min=0.0)


class UncertaintyModel(nn.Module):
    def __init__(self, mu: torch.Tensor, std: torch.Tensor, beta: torch.Tensor):
        super().__init__()
        self.register_buffer("mu", mu)
        self.register_buffer("std", std)
        self.register_buffer("beta", beta)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        s, promo, trend_abs, disagreement, confirmed_ratio = [x[:, i] for i in range(5)]
        one = torch.ones_like(s)
        b = torch.stack(
            [
                one,
                s,
                promo,
                trend_abs,
                disagreement,
                confirmed_ratio,
                promo * disagreement,
                promo * s,
                disagreement * confirmed_ratio,
                trend_abs * s,
            ],
            dim=1,
        )
        z = (b - self.mu) / self.std
        z[:, 0] = 1.0
        return torch.clamp(z @ self.beta.T, min=0.0, max=1.0)


def compact_pt2(path: Path) -> None:
    tmp = path.with_suffix(".tmp.pt2")
    with zipfile.ZipFile(path, "r") as src, zipfile.ZipFile(
        tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as dst:
        for item in src.infolist():
            dst.writestr(
                item.filename,
                src.read(item.filename),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    tmp.replace(path)


def export_model(model: nn.Module, width: int, path: Path) -> None:
    model = model.eval()
    exported = torch.export.export(model, (torch.zeros((1, width), dtype=torch.float32),))
    torch.export.save(exported, path)
    compact_pt2(path)
    # Validate the compact archive immediately.
    torch.export.load(path)


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    a_features = [
        "last4_mean",
        "last4_std",
        "trend",
        "promotion",
        "price_index",
        "confirmed_orders",
        "seasonal_index",
    ]
    a_targets = ["target_w1", "target_w2", "target_w3", "target_w4"]
    a_all = read_csv(TRAINING_DIR / "model_a_training.csv", a_features + a_targets)
    a_x, a_y = a_all[:, : len(a_features)], a_all[:, len(a_features) :]
    a_mu, a_std, a_beta, a_metrics = fit_ridge(a_x, a_y, basis_a, ridge_lambda=1.0)

    b_features = [
        "last4_std",
        "promotion",
        "trend_abs",
        "forecast_disagreement",
        "confirmed_ratio",
    ]
    b_targets = ["target_uncertainty"]
    b_all = read_csv(TRAINING_DIR / "model_b_training.csv", b_features + b_targets)
    b_x, b_y = b_all[:, : len(b_features)], b_all[:, len(b_features) :]
    b_mu, b_std, b_beta, b_metrics = fit_ridge(b_x, b_y, basis_b, ridge_lambda=1.5)

    export_model(ForecastModel(a_mu, a_std, a_beta), len(a_features), MODELS_DIR / "model_a.pt2")
    export_model(UncertaintyModel(b_mu, b_std, b_beta), len(b_features), MODELS_DIR / "model_b.pt2")

    print(f"model_a rows={len(a_x)} validation={len(a_x) - int(len(a_x) * 0.80)} metrics={a_metrics}")
    print(f"model_b rows={len(b_x)} validation={len(b_x) - int(len(b_x) * 0.80)} metrics={b_metrics}")


if __name__ == "__main__":
    main()
