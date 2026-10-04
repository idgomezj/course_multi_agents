from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from .config import student_path


DEFAULT_TRAINING_CONFIG: dict[str, Any] = {
    "models": {
        "model_a": {
            "architecture": "medium",
            "hidden_layers": None,
            "activation": "relu",
            "dropout": 0.0,
            "epochs": 120,
            "learning_rate": 0.003,
            "batch_size": 64,
            "optimizer": "adamw",
            "loss": "auto",
            "weight_decay": 0.0001,
        },
        "model_b": {
            "architecture": "medium",
            "hidden_layers": None,
            "activation": "relu",
            "dropout": 0.0,
            "epochs": 120,
            "learning_rate": 0.003,
            "batch_size": 64,
            "optimizer": "adamw",
            "loss": "auto",
            "weight_decay": 0.0001,
        },
    },
    "validation": {"method": "chronological", "validation_fraction": 0.20, "seed": 42},
}

DEFAULT_RUNTIME_CONFIG: dict[str, Any] = {
    "forecast_policy": {
        "weights": {
            "model_a": 0.40,
            "confirmed_orders": 0.25,
            "moving_average": 0.15,
            "exponential_smoothing": 0.10,
            "seasonal": 0.10,
        },
        "high_uncertainty_threshold": 0.35,
        "high_uncertainty_model_multiplier": 0.70,
        "high_uncertainty_confirmed_multiplier": 1.20,
    },
    "risk_policy": {
        "medium_threshold": 0.25,
        "high_threshold": 0.50,
        "safety_stock_factor": 1.65,
        "forecast_disagreement_review": 0.25,
    },
    "planning_objectives": {
        "priorities": {
            "service": 0.40,
            "total_cost": 0.35,
            "ending_inventory": 0.15,
            "plan_stability": 0.10,
        },
        "soft_constraints": {},
    },
    "tool_policy": {
        "required_before_finalize": ["calculate_plan_cost", "validate_plan"],
        "max_replans": 2,
        "guidance": [],
    },
    "manager_llm": {
        "provider": None,
        "temperature": 0.20,
        "max_tokens": 3000,
        "reasoning_mode": "medium",
        "max_rag_documents": 5,
        "include_model_diagnostics": True,
        "include_cost_breakdown": True,
        "include_previous_plan": False,
    },
    "business_assumptions": {},
}


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return value


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _float(value: Any, default: float, low: float | None = None, high: float | None = None) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if low is not None:
        number = max(low, number)
    if high is not None:
        number = min(high, number)
    return number


def _int(value: Any, default: int, low: int | None = None, high: int | None = None) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    if low is not None:
        number = max(low, number)
    if high is not None:
        number = min(high, number)
    return number


def _normalize_weights(weights: dict[str, Any], defaults: dict[str, float]) -> dict[str, float]:
    parsed = {key: max(0.0, _float(weights.get(key), default)) for key, default in defaults.items()}
    total = sum(parsed.values())
    if total <= 1e-12:
        return dict(defaults)
    return {key: value / total for key, value in parsed.items()}


