from __future__ import annotations

import os
import logging
from time import perf_counter
from functools import lru_cache
from typing import Any

import httpx
from dotenv import load_dotenv

from .observability import current_trace_id, log_event

load_dotenv()

logger = logging.getLogger(__name__)


class DataApiError(RuntimeError):
    pass


class DataApiClient:
    def __init__(
        self,
        base_url: str | None = None,
        team_token: str | None = None,
        instructor_token: str | None = None,
        client_type: str | None = None,
        timeout: float = 20.0,
    ):
        self.base_url = (base_url or os.getenv("DATA_API_URL", "https://course-agentic-api.idgomezj.com")).rstrip("/")
        self.team_token = team_token if team_token is not None else os.getenv("DATA_API_TOKEN")
        self.instructor_token = (
            instructor_token if instructor_token is not None else os.getenv("DATA_API_INSTRUCTOR_TOKEN")
        )
        self.client_type = (
            client_type
            if client_type is not None
            else os.getenv("DATA_API_CLIENT_TYPE", "challenge-runtime")
        )
        self.timeout = timeout
        self._start_context_cache: dict[str, dict[str, Any]] = {}

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.team_token:
            headers["X-Team-Token"] = self.team_token
        if self.instructor_token:
            headers["X-Instructor-Token"] = self.instructor_token
        if self.client_type:
            headers["X-Client-Type"] = self.client_type
        return headers

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        started = perf_counter()
        headers = self._headers()
        headers["X-Trace-Id"] = current_trace_id()
        log_event(
            logger,
            "data_api.request.started",
            method="GET",
            base_url=self.base_url,
            path=path,
            params=params or {},
            timeout_seconds=self.timeout,
            auth_mode="instructor" if self.instructor_token else ("team" if self.team_token else "none"),
        )
        try:
            response = httpx.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            log_event(
                logger,
                "data_api.request.failed",
                level=logging.ERROR,
                path=path,
                duration_ms=round((perf_counter() - started) * 1000, 2),
                error=str(exc),
            )
            raise DataApiError(f"Could not reach Data API at {self.base_url}: {exc}") from exc

        log_event(
            logger,
            "data_api.request.completed",
            path=path,
            status_code=response.status_code,
            duration_ms=round((perf_counter() - started) * 1000, 2),
            response_bytes=len(response.content),
        )

        if response.status_code >= 400:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except Exception:
                pass
            raise DataApiError(f"Data API {response.status_code} for {path}: {detail}")
        return response.json()

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        started = perf_counter()
        headers = self._headers()
        headers["X-Trace-Id"] = current_trace_id()
        log_event(
            logger,
            "data_api.request.started",
            method="POST",
            base_url=self.base_url,
            path=path,
            timeout_seconds=self.timeout,
            auth_mode="instructor" if self.instructor_token else ("team" if self.team_token else "none"),
        )
        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            log_event(
                logger,
                "data_api.request.failed",
                level=logging.ERROR,
                path=path,
                duration_ms=round((perf_counter() - started) * 1000, 2),
                error=str(exc),
            )
            raise DataApiError(f"Could not reach Data API at {self.base_url}: {exc}") from exc

        log_event(
            logger,
            "data_api.request.completed",
            path=path,
            status_code=response.status_code,
            duration_ms=round((perf_counter() - started) * 1000, 2),
            response_bytes=len(response.content),
        )
        if response.status_code >= 400:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except Exception:
                pass
            raise DataApiError(f"Data API {response.status_code} for {path}: {detail}")
        return response.json()

    def health(self) -> dict[str, Any]:
        return self._get("/health")

    def list_teams(self) -> list[dict[str, Any]]:
        return self._get("/v1/teams")

    def start_context(self, team_id: str, *, refresh: bool = False) -> dict[str, Any]:
        """Load the canonical case context before any scenario/model-resolution work."""
        if not refresh and team_id in self._start_context_cache:
            return self._start_context_cache[team_id]
        payload = self._get(f"/v1/teams/{team_id}/start-context")
        self._start_context_cache[team_id] = payload
        return payload

    def bootstrap(self, team_id: str) -> dict[str, Any]:
        # Kept for compatibility. New runtime code should use start_context().
        return self._get(f"/v1/teams/{team_id}/bootstrap")

    def get_case(self, team_id: str) -> dict[str, Any]:
        return self._get(f"/v1/teams/{team_id}/case")

    def get_knowledge(self, team_id: str) -> list[dict[str, str]]:
        return self._get(f"/v1/teams/{team_id}/knowledge")



    def get_scenarios(self, team_id: str) -> list[dict[str, Any]]:
        """Return the scenario set selected by the active token scope."""
        self.start_context(team_id)
        return self._get(f"/v1/teams/{team_id}/scenarios")

    def get_scenario(self, team_id: str, scenario_id: str) -> dict[str, Any]:
        """Return only the fields this token is allowed to see."""
        self.start_context(team_id)
        return self._get(f"/v1/teams/{team_id}/scenarios/{scenario_id}")

    def evaluate_scenario(
        self,
        team_id: str,
        scenario_id: str,
        plan: dict[str, Any],
        trace: list[dict[str, Any]],
        rag_hits: list[str],
    ) -> dict[str, Any]:
        return self._post(
            f"/v1/teams/{team_id}/scenarios/{scenario_id}/evaluate",
            {
                "plan": plan,
                "trace": trace,
                "rag_hits": rag_hits,
            },
        )

    # Backward-compatible names now use token-selected scenario scope.
    def get_public_scenarios(self, team_id: str) -> list[dict[str, Any]]:
        return self.get_scenarios(team_id)

    def get_public_scenario(self, team_id: str, scenario_id: str) -> dict[str, Any]:
        return self.get_scenario(team_id, scenario_id)


@lru_cache
def get_data_client() -> DataApiClient:
    return DataApiClient()
