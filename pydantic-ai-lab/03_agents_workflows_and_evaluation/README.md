# 03 — Agents, Workflows, Reliability, and Evaluation

## Goal

Teach the core engineering ideas behind an agent without spending separate chapters on every production feature.

This module compresses:

- the agent loop
- planning
- execution
- structured validation
- retries
- stopping conditions
- guardrails
- local logging
- deterministic workflows
- evaluation datasets
- deterministic evaluators
- LLM-as-judge
- offline testing

## Agent loop

A plain LLM request is approximately:

```text
prompt
  ↓
model
  ↓
response
```

An agentic workflow adds control:

```text
goal
 ↓
plan
 ↓
execute
 ↓
validate
 ↓
pass? ── yes ──► final
  │
  no
  ↓
revision
  └──────────────► validate again
```

The important idea is not the number of agents. It is the **loop plus application control**.

## Run

```bash
python 01_single_agent_workflow.py
python 02_local_evaluation.py
python 03_offline_test_model.py
```

## Reliability

The demo contains several simple reliability mechanisms:

- typed `Plan`
- typed `Validation`
- input-length guardrail
- maximum retry count
- explicit stop condition
- no arbitrary shell/tool access
- local logs

Production systems usually add more sophisticated retries, timeouts, rate limits, authorization, and observability.

## Evaluation

We use two complementary forms.

### Deterministic

```text
expected terms / constraints
      ↓
Python check
      ↓
pass/fail
```

Cheap, reproducible, but narrow.

### LLM judge

```text
prompt + candidate
      ↓
judge model
      ↓
structured score
```

Flexible, but nondeterministic and costs another model call.

Real evaluation usually combines both.

Pydantic also provides **Pydantic Evals**, but this compressed module implements the mechanics directly so there is less framework surface to teach.

## Offline testing

Pydantic AI provides the built-in `test` model.

That means some application plumbing can be exercised without any provider API call.

This is useful for unit tests.

## Observability

We intentionally use normal Python logging to a local file:

```text
outputs/workflow.log
```

Pydantic AI is OpenTelemetry-native and can integrate with hosted observability, but no hosted service is required for this course.

## Where Pydantic Graph fits

For a few explicit steps, normal Python control flow is easier to teach.

Use Pydantic Graph when the workflow becomes a larger state machine with many branches, joins, parallel paths, and persistent transitions.

The concept is retained here; the extra framework is intentionally omitted because the course has only a few days.
