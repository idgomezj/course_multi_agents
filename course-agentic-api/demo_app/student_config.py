from __future__ import annotations

import yaml
from copy import deepcopy
from pathlib import Path
from typing import Any

from .config import DEMO_DIR


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return value


def _normalize_weights(weights: dict[str, Any]) -> dict[str, float]:
    parsed = {str(k): max(0.0, float(v)) for k, v in weights.items()}
    total = sum(parsed.values())
    if total <= 1e-12:
        raise ValueError("Configured weights must sum to a positive value")
    return {k: v / total for k, v in parsed.items()}


def load_feature_config() -> dict[str, Any]:
    return _read_yaml(DEMO_DIR / "training" / "feature_config.yaml")


def load_training_config() -> dict[str, Any]:
    return _read_yaml(DEMO_DIR / "training" / "training_config.yaml")


def load_document_priorities() -> dict[str, Any]:
    return _read_yaml(DEMO_DIR / "rag" / "document_priorities.yaml")


def load_runtime_config() -> dict[str, Any]:
    cfg = {
        "forecast_policy": _read_yaml(DEMO_DIR / "config" / "forecast_policy.yaml"),
        "risk_policy": _read_yaml(DEMO_DIR / "config" / "risk_policy.yaml"),
        "planning_objectives": _read_yaml(DEMO_DIR / "config" / "planning_objectives.yaml"),
        "tool_policy": _read_yaml(DEMO_DIR / "config" / "tool_policy.yaml"),
        "manager_llm": _read_yaml(DEMO_DIR / "config" / "manager_llm.yaml"),
        "business_assumptions": _read_yaml(DEMO_DIR / "assumptions" / "business_assumptions.yaml"),
        "feature_config": load_feature_config(),
        "document_priorities": load_document_priorities(),
    }

    fp = cfg["forecast_policy"]
    fp["weights"] = _normalize_weights(fp.get("weights", {}))
    fp["high_uncertainty_threshold"] = max(0.0, min(1.0, float(fp.get("high_uncertainty_threshold", 0.30))))
    fp["high_uncertainty_model_multiplier"] = max(0.0, float(fp.get("high_uncertainty_model_multiplier", 0.80)))
    fp["high_uncertainty_confirmed_multiplier"] = max(0.0, float(fp.get("high_uncertainty_confirmed_multiplier", 1.15)))

    rp = cfg["risk_policy"]
    rp["medium_threshold"] = max(0.0, min(1.0, float(rp.get("medium_threshold", 0.20))))
    rp["high_threshold"] = max(0.0, min(1.0, float(rp.get("high_threshold", 0.45))))
    if rp["high_threshold"] <= rp["medium_threshold"]:
        raise ValueError("risk_policy.high_threshold must exceed medium_threshold")
    rp["safety_stock_factor"] = max(0.25, min(4.0, float(rp.get("safety_stock_factor", 1.40))))

    planning = cfg["planning_objectives"]
    planning["priorities"] = _normalize_weights(planning.get("priorities", {}))

    llm = cfg["manager_llm"]
    llm["temperature"] = max(0.0, min(2.0, float(llm.get("temperature", 0.10))))
    llm["max_tokens"] = max(256, min(16000, int(llm.get("max_tokens", 3500))))
    llm["max_rag_documents"] = max(1, min(12, int(llm.get("max_rag_documents", 5))))

    return cfg


def config_status() -> dict[str, bool]:
    paths = {
        "training_config": DEMO_DIR / "training" / "training_config.yaml",
        "feature_config": DEMO_DIR / "training" / "feature_config.yaml",
        "rag_config": DEMO_DIR / "rag" / "config.yaml",
        "document_priorities": DEMO_DIR / "rag" / "document_priorities.yaml",
        "forecast_policy": DEMO_DIR / "config" / "forecast_policy.yaml",
        "risk_policy": DEMO_DIR / "config" / "risk_policy.yaml",
        "planning_objectives": DEMO_DIR / "config" / "planning_objectives.yaml",
        "tool_policy": DEMO_DIR / "config" / "tool_policy.yaml",
        "manager_llm": DEMO_DIR / "config" / "manager_llm.yaml",
        "business_assumptions": DEMO_DIR / "assumptions" / "business_assumptions.yaml",
    }
    return {name: path.exists() for name, path in paths.items()}
