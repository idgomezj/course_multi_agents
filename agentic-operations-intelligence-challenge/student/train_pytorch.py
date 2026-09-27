from __future__ import annotations

import argparse
import math

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from challenge.config import student_path
from challenge.data_api import get_data_client
from challenge.training_data import generate_training_frame


class StudentNet(nn.Module):
    """Starter network. Improve architecture/training, but keep the API model contract."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        mean: torch.Tensor,
        std: torch.Tensor,
        probability: bool,
    ):
        super().__init__()
        self.register_buffer("x_mean", mean)
        self.register_buffer("x_std", torch.where(std < 1e-6, torch.ones_like(std), std))
        self.network = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, output_dim),
        )
        self.probability = probability

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = (x - self.x_mean) / self.x_std
        y = self.network(x)
        return torch.sigmoid(y) if self.probability else y


def validation_metrics(
    model: nn.Module,
    x_val: torch.Tensor,
    y_val: torch.Tensor,
    classification: bool,
) -> str:
    model.eval()
    with torch.no_grad():
        prediction = model(x_val)

    if not classification:
        mse = torch.mean((prediction - y_val) ** 2).item()
        rmse = math.sqrt(mse)
        mae = torch.mean(torch.abs(prediction - y_val)).item()
        return f"validation_mse={mse:.3f} validation_rmse={rmse:.3f} validation_mae={mae:.3f}"

    eps = 1e-8
    bce = nn.BCELoss()(prediction, y_val).item()
    predicted = prediction >= 0.5
    actual = y_val >= 0.5
    accuracy = (predicted == actual).float().mean().item()
    tp = (predicted & actual).float().sum().item()
    fp = (predicted & ~actual).float().sum().item()
    fn = (~predicted & actual).float().sum().item()
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    f1 = 2 * precision * recall / (precision + recall + eps)
    return (
        f"validation_bce={bce:.4f} validation_accuracy={accuracy:.3f} "
        f"validation_precision={precision:.3f} validation_recall={recall:.3f} "
        f"validation_f1={f1:.3f}"
    )


def export_model(model: nn.Module, input_dim: int, output) -> None:
    """Export with the current PyTorch Export format instead of deprecated TorchScript tracing."""
    model.eval()
    example = torch.zeros((1, input_dim), dtype=torch.float32)
    exported_program = torch.export.export(model, (example,))
    torch.export.save(exported_program, str(output))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", required=True, choices=[f"team_{i}" for i in range(1, 6)])
    parser.add_argument("--model", required=True, choices=["model_a", "model_b"])
    parser.add_argument("--rows", type=int, default=1400)
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--lr", type=float, default=0.003)
    args = parser.parse_args()

    torch.manual_seed(42)

    workspace = student_path(args.team)
    spec = get_data_client().get_model_spec(args.team)
    mspec = spec["models"][args.model]
    df = generate_training_frame(args.team, args.model, rows=args.rows, seed=42)

    features, targets = mspec["features"], mspec["targets"]
    split = int(len(df) * 0.8)
    train_df, val_df = df.iloc[:split], df.iloc[split:]
    x_train = torch.tensor(train_df[features].values, dtype=torch.float32)
    y_train = torch.tensor(train_df[targets].values, dtype=torch.float32)
    x_val = torch.tensor(val_df[features].values, dtype=torch.float32)
    y_val = torch.tensor(val_df[targets].values, dtype=torch.float32)

    classification = mspec["kind"] == "classification"
    model = StudentNet(
        len(features),
        len(targets),
        x_train.mean(dim=0),
        x_train.std(dim=0),
        classification,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    loss_fn = nn.BCELoss() if classification else nn.MSELoss()
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=64, shuffle=True)

    for epoch in range(args.epochs):
        model.train()
        for xb, yb in loader:
            loss = loss_fn(model(xb), yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if epoch % 20 == 0 or epoch == args.epochs - 1:
            print(f"epoch={epoch:03d} {validation_metrics(model, x_val, y_val, classification)}")

    output_dir = workspace / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / mspec["artifact"]
    export_model(model, len(features), output)
    print(validation_metrics(model, x_val, y_val, classification))
    print(f"Saved PyTorch Export model: {output}")


if __name__ == "__main__":
    main()
