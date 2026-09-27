# Agentic Operations Data API

Standalone FastAPI service for all immutable/team-assigned data used by the Agentic Operations Intelligence Challenge.

## What this service owns

- merged business case data;
- inventory, products, BOM, suppliers, costs, policies and capacity;
- RAG source documents;
- PyTorch model contracts;
- **team-specific public training-data distributions**;
- public development scenarios.

The student application contains no runtime copy of those assets.

## Why the training data also lives here

The five teams are intentionally different at the ML level, not only at the Skill/RAG level.

Examples:
- Team 1 receives volatile/promotional demand distributions;
- Team 2 receives low-variance stable-demand distributions and excess-inventory labels;
- Team 3 receives short-lead-time JIT supplier patterns;
- Team 4 receives broad disruption and quality-risk supplier patterns;
- Team 5 receives high-utilization/downtime/capacity patterns.

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
python run.py
```

Runs on `http://localhost:8100`.

## Security note

This branch is architecturally independent from the student application, but a branch in a public GitHub repository is still public. For real anti-copy isolation, deploy this service from a private repository/private artifact and keep the production team datasets and token map there.


## Case 0 worked example

The API branch includes `team_0`, a fully worked reference case for classroom demonstration.

It provides:
- a balanced manufacturing business case;
- a demand-forecast model contract;
- a supplier-delay model contract;
- company documents for RAG;
- three public scenarios;
- a published worked plan for `T0-P01` in `demo_case_0_solution/README.md`.

All Case 0 artifacts now live only on this service branch under `data/teams/team_0*` and `demo_case_0_solution/`.

The solved package includes:
- Case 0 business/scenario data;
- Case 0 model contract;
- RAG source documents;
- solved RAG configuration;
- solved Skills;
- PyTorch training script;
- structured reference plan and benchmark explanation.

Case 0 is for demonstration only. Teams 1–5 remain the graded cases.