def load_model_contract(team_id: str) -> dict[str, Any]:
    path = student_path(team_id) / "training" / "model_contract.json"
    if not path.exists():
        raise FileNotFoundError(f"Model contract not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_feature_config(team_id: str) -> dict[str, Any]:
    workspace = student_path(team_id)
    contract = load_model_contract(team_id)
    raw = _read_yaml(workspace / "training" / "feature_config.yaml")
    raw_models = raw.get("models", {}) if isinstance(raw.get("models", {}), dict) else {}
    models: dict[str, Any] = {}
    for model_key, spec in contract.get("models", {}).items():
        allowed = list(spec.get("features", []))
        configured = raw_models.get(model_key, {})
        if not isinstance(configured, dict):
            configured = {}
        enabled = configured.get("enabled_features", allowed)
        if enabled is None:
            enabled = allowed
        if not isinstance(enabled, list):
            raise ValueError(f"feature_config.yaml {model_key}.enabled_features must be a list")
        unknown = [name for name in enabled if name not in allowed]
        if unknown:
            raise ValueError(
                f"feature_config.yaml enables unknown features for {model_key}: {unknown}. "
                f"Allowed features: {allowed}"
            )
        if not enabled:
            raise ValueError(f"At least one feature must remain enabled for {model_key}")
        models[model_key] = {
            "enabled_features": enabled,
            "disabled_features": [name for name in allowed if name not in enabled],
        }
    return {"models": models}


def load_training_config(team_id: str) -> dict[str, Any]:
    workspace = student_path(team_id)
    cfg = _deep_merge(DEFAULT_TRAINING_CONFIG, _read_yaml(workspace / "training" / "training_config.yaml"))
    for model_key in ("model_a", "model_b"):
        model = cfg.setdefault("models", {}).setdefault(model_key, {})
        model["architecture"] = str(model.get("architecture", "medium")).lower()
        if model["architecture"] not in {"small", "medium", "large", "custom"}:
            raise ValueError(f"Unsupported architecture '{model['architecture']}' for {model_key}")
        model["activation"] = str(model.get("activation", "relu")).lower()
        if model["activation"] not in {"relu", "silu", "tanh"}:
            raise ValueError(f"Unsupported activation '{model['activation']}' for {model_key}")
        model["dropout"] = _float(model.get("dropout"), 0.0, 0.0, 0.75)
        model["epochs"] = _int(model.get("epochs"), 120, 10, 2000)
        model["learning_rate"] = _float(model.get("learning_rate"), 0.003, 1e-6, 1.0)
        model["batch_size"] = _int(model.get("batch_size"), 64, 4, 4096)
        model["optimizer"] = str(model.get("optimizer", "adamw")).lower()
        if model["optimizer"] not in {"adam", "adamw"}:
            raise ValueError(f"Unsupported optimizer '{model['optimizer']}' for {model_key}")
        model["loss"] = str(model.get("loss", "auto")).lower()
        if model["loss"] not in {"auto", "mse", "mae", "huber", "bce"}:
            raise ValueError(f"Unsupported loss '{model['loss']}' for {model_key}")
        model["weight_decay"] = _float(model.get("weight_decay"), 0.0001, 0.0, 1.0)
        hidden = model.get("hidden_layers")
        if hidden is not None:
            if not isinstance(hidden, list) or not hidden or any(int(v) <= 0 for v in hidden):
                raise ValueError(f"{model_key}.hidden_layers must be a non-empty list of positive integers")
            model["hidden_layers"] = [min(1024, int(v)) for v in hidden[:6]]
    validation = cfg.setdefault("validation", {})
    validation["method"] = str(validation.get("method", "chronological")).lower()
    if validation["method"] not in {"chronological", "random"}:
        raise ValueError("validation.method must be chronological or random")
    validation["validation_fraction"] = _float(validation.get("validation_fraction"), 0.20, 0.10, 0.40)
    validation["seed"] = _int(validation.get("seed"), 42, 0, 2_147_483_647)
    return cfg


def load_document_priorities(team_id: str) -> dict[str, Any]:
    workspace = student_path(team_id)
    raw = _read_yaml(workspace / "rag" / "document_priorities.yaml")
    default_weight = _float(raw.get("default_weight"), 1.0, 0.10, 2.0)
    authority_defaults = {
        "official": 1.20,
        "contract": 1.15,
        "advisory": 1.0,
        "draft": 0.75,
        "obsolete": 0.40,
        "irrelevant": 0.20,
    }
    authority_weights = raw.get("authority_weights", {})
    if not isinstance(authority_weights, dict):
        authority_weights = {}
    authority_weights = {
        key: _float(authority_weights.get(key), value, 0.10, 2.0)
        for key, value in authority_defaults.items()
    }
    docs = raw.get("documents", {})
    if not isinstance(docs, dict):
        raise ValueError("document_priorities.yaml documents must be a mapping")
    normalized_docs: dict[str, Any] = {}
    for name, value in docs.items():
        if isinstance(value, (int, float)):
            normalized_docs[str(name)] = {"weight": _float(value, 1.0, 0.10, 2.0), "authority": "advisory"}
        elif isinstance(value, dict):
            authority = str(value.get("authority", "advisory")).lower()
            normalized_docs[str(name)] = {
                "weight": _float(value.get("weight"), 1.0, 0.10, 2.0),
                "authority": authority if authority in authority_weights else "advisory",
                "effective_date": value.get("effective_date"),
                "notes": value.get("notes"),
            }
        else:
            raise ValueError(f"Invalid document priority entry for {name}")
    return {"default_weight": default_weight, "authority_weights": authority_weights, "documents": normalized_docs}


def load_runtime_config(team_id: str) -> dict[str, Any]:
    workspace = student_path(team_id)
    cfg = deepcopy(DEFAULT_RUNTIME_CONFIG)
    file_map = {
        "forecast_policy": workspace / "config" / "forecast_policy.yaml",
        "risk_policy": workspace / "config" / "risk_policy.yaml",
        "planning_objectives": workspace / "config" / "planning_objectives.yaml",
        "tool_policy": workspace / "config" / "tool_policy.yaml",
        "manager_llm": workspace / "config" / "manager_llm.yaml",
        "business_assumptions": workspace / "assumptions" / "business_assumptions.yaml",
    }
    for key, path in file_map.items():
        raw = _read_yaml(path)
        cfg[key] = raw if key == "business_assumptions" else _deep_merge(cfg[key], raw)

    fp = cfg["forecast_policy"]
    fp["weights"] = _normalize_weights(fp.get("weights", {}), DEFAULT_RUNTIME_CONFIG["forecast_policy"]["weights"])
    fp["high_uncertainty_threshold"] = _float(fp.get("high_uncertainty_threshold"), 0.35, 0.0, 1.0)
    fp["high_uncertainty_model_multiplier"] = _float(fp.get("high_uncertainty_model_multiplier"), 0.70, 0.0, 2.0)
    fp["high_uncertainty_confirmed_multiplier"] = _float(fp.get("high_uncertainty_confirmed_multiplier"), 1.20, 0.0, 2.0)

    rp = cfg["risk_policy"]
    rp["medium_threshold"] = _float(rp.get("medium_threshold"), 0.25, 0.0, 1.0)
    rp["high_threshold"] = _float(rp.get("high_threshold"), 0.50, 0.0, 1.0)
    if rp["high_threshold"] <= rp["medium_threshold"]:
        raise ValueError("risk_policy.high_threshold must be greater than medium_threshold")
    rp["safety_stock_factor"] = _float(rp.get("safety_stock_factor"), 1.65, 0.25, 4.0)
    rp["forecast_disagreement_review"] = _float(rp.get("forecast_disagreement_review"), 0.25, 0.0, 2.0)

    planning = cfg["planning_objectives"]
    priorities = planning.get("priorities", {}) if isinstance(planning.get("priorities", {}), dict) else {}
    planning["priorities"] = _normalize_weights(priorities, DEFAULT_RUNTIME_CONFIG["planning_objectives"]["priorities"])
    if not isinstance(planning.get("soft_constraints", {}), dict):
        raise ValueError("planning_objectives.soft_constraints must be a mapping")

    tp = cfg["tool_policy"]
    required = tp.get("required_before_finalize", ["calculate_plan_cost", "validate_plan"])
    if not isinstance(required, list):
        raise ValueError("tool_policy.required_before_finalize must be a list")
    tp["required_before_finalize"] = [str(x) for x in required]
    tp["max_replans"] = _int(tp.get("max_replans"), 2, 0, 6)
    if not isinstance(tp.get("guidance", []), list):
        raise ValueError("tool_policy.guidance must be a list")

    llm = cfg["manager_llm"]
    provider = llm.get("provider")
    if provider in {"", "default", "null"}:
        provider = None
    if provider is not None:
        provider = str(provider).lower()
        if provider not in {"google", "openai", "anthropic", "deepseek"}:
            raise ValueError("manager_llm.provider must be google, openai, anthropic, deepseek, or null")
    llm["provider"] = provider
    llm["temperature"] = _float(llm.get("temperature"), 0.20, 0.0, 2.0)
    llm["max_tokens"] = _int(llm.get("max_tokens"), 3000, 256, 16000)
    llm["reasoning_mode"] = str(llm.get("reasoning_mode", "medium")).lower()
    if llm["reasoning_mode"] not in {"low", "medium", "high"}:
        raise ValueError("manager_llm.reasoning_mode must be low, medium, or high")
    llm["max_rag_documents"] = _int(llm.get("max_rag_documents"), 5, 1, 12)
    for key in ("include_model_diagnostics", "include_cost_breakdown", "include_previous_plan"):
        llm[key] = bool(llm.get(key, DEFAULT_RUNTIME_CONFIG["manager_llm"][key]))

    cfg["feature_config"] = load_feature_config(team_id)
    cfg["document_priorities"] = load_document_priorities(team_id)
    return cfg


def config_file_status(team_id: str) -> dict[str, bool]:
    workspace = student_path(team_id)
    paths = {
        "training_config": workspace / "training" / "training_config.yaml",
        "feature_config": workspace / "training" / "feature_config.yaml",
        "rag_config": workspace / "rag" / "config.yaml",
        "document_priorities": workspace / "rag" / "document_priorities.yaml",
        "forecast_policy": workspace / "config" / "forecast_policy.yaml",
        "risk_policy": workspace / "config" / "risk_policy.yaml",
        "planning_objectives": workspace / "config" / "planning_objectives.yaml",
        "tool_policy": workspace / "config" / "tool_policy.yaml",
        "manager_llm": workspace / "config" / "manager_llm.yaml",
        "business_assumptions": workspace / "assumptions" / "business_assumptions.yaml",
    }
    return {name: path.exists() for name, path in paths.items()}


def student_config_summary(team_id: str) -> dict[str, Any]:
    return {
        "runtime": load_runtime_config(team_id),
        "training": load_training_config(team_id),
        "config_files": config_file_status(team_id),
    }
