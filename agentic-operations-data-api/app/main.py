from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query

from .auth import authorize_team, authorized_teams
from .store import (
    case_without_scenarios,
    load_knowledge,
    load_model_spec,
    public_scenario,
    public_scenarios,
)
from .training_data import generate_training_rows

app = FastAPI(
    title="Agentic Operations Challenge Data API",
    version="1.0.0",
    description="Team-scoped source of business data, RAG knowledge, model contracts and public scenarios.",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "agentic-operations-data-api", "version": "1.0.0"}


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
        data = generate_training_rows(team_id, model_key, rows=rows, seed=seed)
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
