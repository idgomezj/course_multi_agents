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


def _presented_token(
    x_scenario_token: str | None,
    x_team_token: str | None,
) -> str | None:
    # X-Scenario-Token is explicit and preferred. X-Team-Token remains supported
    # so existing clients do not break.
    return x_scenario_token or x_team_token


def scenario_scope_for_token(team_id: str, token: str | None) -> str | None:
    settings = get_settings()
    team_cfg = settings.scenario_access.get(team_id, {})
    for scope in ("public", "hidden"):
        expected = team_cfg.get(scope, {}).get("token")
        if _equal(token, str(expected) if expected else None):
            return scope

    # Legacy team tokens map to public scope only.
    if _equal(token, settings.team_tokens.get(team_id)):
        return "public"
    return None


def authorize_team(
    team_id: str,
    x_team_token: str | None = Header(default=None),
    x_scenario_token: str | None = Header(default=None),
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

    token = _presented_token(x_scenario_token, x_team_token)
    scope = scenario_scope_for_token(team_id, token)
    if scope:
        log_event(logger, "auth.team.allowed", team_id=team_id, auth_mode=f"scenario_{scope}")
        return team_id

    log_event(
        logger,
        "auth.team.denied",
        level=logging.WARNING,
        team_id=team_id,
        has_team_token=bool(x_team_token),
        has_scenario_token=bool(x_scenario_token),
        has_instructor_token=bool(x_instructor_token),
    )
    raise HTTPException(status_code=403, detail="Token is not authorized for this team")


def authorize_scenario_access(
    team_id: str,
    x_team_token: str | None = Header(default=None),
    x_scenario_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> str:
    """Return public, hidden, or instructor according to the presented token."""
    settings = get_settings()
    if team_id not in available_teams():
        raise HTTPException(status_code=404, detail="Unknown team")

    if settings.allow_unauthenticated_dev:
        return "public"
    if _equal(x_instructor_token, settings.instructor_token):
        return "instructor"

    token = _presented_token(x_scenario_token, x_team_token)
    scope = scenario_scope_for_token(team_id, token)
    if scope:
        log_event(logger, "auth.scenario.allowed", team_id=team_id, scenario_scope=scope)
        return scope

    log_event(logger, "auth.scenario.denied", level=logging.WARNING, team_id=team_id)
    raise HTTPException(status_code=403, detail="Scenario token is not authorized for this team")


def start_context_scenario_access(
    team_id: str,
    x_team_token: str | None = Header(default=None),
    x_scenario_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> str:
    """Resolve start-context scope.

    Public start context is intentionally open: no token means public scope.
    A valid hidden token upgrades only this request to hidden scope. If a token
    is presented but is invalid for the requested team, reject it rather than
    silently treating it as public.
    """
    settings = get_settings()
    if team_id not in available_teams():
        raise HTTPException(status_code=404, detail="Unknown team")

    if _equal(x_instructor_token, settings.instructor_token):
        log_event(logger, "auth.start_context.allowed", team_id=team_id, auth_mode="instructor")
        return "instructor"

    token = _presented_token(x_scenario_token, x_team_token)
    if not token:
        log_event(logger, "auth.start_context.allowed", team_id=team_id, auth_mode="open_public")
        return "public"

    scope = scenario_scope_for_token(team_id, token)
    if scope:
        log_event(
            logger,
            "auth.start_context.allowed",
            team_id=team_id,
            auth_mode=f"scenario_{scope}",
        )
        return scope

    log_event(
        logger,
        "auth.start_context.denied",
        level=logging.WARNING,
        team_id=team_id,
        has_team_token=bool(x_team_token),
        has_scenario_token=bool(x_scenario_token),
    )
    raise HTTPException(status_code=403, detail="Token is not authorized for this team")


def require_public_scenario_access(
    team_id: str,
    x_team_token: str | None = Header(default=None),
    x_scenario_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> str:
    scope = authorize_scenario_access(team_id, x_team_token, x_scenario_token, x_instructor_token)
    if scope not in {"public", "instructor"}:
        raise HTTPException(status_code=403, detail="Public-scenario token required")
    return scope


def require_hidden_scenario_access(
    team_id: str,
    x_team_token: str | None = Header(default=None),
    x_scenario_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> str:
    scope = authorize_scenario_access(team_id, x_team_token, x_scenario_token, x_instructor_token)
    if scope not in {"hidden", "instructor"}:
        raise HTTPException(status_code=403, detail="Hidden-scenario token required")
    return scope


def authorized_teams(
    x_team_token: str | None = Header(default=None),
    x_scenario_token: str | None = Header(default=None),
    x_instructor_token: str | None = Header(default=None),
) -> list[str]:
    settings = get_settings()
    teams = list(available_teams())
    if settings.allow_unauthenticated_dev or _equal(x_instructor_token, settings.instructor_token):
        mode = "unauthenticated_dev" if settings.allow_unauthenticated_dev else "instructor"
        log_event(logger, "auth.teams.allowed", auth_mode=mode, teams=teams)
        return teams

    token = _presented_token(x_scenario_token, x_team_token)
    for team in teams:
        scope = scenario_scope_for_token(team, token)
        if scope:
            log_event(logger, "auth.teams.allowed", auth_mode=f"scenario_{scope}", teams=[team])
            return [team]

    log_event(
        logger,
        "auth.teams.denied",
        level=logging.WARNING,
        has_team_token=bool(x_team_token),
        has_scenario_token=bool(x_scenario_token),
        has_instructor_token=bool(x_instructor_token),
    )
    raise HTTPException(status_code=403, detail="Invalid team/scenario token")
