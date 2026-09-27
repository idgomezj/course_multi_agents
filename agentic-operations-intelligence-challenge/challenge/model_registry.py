from __future__ import annotations

from pathlib import Path

import logging

import torch
from torch import nn

from .observability import log_event

logger = logging.getLogger(__name__)


class StudentModelRegistry:
    """Load current PyTorch Export artifacts, with read-only TorchScript compatibility."""

    def __init__(self, model_dir: Path, spec: dict):
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.spec = spec
        self._cache: dict[str, nn.Module] = {}
        log_event(
            logger,
            "models.registry.ready",
            model_dir=str(self.model_dir),
            model_keys=sorted(self.spec.get("models", {})),
        )

    def model_spec(self, key: str) -> dict:
        if key not in self.spec["models"]:
            raise ValueError(f"Unknown model key {key}")
        return self.spec["models"][key]

    def _artifact_path(self, key: str) -> Path:
        filename = self.model_spec(key)["artifact"]
        preferred = self.model_dir / filename
        if preferred.exists():
            return preferred

        # Backward compatibility for artifacts produced before the migration
        # from TorchScript (.pt) to torch.export (.pt2).
        if preferred.suffix == ".pt2":
            legacy = preferred.with_suffix(".pt")
            if legacy.exists():
                return legacy
        return preferred

    def has_model(self, key: str) -> bool:
        path = self._artifact_path(key)
        ready = path.exists()
        log_event(logger, "models.artifact.status", level=logging.DEBUG, model_key=key, path=str(path), ready=ready)
        return ready

    def _load(self, key: str) -> nn.Module:
        path = self._artifact_path(key)
        if not path.exists():
            raise FileNotFoundError(
                f"{self.model_spec(key)['artifact']} not found. "
                f"Train/export {key} before using this prediction tool."
            )

        log_event(logger, "models.load.started", model_key=key, path=str(path), format=path.suffix)
        if path.suffix == ".pt2":
            exported_program = torch.export.load(str(path))
            model = exported_program.module()
        else:
            # Legacy compatibility only. New training code no longer creates TorchScript artifacts.
            model = torch.jit.load(str(path), map_location="cpu").eval()
        log_event(logger, "models.load.completed", model_key=key, path=str(path), format=path.suffix)
        return model

    def predict(self, key: str, feature_values: dict[str, float]) -> list[float]:
        spec = self.model_spec(key)
        if key not in self._cache:
            self._cache[key] = self._load(key)

        ordered = [float(feature_values[name]) for name in spec["features"]]
        x = torch.tensor([ordered], dtype=torch.float32)
        with torch.no_grad():
            y = self._cache[key](x)
        output = [float(v) for v in y.reshape(-1).tolist()]
        log_event(
            logger,
            "models.predict.completed",
            model_key=key,
            task=spec.get("task"),
            features=feature_values,
            ordered_features=spec.get("features"),
            output=output,
        )
        return output
