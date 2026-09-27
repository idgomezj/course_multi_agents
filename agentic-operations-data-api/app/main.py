from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException, Query
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

app = FastAPI(
    title="Agentic Operations Challenge Data API + Case 0 Demo",
    version="1.2.0",
    description="Team-scoped data service plus a self-contained fully solved Case 0 end-to-end demonstration.",
)


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
        selected_model, _settings = resolve_manager_model(model_id)
        plan, deps = await run_manager(scenario, model_id)
        result = evaluate_plan(deps.case, scenario, plan, deps.trace, deps.rag_hits)
        payload = result.model_dump()
        payload["manager_model_id"] = model_id or default_manager_model_id()
        payload["manager_model"] = selected_model
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Case 0 AI run failed: {exc}",
        ) from exc
