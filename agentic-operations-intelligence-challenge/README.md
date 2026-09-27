# Agentic Operations Intelligence Challenge

Final project platform for **LLM Agents + Pydantic AI + RAG + Skills + PyTorch + operations planning**.

## Architecture

Business/team data is no longer stored in this application. The main application obtains it from the standalone FastAPI service maintained on branch:

`service/agentic-operations-data-api`

```text
                    DATA API
     case + knowledge + model contract
       + training data + public scenarios
                         │
                         ▼
                MAIN APPLICATION
                         │
                  Pydantic AI Manager
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
             RAG       Skills    PyTorch
              └──────────┼──────────┘
                         ▼
                       Tools
                         │
                         ▼
                Structured monthly plan
                         │
                         ▼
              simulator + cost evaluator
```

Each team receives a different `DATA_API_TOKEN`. The Data API authorizes that token only for the assigned team.

## What students modify

Only:

```text
student/team_X/
├── models/   # model_a.pt2 + model_b.pt2
├── rag/      # retrieval configuration
└── skills/   # procedural Skills
```

Students do not modify the Manager, application, tools, schemas, simulator, cost engine or evaluator.

## What now comes from the Data API

For the authorized team:

- products and demand history;
- materials and initial inventory;
- BOM;
- suppliers and commercial parameters;
- production lines/capacity;
- open purchase orders;
- policies and cost parameters;
- RAG source documents;
- PyTorch model specification;
- public PyTorch training data;
- public development scenarios.

There are no runtime copies of those assets under this folder.

## Local setup

Run the Data API first (from its independent branch/deployment), then:

```bash
cd agentic-operations-intelligence-challenge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure:

```text
GOOGLE_API_KEY=...
DATA_API_URL=http://localhost:8100
DATA_API_TOKEN=<token assigned to this team>
```

Train:

```bash
python student/train_pytorch.py --team team_3 --model model_a
python student/train_pytorch.py --team team_3 --model model_b
```

Run:

```bash
python run.py
```

Open `http://localhost:8000`.

## Team packages

```bash
python scripts/build_student_package.py --team team_3
```

The ZIP contains **no case dataset or RAG source documents**. Those arrive at runtime through the API.

## Security

The final hidden evaluator, hidden scenarios, seeds, final holdouts and benchmark solutions must remain outside both the student package and the public Data API.

Also note: a branch in a public GitHub repository is itself public. For real team-data isolation, deploy the Data API from a private repository/deployment artifact even if this branch remains the development source.



## Manager LLM providers

The Manager is provider-independent through Pydantic AI. The UI can select one of four providers for each run:

- `google` — Google Gemini
- `openai` — OpenAI / ChatGPT models through the OpenAI API
- `anthropic` — Anthropic Claude
- `deepseek` — DeepSeek

Configure only the providers you want to use in `.env`:

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

`MANAGER_PROVIDER` controls the default selection. The browser can still choose any configured provider for an individual evaluation.

`MANAGER_MODEL` remains supported as a legacy explicit model-string override when no provider is selected by the request.

For DeepSeek V4 the runtime disables thinking mode for the Manager because the challenge depends on reliable tool use and structured Pydantic output.

API:

```text
GET /api/manager-models
```

returns the available provider/model choices and whether the required API-key environment variable is configured. It never returns the key value itself.


## Evaluation and scoring

The score cards are intentionally separated into:

- **Operational** — feasibility, service, and realized cost;
- **RAG** — retrieval of expected organizational evidence;
- **Skills / Tools** — procedural Skill usage, expected operational-tool coverage, cost/validation discipline, and tool-call efficiency.

The runtime API now returns an `evaluation_breakdown` object showing exactly how each score was produced. The UI displays this breakdown below the headline score cards.

The full formula, penalties, examples, and the distinction between runtime evaluation and final academic grading are documented in [EVALUATION.md](./EVALUATION.md).


## Logs and observability

The application now emits correlated structured logs for HTTP requests, LLM Manager runs, every tool call, Skills, RAG, PyTorch inference, Data API calls, training, simulation, and evaluation.

Each request has a `trace_id`, and that trace is forwarded to the Data API using `X-Trace-Id`. Secrets/tokens are automatically redacted.

Default file:

```text
logs/challenge.log
```

For the complete event catalog, configuration, examples, and trace-following instructions, see [LOGGING.md](./LOGGING.md).
