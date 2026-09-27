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
├── models/   # model_a.pt + model_b.pt
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
