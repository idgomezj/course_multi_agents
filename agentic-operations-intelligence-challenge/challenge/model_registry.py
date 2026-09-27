from __future__ import annotations

import json
from pathlib import Path

import torch


class StudentModelRegistry:
    """Loads student-exported TorchScript models.

    Each model receives a single 2-D tensor [batch, features]. Students may use any
    PyTorch architecture as long as the exported TorchScript artifact respects the
    feature order and output shape declared in spec.json.
    """

    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.spec_path = model_dir / "spec.json"
        self.spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
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
