from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


@dataclass(frozen=True)
class Settings:
    team_tokens: dict[str, str]
    instructor_token: str | None
    allow_unauthenticated_dev: bool


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
        instructor_token=os.getenv("INSTRUCTOR_TOKEN") or None,
        allow_unauthenticated_dev=os.getenv("ALLOW_UNAUTHENTICATED_DEV", "false").lower() == "true",
    )
