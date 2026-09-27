from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import FRONTEND_DIR
from .data_api import DataApiError, get_data_client
from .evaluator import evaluate_plan
from .llm_config import default_manager_model_id, manager_model_status
from .manager import run_manager
from .scenarios import get_public_scenario, list_public_scenarios, student_visible_scenario
from .training_data import generate_training_frame

app = FastAPI(title="Agentic Operations Intelligence Challenge", version="0.2.0")


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
    try:
        scenario = get_public_scenario(request.team_id, request.scenario_id)
        plan, deps = await run_manager(request.team_id, scenario, request.model_id)
        result = evaluate_plan(deps.case, scenario, plan, deps.trace, deps.rag_hits)
        return result.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DataApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {exc}") from exc
