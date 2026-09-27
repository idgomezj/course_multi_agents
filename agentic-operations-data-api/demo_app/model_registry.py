from __future__ import annotations

from pathlib import Path

import torch
from torch import nn


class StudentModelRegistry:
    """Load current PyTorch Export artifacts, with read-only TorchScript compatibility."""

    def __init__(self, model_dir: Path, spec: dict):
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.spec = spec
        self._cache: dict[str, nn.Module] = {}

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
        return self._artifact_path(key).exists()

    def _load(self, key: str) -> nn.Module:
        path = self._artifact_path(key)
        if not path.exists():
            raise FileNotFoundError(
                f"{self.model_spec(key)['artifact']} not found. "
                f"Train/export {key} before using this prediction tool."
            )

        if path.suffix == ".pt2":
            exported_program = torch.export.load(str(path))
            return exported_program.module()

        # Legacy compatibility only. New training code no longer creates
        # TorchScript artifacts.
        return torch.jit.load(str(path), map_location="cpu").eval()

    def predict(self, key: str, feature_values: dict[str, float]) -> list[float]:
        spec = self.model_spec(key)
        if key not in self._cache:
            self._cache[key] = self._load(key)

        ordered = [float(feature_values[name]) for name in spec["features"]]
        x = torch.tensor([ordered], dtype=torch.float32)
        with torch.no_grad():
            y = self._cache[key](x)
        return [float(v) for v in y.reshape(-1).tolist()]
