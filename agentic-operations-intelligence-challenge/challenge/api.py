from __future__ import annotations

import logging
from time import perf_counter

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import FRONTEND_DIR
from .data_api import DataApiError, get_data_client
from .evaluator import evaluate_plan
from .llm_config import default_manager_model_id, manager_model_status, resolve_manager_model
from .manager import run_manager
from .observability import log_event, new_trace_id, reset_trace_context, set_trace_context, setup_logging
from .scenarios import get_public_scenario, list_public_scenarios, student_visible_scenario
from .training_data import generate_training_frame

setup_logging("agentic-operations-challenge")
logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic Operations Intelligence Challenge", version="0.3.0")


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or new_trace_id()
    tokens = set_trace_context(trace_id)
    started = perf_counter()
    log_event(logger, "http.request.started", method=request.method, path=request.url.path, query=str(request.url.query), client=str(request.client))
    try:
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        log_event(logger, "http.request.completed", method=request.method, path=request.url.path, status_code=response.status_code, duration_ms=round((perf_counter()-started)*1000, 2))
        return response
    except Exception as exc:
        log_event(logger, "http.request.failed", level=logging.ERROR, method=request.method, path=request.url.path, duration_ms=round((perf_counter()-started)*1000, 2), error=str(exc))
        raise
    finally:
        reset_trace_context(tokens)


class EvaluateRequest(BaseModel):
    team_id: str
    scenario_id: str
    model_id: str | None = None


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/app.js")
def js():
    return FileResponse(FRONTEND_DIR / "app.js", media_type="application/javascript")


@app.get("/api/health")
def health():
    try:
        data_api = get_data_client().health()
    except Exception as exc:
        data_api = {"status": "error", "detail": str(exc)}
    return {
        "status": "ok",
        "manager_model_id": default_manager_model_id(),
        "manager_models": manager_model_status(),
        "data_api": data_api,
    }


@app.get("/api/manager-models")
def manager_models():
    return {
        "default_model_id": default_manager_model_id(),
        "models": manager_model_status(),
    }


@app.get("/api/teams")
def teams():
    try:
        return get_data_client().list_teams()
    except DataApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/scenarios/{team_id}")
def scenarios(team_id: str):
    try:
        return [student_visible_scenario(x) for x in list_public_scenarios(team_id)]
    except DataApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/training-data/{team_id}/{model_key}")
def training_data(team_id: str, model_key: str, rows: int = 1000, seed: int = 42):
    try:
        df = generate_training_frame(team_id, model_key, rows=max(100, min(rows, 5000)), seed=seed)
        return {"columns": list(df.columns), "rows": df.to_dict(orient="records")}
    except DataApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/evaluate")
async def evaluate(request: EvaluateRequest):
    log_event(logger, "evaluation.requested", team_id=request.team_id, scenario_id=request.scenario_id, model_id=request.model_id)
    try:
        scenario = get_public_scenario(request.team_id, request.scenario_id)
        selected_model, _settings = resolve_manager_model(request.model_id)
        plan, deps = await run_manager(request.team_id, scenario, request.model_id)
        result = evaluate_plan(deps.case, scenario, plan, deps.trace, deps.rag_hits)
        payload = result.model_dump()
        payload["manager_model_id"] = request.model_id or default_manager_model_id()
        payload["manager_model"] = selected_model
        log_event(
            logger,
            "evaluation.completed",
            team_id=request.team_id,
            scenario_id=request.scenario_id,
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
            violations=payload.get("violations"),
            tool_calls=len(payload.get("trace", [])),
        )
        return payload
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DataApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {exc}") from exc
