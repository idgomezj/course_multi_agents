# Agentic Operations Data API

Standalone FastAPI service for the Agentic Operations Intelligence Challenge.

This branch now has **two roles**:

1. provide team-scoped business/training/RAG data through the Data API;
2. run **Case 0 completely end-to-end on this branch**, without using `main`.

## Run Case 0 completely from this branch

Checkout:

```bash
git checkout service/agentic-operations-data-api
cd agentic-operations-data-api
```

Create the environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Google API key to `.env`:

```text
MANAGER_MODEL=google:gemini-2.5-flash
GOOGLE_API_KEY=YOUR_KEY
```

Train the two solved Case 0 PyTorch models:

```bash
python demo_case_0_solution/train_models.py
```

This creates:

```text
demo_case_0_solution/models/
├── model_a.pt2
└── model_b.pt2
```

Start the single FastAPI service:

```bash
python run.py
```

Then open:

```text
http://localhost:8100/demo
```

The page lets you:

- evaluate the published T0-P01 reference plan through the simulator/cost engine without an LLM;
- run the **AI Manager end-to-end** through RAG, Skills, PyTorch models, tools, structured planning, simulation and scoring;
- inspect constraint violations;
- inspect the complete tool trace;
- inspect the final structured monthly plan.

## Case 0 architecture

```text
Case 0 local data
      │
      ├── PyTorch model contract + training data
      ├── RAG documents
      ├── solved RAG configuration
      └── solved Skills
      │
      ▼
Pydantic AI Manager
      │
      ├── RAG retrieval
      ├── Skills
      ├── PyTorch prediction tools
      ├── inventory/BOM/supplier/capacity tools
      ├── cost tools
      └── validate_plan
      │
      ▼
Structured Monthly Plan
      │
      ▼
Independent Simulator
      │
      ├── feasibility
      ├── service
      └── realized total cost
      │
      ▼
Evaluator / Scores
```

## Case 0 files

```text
data/teams/team_0.yaml
data/teams/team_0/
├── model_spec.json
└── documents/
    ├── company_facts.md
    ├── operations_policy.md
    └── supplier_contracts.md

demo_case_0_solution/
├── README.md
├── train_models.py
├── reference_plan.json
├── models/                 # generated locally
├── rag/config.yaml
├── skills/
│   ├── monthly_planning.md
│   ├── supplier_selection.md
│   └── cost_optimization.md
└── frontend/

demo_app/
├── manager.py
├── tools.py
├── rag.py
├── skills.py
├── model_registry.py
├── simulator.py
├── cost_engine.py
└── evaluator.py
```

## Data API endpoints

- `GET /health`
- `GET /v1/teams`
- `GET /v1/teams/{team_id}/bootstrap`
- `GET /v1/teams/{team_id}/case`
- `GET /v1/teams/{team_id}/knowledge`
- `GET /v1/teams/{team_id}/model-spec`
- `GET /v1/teams/{team_id}/training-data/{model_key}`
- `GET /v1/teams/{team_id}/scenarios/public`
- `GET /v1/teams/{team_id}/scenarios/public/{scenario_id}`
- `GET /v1/teams/team_0/reference-solution`

## Authentication

The committed values in `.env.example` are demo values only. Team tokens restrict the running Data API by team.

Because this GitHub repository/branch is currently public, these demo tokens are not secrets. Generate completely new credentials after moving this service to the private repository.

## Important separation

Case 0 lives on this service branch. It does not need `main` to run the demo.

Teams 1–5 remain the graded cases. Hidden final scenarios, final PyTorch holdouts, hidden RAG queries, benchmark/oracle data and final-evaluator credentials must remain private.
