from __future__ import annotations

import argparse
import logging
import math
from pathlib import Path
from time import perf_counter

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from challenge.config import student_path
from challenge.observability import log_event, reset_trace_context, set_trace_context, setup_logging
from challenge.training_data import load_model_spec, load_training_frame

logger = setup_logging("agentic-operations-training")


class StudentNet(nn.Module):
    """Starter network.

    Students are expected to improve the architecture/training procedure when justified,
    while preserving the fixed input/output contract in training/model_contract.json.
    """

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


def export_model(model: nn.Module, input_dim: int, output: Path) -> None:
    model.eval()
    example = torch.zeros((1, input_dim), dtype=torch.float32)
    exported_program = torch.export.export(model, (example,))
    torch.export.save(exported_program, str(output))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Train one assigned PyTorch model from a supervised CSV built by the student. "
            "The platform does not generate training rows."
        )
    )
    parser.add_argument("--team", required=True, choices=[f"team_{i}" for i in range(1, 6)])
    parser.add_argument("--model", required=True, choices=["model_a", "model_b"])
    parser.add_argument(
        "--dataset",
        default=None,
        help=(
            "Optional path to the student-built supervised CSV. Defaults to "
            "student/team_X/training/<model>_training.csv."
        ),
    )
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--lr", type=float, default=0.003)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    tokens = set_trace_context()
    started = perf_counter()
    torch.manual_seed(args.seed)

    workspace = student_path(args.team)
    spec = load_model_spec(args.team)
    mspec = spec["models"][args.model]
    dataset_path = Path(args.dataset) if args.dataset else workspace / "training" / f"{args.model}_training.csv"

    log_event(
        logger,
        "training.run.started",
        team_id=args.team,
        model_key=args.model,
        dataset=str(dataset_path),
        epochs=args.epochs,
        learning_rate=args.lr,
        batch_size=args.batch_size,
        seed=args.seed,
        workspace=str(workspace),
    )

    df = load_training_frame(args.team, args.model, dataset_path)
    features, targets = mspec["features"], mspec["targets"]

    # Default split preserves row order. Students should choose a split appropriate
    # to their case and document any change, especially for time-dependent data.
    split = int(len(df) * 0.8)
    if split <= 0 or split >= len(df):
        raise ValueError("Training dataset must contain enough rows for train/validation splits")

    train_df, val_df = df.iloc[:split], df.iloc[split:]
    x_train = torch.tensor(train_df[features].values, dtype=torch.float32)
    y_train = torch.tensor(train_df[targets].values, dtype=torch.float32)
    x_val = torch.tensor(val_df[features].values, dtype=torch.float32)
    y_val = torch.tensor(val_df[targets].values, dtype=torch.float32)

    classification = mspec["kind"] == "classification"
    log_event(
        logger,
        "training.dataset.ready",
        team_id=args.team,
        model_key=args.model,
        task=mspec.get("task"),
        kind=mspec.get("kind"),
        features=features,
        targets=targets,
        train_rows=len(train_df),
        validation_rows=len(val_df),
        source=str(dataset_path),
    )

    model = StudentNet(
        len(features),
        len(targets),
        x_train.mean(dim=0),
        x_train.std(dim=0),
        classification,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    loss_fn = nn.BCELoss() if classification else nn.MSELoss()
    loader = DataLoader(
        TensorDataset(x_train, y_train),
        batch_size=args.batch_size,
        shuffle=True,
    )

    for epoch in range(args.epochs):
        model.train()
        last_loss = None
        for xb, yb in loader:
            loss = loss_fn(model(xb), yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            last_loss = loss

        metrics_text = validation_metrics(model, x_val, y_val, classification)
        log_event(
            logger,
            "training.epoch.completed",
            level=logging.DEBUG,
            team_id=args.team,
            model_key=args.model,
            epoch=epoch,
            training_loss=float(last_loss.detach()) if last_loss is not None else None,
            validation_metrics=metrics_text,
        )
        if epoch % 20 == 0 or epoch == args.epochs - 1:
            print(f"epoch={epoch:03d} {metrics_text}")

    output_dir = workspace / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / mspec["artifact"]
    export_model(model, len(features), output)

    final_metrics = validation_metrics(model, x_val, y_val, classification)
    print(final_metrics)
    print(f"Saved PyTorch Export model: {output}")
    log_event(
        logger,
        "training.run.completed",
        team_id=args.team,
        model_key=args.model,
        artifact=str(output),
        artifact_format=output.suffix,
        validation_metrics=final_metrics,
        duration_ms=round((perf_counter() - started) * 1000, 2),
    )
    reset_trace_context(tokens)


if __name__ == "__main__":
    main()
