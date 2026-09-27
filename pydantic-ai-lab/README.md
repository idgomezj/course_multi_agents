# Pydantic AI — Compressed External LLM Track

This track starts after `llm-lab/08_qlora_finetuning_workbench`.

The first eight LLM labs answer:

> How does an LLM work, and how can its weights be adapted?

These four modules answer:

> How do we build useful applications and agent systems around an external LLM?

## Constraint

The only runtime network dependency is the configured LLM provider.

Everything else is local:

- Python tools
- SQLite memory
- local text files
- local retrieval
- local MCP server
- local evaluation
- local state
- optional local FastAPI service

No Redis, Postgres, pgvector, hosted vector database, Logfire, remote MCP server, or cloud workflow engine is required.

## Four-module plan

| # | Module | Concepts compressed into it |
|---|---|---|
| 01 | `01_llm_api_and_structured_output` | external LLM API, provider abstraction, prompts/instructions, sync runs, typed Pydantic outputs, usage, conversation history |
| 02 | `02_tools_memory_rag_mcp` | function tools, RunContext/dependencies, SQLite memory, local retrieval/RAG, vector-similarity concept, local MCP |
| 03 | `03_agents_workflows_and_evaluation` | agent loop, planning, execution, validation, retries, guardrails, deterministic workflow, local evaluation, logging |
| 04 | `04_multi_agent_capstone` | multiple agents, parallel specialists, programmatic handoff, supervisor synthesis, shared typed state, critic/validator, optional FastAPI |

## Setup

Create or activate one Python environment, then from this directory:

```bash
pip install -r requirements.txt
```

Set the Pydantic AI model string:

```bash
export LLM_MODEL="openai:<your-model>"
```

Then set the API key required by that provider, for example:

```bash
export OPENAI_API_KEY="..."
```

Pydantic AI supports multiple providers; changing `LLM_MODEL` lets the course code remain mostly unchanged.

Examples of model-string families include:

```text
openai:...
anthropic:...
google-gla:...
groq:...
mistral:...
openrouter:...
```

Use a model your API account actually has access to.

## Teaching order

If time is very limited:

```text
Day 1
01 → API + typed output

Day 2
02 → tools + local memory + RAG + MCP

Day 3
03 → single-agent workflow + reliability + evals

Day 4
04 → multi-agent capstone
```

## What is intentionally omitted

The course explains these ideas but does not require their external infrastructure:

- hosted observability → use local Python logging
- hosted vector DB → use local retrieval
- distributed durable execution → explain concept only
- remote MCP → use an in-process local MCP server
- provider gateway → explain model abstraction only
- Pydantic Graph → explain when to use it; use explicit Python orchestration for the compressed course

This keeps the concepts while making the course teachable in a few days.


## Concepts retained without separate modules

Because this track must fit into only a few days, several production concepts are taught at the point where they naturally appear instead of getting their own chapter:

| Concept | Where it appears |
|---|---|
| Provider abstraction / model switching | Module 01 |
| Usage and cost awareness | Module 01 via `result.usage` |
| Conversation context | Module 01 |
| Structured outputs / validation | Modules 01, 03, 04 |
| Tool calling | Module 02 |
| Dependency injection | Module 02 |
| Persistent memory | Module 02 with SQLite |
| RAG / retrieval | Module 02 with local vector similarity |
| Embeddings | Explained in Module 02 as the semantic replacement for the local lexical vectors |
| MCP | Module 02 with an in-process local server |
| Agent loop | Module 03 |
| Planning | Module 03 |
| Retries / stop conditions | Module 03 |
| Guardrails / security | Modules 02–03: explicit tools, validation, input limits |
| Observability | Module 03 with local logs; OpenTelemetry/Logfire explained as the production upgrade |
| Evals | Module 03: deterministic + LLM judge |
| Offline testing | Module 03 with Pydantic AI's `test` model |
| Human-in-the-loop | Explained as an approval checkpoint before consequential tools |
| Durable execution | Illustrated by persisted state; Temporal/DBOS/etc. are explained but not required |
| Agent delegation | Module 04 |
| Programmatic handoff | Module 04 |
| Parallel agents | Module 04 |
| Supervisor / worker | Module 04 |
| Critic / validator | Module 04 |
| Shared state | Module 04 |
| Pydantic Graph | Explained in Modules 03–04 as the upgrade for complex state machines |
| FastAPI integration | Optional local endpoint in Module 04 |
| Provider fallback / gateway | Explained as a production extension; not required for the class |

## What requires an external service?

At runtime, only this:

```text
configured LLM provider API
```

Everything else demonstrated by the course is local.

An embedding API is **not required**. Module 02 deliberately uses a local lexical vector retriever so the RAG mechanics can be taught without a second API or model download.

If later you want semantic retrieval, the retriever interface can be replaced by embeddings while the rest of the RAG pipeline stays the same.
