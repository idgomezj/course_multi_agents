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
from demo_app.student_config import load_feature_config, load_training_config

TEAM_ID = "team_0"
TRAINING_DIR = Path(__file__).resolve().parent / "training"
logger = setup_logging("agentic-operations-case0-training")

ARCHITECTURES = {
    "small": [16],
    "medium": [32, 16],
    "large": [64, 32, 16],
}


def _activation(name: str) -> nn.Module:
    return {"relu": nn.ReLU(), "silu": nn.SiLU(), "tanh": nn.Tanh()}[name]


class ReferenceNet(nn.Module):
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        x_mean: torch.Tensor,
        x_std: torch.Tensor,
        classification: bool,
        hidden_layers: list[int],
        activation: str,
        dropout: float,
    ):
        super().__init__()
        self.register_buffer("x_mean", x_mean)
        self.register_buffer("x_std", torch.where(x_std < 1e-6, torch.ones_like(x_std), x_std))
        layers: list[nn.Module] = []
        previous = input_dim
        for width in hidden_layers:
            layers.append(nn.Linear(previous, int(width)))
            layers.append(_activation(activation))
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            previous = int(width)
        layers.append(nn.Linear(previous, output_dim))
        self.layers = nn.Sequential(*layers)
        self.classification = classification

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = (x - self.x_mean) / self.x_std
        y = self.layers(x)
        return torch.sigmoid(y) if self.classification else y


def metrics(model: nn.Module, x_val: torch.Tensor, y_val: torch.Tensor, classification: bool) -> str:
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


def _loss(name: str, classification: bool) -> nn.Module:
    if classification:
        if name not in {"auto", "bce"}:
            raise ValueError("Classification reference model supports auto/bce")
        return nn.BCELoss()
    if name in {"auto", "mse"}:
        return nn.MSELoss()
    if name == "mae":
        return nn.L1Loss()
    if name == "huber":
        return nn.SmoothL1Loss()
    raise ValueError(f"Unsupported regression loss: {name}")


def _split(df: pd.DataFrame, method: str, fraction: float, seed: int):
    working = df.sample(frac=1.0, random_state=seed).reset_index(drop=True) if method == "random" else df.reset_index(drop=True)
    index = int(len(working) * (1.0 - fraction))
    if index <= 0 or index >= len(working):
        raise ValueError("Invalid Case 0 train/validation split")
    return working.iloc[:index], working.iloc[index:]


