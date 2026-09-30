from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_SCENARIO_ACCESS_FILE = DATA_DIR / "scenario_access.json"


@dataclass(frozen=True)
class Settings:
    # Legacy/general team tokens are still accepted for non-hidden access.
    team_tokens: dict[str, str]
    # team_id -> scope(public|hidden) -> token/share-field configuration
    scenario_access: dict[str, dict[str, dict[str, Any]]]
    instructor_token: str | None
    allow_unauthenticated_dev: bool


def _load_scenario_access() -> dict[str, dict[str, dict[str, Any]]]:
    configured = os.getenv("SCENARIO_ACCESS_FILE")
    path = Path(configured) if configured else DEFAULT_SCENARIO_ACCESS_FILE
    if not path.is_absolute():
        path = ROOT / path

    payload: dict[str, Any] = {}
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    teams = payload.get("teams", {})
    if not isinstance(teams, dict):
        raise RuntimeError("scenario_access.json must contain an object named 'teams'")

    # Optional production override. This changes token values only; the checked-in
    # file remains the authoritative place for share-field policy.
    # Shape: {"team_1":{"public":"...","hidden":"..."}, ...}
    override_raw = os.getenv("SCENARIO_TOKENS_JSON", "").strip()
    if override_raw:
        try:
            overrides = json.loads(override_raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("SCENARIO_TOKENS_JSON must be valid JSON") from exc
        if not isinstance(overrides, dict):
            raise RuntimeError("SCENARIO_TOKENS_JSON must be a JSON object")
        for team_id, scopes in overrides.items():
            if not isinstance(scopes, dict):
                continue
            team_cfg = teams.setdefault(str(team_id), {})
            for scope in ("public", "hidden"):
                if scope in scopes:
                    scope_cfg = team_cfg.setdefault(scope, {})
                    scope_cfg["token"] = str(scopes[scope])

    return {
        str(team_id): {
            str(scope): dict(scope_cfg)
            for scope, scope_cfg in team_cfg.items()
            if isinstance(scope_cfg, dict)
        }
        for team_id, team_cfg in teams.items()
        if isinstance(team_cfg, dict)
    }


@lru_cache
def get_settings() -> Settings:
    raw = os.getenv("TEAM_TOKENS_JSON", "{}")
    try:
        tokens = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("TEAM_TOKENS_JSON must be valid JSON") from exc
    if not isinstance(tokens, dict):
        raise RuntimeError("TEAM_TOKENS_JSON must be a JSON object")

    return Settings(
        team_tokens={str(k): str(v) for k, v in tokens.items()},
        scenario_access=_load_scenario_access(),
        instructor_token=os.getenv("INSTRUCTOR_TOKEN") or None,
        allow_unauthenticated_dev=os.getenv("ALLOW_UNAUTHENTICATED_DEV", "false").lower() == "true",
    )


def scenario_scope_config(team_id: str, scope: str) -> dict[str, Any]:
    return dict(get_settings().scenario_access.get(team_id, {}).get(scope, {}))
