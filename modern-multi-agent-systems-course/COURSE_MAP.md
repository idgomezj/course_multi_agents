# Course Map

## Module 1 — Agent Foundations and LLM Integration

Question answered:

> What is an agent, and where does an LLM fit inside an agent architecture?

Practices:

1. `01_basic_llm.py`
2. `02_structured_output.py`
3. `03_context_and_history.py`

Key distinction:

```text
AGENT != MODEL

Agent =
role
+ state
+ goals
+ instructions
+ tools
+ policies
+ model
```

---

## Module 2 — Capabilities, Knowledge, and Communication

Question answered:

> What can the agent know, access, and do?

Practices:

1. `01_tools_dependencies_toolsets.py`
2. `02_embeddings_rag_memory.py`
3. `03_mcp_approval_security.py`

Key distinctions:

```text
Memory != RAG

Memory = application state across interactions
RAG    = retrieve external knowledge for the current task
```

```text
MCP = Agent <-> Tools / Resources
```

---

## Module 3 — Engineering, Coordination, and Reliability

Question answered:

> How do we make agent behavior controlled, bounded, observable, and testable?

Practices:

1. `01_agent_loop_and_graph.py`
2. `02_limits_hooks_and_guardrails.py`
3. `03_evaluation.py`

Key distinction:

```text
Model-controlled workflow
vs.
Application-controlled workflow
```

---

## Module 4 — Modern Multi-Agent Systems

Question answered:

> How do specialized agents collaborate inside one application and across services?

Practices:

1. `01_orchestration_patterns.py`
2. `02_delegation_and_subagents.py`
3. `03_a2a_distributed_agents.py`
4. `04_capstone.py`

Key distinction:

```text
MCP = Agent <-> Tool
A2A = Agent <-> Agent
```

## Final Mental Model

```text
LLM
 ↓
typed application component
 ↓
agent
 ↓
tools + memory + RAG + MCP
 ↓
controlled workflow
 ↓
evaluation + safety + budgets
 ↓
multi-agent orchestration
 ↓
distributed agent systems
```