def train(model_key: str, output_dir: Path) -> None:
    started = perf_counter()
    spec = load_model_spec(TEAM_ID)["models"][model_key]
    training_cfg = load_training_config()
    feature_cfg = load_feature_config()
    model_cfg = training_cfg["models"][model_key]
    validation_cfg = training_cfg["validation"]

    dataset = TRAINING_DIR / f"{model_key}_training.csv"
    if not dataset.exists():
        raise FileNotFoundError(f"Case 0 training dataset not found: {dataset}")

    df = pd.read_csv(dataset)
    features = list(spec["features"])
    targets = list(spec["targets"])
    required_columns = features + targets
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"{dataset} is missing required columns: {missing}")
    if df[required_columns].isnull().any().any():
        raise ValueError(f"{dataset} must contain no null values in fixed model-contract columns")
    if len(df) < 100:
        raise ValueError(f"{dataset} does not contain enough rows for Case 0 validation")

    enabled = set(feature_cfg.get("models", {}).get(model_key, {}).get("enabled_features", features))
    unknown = sorted(enabled - set(features))
    if unknown:
        raise ValueError(f"Unknown enabled features for {model_key}: {unknown}")
    if not enabled:
        raise ValueError(f"At least one feature must remain enabled for {model_key}")
    disabled = [name for name in features if name not in enabled]
    for name in disabled:
        df[name] = 0.0

    train_df, val_df = _split(
        df,
        str(validation_cfg.get("method", "chronological")).lower(),
        float(validation_cfg.get("validation_fraction", 0.18)),
        int(validation_cfg.get("seed", 42)),
    )

    x_train = torch.tensor(train_df[features].values, dtype=torch.float32)
    y_train = torch.tensor(train_df[targets].values, dtype=torch.float32)
    x_val = torch.tensor(val_df[features].values, dtype=torch.float32)
    y_val = torch.tensor(val_df[targets].values, dtype=torch.float32)

    classification = spec["kind"] == "classification"
    architecture = str(model_cfg.get("architecture", "custom")).lower()
    hidden_layers = model_cfg.get("hidden_layers") or ARCHITECTURES.get(architecture, ARCHITECTURES["medium"])
    model = ReferenceNet(
        len(features),
        len(targets),
        x_train.mean(dim=0),
        x_train.std(dim=0),
        classification,
        [int(x) for x in hidden_layers],
        str(model_cfg.get("activation", "relu")).lower(),
        float(model_cfg.get("dropout", 0.0)),
    )

    optimizer_cls = torch.optim.Adam if str(model_cfg.get("optimizer", "adamw")).lower() == "adam" else torch.optim.AdamW
    optimizer = optimizer_cls(
        model.parameters(),
        lr=float(model_cfg.get("learning_rate", 0.002)),
        weight_decay=float(model_cfg.get("weight_decay", 0.0002)),
    )
    loss_fn = _loss(str(model_cfg.get("loss", "auto")).lower(), classification)
    loader = DataLoader(
        TensorDataset(x_train, y_train),
        batch_size=int(model_cfg.get("batch_size", 96)),
        shuffle=True,
    )

    log_event(
        logger,
        "training.model.started",
        team_id=TEAM_ID,
        model_key=model_key,
        task=spec.get("task"),
        kind=spec.get("kind"),
        artifact=spec.get("artifact"),
        training_config=model_cfg,
        validation_config=validation_cfg,
        enabled_features=sorted(enabled),
        disabled_features=disabled,
        train_rows=len(train_df),
        validation_rows=len(val_df),
    )

    best_loss = float("inf")
    best_state = None
    patience = 0
    epochs = int(model_cfg.get("epochs", 240))
    for epoch in range(epochs):
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

        if epoch % 20 == 0:
            log_event(logger, "training.progress", team_id=TEAM_ID, model_key=model_key, epoch=epoch, validation_loss=val_loss, best_loss=best_loss)

        if patience >= 30:
            log_event(logger, "training.early_stopping", team_id=TEAM_ID, model_key=model_key, epoch=epoch, best_loss=best_loss)
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / spec["artifact"]
    example = torch.zeros((1, len(features)), dtype=torch.float32)
    torch.export.save(torch.export.export(model, (example,)), str(artifact))

    loaded = torch.export.load(str(artifact)).module()
    with torch.inference_mode():
        check = loaded(torch.zeros((1, len(features)), dtype=torch.float32))
    if tuple(check.shape) != (1, len(targets)):
        raise ValueError(f"Export validation failed for {model_key}: {tuple(check.shape)}")

    final_metrics = metrics(model, x_val, y_val, classification)
    print(f"{model_key}: {final_metrics}; enabled_features={sorted(enabled)}; saved={artifact}")
    log_event(
        logger,
        "training.model.completed",
        team_id=TEAM_ID,
        model_key=model_key,
        artifact=str(artifact),
        artifact_format=artifact.suffix,
        validation_metrics=final_metrics,
        export_shape=list(check.shape),
        best_loss=best_loss,
        duration_ms=round((perf_counter() - started) * 1000, 2),
    )


if __name__ == "__main__":
    tokens = set_trace_context()
    try:
        cfg = load_training_config()
        torch.manual_seed(int(cfg.get("validation", {}).get("seed", 42)))
        target = Path("demo_case_0_solution/models")
        log_event(logger, "training.run.started", team_id=TEAM_ID, training_config=cfg, output_dir=str(target))
        train("model_a", target)
        train("model_b", target)
        log_event(logger, "training.run.completed", team_id=TEAM_ID, output_dir=str(target))
    finally:
        reset_trace_context(tokens)
