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
from challenge.student_config import load_feature_config, load_training_config
from challenge.training_data import load_model_spec, load_training_frame

logger = setup_logging("agentic-operations-training")

ARCHITECTURES = {"small": [16], "medium": [32, 16], "large": [64, 32, 16]}


def _activation(name: str) -> nn.Module:
    return {"relu": nn.ReLU(), "silu": nn.SiLU(), "tanh": nn.Tanh()}[name]


class StudentNet(nn.Module):
    """Configuration-driven starter network with a fixed model I/O contract."""

    def __init__(self, input_dim: int, output_dim: int, mean: torch.Tensor, std: torch.Tensor,
                 probability: bool, hidden_layers: list[int], activation: str, dropout: float):
        super().__init__()
        self.register_buffer("x_mean", mean)
        self.register_buffer("x_std", torch.where(std < 1e-6, torch.ones_like(std), std))
        layers: list[nn.Module] = []
        previous = input_dim
        for width in hidden_layers:
            layers.append(nn.Linear(previous, int(width)))
            layers.append(_activation(activation))
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            previous = int(width)
        layers.append(nn.Linear(previous, output_dim))
        self.network = nn.Sequential(*layers)
        self.probability = probability

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = (x - self.x_mean) / self.x_std
        y = self.network(x)
        return torch.sigmoid(y) if self.probability else y


def validation_metrics(model: nn.Module, x_val: torch.Tensor, y_val: torch.Tensor, classification: bool) -> str:
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
    return f"validation_bce={bce:.4f} validation_accuracy={accuracy:.3f} validation_precision={precision:.3f} validation_recall={recall:.3f} validation_f1={f1:.3f}"


def export_model(model: nn.Module, input_dim: int, output: Path) -> None:
    model.eval()
    exported_program = torch.export.export(model, (torch.zeros((1, input_dim), dtype=torch.float32),))
    torch.export.save(exported_program, str(output))


def _loss(name: str, classification: bool) -> nn.Module:
    if classification:
        if name not in {"auto", "bce"}:
            raise ValueError("Classification models support loss: auto or bce")
        return nn.BCELoss()
    if name in {"auto", "mse"}:
        return nn.MSELoss()
    if name == "mae":
        return nn.L1Loss()
    if name == "huber":
        return nn.SmoothL1Loss()
    raise ValueError(f"Regression model does not support loss '{name}'")


def _split_frame(df, method: str, validation_fraction: float, seed: int):
    working = df.sample(frac=1.0, random_state=seed).reset_index(drop=True) if method == "random" else df.reset_index(drop=True)
    split = int(len(working) * (1.0 - validation_fraction))
    if split <= 0 or split >= len(working):
        raise ValueError("Training dataset must contain enough rows for train/validation splits")
    return working.iloc[:split], working.iloc[split:]


