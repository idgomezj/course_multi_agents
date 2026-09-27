from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


class DataApiError(RuntimeError):
    pass


class DataApiClient:
    def __init__(
        self,
        base_url: str | None = None,
        team_token: str | None = None,
        instructor_token: str | None = None,
        timeout: float = 20.0,
    ):
        self.base_url = (base_url or os.getenv("DATA_API_URL", "http://localhost:8100")).rstrip("/")
        self.team_token = team_token if team_token is not None else os.getenv("DATA_API_TOKEN")
        self.instructor_token = (
            instructor_token if instructor_token is not None else os.getenv("DATA_API_INSTRUCTOR_TOKEN")
        )
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.team_token:
            headers["X-Team-Token"] = self.team_token
        if self.instructor_token:
            headers["X-Instructor-Token"] = self.instructor_token
        return headers

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise DataApiError(f"Could not reach Data API at {self.base_url}: {exc}") from exc

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

    def bootstrap(self, team_id: str) -> dict[str, Any]:
        return self._get(f"/v1/teams/{team_id}/bootstrap")

    def get_case(self, team_id: str) -> dict[str, Any]:
        return self._get(f"/v1/teams/{team_id}/case")

    def get_knowledge(self, team_id: str) -> list[dict[str, str]]:
        return self._get(f"/v1/teams/{team_id}/knowledge")

    def get_model_spec(self, team_id: str) -> dict[str, Any]:
        return self._get(f"/v1/teams/{team_id}/model-spec")

    def get_training_rows(
        self,
        team_id: str,
        model_key: str,
        rows: int = 1400,
        seed: int = 42,
    ) -> list[dict[str, Any]]:
        payload = self._get(
            f"/v1/teams/{team_id}/training-data/{model_key}",
            params={"rows": rows, "seed": seed},
        )
        return payload["rows"]

    def get_public_scenarios(self, team_id: str) -> list[dict[str, Any]]:
        return self._get(f"/v1/teams/{team_id}/scenarios/public")

    def get_public_scenario(self, team_id: str, scenario_id: str) -> dict[str, Any]:
        return self._get(f"/v1/teams/{team_id}/scenarios/public/{scenario_id}")


@lru_cache
def get_data_client() -> DataApiClient:
    return DataApiClient()
