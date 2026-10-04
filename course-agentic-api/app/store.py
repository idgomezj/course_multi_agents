from __future__ import annotations

import json
import logging
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .config import DATA_DIR, scenario_scope_config
from .observability import log_event

logger = logging.getLogger(__name__)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@lru_cache
def load_start_context_config() -> dict[str, Any]:
    path = DATA_DIR / "start_context.json"
    if not path.exists():
        raise FileNotFoundError(f"Canonical start context is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    log_event(
        logger,
        "store.start_context.loaded",
        path=str(path),
        version=payload.get("version"),
    )
    return payload


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = deepcopy(value)
    return out


@lru_cache
def available_teams() -> tuple[str, ...]:
    teams = tuple(sorted(p.stem for p in (DATA_DIR / "teams").glob("team_*.yaml")))
    log_event(logger, "store.teams.discovered", level=logging.DEBUG, teams=teams)
    return teams


@lru_cache
def load_case(team_id: str) -> dict[str, Any]:
    if team_id not in available_teams():
        raise KeyError(team_id)
    merged = _deep_merge(
        _load_yaml(DATA_DIR / "base.yaml"),
        _load_yaml(DATA_DIR / "teams" / f"{team_id}.yaml"),
    )
    merged["team_id"] = team_id
    log_event(logger, "store.case.loaded", team_id=team_id, product_count=len(merged.get("products", {})), material_count=len(merged.get("materials", {})), supplier_count=len(merged.get("suppliers", {})), line_count=len(merged.get("lines", {})))
    return merged


@lru_cache
def load_model_spec(team_id: str) -> dict[str, Any]:
    if team_id not in available_teams():
        raise KeyError(team_id)
    path = DATA_DIR / "teams" / team_id / "model_spec.json"
    spec = json.loads(path.read_text(encoding="utf-8"))
    log_event(logger, "store.model_spec.loaded", team_id=team_id, path=str(path), model_keys=sorted(spec.get("models", {})))
    return spec


@lru_cache
def load_training_source(team_id: str) -> dict[str, Any]:
    """Load the raw historical JSON source used for student model development.

    This is intentionally not a model-ready training dataset. Team 1-5 payloads
    contain raw imperfect evidence that students must inspect, clean, transform
    and label. Team 0 returns a worked imperfect sample that demonstrates the same
    analysis process before the committed reference CSVs are used for reproducible
    instructor model training.
    """
    if team_id not in available_teams():
        raise KeyError(team_id)

    path = DATA_DIR / "training_sources" / f"{team_id}.json"
    if not path.exists():
        raise KeyError(f"Raw training source not found for {team_id}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    log_event(
        logger,
        "store.training_source.loaded",
        team_id=team_id,
        path=str(path),
        record_count=len(records),
        columns=sorted(records[0]) if records else [],
    )
    return payload


@lru_cache
def load_knowledge(team_id: str) -> tuple[dict[str, str], ...]:
    if team_id not in available_teams():
        raise KeyError(team_id)
    team_root = DATA_DIR / "teams" / team_id
    roots = [team_root / "knowledge", team_root / "documents"]
    documents = []
    for root in roots:
        if not root.exists():
            continue
        documents.extend(
            {"name": p.name, "content": p.read_text(encoding="utf-8")}
            for p in sorted(root.glob("*.md"))
        )
    log_event(logger, "store.knowledge.loaded", team_id=team_id, document_count=len(documents), sources=[x["name"] for x in documents])
    return tuple(documents)


def public_scenarios(team_id: str) -> list[dict[str, Any]]:
    """Full internal public scenario definitions.

    API routes must project these through scenario_shared_view before returning
    them to a student token.
    """
    return deepcopy(load_case(team_id).get("public_scenarios", []))


@lru_cache
def _load_hidden_scenarios(team_id: str) -> tuple[dict[str, Any], ...]:
    if team_id not in available_teams() or team_id == "team_0":
        return tuple()

    path = DATA_DIR / "scenarios" / team_id / "hidden.json"
    if not path.exists():
        return tuple()

    payload = json.loads(path.read_text(encoding="utf-8"))
    scenarios = payload.get("scenarios", [])
    if not isinstance(scenarios, list):
        raise ValueError(f"{path} must contain a list named 'scenarios'")

    log_event(
        logger,
        "store.hidden_scenarios.loaded",
        team_id=team_id,
        path=str(path),
        scenario_count=len(scenarios),
    )
    return tuple(deepcopy(scenarios))


def hidden_scenarios(team_id: str) -> list[dict[str, Any]]:
    """Full internal hidden scenario definitions."""
    return deepcopy(list(_load_hidden_scenarios(team_id)))


def scenarios_for_scope(team_id: str, scope: str) -> list[dict[str, Any]]:
    if scope == "public":
        return public_scenarios(team_id)
    if scope == "hidden":
        return hidden_scenarios(team_id)
    raise KeyError(f"Unknown scenario scope: {scope}")


def scenario_for_scope(team_id: str, scope: str, scenario_id: str) -> dict[str, Any]:
    for scenario in scenarios_for_scope(team_id, scope):
        if scenario.get("id") == scenario_id:
            return scenario
    raise KeyError(scenario_id)


def public_scenario(team_id: str, scenario_id: str) -> dict[str, Any]:
    return scenario_for_scope(team_id, "public", scenario_id)


def hidden_scenario(team_id: str, scenario_id: str) -> dict[str, Any]:
    return scenario_for_scope(team_id, "hidden", scenario_id)


def scenario_shared_view(
    team_id: str,
    scope: str,
    scenario: dict[str, Any],
    *,
    detail: bool,
) -> dict[str, Any]:
    """Project a full scenario to only fields allowed for this token scope."""
    cfg = scenario_scope_config(team_id, scope)
    key = "detail_fields" if detail else "list_fields"
    fields = cfg.get(key, ["id", "title", "description", "visible"])
    return {
        field: deepcopy(scenario[field])
        for field in fields
        if field in scenario
    }


def case_without_scenarios(team_id: str) -> dict[str, Any]:
    case = deepcopy(load_case(team_id))
    case.pop("public_scenarios", None)
    return case


def reference_solution(team_id: str, scenario_id: str = "T0-P01") -> dict[str, Any]:
    """Return a published Case 0 reference solution for one public scenario."""
    if team_id != "team_0":
        raise KeyError("Published reference solutions exist only for team_0")

    scenario = public_scenario(team_id, scenario_id)
    path = DATA_DIR.parent / "demo_case_0_solution" / "reference_plans" / f"{scenario_id}.json"

    if not path.exists():
        raise KeyError(f"Case 0 reference plan is missing for {scenario_id}: {path}")

    plan = json.loads(path.read_text(encoding="utf-8"))
    if plan.get("scenario_id") != scenario_id:
        raise ValueError(
            f"Reference plan scenario mismatch: requested {scenario_id}, file contains {plan.get('scenario_id')}"
        )

    log_event(
        logger,
        "store.reference_solution.loaded",
        team_id=team_id,
        path=str(path),
        scenario_id=scenario_id,
    )
    return {
        "scenario_id": scenario_id,
        "purpose": "Published worked solution for the fully solved Case 0 teaching demo.",
        "reference_plan": plan,
        "reference_evaluation": {
            "benchmark_cost": scenario.get("benchmark_cost"),
            "service_level_target": load_case(team_id).get("policies", {}).get("service_level_target"),
        },
    }
