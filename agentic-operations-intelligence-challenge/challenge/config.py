from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENT_DIR = ROOT / "student"
FRONTEND_DIR = ROOT / "frontend"


def student_path(team_id: str) -> Path:
    path = STUDENT_DIR / team_id
    if not path.exists():
        raise ValueError(
            f"Student workspace not found for {team_id}. "
            "Use the team package assigned by the instructor."
        )
    return path
