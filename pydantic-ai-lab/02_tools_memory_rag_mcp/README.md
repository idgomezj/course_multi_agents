# 02 — Tools, Memory, Local RAG, and MCP

## Goal

Give the external LLM access to application capabilities without requiring any external infrastructure beyond the LLM API.

This module compresses:

- function/tool calling
- tool schemas and validation
- dependency injection with `RunContext`
- persistent memory
- local retrieval
- the RAG pipeline
- vector similarity as a concept
- local MCP
- safe local tools

## Run

```bash
python 01_local_retrieval.py
python 02_agent_tools_memory_rag.py
python 03_local_mcp.py
```

## Tools

An LLM cannot directly execute your Python functions.

Pydantic AI exposes selected functions as schemas:

```text
LLM decides it needs data/action
          ↓
tool call with typed arguments
          ↓
Pydantic validates arguments
          ↓
your local Python function runs
          ↓
tool result returned to LLM
          ↓
LLM continues
```

The tools in this lab are local and allowlisted.

There is no arbitrary shell execution.

## Dependency injection

The agent does not need global database/retriever state.

```text
Dependencies
├── LocalRetriever
└── SQLiteMemory
       ↓
RunContext[Dependencies]
       ↓
tools
```

This pattern becomes useful for testing and production applications.

## Memory

We use Python's built-in SQLite.

```text
LLM
 ↓
remember tool
 ↓
SQLite

later run
 ↓
recall tool
 ↓
SQLite
 ↓
LLM
```

This is application memory, not weight training and not magical model memory.

## RAG

The complete idea is:

```text
local documents
      ↓
split/index
      ↓
query representation
      ↓
similarity
      ↓
top-k passages
      ↓
LLM context/tool result
      ↓
answer
```

### Why no vector database?

You asked for no external infrastructure.

So this module implements a tiny local TF-IDF-style vector retriever with cosine similarity using only Python.

It teaches the same retrieval mechanics:

```text
document → vector
query → vector
cosine similarity
top-k
```

It is lexical rather than semantic.

In a larger application you can swap this component for:

- an embedding API from the same provider
- a local embedding model
- pgvector
- a hosted vector database

without changing the overall RAG architecture.

## MCP

MCP standardizes how an AI application discovers and invokes tools.

This lab creates an **in-process FastMCP server**:

```text
Pydantic AI Agent
      ↓
MCPToolset
      ↓
local FastMCP server
      ↓
local Python tools
```

No network server is required.

Pydantic AI also supports local stdio MCP and remote Streamable HTTP MCP, but those transports are not required for this compressed course.
