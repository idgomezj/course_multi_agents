from __future__ import annotations

import hmac

from fastapi import Header, HTTPException

from .config import get_settings
from .store import available_teams


def _equal(a: str | None, b: str | None) -> bool:
    return bool(a and b and hmac.compare_digest(a, b))


def authorize_team(
    team_id: str,
    x_team_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> str:
    settings = get_settings()
    if team_id not in available_teams():
        raise HTTPException(status_code=404, detail="Unknown team")

    if settings.allow_unauthenticated_dev:
        return team_id
    if _equal(x_instructor_token, settings.instructor_token):
        return team_id
    expected = settings.team_tokens.get(team_id)
    if _equal(x_team_token, expected):
        return team_id
    raise HTTPException(status_code=403, detail="Token is not authorized for this team")


def authorized_teams(
    x_team_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> list[str]:
    settings = get_settings()
    teams = list(available_teams())
    if settings.allow_unauthenticated_dev or _equal(x_instructor_token, settings.instructor_token):
        return teams
    for team in teams:
        if _equal(x_team_token, settings.team_tokens.get(team)):
            return [team]
    raise HTTPException(status_code=403, detail="Invalid team token")
