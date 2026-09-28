from __future__ import annotations

import logging
import math
from time import perf_counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from app.observability import log_event, reset_trace_context, set_trace_context, setup_logging
from app.store import load_model_spec

TEAM_ID = "team_0"
TRAINING_DIR = Path(__file__).resolve().parent / "training"
logger = setup_logging("agentic-operations-case0-training")


class ReferenceNet(nn.Module):
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        x_mean: torch.Tensor,
        x_std: torch.Tensor,
        classification: bool,
    ):
        super().__init__()
        self.register_buffer("x_mean", x_mean)
        self.register_buffer("x_std", torch.where(x_std < 1e-6, torch.ones_like(x_std), x_std))
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.08),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim),
        )
        self.classification = classification

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = (x - self.x_mean) / self.x_std
        y = self.layers(x)
        return torch.sigmoid(y) if self.classification else y


def metrics(
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
        return f"mse={mse:.3f} rmse={rmse:.3f} mae={mae:.3f}"

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
        f"bce={bce:.4f} accuracy={accuracy:.3f} "
        f"precision={precision:.3f} recall={recall:.3f} f1={f1:.3f}"
    )


def train(model_key: str, output_dir: Path) -> None:
    started = perf_counter()
    spec = load_model_spec(TEAM_ID)["models"][model_key]
    log_event(
        logger,
        "training.model.started",
        team_id=TEAM_ID,
        model_key=model_key,
        task=spec.get("task"),
        kind=spec.get("kind"),
        artifact=spec.get("artifact"),
        features=spec.get("features"),
        targets=spec.get("targets"),
    )
    dataset = TRAINING_DIR / f"{model_key}_training.csv"
    if not dataset.exists():
        raise FileNotFoundError(f"Clean Case 0 training dataset not found: {dataset}")

    df = pd.read_csv(dataset)
    required_columns = list(spec["features"]) + list(spec["targets"])
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"{dataset} is missing required columns: {missing}")
    if df[required_columns].isnull().any().any():
        raise ValueError(f"{dataset} must be clean and contain no null values in model columns")
    if len(df) < 100:
        raise ValueError(f"{dataset} does not contain enough rows for Case 0 validation")

    split = int(len(df) * 0.82)
    train_df = df.iloc[:split]
    val_df = df.iloc[split:]

    x_train = torch.tensor(train_df[spec["features"]].values, dtype=torch.float32)
    y_train = torch.tensor(train_df[spec["targets"]].values, dtype=torch.float32)
    x_val = torch.tensor(val_df[spec["features"]].values, dtype=torch.float32)
    y_val = torch.tensor(val_df[spec["targets"]].values, dtype=torch.float32)

    classification = spec["kind"] == "classification"
    log_event(
        logger,
        "training.dataset.ready",
        team_id=TEAM_ID,
        model_key=model_key,
        rows=len(df),
        train_rows=len(train_df),
        validation_rows=len(val_df),
        classification=classification,
        dataset=str(dataset),
    )
    model = ReferenceNet(
        len(spec["features"]),
        len(spec["targets"]),
        x_train.mean(dim=0),
        x_train.std(dim=0),
        classification,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=2e-4)
    loss_fn = nn.BCELoss() if classification else nn.MSELoss()
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=96, shuffle=True)

    best_loss = float("inf")
    best_state = None
    patience = 0

    for epoch in range(240):
        model.train()
        for xb, yb in loader:
            loss = loss_fn(model(xb), yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            val_loss = float(loss_fn(model(x_val), y_val))

        if val_loss < best_loss - 1e-6:
            best_loss = val_loss
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            patience = 0
        else:
            patience += 1

        log_event(
            logger,
            "training.epoch.completed",
            level=logging.DEBUG,
            team_id=TEAM_ID,
            model_key=model_key,
            epoch=epoch,
            validation_loss=val_loss,
            best_loss=best_loss,
            patience=patience,
        )

        if epoch % 20 == 0:
            log_event(
                logger,
                "training.progress",
                team_id=TEAM_ID,
                model_key=model_key,
                epoch=epoch,
                validation_loss=val_loss,
                best_loss=best_loss,
            )

        if patience >= 30:
            log_event(logger, "training.early_stopping", team_id=TEAM_ID, model_key=model_key, epoch=epoch, best_loss=best_loss)
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / spec["artifact"]
    example = torch.zeros((1, len(spec["features"])), dtype=torch.float32)
    exported_program = torch.export.export(model, (example,))
    torch.export.save(exported_program, str(artifact))

    final_metrics = metrics(model, x_val, y_val, classification)
    print(f"{model_key}: {final_metrics}; saved={artifact}")
    log_event(
        logger,
        "training.model.completed",
        team_id=TEAM_ID,
        model_key=model_key,
        artifact=str(artifact),
        artifact_format=artifact.suffix,
        validation_metrics=final_metrics,
        best_loss=best_loss,
        duration_ms=round((perf_counter() - started) * 1000, 2),
    )


if __name__ == "__main__":
    tokens = set_trace_context()
    try:
        torch.manual_seed(42)
        target = Path("demo_case_0_solution/models")
        log_event(logger, "training.run.started", team_id=TEAM_ID, seed=42, output_dir=str(target))
        train("model_a", target)
        train("model_b", target)
        log_event(logger, "training.run.completed", team_id=TEAM_ID, output_dir=str(target))
    finally:
        reset_trace_context(tokens)
