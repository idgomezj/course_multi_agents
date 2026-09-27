from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
STUDENT_DIR = ROOT / "student"
FRONTEND_DIR = ROOT / "frontend"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def available_teams() -> list[str]:
    return sorted(p.stem for p in CASES_DIR.glob("team_*.yaml"))


def load_case(team_id: str) -> dict[str, Any]:
    if team_id not in available_teams():
        raise ValueError(f"Unknown team_id: {team_id}")
    base = load_yaml(CASES_DIR / "base.yaml")
    team = load_yaml(CASES_DIR / f"{team_id}.yaml")
    merged = deep_merge(base, team)
    merged["team_id"] = team_id
    return merged


def student_path(team_id: str) -> Path:
    path = STUDENT_DIR / team_id
    if not path.exists():
        raise ValueError(f"Student workspace not found for {team_id}")
    return path