def main() -> None:
    parser = argparse.ArgumentParser(description="Train one assigned model using YAML training/feature settings.")
    parser.add_argument("--team", required=True, choices=[f"team_{i}" for i in range(1, 6)])
    parser.add_argument("--model", required=True, choices=["model_a", "model_b"])
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--epochs", type=int, default=None, help="Optional YAML override")
    parser.add_argument("--lr", type=float, default=None, help="Optional YAML override")
    parser.add_argument("--batch-size", type=int, default=None, help="Optional YAML override")
    parser.add_argument("--seed", type=int, default=None, help="Optional YAML override")
    args = parser.parse_args()

    tokens = set_trace_context()
    started = perf_counter()
    workspace = student_path(args.team)
    spec = load_model_spec(args.team)
    mspec = spec["models"][args.model]
    training_cfg = load_training_config(args.team)
    feature_cfg = load_feature_config(args.team)
    model_cfg = dict(training_cfg["models"][args.model])
    validation_cfg = dict(training_cfg["validation"])

    if args.epochs is not None:
        model_cfg["epochs"] = args.epochs
    if args.lr is not None:
        model_cfg["learning_rate"] = args.lr
    if args.batch_size is not None:
        model_cfg["batch_size"] = args.batch_size
    if args.seed is not None:
        validation_cfg["seed"] = args.seed

    seed = int(validation_cfg["seed"])
    torch.manual_seed(seed)
    dataset_path = Path(args.dataset) if args.dataset else workspace / "training" / f"{args.model}_training.csv"
    df = load_training_frame(args.team, args.model, dataset_path).copy()
    features, targets = list(mspec["features"]), list(mspec["targets"])
    enabled = set(feature_cfg["models"][args.model]["enabled_features"])
    disabled = [name for name in features if name not in enabled]
    for name in disabled:
        df[name] = 0.0

    train_df, val_df = _split_frame(df, validation_cfg["method"], float(validation_cfg["validation_fraction"]), seed)
    x_train = torch.tensor(train_df[features].values, dtype=torch.float32)
    y_train = torch.tensor(train_df[targets].values, dtype=torch.float32)
    x_val = torch.tensor(val_df[features].values, dtype=torch.float32)
    y_val = torch.tensor(val_df[targets].values, dtype=torch.float32)

    classification = mspec["kind"] == "classification"
    architecture = model_cfg["architecture"]
    hidden_layers = model_cfg.get("hidden_layers") or ARCHITECTURES[architecture if architecture != "custom" else "medium"]
    model = StudentNet(
        len(features), len(targets), x_train.mean(dim=0), x_train.std(dim=0), classification,
        [int(v) for v in hidden_layers], model_cfg["activation"], float(model_cfg["dropout"])
    )
    optimizer_cls = torch.optim.Adam if model_cfg["optimizer"] == "adam" else torch.optim.AdamW
    optimizer = optimizer_cls(model.parameters(), lr=float(model_cfg["learning_rate"]), weight_decay=float(model_cfg["weight_decay"]))
    loss_fn = _loss(model_cfg["loss"], classification)
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=int(model_cfg["batch_size"]), shuffle=True)

    log_event(
        logger, "training.run.started", team_id=args.team, model_key=args.model, dataset=str(dataset_path),
        training_config=model_cfg, validation_config=validation_cfg, enabled_features=sorted(enabled),
        disabled_features=disabled, train_rows=len(train_df), validation_rows=len(val_df)
    )

    epochs = int(model_cfg["epochs"])
    for epoch in range(epochs):
        model.train()
        last_loss = None
        for xb, yb in loader:
            loss = loss_fn(model(xb), yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            last_loss = loss
        metrics_text = validation_metrics(model, x_val, y_val, classification)
        log_event(logger, "training.epoch.completed", level=logging.DEBUG, team_id=args.team, model_key=args.model,
                  epoch=epoch, training_loss=float(last_loss.detach()) if last_loss is not None else None,
                  validation_metrics=metrics_text)
        if epoch % 20 == 0 or epoch == epochs - 1:
            print(f"epoch={epoch:03d} {metrics_text}")

    output_dir = workspace / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / mspec["artifact"]
    export_model(model, len(features), output)
    loaded = torch.export.load(str(output)).module()
    with torch.inference_mode():
        check = loaded(torch.zeros((1, len(features)), dtype=torch.float32))
    if tuple(check.shape) != (1, len(targets)):
        raise ValueError(f"Export validation failed: expected (1, {len(targets)}), got {tuple(check.shape)}")

    final_metrics = validation_metrics(model, x_val, y_val, classification)
    print(final_metrics)
    print(f"enabled_features={sorted(enabled)}")
    print(f"Saved PyTorch Export model: {output}")
    log_event(logger, "training.run.completed", team_id=args.team, model_key=args.model, artifact=str(output),
              artifact_format=output.suffix, validation_metrics=final_metrics, export_shape=list(check.shape),
              duration_ms=round((perf_counter() - started) * 1000, 2))
    reset_trace_context(tokens)


if __name__ == "__main__":
    main()
