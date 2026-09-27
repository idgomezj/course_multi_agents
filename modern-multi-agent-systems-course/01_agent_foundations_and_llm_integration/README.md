# Module 1 — Agent Foundations and LLM Integration

## Objective

This module explains what an agent is and shows where an external LLM fits inside a modern agent architecture.

The central idea is:

```text
AGENT != MODEL
```

An agent can be described as:

```text
role
+ goals
+ state
+ capabilities
+ policies
+ decision mechanism
+ actions
```

An LLM can provide part of the decision mechanism, but the application still owns the agent's boundaries, state, tools, permissions, and orchestration.

## Theory

### Distributed AI and agents

A software agent:

- receives information from an environment,
- keeps or receives state,
- makes a decision,
- performs an action,
- has some degree of autonomy.

A reactive agent maps observations directly to actions.

A cognitive agent reasons using state, goals, beliefs, or plans.

A hybrid agent combines fast deterministic behavior with slower deliberative behavior.

### Agent vs. LLM

An LLM is a model that transforms context into generated output.

An agent is an application architecture around a decision mechanism.

```text
Environment
    ↓
Perception / Context
    ↓
Agent State
    ↓
Reasoning
    ├── rules
    ├── optimization
    ├── ML model
    └── LLM
    ↓
Policy / Validation
    ↓
Action
```

## Practice 1 — Basic External LLM

`01_basic_llm.py` demonstrates:

- provider/model abstraction,
- instructions,
- one agent run,
- usage metadata,
- run and conversation identifiers.

Run:

```bash
python 01_basic_llm.py
```

## Practice 2 — Structured Output

`02_structured_output.py` replaces fragile free-form parsing with a validated Pydantic model.

```text
LLM response
    ↓
Pydantic schema
    ↓
validated Python object
```

Run:

```bash
python 02_structured_output.py
```

## Practice 3 — Context and Message History

`03_context_and_history.py` demonstrates that conversational memory is supplied by the application.

```text
previous messages
      ↓
message_history
      ↓
new agent run
```

Run:

```bash
python 03_context_and_history.py
```

## Concepts to Explain in Class

### Prompt vs. instructions

- user prompt: the current task or request,
- instructions: persistent behavioral guidance supplied by the application.

### Context vs. memory

- context: information available in the current model request,
- message history: previous conversation messages re-supplied by the application,
- persistent memory: application data stored outside the model and loaded when useful.

### Usage and cost

Every model call consumes resources.

Students should inspect:

```python
result.usage
```

before moving to multi-agent systems, where one user request can create many model requests.

## Prerequisites

Install course dependencies from the root:

```bash
cd modern-multi-agent-systems-course
python -m pip install -r requirements.txt
cp .env.example .env
```

Configure `LLM_MODEL` and the API key required by the selected provider.

## Learning Check

A student should be able to answer:

1. Why is an LLM not automatically an agent?
2. What is the difference between free-form and structured output?
3. Who owns conversation history?
4. Why does usage accounting become important before introducing multiple agents?


## Classical MAS Reference

Before the LLM practices, review:

```text
FOUNDATIONS.md
```

It covers Distributed AI, agent vs. object, beliefs, goals, capabilities, commitments, and the main classical agent types.
