# Agentic Operations Intelligence Challenge

Final project platform for **LLM Agents + Pydantic AI + RAG + Skills + PyTorch + operations planning**.

This folder now contains both the project specification **and a runnable public MVP**.

## What students change

Only:

```text
student/team_X/
├── models/   # train/export PyTorch TorchScript models
├── rag/      # improve retrieval configuration
└── skills/   # improve procedural Skills
```

They do **not** modify the Manager, application, tools, simulator, cost engine, schemas or evaluator.

## What the instructor provides

- FastAPI backend;
- frontend dashboard;
- Pydantic AI Manager;
- common toolbox;
- RAG runtime;
- Skill loader;
- PyTorch model adapter;
- manufacturing data/contracts/policies;
- public development scenarios;
- independent simulator and cost engine;
- public evaluation feedback.

The final hidden evaluator, seeds, holdouts and benchmark solutions remain outside this public repository.

## Five different problem families

| Team | Case | PyTorch models |
|---|---|---|
| 1 | Volatile Demand | Demand Forecast + Demand Uncertainty |
| 2 | Stable Make-to-Stock | Demand Forecast + Excess Inventory Risk |
| 3 | Just-in-Time | Supplier Delay + Arrival-Time Prediction |
| 4 | Unreliable Supply | Supplier Delay + Supplier Quality Risk |
| 5 | Capacity-Constrained Plant | Downtime Risk + Production Feasibility |

All teams use the same application/toolbox but different business economics, RAG knowledge, Skills, model targets and scenario families.

## Evaluation idea

The Manager returns a structured monthly plan. The evaluator does not compare free text with an answer key.

```text
Manager plan
   ↓
constraint validation
   ↓
month simulation
   ↓
service measurement
   ↓
realized cost
   ↓
benchmark comparison
   ↓
score
```

The cost engine includes purchasing, production, holding, working capital, stockout/lost sales, overtime, changeovers, line stops and expedite costs. The weights differ by case.

## Quick start

```bash
cd agentic-operations-intelligence-challenge
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add a Gemini API key to `.env` if using the default Google model.

Train the two starter models for one team:

```bash
python student/train_pytorch.py --team team_1 --model model_a
python student/train_pytorch.py --team team_1 --model model_b
```

Run the platform:

```bash
python run.py
```

Open `http://localhost:8000`.

Run public engine tests:

```bash
pytest -q
```

## Create a package for one student team

Do not hand students the entire repository. Build the specific package:

```bash
python scripts/build_student_package.py --team team_3
```

The generated ZIP contains the shared runtime plus only Team 3's case, knowledge and editable workspace.

## Sharing boundary

Read **SHARING_MATRIX.md** before distribution.

The following must never be committed to this public repository:

- final hidden scenarios;
- hidden seeds;
- final PyTorch holdouts;
- hidden RAG queries and expected evidence;
- benchmark plans/costs for final tests;
- realized hidden future events;
- final evaluator credentials.

Those belong in private instructor infrastructure.
