# Module 2 — Capabilities, Knowledge, and Communication

## Objective

This module turns an LLM-backed application into a useful agent by giving it controlled access to:

- tools,
- dependencies,
- reusable toolsets,
- local knowledge,
- persistent memory,
- semantic retrieval,
- MCP,
- human approval.

It also introduces the security boundary between **untrusted data** and **trusted application instructions**.

## 1. Tools, Dependencies, and Toolsets

Run:

```bash
python 01_tools_dependencies_toolsets.py
```

The example uses:

- `RunContext`,
- a typed dependency object,
- `FunctionToolset`,
- local inventory functions.

The application controls what the model can do.

```text
Agent
  ↓
Toolset
  ↓
Allowlisted functions
  ↓
Application data
```

A tool is not simply a prompt instruction. It is an executable application capability with a schema and implementation controlled by code.

## 2. Embeddings, Semantic RAG, and Memory

Run:

```bash
python 02_embeddings_rag_memory.py
```

### What is an embedding?

An embedding transforms text into a numeric vector that represents semantic information.

```text
"inventory is low"
        ↓
embedding model
        ↓
[0.12, -0.44, 0.81, ...]
```

Texts with similar meaning tend to have nearby vectors.

### Semantic RAG

The example uses:

```text
local .txt files
      ↓
SentenceTransformer
      ↓
local vectors
      ↓
cosine similarity
      ↓
top-k passages
      ↓
agent
```

No vector database is required.

The embedding model is `sentence-transformers/all-MiniLM-L6-v2`.

The first run normally downloads the model. Once cached, embeddings are computed locally.

### RAG vs. Memory

```text
RAG
=
retrieve external knowledge relevant to the current task

Memory
=
persist application state across runs
```

The example stores memory in SQLite and knowledge in local text files.

## 3. MCP, Approval, and Security

Run:

```bash
python 03_mcp_approval_security.py
```

The example creates an in-process local FastMCP server and exposes inventory as an MCP tool.

Pydantic AI's `MCP` capability connects the agent to that server.

```text
Agent
  ↓
MCP capability
  ↓
local MCP server
  ↓
inventory_status()
```

The purchase-order function is separate:

```python
@agent.tool_plain(requires_approval=True)
```

When the model proposes the action, the run stops at an approval boundary and the human can approve or reject it.

```text
Agent wants action
       ↓
Approval gate
   ┌───┴───┐
approve   reject
   │        │
execute   denied
```

## Deferred Tools

Approval is one form of deferred execution.

Another use case is a tool whose result will be produced later by:

- a worker,
- a frontend,
- another service,
- a human.

The important idea is:

```text
model requests action
      ↓
application may pause
      ↓
external decision/result arrives
      ↓
agent continues
```

## Capabilities

Modern Pydantic AI uses **capabilities** as reusable units that can bundle combinations of:

- tools/toolsets,
- instructions,
- lifecycle hooks,
- model settings,
- model selection behavior.

MCP and deferred-call handling in the example are both capabilities.

## Prompt Injection Boundary

Never assume retrieved content is trustworthy.

Wrong architecture:

```text
web/document text
      ↓
treated as instructions
      ↓
powerful tool
```

Better architecture:

```text
untrusted content
      ↓
extract facts
      ↓
typed validation
      ↓
policy / approval
      ↓
tool
```

## Learning Check

Students should be able to explain:

1. why tools should be allowlisted,
2. the difference between a tool and a toolset,
3. what a capability is,
4. what an embedding represents,
5. why semantic RAG differs from keyword search,
6. why RAG and memory solve different problems,
7. what problem MCP solves,
8. why sensitive tools need approval,
9. why retrieved text must not automatically become trusted instructions.
