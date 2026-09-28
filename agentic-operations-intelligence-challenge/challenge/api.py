from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import FRONTEND_DIR, available_teams, load_case
from .evaluator import evaluate_plan
from .manager import run_manager
from .scenarios import get_public_scenario, list_public_scenarios, student_visible_scenario

app = FastAPI(title="Agentic Operations Intelligence Challenge", version="0.1.0")


class EvaluateRequest(BaseModel):
    team_id: str
    scenario_id: str


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/app.js")
def js():
    return FileResponse(FRONTEND_DIR / "app.js", media_type="application/javascript")


@app.get("/api/health")
def health():
    return {"status": "ok", "manager_model": os.getenv("MANAGER_MODEL", "google:gemini-3.7-flash")}


@app.get("/api/teams")
def teams():
    return [
        {
            "team_id": team,
            "name": load_case(team)["name"],
            "description": load_case(team)["description"],
            "objective": load_case(team)["objective"],
        }
        for team in available_teams()
    ]


@app.get("/api/scenarios/{team_id}")
def scenarios(team_id: str):
    try:
        return [student_visible_scenario(x) for x in list_public_scenarios(team_id)]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/training-data/{team_id}/{model_key}")
def training_data(team_id: str, model_key: str, rows: int = 1000, seed: int = 42):
    try:
        df = generate_training_frame(team_id, model_key, rows=max(100, min(rows, 5000)), seed=seed)
        return {"columns": list(df.columns), "rows": df.to_dict(orient="records")}
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/evaluate")
async def evaluate(request: EvaluateRequest):
    try:
        scenario = get_public_scenario(request.team_id, request.scenario_id)
        plan, deps = await run_manager(request.team_id, scenario)
        result = evaluate_plan(deps.case, scenario, plan, deps.trace, deps.rag_hits)
        return result.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {exc}") from exc
