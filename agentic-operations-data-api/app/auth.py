from __future__ import annotations

import hmac
import logging

from fastapi import Header, HTTPException

from .config import get_settings
from .store import available_teams
from .observability import log_event

logger = logging.getLogger(__name__)


def _equal(a: str | None, b: str | None) -> bool:
    return bool(a and b and hmac.compare_digest(a, b))


def authorize_team(
    team_id: str,
    x_team_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> str:
    settings = get_settings()
    if team_id not in available_teams():
        log_event(logger, "auth.team.unknown", level=logging.WARNING, team_id=team_id)
        raise HTTPException(status_code=404, detail="Unknown team")

    if settings.allow_unauthenticated_dev:
        log_event(logger, "auth.team.allowed", team_id=team_id, auth_mode="unauthenticated_dev")
        return team_id
    if _equal(x_instructor_token, settings.instructor_token):
        log_event(logger, "auth.team.allowed", team_id=team_id, auth_mode="instructor")
        return team_id
    expected = settings.team_tokens.get(team_id)
    if _equal(x_team_token, expected):
        log_event(logger, "auth.team.allowed", team_id=team_id, auth_mode="team")
        return team_id
    log_event(logger, "auth.team.denied", level=logging.WARNING, team_id=team_id, has_team_token=bool(x_team_token), has_instructor_token=bool(x_instructor_token))
    raise HTTPException(status_code=403, detail="Token is not authorized for this team")


def authorized_teams(
    x_team_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> list[str]:
    settings = get_settings()
    teams = list(available_teams())
    if settings.allow_unauthenticated_dev or _equal(x_instructor_token, settings.instructor_token):
        mode = "unauthenticated_dev" if settings.allow_unauthenticated_dev else "instructor"
        log_event(logger, "auth.teams.allowed", auth_mode=mode, teams=teams)
        return teams
    for team in teams:
        if _equal(x_team_token, settings.team_tokens.get(team)):
            log_event(logger, "auth.teams.allowed", auth_mode="team", teams=[team])
            return [team]
    log_event(logger, "auth.teams.denied", level=logging.WARNING, has_team_token=bool(x_team_token), has_instructor_token=bool(x_instructor_token))
    raise HTTPException(status_code=403, detail="Invalid team token")
