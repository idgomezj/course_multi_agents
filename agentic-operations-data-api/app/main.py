from __future__ import annotations

import os
import logging
from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse

from .auth import authorize_team, authorized_teams
from .store import (
    case_without_scenarios,
    load_case,
    load_knowledge,
    load_model_spec,
    public_scenario,
    public_scenarios,
    reference_solution,
)
from .training_data import generate_training_rows
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
    version="1.2.0",
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
    return {"status": "ok", "service": "agentic-operations-data-api", "version": "1.2.0"}


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
        "model_spec": load_model_spec(team_id),
        "public_scenarios": public_scenarios(team_id),
    }


@app.get("/v1/teams/{team_id}/case")
def case(team_id: str, _: str = Depends(authorize_team)):
    return case_without_scenarios(team_id)


@app.get("/v1/teams/{team_id}/knowledge")
def knowledge(team_id: str, _: str = Depends(authorize_team)):
    return list(load_knowledge(team_id))


@app.get("/v1/teams/{team_id}/model-spec")
def model_spec(team_id: str, _: str = Depends(authorize_team)):
    return load_model_spec(team_id)


@app.get("/v1/teams/{team_id}/training-data/{model_key}")
def training_data(
    team_id: str,
    model_key: str,
    rows: int = Query(default=1400, ge=100, le=10000),
    seed: int = Query(default=42, ge=0, le=2_147_483_647),
    _: str = Depends(authorize_team),
):
    try:
        log_event(logger, "training_data.requested", team_id=team_id, model_key=model_key, rows=rows, seed=seed)
        data = generate_training_rows(team_id, model_key, rows=rows, seed=seed)
        log_event(logger, "training_data.generated", team_id=team_id, model_key=model_key, rows=len(data), columns=sorted(data[0]) if data else [])
        return {"team_id": team_id, "model_key": model_key, "rows": data}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/v1/teams/{team_id}/scenarios/public")
def scenarios(team_id: str, _: str = Depends(authorize_team)):
    return public_scenarios(team_id)


@app.get("/v1/teams/{team_id}/scenarios/public/{scenario_id}")
def scenario(team_id: str, scenario_id: str, _: str = Depends(authorize_team)):
    try:
        return public_scenario(team_id, scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown scenario") from exc


@app.get("/v1/teams/{team_id}/reference-solution")
def solved_reference(team_id: str, _: str = Depends(authorize_team)):
    try:
        return reference_solution(team_id)
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
    solved = reference_solution("team_0")
    if scenario_id != solved["scenario_id"]:
        raise HTTPException(
            status_code=400,
            detail=f"The published worked reference exists only for {solved['scenario_id']}. "
                   "Use 'Run AI Manager end-to-end' for the other Case 0 scenarios.",
        )

    scenario = public_scenario("team_0", scenario_id)
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
