from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .config import DATA_DIR


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = deepcopy(value)
    return out


@lru_cache
def available_teams() -> tuple[str, ...]:
    return tuple(sorted(p.stem for p in (DATA_DIR / "teams").glob("team_*.yaml")))


@lru_cache
def load_case(team_id: str) -> dict[str, Any]:
    if team_id not in available_teams():
        raise KeyError(team_id)
    merged = _deep_merge(
        _load_yaml(DATA_DIR / "base.yaml"),
        _load_yaml(DATA_DIR / "teams" / f"{team_id}.yaml"),
    )
    merged["team_id"] = team_id
    return merged


@lru_cache
def load_model_spec(team_id: str) -> dict[str, Any]:
    if team_id not in available_teams():
        raise KeyError(team_id)
    path = DATA_DIR / "teams" / team_id / "model_spec.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache
def load_knowledge(team_id: str) -> tuple[dict[str, str], ...]:
    if team_id not in available_teams():
        raise KeyError(team_id)
    team_root = DATA_DIR / "teams" / team_id
    roots = [team_root / "knowledge", team_root / "documents"]
    documents = []
    for root in roots:
        if not root.exists():
            continue
        documents.extend(
            {"name": p.name, "content": p.read_text(encoding="utf-8")}
            for p in sorted(root.glob("*.md"))
        )
    return tuple(documents)


def public_scenarios(team_id: str) -> list[dict[str, Any]]:
    return deepcopy(load_case(team_id).get("public_scenarios", []))


def public_scenario(team_id: str, scenario_id: str) -> dict[str, Any]:
    for scenario in public_scenarios(team_id):
        if scenario["id"] == scenario_id:
            return scenario
    raise KeyError(scenario_id)


def case_without_scenarios(team_id: str) -> dict[str, Any]:
    case = deepcopy(load_case(team_id))
    case.pop("public_scenarios", None)
    return case
