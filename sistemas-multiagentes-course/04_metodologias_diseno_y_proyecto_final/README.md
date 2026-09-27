# Module 4 — MAS Design Methodologies and Final Capstone

## Objective

This module closes the course by connecting Multi-Agent Systems theory with a repeatable engineering process.

It covers the three methodologies explicitly included in the course syllabus:

- MAS-CommonKADS,
- GAIA,
- MaSE.

It also revisits FIPA as a standardization reference and requires students to design, implement and validate a MAS prototype.

## Methodology perspective

The course does not require students to implement an entire historical methodology mechanically.

Instead, students learn what each methodology emphasizes and reuse the most useful design artifacts.

### MAS-CommonKADS

Useful questions:

- Who are the agents?
- What tasks do they perform?
- What knowledge does each task require?
- How do agents coordinate?

### GAIA

Useful questions:

- What roles exist?
- What are their responsibilities?
- What permissions do they need?
- What activities do they perform?
- What protocols connect the roles?

### MaSE

Useful questions:

- What are the system goals?
- Which roles satisfy those goals?
- What conversations occur?
- Which agent classes implement the roles?
- How are the agents deployed?

## Capstone application

The included example models an operational supply disruption.

A demand spike and inbound delay affect a product.

Four specialist agents analyze different parts of the environment:

```text
Demand Agent
Inventory Agent
Production Agent
Logistics Agent
       │
       ▼
   Coordinator
       │
       ▼
   Validator
       │
       ▼
Integrated Plan
```

An optional LLM supervisor can then produce an executive interpretation of the already validated local state.

This architecture intentionally separates:

```text
domain facts and arithmetic
        ↓
deterministic agents
        ↓
validated shared state
        ↓
optional LLM synthesis
```

The LLM is therefore not the source of operational truth.

## Theory-to-code mapping

| Theory | Capstone implementation |
|---|---|
| Agent roles | Demand, Inventory, Production, Logistics |
| Local knowledge | each agent receives only relevant scenario data |
| Cooperation | specialist reports contribute to one global plan |
| Coordination | `Coordinator.integrate()` |
| Control | `PlanValidator` |
| Shared state | serialized JSON result |
| Hybrid SMA | deterministic agents + optional LLM supervisor |
| Validation | explicit constraint checks |
| Traceability | every report identifies the producing agent |

## Requirements

### Local mode

Only Python 3.11+ is required.

### Optional LLM mode

Install:

```bash
python -m pip install -r requirements.txt
```

Copy:

```bash
cp .env.example .env
```

Configure:

```text
LLM_MODEL=openai:<model-you-can-access>
OPENAI_API_KEY=...
```

Another Pydantic AI-supported provider can be used instead.

## Run fully local

```bash
python app.py
```

No external API is called.

The program writes:

```text
outputs/capstone_result.json
```

## Run with optional LLM supervisor

```bash
python app.py --llm
```

The deterministic multi-agent analysis runs first.

Only after validation does the supervisor receive the local state.

## Validate the result

Inspect:

```text
validation.passed
validation.checks
integrated_plan.service_gap
integrated_plan.actions
```

The default scenario should produce a feasible plan without exceeding production capacity.

## Final project

Use:

```text
plantilla_proyecto_final.md
```

Students should deliver:

1. problem definition,
2. MAS justification,
3. global and local goals,
4. role model,
5. interaction protocol,
6. architecture diagram,
7. executable prototype,
8. at least three scenarios,
9. validation evidence,
10. conclusions.

## Suggested project domains

- production scheduling,
- maintenance coordination,
- supply-chain disruption management,
- warehouse task allocation,
- energy-market negotiation,
- fleet coordination,
- distributed quality control.

## Evaluation questions

A strong project should answer:

- Why are multiple agents preferable to one centralized procedure?
- What knowledge belongs to each agent?
- Which decisions are autonomous?
- How do agents communicate?
- How is cooperation achieved?
- How is coordination enforced?
- What control mechanism detects invalid behavior?
- How is the system validated?

## Key takeaway

The framework is not the architecture.

A successful MAS begins with:

```text
problem
→ goals
→ roles
→ interactions
→ organization
→ coordination
→ implementation
→ validation
```

Python, Pydantic AI, JASON, or another platform are implementation choices made after those design decisions.
