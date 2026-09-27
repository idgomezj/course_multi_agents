# Module 3 — Engineering, Coordination, and Reliability

## Objective

This module addresses a critical question:

> Once an agent can reason and use tools, how do we keep its behavior controlled, bounded, observable, and testable?

The module combines classical coordination/control concepts with modern agent-engineering mechanisms.

## 1. Agent Loop and Pydantic Graph

Run:

```bash
python 01_agent_loop_and_graph.py
```

The example implements:

```text
Goal
 ↓
Draft
 ↓
Review
 ├── pass ──► End
 └── fail ──► Revise
                │
                └──► Draft
```

The worker uses an LLM, but the application owns:

- allowed states,
- retry count,
- validation checks,
- transition rules,
- stopping behavior.

This demonstrates the difference between:

### Model-controlled workflow

```text
LLM decides what happens next
```

and:

### Application-controlled workflow

```text
typed graph decides what transitions are allowed
```

Use a graph when control flow itself is the difficult part: explicit states, branching, resumable transitions, or workflows that must be inspected and reasoned about.

Do not use a graph merely because agents are involved.

## 2. Limits, Hooks, and Guardrails

Run:

```bash
python 02_limits_hooks_and_guardrails.py
```

### Usage limits

Multi-agent systems can amplify cost quickly.

```text
1 request
  ↓
supervisor
  ↓
3 specialists
  ↓
tools
  ↓
retries
```

The example applies:

- request limit,
- total token limit,
- tool-call limit.

Limits are safety controls, not only cost controls. They prevent runaway loops.

### Hooks

The example uses a lifecycle hook before each model request.

Hooks can support:

- local diagnostics,
- metrics,
- policy checks,
- model routing,
- request inspection,
- tool inspection.

### Deterministic guardrails

The calculator tool rejects impossible or unsafe numeric ranges in normal Python.

Important principle:

```text
LLM judgment
+
deterministic policy
```

is often safer than asking the LLM to enforce every rule itself.

## 3. Code-First Evaluation

Run:

```bash
python 03_evaluation.py
```

The example uses **Pydantic Evals**:

```text
Dataset
  ├── Case
  ├── Case
  └── Case
      ↓
Task
      ↓
Evaluator
      ↓
Experiment report
```

The included evaluator is deterministic and checks required concepts.

## Output Evaluation vs. Trajectory Evaluation

For agents, the final answer is only part of correctness.

You may also need to evaluate:

- which tool was selected,
- tool arguments,
- whether RAG was used,
- whether an approval boundary was respected,
- which agent received a handoff,
- number of requests,
- token usage,
- total cost,
- retries,
- final outcome.

Modern agent evaluation therefore includes both:

```text
OUTPUT EVALUATION
+
TRAJECTORY / TRACE EVALUATION
```

Pydantic Evals supports output evaluation as well as span/agentic trajectory evaluation.

## LLM-as-a-Judge

Use deterministic checks whenever possible.

Use an LLM judge when evaluation requires qualitative reasoning such as:

- clarity,
- groundedness,
- relevance,
- completeness,
- policy interpretation.

LLM judges are useful but introduce:

- additional cost,
- nondeterminism,
- model bias.

A mature evaluation strategy combines deterministic checks, model-based evaluation, and human review.

## Persistence vs. Durable Execution

These are different concepts.

### Persistence

```text
save state
stop
load state later
```

Examples:

- JSON
- SQLite
- database conversation history

### Durable execution

```text
workflow step 1 ✓
workflow step 2 ✓
process crashes
        X
restart
        ↓
resume workflow safely
```

Pydantic AI currently integrates with durable execution systems including Temporal, DBOS, Prefect, Restate, and others.

For this compact course, students should understand the architecture but do not need to install a durable workflow engine.

## Cooperation, Coordination, and Control

These classical MAS ideas map naturally to current engineering mechanisms:

| MAS Concept | Modern Implementation Example |
|---|---|
| Cooperation | agents contribute specialized results |
| Coordination | graph/orchestrator controls ordering |
| Control | budgets, policies, validators, approvals |
| Commitment | persisted task/agent state |
| Monitoring | hooks and traces |
| Quality control | evals and critic/validator patterns |

## Learning Check

Students should be able to explain:

1. when a graph is better than free-form autonomous planning,
2. why a model should not enforce every hard business constraint,
3. why multi-agent trees need global budgets,
4. what lifecycle hooks are for,
5. why agent evaluation must inspect behavior, not only final text,
6. the difference between persistence and durable execution.
