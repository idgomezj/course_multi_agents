from __future__ import annotations

import os
import logging
from time import perf_counter
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .auth import (
    authorize_scenario_access,
    authorize_team,
    authorized_teams,
    require_hidden_scenario_access,
    require_public_scenario_access,
)
from .config import scenario_scope_config
from .store import (
    case_without_scenarios,
    load_case,
    load_knowledge,
    load_model_spec,
    load_training_source,
    public_scenario,
    public_scenarios,
    reference_solution,
    scenario_for_scope,
    scenario_shared_view,
    scenarios_for_scope,
)
from .observability import log_event, new_trace_id, reset_trace_context, set_trace_context, setup_logging

from demo_app.config import (
    DEMO_FRONTEND_DIR,
    DEMO_MODELS_DIR,
    DEMO_RAG_CONFIG,
    DEMO_SKILLS_DIR,
)
from demo_app.evaluator import evaluate_plan
from demo_app.llm_config import default_manager_model_id, manager_model_status, resolve_manager_model
from demo_app.manager import run_manager
from demo_app.schemas import MonthlyOperationsPlan
from demo_app.simulator import simulate_month

setup_logging("agentic-operations-data-api")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Operations Challenge Data API + Case 0 Demo",
    version="1.4.0",
    description="Team-scoped data service plus a self-contained fully solved Case 0 end-to-end demonstration.",
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or new_trace_id()
    tokens = set_trace_context(trace_id)
    started = perf_counter()
    log_event(
        logger,
        "http.request.started",
        method=request.method,
        path=request.url.path,
        query=str(request.url.query),
        client=str(request.client),
    )
    try:
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        log_event(
            logger,
            "http.request.completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round((perf_counter() - started) * 1000, 2),
        )
        return response
    except Exception as exc:
        log_event(
            logger,
            "http.request.failed",
            level=logging.ERROR,
            method=request.method,
            path=request.url.path,
            duration_ms=round((perf_counter() - started) * 1000, 2),
            error=str(exc),
        )
        raise
    finally:
        reset_trace_context(tokens)


@app.get("/health")
def health():
    return {"status": "ok", "service": "agentic-operations-data-api", "version": "1.4.0"}


class ScenarioEvaluationRequest(BaseModel):
    plan: MonthlyOperationsPlan
    trace: list[dict[str, Any]] = Field(default_factory=list)
    rag_hits: list[str] = Field(default_factory=list)


def _resolve_scenario_scope(
    access_scope: str,
    requested_scope: str | None = None,
    scenario_id: str | None = None,
) -> str:
    if access_scope in {"public", "hidden"}:
        if requested_scope and requested_scope != access_scope:
            raise HTTPException(
                status_code=403,
                detail=f"This token is scoped to {access_scope} scenarios",
            )
        return access_scope

    if requested_scope in {"public", "hidden"}:
        return requested_scope
    if scenario_id and "-H" in scenario_id:
        return "hidden"
    return "public"


def _evaluation_shared_view(team_id: str, scope: str, payload: dict[str, Any]) -> dict[str, Any]:
    fields = scenario_scope_config(team_id, scope).get("evaluation_fields", [])
    if not fields:
        fields = [
            "team_id",
            "scenario_id",
            "operational_score",
            "feasibility_score",
            "service_score",
            "cost_score",
            "skill_tool_score",
            "rag_score",
            "total_cost",
            "violations",
        ]
    return {field: payload[field] for field in fields if field in payload}


# ---------------------------------------------------------------------------
# Team-scoped Data API
# ---------------------------------------------------------------------------

@app.get("/v1/teams")
def teams(team_ids: list[str] = Depends(authorized_teams)):
    out = []
    for team_id in team_ids:
        case = case_without_scenarios(team_id)
        out.append({
            "team_id": team_id,
            "name": case["name"],
            "description": case["description"],
            "objective": case["objective"],
        })
    return out


@app.get("/v1/teams/{team_id}/bootstrap")
def bootstrap(team_id: str, _: str = Depends(authorize_team)):
    return {
        "team_id": team_id,
        "case": case_without_scenarios(team_id),
        "knowledge": list(load_knowledge(team_id)),
    }


@app.get("/v1/teams/{team_id}/case")
def case(team_id: str, _: str = Depends(authorize_team)):
    return case_without_scenarios(team_id)


@app.get("/v1/teams/{team_id}/knowledge")
def knowledge(team_id: str, _: str = Depends(authorize_team)):
    return list(load_knowledge(team_id))






