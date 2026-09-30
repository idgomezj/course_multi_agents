from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import ROOT
from .observability import log_event

import logging

logger = logging.getLogger(__name__)
_HISTORY_LOCK = threading.Lock()


def history_root() -> Path:
    configured = os.getenv("AI_HISTORY_DIR", "").strip()
    root = Path(configured) if configured else ROOT / "audit" / "history"
    if not root.is_absolute():
        root = ROOT / root
    return root


def team_history_path(team_id: str) -> Path:
    return history_root() / f"{team_id}.json"


def append_team_history(
    team_id: str,
    *,
    who: str,
    question: str,
    summary: str,
) -> dict[str, Any]:
    """Append one AI-assistance record while retaining all prior team history."""
    root = history_root()
    root.mkdir(parents=True, exist_ok=True)
    path = team_history_path(team_id)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    record = {
        "timestamp": timestamp,
        "who": who.strip(),
        "question": question.strip(),
        "summary": summary.strip(),
    }

    with _HISTORY_LOCK:
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"History file is not valid JSON: {path}") from exc
        else:
            payload = {"team_id": team_id, "history": []}

        if payload.get("team_id") != team_id:
            raise RuntimeError(f"History file team mismatch: {path}")

        history = payload.setdefault("history", [])
        if not isinstance(history, list):
            raise RuntimeError(f"History file must contain a list named 'history': {path}")

        history.append(record)

        # Atomic replacement prevents a partial JSON document if the process
        # stops during a write. Existing history entries are retained.
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        tmp.replace(path)
        total_entries = len(history)

    log_event(
        logger,
        "ai_history.appended",
        team_id=team_id,
        who=who,
        total_entries=total_entries,
        history_file=str(path),
    )
    return {
        "saved": True,
        "team_id": team_id,
        "timestamp": timestamp,
        "who": who.strip(),
        "total_entries": total_entries,
    }
