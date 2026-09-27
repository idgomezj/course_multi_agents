# Agentic Operations Data API

Standalone FastAPI service for all immutable/team-assigned data used by the Agentic Operations Intelligence Challenge.

## What this service owns

- merged business case data;
- inventory, products, BOM, suppliers, costs, policies and capacity;
- RAG source documents;
- PyTorch model contracts;
- generated public training datasets;
- public development scenarios.

The student application no longer needs local copies of those assets.

## Team isolation

Each deployment sets `TEAM_TOKENS_JSON`. A student's `X-Team-Token` can access only that team's endpoints. An instructor token can access every team.

## Endpoints

- `GET /health`
- `GET /v1/teams`
- `GET /v1/teams/{team_id}/bootstrap`
- `GET /v1/teams/{team_id}/case`
- `GET /v1/teams/{team_id}/knowledge`
- `GET /v1/teams/{team_id}/model-spec`
- `GET /v1/teams/{team_id}/training-data/{model_key}`
- `GET /v1/teams/{team_id}/scenarios/public`
- `GET /v1/teams/{team_id}/scenarios/public/{scenario_id}`

## Run

```bash
cd agentic-operations-data-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export TEAM_TOKENS_JSON='{"team_1":"dev-team-1"}'
export INSTRUCTOR_TOKEN='dev-instructor'
python run.py
```

Runs on `http://localhost:8100`.

## Security note

This branch exists to keep the service implementation independent from the student application. If this GitHub repository remains public, branch contents are still readable through GitHub. For real anti-copy isolation, deploy this branch from a **private repository or private deployment artifact** and keep team datasets/secrets there. API authentication protects the running service; it cannot make a public Git branch private.
