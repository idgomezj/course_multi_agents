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


## Choose Gemini, OpenAI/ChatGPT, Claude, or DeepSeek

The Case 0 demo is no longer tied to a single LLM provider. The browser at `/demo` has a **Manager LLM** selector.

Supported provider ids:

```text
google
openai
anthropic
deepseek
```

Configure the providers you want in `.env`:

```text
MANAGER_PROVIDER=google

GOOGLE_MANAGER_MODEL=google:gemini-2.5-flash
GOOGLE_API_KEY=...

OPENAI_MANAGER_MODEL=openai:gpt-5.6-sol
OPENAI_API_KEY=...

ANTHROPIC_MANAGER_MODEL=anthropic:claude-sonnet-4-6
ANTHROPIC_API_KEY=...

DEEPSEEK_MANAGER_MODEL=deepseek:deepseek-v4-flash
DEEPSEEK_API_KEY=...
```

Then restart:

```bash
python run.py
```

Open:

```text
http://localhost:8100/demo
```

Choose the provider from **Manager LLM** and run the same Case 0 scenario. This makes it possible to compare the exact same tools, RAG, Skills, PyTorch models and evaluator while changing only the LLM Manager.

The API also exposes:

```text
GET /demo/api/manager-models
```

which returns provider/model names plus a boolean showing whether the required key is configured. API-key values are never returned.

You can also call a provider directly:

```bash
curl -X POST "http://localhost:8100/demo/api/run/T0-P01?model_id=openai"
curl -X POST "http://localhost:8100/demo/api/run/T0-P01?model_id=anthropic"
curl -X POST "http://localhost:8100/demo/api/run/T0-P01?model_id=deepseek"
curl -X POST "http://localhost:8100/demo/api/run/T0-P01?model_id=google"
```

For DeepSeek V4, thinking mode is disabled for the Manager because this demo relies on reliable function-tool use and structured Pydantic output.


## Evaluation and scoring

The score cards are intentionally separated into:

- **Operational** — feasibility, service, and realized cost;
- **RAG** — retrieval of expected organizational evidence;
- **Skills / Tools** — procedural Skill usage, expected operational-tool coverage, cost/validation discipline, and tool-call efficiency.

The runtime API now returns an `evaluation_breakdown` object showing exactly how each score was produced. The UI displays this breakdown below the headline score cards.

The full formula, penalties, examples, and the distinction between runtime evaluation and final academic grading are documented in [EVALUATION.md](./EVALUATION.md).


## Logs and observability

The service and Case 0 demo now emit correlated structured logs for the complete execution path:

- HTTP requests and latency;
- authorization decisions without exposing credentials;
- team/case/model/RAG asset loading;
- selected LLM provider and resolved model;
- Manager prompt and lifecycle;
- every tool call;
- Skill discovery/loading;
- RAG searches, sources, chunks, and similarity scores;
- PyTorch model loading and inference;
- training-data generation and Case 0 model training;
- simulator weekly state, production, receipts, inventory, service, and cost;
- evaluation scores and detailed breakdowns.

Each request gets an `X-Trace-Id` response header. Search that trace id in the log to reconstruct a complete run.

Default file:

```text
logs/data-api.log
```

Recommended development settings:

```text
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/data-api.log
LOG_PAYLOADS=true
```

Use `LOG_LEVEL=DEBUG` for the most detailed simulator/training events.

Sensitive fields such as API keys, tokens, authorization values, passwords, secrets, cookies, and credentials are automatically redacted.

See [LOGGING.md](./LOGGING.md) for the complete configuration and event behavior.
