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
