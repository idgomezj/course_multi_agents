from __future__ import annotations

import json
from pathlib import Path
from threading import RLock

import torch
from torch import nn


_TORCH_MODEL_LOAD_LOCK = RLock()
_GLOBAL_MODEL_CACHE: dict[tuple[str, int, int], nn.Module] = {}


def _artifact_signature(path: Path) -> tuple[str, int, int]:
    stat = path.stat()
    return (str(path.resolve()), stat.st_mtime_ns, stat.st_size)


class StudentModelRegistry:
    """Load student PyTorch Export artifacts using the local fixed model contract."""

    def __init__(self, model_dir: Path, spec: dict | None = None):
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        if spec is None:
            contract = model_dir.parent / "training" / "model_contract.json"
            if not contract.exists():
                raise FileNotFoundError(
                    f"Local model contract not found: {contract}. "
                    "The student model contract is distributed with the case, not by the Data API."
                )
            spec = json.loads(contract.read_text(encoding="utf-8"))
        self.spec = spec
        self._cache: dict[str, nn.Module] = {}
        self._cache_lock = RLock()

    def model_spec(self, key: str) -> dict:
        if key not in self.spec["models"]:
            raise ValueError(f"Unknown model key {key}")
        return self.spec["models"][key]

    def _artifact_path(self, key: str) -> Path:
        filename = self.model_spec(key)["artifact"]
        preferred = self.model_dir / filename
        if preferred.exists():
            return preferred
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
                f"Build the training dataset and train/export {key} before running this prediction tool."
            )

        signature = _artifact_signature(path)
        with _TORCH_MODEL_LOAD_LOCK:
            cached = _GLOBAL_MODEL_CACHE.get(signature)
            if cached is not None:
                return cached

            if path.suffix == ".pt2":
                model = torch.export.load(str(path)).module()
            else:
                model = torch.jit.load(str(path), map_location="cpu")
                model.eval()

            _GLOBAL_MODEL_CACHE[signature] = model
            return model

    def _get_model(self, key: str) -> nn.Module:
        with self._cache_lock:
            if key not in self._cache:
                self._cache[key] = self._load(key)
            return self._cache[key]

    def predict(self, key: str, feature_values: dict[str, float]) -> list[float]:
        spec = self.model_spec(key)
        model = self._get_model(key)
        ordered = [float(feature_values[name]) for name in spec["features"]]
        x = torch.tensor([ordered], dtype=torch.float32)
        with torch.inference_mode():
            y = model(x)
        return [float(v) for v in y.reshape(-1).tolist()]
