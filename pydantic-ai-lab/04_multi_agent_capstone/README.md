# 04 — Multi-Agent Capstone

## Goal

Finish the compressed course with one small system that demonstrates the essential multi-agent patterns without external infrastructure.

This module compresses:

- specialist agents
- programmatic handoff
- agent delegation through a tool
- parallel execution
- supervisor/worker pattern
- critic/validator
- shared typed state
- local persistence
- optional FastAPI service
- when graph orchestration becomes useful

## Run

### Main capstone

```bash
python 01_parallel_multi_agent.py
```

### Delegation pattern

```bash
python 02_agent_delegation.py
```

### Optional local API

```bash
uvicorn api:app --reload
```

Then POST locally to `/run`.

The API itself is local. The agents still call the configured LLM provider.

## Main architecture

```text
                    USER GOAL
                        │
                        ▼
              application orchestrator
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
      architecture agent    reliability agent
              │                   │
              └─────────┬─────────┘
                        ▼
                    critic
                        │
                        ▼
                   supervisor
                        │
                        ▼
                typed final result
                        │
                        ▼
            outputs/capstone_state.json
```

The two specialists run concurrently with `asyncio.gather`.

This is a **programmatic handoff** pattern: application code decides which agent runs next.

## Delegation pattern

The second script demonstrates another pattern:

```text
manager agent
     │
     ├── decides specialist is needed
     │
     ▼
tool: ask_python_specialist(...)
     │
     ▼
specialist agent
     │
     ▼
tool result back to manager
     │
     ▼
manager final response
```

Here an agent delegates to another agent through a registered tool.

## Shared state

The main capstone stores all stages in a typed Pydantic model:

```text
SharedState
├── goal
├── architecture_report
├── reliability_report
├── critique
└── final
```

It is serialized locally to JSON.

A production system might store equivalent state in PostgreSQL or a durable workflow engine, but that infrastructure is not required to understand the pattern.

## Supervisor vs critic

The critic does not own the final response.

Its job is:

```text
find conflicts
find omissions
approve/reject
```

The supervisor then synthesizes the final decision.

This is similar to validator/reconciliation patterns commonly used in multi-agent systems.

## Where graphs fit

Pydantic AI documents several multi-agent complexity levels:

```text
single agent
delegation
programmatic handoff
graph control flow
deep autonomous agents
```

This compressed course stops at explicit Python orchestration because it is much easier to teach quickly.

If the workflow grows into many branches, joins, persistent transitions, or complex parallel execution, **Pydantic Graph** is the natural next tool.

## What we intentionally do not require

- distributed queues
- Temporal
- Redis
- PostgreSQL
- remote MCP
- hosted tracing
- Kubernetes
- a vector database

Those are deployment choices, not prerequisites for learning agent architecture.

## Final mental model

After the original LLM labs and these four modules, the student should understand:

```text
HOW THE MODEL WORKS
        ↓
HOW TO CALL A MODEL
        ↓
STRUCTURED OUTPUT
        ↓
TOOLS
        ↓
MEMORY / RAG / MCP
        ↓
AGENT LOOP
        ↓
VALIDATION / EVALS
        ↓
MULTIPLE AGENTS
        ↓
ORCHESTRATION
```

That is enough foundation to start building real agent applications without spending weeks on framework-specific details.
