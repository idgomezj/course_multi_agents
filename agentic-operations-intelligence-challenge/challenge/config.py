from __future__ import annotations

import os
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


def student_team_ids() -> list[str]:
    """Teams available to this student runtime. Case 0 is instructor-only."""
    assigned = os.getenv("ASSIGNED_TEAM_ID", "").strip()
    if assigned:
        if assigned not in {f"team_{i}" for i in range(1, 6)}:
            raise ValueError(
                "ASSIGNED_TEAM_ID must be one of team_1, team_2, team_3, team_4, team_5"
            )
        student_path(assigned)
        return [assigned]

    teams = [
        path.name
        for path in sorted(STUDENT_DIR.glob("team_*"))
        if path.is_dir() and path.name in {f"team_{i}" for i in range(1, 6)}
    ]
    if not teams:
        raise ValueError("No Team 1–5 student workspace is available.")
    return teams
