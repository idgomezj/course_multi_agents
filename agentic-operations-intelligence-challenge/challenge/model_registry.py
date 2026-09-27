from __future__ import annotations

from pathlib import Path

import torch


class StudentModelRegistry:
    """Loads student TorchScript artifacts using the model contract supplied by the Data API."""

    def __init__(self, model_dir: Path, spec: dict):
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.spec = spec
        self._cache: dict[str, torch.jit.ScriptModule] = {}

    def model_spec(self, key: str) -> dict:
        if key not in self.spec["models"]:
            raise ValueError(f"Unknown model key {key}")
        return self.spec["models"][key]

    def has_model(self, key: str) -> bool:
        filename = self.model_spec(key)["artifact"]
        return (self.model_dir / filename).exists()

    def predict(self, key: str, feature_values: dict[str, float]) -> list[float]:
        spec = self.model_spec(key)
        filename = spec["artifact"]
        path = self.model_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"{filename} not found. Train/export {key} before using this prediction tool."
            )
        if key not in self._cache:
            self._cache[key] = torch.jit.load(str(path), map_location="cpu").eval()
        ordered = [float(feature_values[name]) for name in spec["features"]]
        x = torch.tensor([ordered], dtype=torch.float32)
        with torch.no_grad():
            y = self._cache[key](x)
        return [float(v) for v in y.reshape(-1).tolist()]