@app.get("/v1/teams/{team_id}/training-source.json")
def training_source(team_id: str, _: str = Depends(authorize_team)):
    """Return the team's raw historical model-development data as JSON.

    The payload is intentionally messy and not ML-ready. It does not contain
    precomputed feature matrices, model-specific labels, train/validation splits,
    or cleaning decisions.
    """
    try:
        payload = load_training_source(team_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    log_event(
        logger,
        "training_source.requested",
        team_id=team_id,
        record_count=payload.get("record_count"),
    )
    return payload


@app.get("/v1/teams/{team_id}/scenarios")
def token_scoped_scenarios(
    team_id: str,
    scope: str | None = Query(default=None),
    access_scope: str = Depends(authorize_scenario_access),
):
    effective_scope = _resolve_scenario_scope(access_scope, scope)
    return [
        scenario_shared_view(team_id, effective_scope, scenario, detail=False)
        for scenario in scenarios_for_scope(team_id, effective_scope)
    ]


@app.get("/v1/teams/{team_id}/scenarios/public")
def public_scenario_list(
    team_id: str,
    _: str = Depends(require_public_scenario_access),
):
    return [
        scenario_shared_view(team_id, "public", scenario, detail=False)
        for scenario in public_scenarios(team_id)
    ]


@app.get("/v1/teams/{team_id}/scenarios/public/{scenario_id}")
def public_scenario_detail(
    team_id: str,
    scenario_id: str,
    _: str = Depends(require_public_scenario_access),
):
    try:
        scenario = scenario_for_scope(team_id, "public", scenario_id)
        return scenario_shared_view(team_id, "public", scenario, detail=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown public scenario") from exc


@app.get("/v1/teams/{team_id}/scenarios/hidden")
def hidden_scenario_list(
    team_id: str,
    _: str = Depends(require_hidden_scenario_access),
):
    return [
        scenario_shared_view(team_id, "hidden", scenario, detail=False)
        for scenario in scenarios_for_scope(team_id, "hidden")
    ]


@app.get("/v1/teams/{team_id}/scenarios/hidden/{scenario_id}")
def hidden_scenario_detail(
    team_id: str,
    scenario_id: str,
    _: str = Depends(require_hidden_scenario_access),
):
    try:
        scenario = scenario_for_scope(team_id, "hidden", scenario_id)
        return scenario_shared_view(team_id, "hidden", scenario, detail=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown hidden scenario") from exc


@app.post("/v1/teams/{team_id}/scenarios/{scenario_id}/evaluate")
def evaluate_team_scenario(
    team_id: str,
    scenario_id: str,
    request: ScenarioEvaluationRequest,
    scope: str | None = Query(default=None),
    access_scope: str = Depends(authorize_scenario_access),
):
    effective_scope = _resolve_scenario_scope(access_scope, scope, scenario_id)
    try:
        scenario = scenario_for_scope(team_id, effective_scope, scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown scenario") from exc

    if request.plan.team_id != team_id or request.plan.scenario_id != scenario_id:
        raise HTTPException(
            status_code=400,
            detail="Plan team_id/scenario_id must match the evaluation path",
        )

    result = evaluate_plan(
        load_case(team_id),
        scenario,
        request.plan,
        request.trace,
        set(request.rag_hits),
    )
    payload = result.model_dump()
    log_event(
        logger,
        "scenario.evaluation.completed",
        team_id=team_id,
        scenario_id=scenario_id,
        scenario_scope=effective_scope,
        operational_score=payload.get("operational_score"),
    )
    return _evaluation_shared_view(team_id, effective_scope, payload)


@app.get("/v1/teams/{team_id}/scenarios/{scenario_id}")
def token_scoped_scenario_detail(
    team_id: str,
    scenario_id: str,
    scope: str | None = Query(default=None),
    access_scope: str = Depends(authorize_scenario_access),
):
    effective_scope = _resolve_scenario_scope(access_scope, scope, scenario_id)
    try:
        scenario = scenario_for_scope(team_id, effective_scope, scenario_id)
        return scenario_shared_view(team_id, effective_scope, scenario, detail=True)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown scenario") from exc


@app.get("/v1/teams/{team_id}/reference-solution")
def solved_reference(
    team_id: str,
    scenario_id: str = Query(default="T0-P01"),
    _: str = Depends(authorize_team),
):
    try:
        return reference_solution(team_id, scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Self-contained Case 0 full-stack demo
# ---------------------------------------------------------------------------

@app.get("/demo")
def demo_home():
    return FileResponse(DEMO_FRONTEND_DIR / "index.html")


@app.get("/demo/app.js")
def demo_javascript():
    return FileResponse(DEMO_FRONTEND_DIR / "app.js", media_type="application/javascript")


@app.get("/demo/api/status")
def demo_status():
    case_ok = False
    try:
        load_case("team_0")
        case_ok = True
    except Exception:
        pass

    skill_files = list(DEMO_SKILLS_DIR.glob("*.md"))
    model_spec = load_model_spec("team_0")["models"]
    model_status = {}
    for key, spec in model_spec.items():
        preferred = DEMO_MODELS_DIR / spec["artifact"]
        legacy = preferred.with_suffix(".pt") if preferred.suffix == ".pt2" else preferred
        model_status[key] = {
            "ready": preferred.exists() or legacy.exists(),
            "artifact": spec["artifact"],
            "legacy_artifact_present": legacy.exists() and not preferred.exists(),
        }

    return {
        "case_loaded": case_ok,
        "rag_ready": DEMO_RAG_CONFIG.exists(),
        "skill_count": len(skill_files),
        "models": model_status,
        "manager_model_id": default_manager_model_id(),
        "manager_models": manager_model_status(),
    }


@app.get("/demo/api/manager-models")
def demo_manager_models():
    return {
        "default_model_id": default_manager_model_id(),
        "models": manager_model_status(),
    }


@app.get("/demo/api/scenarios")
def demo_scenarios():
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "description": s.get("description", ""),
            "visible": s.get("visible", {}),
        }
        for s in public_scenarios("team_0")
    ]


@app.get("/demo/api/reference/{scenario_id}")
def demo_reference(scenario_id: str):
    log_event(logger, "demo.reference.requested", team_id="team_0", scenario_id=scenario_id)
    try:
        solved = reference_solution("team_0", scenario_id)
        scenario = public_scenario("team_0", scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    plan = MonthlyOperationsPlan.model_validate(solved["reference_plan"])
    sim = simulate_month(load_case("team_0"), scenario, plan)
    log_event(
        logger,
        "demo.reference.completed",
        team_id="team_0",
        scenario_id=scenario_id,
        feasible=sim.feasible,
        service_level=sim.service_level,
        total_cost=sim.total_cost,
        benchmark_cost=scenario.get("benchmark_cost"),
        violations=[v.model_dump() for v in sim.violations],
    )
    return {
        "mode": "published_reference",
        "scenario_id": scenario_id,
        "benchmark_cost": scenario.get("benchmark_cost"),
        "plan": plan.model_dump(),
        "simulation": sim.model_dump(),
    }


@app.post("/demo/api/run/{scenario_id}")
async def demo_run_agent(
    scenario_id: str,
    model_id: str | None = Query(default=None),
):
    try:
        scenario = public_scenario("team_0", scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown Case 0 scenario") from exc

    try:
        log_event(logger, "demo.ai_run.requested", team_id="team_0", scenario_id=scenario_id, model_id=model_id)
        selected_model, _settings = resolve_manager_model(model_id)
        plan, deps = await run_manager(scenario, model_id)
        result = evaluate_plan(deps.case, scenario, plan, deps.trace, deps.rag_hits)
        payload = result.model_dump()
        payload["manager_model_id"] = model_id or default_manager_model_id()
        payload["manager_model"] = selected_model
        log_event(
            logger,
            "demo.ai_run.completed",
            team_id="team_0",
            scenario_id=scenario_id,
            manager_model=selected_model,
            operational_score=payload.get("operational_score"),
            feasibility_score=payload.get("feasibility_score"),
            service_score=payload.get("service_score"),
            cost_score=payload.get("cost_score"),
            rag_score=payload.get("rag_score"),
            skill_tool_score=payload.get("skill_tool_score"),
            total_cost=payload.get("total_cost"),
            benchmark_cost=payload.get("benchmark_cost"),
            cost_gap=payload.get("cost_gap"),
            tool_calls=len(payload.get("trace", [])),
            violations=payload.get("violations"),
        )
        return payload
    except Exception as exc:
        log_event(logger, "demo.ai_run.failed", level=logging.ERROR, team_id="team_0", scenario_id=scenario_id, model_id=model_id, error=str(exc))
        raise HTTPException(
            status_code=500,
            detail=f"Case 0 AI run failed: {exc}",
        ) from exc
