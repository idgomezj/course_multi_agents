# Agentic Operations Data API

Standalone FastAPI service for the Agentic Operations Intelligence Challenge.

This branch now has **two roles**:

1. provide team-scoped **runtime business/scenario/RAG data** through the Data API;
2. run **Case 0 completely end-to-end on this branch**, without using `main`.

Ready-made student model training data is intentionally **not** served by the API. Teams 1–5 receive raw historical JSON through a team-scoped endpoint plus a local model contract, then construct the supervised datasets themselves. Case 0 is the exception: it has committed clean, ready-to-train CSVs for platform validation.

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

- evaluate the published T0-P01, T0-P02, or T0-P03 reference plan through the simulator/cost engine without an LLM;
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
├── training/
│   ├── README.md
│   ├── model_a_training.csv
│   └── model_b_training.csv
├── reference_plans/
│   ├── T0-P01.json
│   ├── T0-P02.json
│   └── T0-P03.json
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

The canonical first call for any team activity is:

- `GET /v1/teams/{team_id}/start-context` — complete student-visible case context, knowledge, authorized scenario list, workflow/resources, and AI-client tutor policy when an AI client is detected

The challenge runtime loads this context before scenario/model-resolution work.

Other endpoints:

- `GET /health`
- `GET /v1/teams`
- `GET /v1/teams/{team_id}/bootstrap`
- `GET /v1/teams/{team_id}/case`
- `GET /v1/teams/{team_id}/knowledge`
- `GET /v1/teams/{team_id}/training-source.json` — raw historical JSON for Teams 1–5; not model-ready
- `GET /v1/teams/{team_id}/scenarios` — the token selects the public or hidden scenario set
- `GET /v1/teams/{team_id}/scenarios/{scenario_id}` — token-scoped scenario detail
- `POST /v1/teams/{team_id}/scenarios/{scenario_id}/evaluate` — server-side scoring using the internal scenario
- `GET /v1/teams/{team_id}/scenarios/public` — explicit public compatibility route
- `GET /v1/teams/{team_id}/scenarios/hidden` — explicit hidden route
- `GET /v1/teams/team_0/reference-solution?scenario_id=T0-P01`
- `GET /v1/teams/team_0/reference-solution?scenario_id=T0-P02`
- `GET /v1/teams/team_0/reference-solution?scenario_id=T0-P03`

## Canonical start context

`/v1/teams/{team_id}/start-context` is designed as the authoritative starting point. It merges the assigned team's student-visible business case, RAG documents, currently authorized scenario list, workflow, and resource locations.

The service classifies the caller using, in order:

1. `X-Client-Type`;
2. `X-AI-Client`;
3. User-Agent heuristics.

Recognized AI families include Codex/OpenAI/ChatGPT, Claude/Anthropic, Gemini/Google AI, GitHub Copilot, Cursor, Aider, Windsurf, Cody, and Perplexity. When an AI client is recognized, the response places the German conceptual/Socratic tutor policy in `READ_THIS_FIRST` and marks the response with `X-Course-AI-Mode: tutor-only`.

The built-in challenge application identifies itself as `challenge-runtime`, so its Operations Manager receives the operational runtime context rather than tutor-only behavior.

**Important:** HTTP client identification is best-effort. Headers can be changed or spoofed, and an external AI is not technically forced to obey text returned by an API. This mechanism is an instructional/academic-integrity control, not a security boundary.

The editable policy text and workflow live in:

```text
data/start_context.json
```

## Authentication

Teams 1–5 have exactly **two scenario tokens each**: one public token and one hidden token. They are controlled in `data/scenario_access.json`; see `SCENARIO_ACCESS.md` for the current values and field-sharing policy.

The same token also authorizes that team's base case, knowledge, and training-source requests. Send the active token as `X-Scenario-Token` or through the backward-compatible `X-Team-Token` header.

The checked-in credentials are for development/course control. If students can read this branch, those values and any hidden JSON stored here are not secret. For a real exam deployment, run the service from an instructor-only source or inject production credentials and hidden scenario files at deployment time.

## Important separation

Case 0 lives on this service branch. It does not need `main` to run the demo.

Teams 1–5 remain the graded cases. Their supervised training rows are not generated by this API. The API exposes raw historical JSON for the authorized team, while the package contains the fixed local model contract and case guidance; students must create the model-specific training tables themselves.

Public scenarios currently live in `data/teams/team_X.yaml`. Hidden scenario definitions live under `data/scenarios/team_X/hidden.json`. The API projects only fields allowed for the presented token; realized outcomes and evaluator expectations stay server-side.


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
- internal Case 0 reference-model training;
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


## Case 0 published references

All three public Case 0 scenarios have deterministic worked references:

| Scenario | Purpose | Feasible | Service | Reference cost |
|---|---|---:|---:|---:|
| T0-P01 | Balanced month | YES | 100% | 79,249.05 |
| T0-P02 | Supplier-risk trade-off | YES | 100% | 77,827.30 |
| T0-P03 | Promotion/demand increase | YES | 100% | 82,983.90 |

The browser's **Evaluate published reference** action works for every scenario.

The references are separate files under `demo_case_0_solution/reference_plans/`; there is no longer a single T0-P01-only reference file.

The AI Manager path remains independent and does not load these reference plans.
