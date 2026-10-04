from __future__ import annotations

from pathlib import Path
from threading import RLock

import logging

import torch
from torch import nn

from .observability import log_event

logger = logging.getLogger(__name__)

_TORCH_MODEL_LOAD_LOCK = RLock()
_GLOBAL_MODEL_CACHE: dict[tuple[str, int, int], nn.Module] = {}


def _artifact_signature(path: Path) -> tuple[str, int, int]:
    stat = path.stat()
    return (str(path.resolve()), stat.st_mtime_ns, stat.st_size)


class StudentModelRegistry:
    """Load PyTorch Export artifacts safely and apply student feature masks consistently."""

    def __init__(self, model_dir: Path, spec: dict, feature_config: dict | None = None):
        self.model_dir = model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.spec = spec
        self.feature_config = feature_config or {"models": {}}
        self._cache: dict[str, nn.Module] = {}
        self._cache_lock = RLock()
        log_event(
            logger,
            "models.registry.ready",
            model_dir=str(self.model_dir),
            model_keys=sorted(self.spec.get("models", {})),
            feature_config=self.feature_config,
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
                f"{self.model_spec(key)['artifact']} not found. Train/export {key} before using this prediction tool."
            )
        signature = _artifact_signature(path)
        with _TORCH_MODEL_LOAD_LOCK:
            cached = _GLOBAL_MODEL_CACHE.get(signature)
            if cached is not None:
                log_event(logger, "models.load.cache_hit", model_key=key, path=str(path), format=path.suffix)
                return cached
            log_event(logger, "models.load.started", model_key=key, path=str(path), format=path.suffix, serialized_load=True)
            try:
                if path.suffix == ".pt2":
                    model = torch.export.load(str(path)).module()
                else:
                    model = torch.jit.load(str(path), map_location="cpu")
                    model.eval()
            except Exception as exc:
                log_event(logger, "models.load.failed", level=logging.ERROR, model_key=key, path=str(path), format=path.suffix, error=str(exc))
                raise
            _GLOBAL_MODEL_CACHE[signature] = model
            log_event(logger, "models.load.completed", model_key=key, path=str(path), format=path.suffix, serialized_load=True)
            return model

    def _get_model(self, key: str) -> nn.Module:
        with self._cache_lock:
            if key not in self._cache:
                self._cache[key] = self._load(key)
            return self._cache[key]

    def warmup(self) -> dict[str, bool]:
        status: dict[str, bool] = {}
        for key in self.spec.get("models", {}):
            if not self.has_model(key):
                status[key] = False
                continue
            self._get_model(key)
            status[key] = True
        log_event(logger, "models.warmup.completed", status=status)
        return status

    def enabled_features(self, key: str) -> set[str]:
        spec_features = list(self.model_spec(key).get("features", []))
        cfg = self.feature_config.get("models", {}).get(key, {})
        return set(cfg.get("enabled_features", spec_features))

    def predict(self, key: str, feature_values: dict[str, float]) -> list[float]:
        spec = self.model_spec(key)
        model = self._get_model(key)
        enabled = self.enabled_features(key)
        masked_features = {
            name: float(feature_values[name]) if name in enabled else 0.0
            for name in spec["features"]
        }
        ordered = [masked_features[name] for name in spec["features"]]
        x = torch.tensor([ordered], dtype=torch.float32)
        with torch.inference_mode():
            y = model(x)
        output = [float(v) for v in y.reshape(-1).tolist()]
        log_event(
            logger,
            "models.predict.completed",
            model_key=key,
            task=spec.get("task"),
            features=feature_values,
            masked_features=masked_features,
            enabled_features=sorted(enabled),
            ordered_features=spec.get("features"),
            output=output,
        )
        return output
