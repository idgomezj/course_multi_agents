# Module 1 — Distributed AI and Agent Foundations

## Objective

This module introduces the conceptual foundations of Distributed Artificial Intelligence (DAI) and autonomous agents.

Students should finish the module able to explain:

- why intelligence may be distributed,
- what makes a software entity an agent,
- how an agent differs from a passive software object,
- the role of beliefs, capabilities, decisions and commitments,
- the main agent typologies used in Multi-Agent Systems.

## Example application

The example models an intelligent manufacturing cell.

It implements three agent styles:

### Reactive agent

The reactive agent responds directly to machine temperature.

```text
temperature
   ↓
threshold rule
   ↓
continue / slow / stop
```

It does not build a plan.

### Cognitive agent

The cognitive agent maintains beliefs about:

- machine availability,
- production queue,
- urgent orders.

It also has explicit capabilities and records commitments when it accepts work.

This illustrates the relationship:

```text
beliefs
   +
capabilities
   +
goal condition
   ↓
decision
   ↓
commitment
```

### Hybrid agent

The hybrid agent combines:

1. a fast reactive safety layer,
2. a cognitive production-planning layer.

Safety decisions take priority over normal planning.

This demonstrates why real industrial agents often combine multiple decision mechanisms.

## Theory-to-code mapping

| Theory | Code |
|---|---|
| Perception | `Perception` dataclass |
| Beliefs | `AgentState.beliefs` |
| Capabilities | `AgentState.capabilities` |
| Decisions | `Decision` |
| Commitments | `AgentState.commitments` |
| Reactive agent | `ReactiveAgent` |
| Cognitive agent | `CognitiveAgent` |
| Hybrid agent | `HybridAgent` |
| Environment change | scenario inputs |

## Requirements

- Python 3.11 or newer
- No external service
- No third-party Python dependency

## Run

From this module directory:

```bash
python app.py
```

Expected behavior:

- normal temperature allows production,
- high temperature activates the reactive safety response,
- critical temperature produces an emergency stop,
- the cognitive agent prioritizes urgent work when safety does not intervene.

## Suggested classroom exercise

Ask students to add an `AdaptiveAgent` that changes its temperature warning threshold according to a moving average of recent observations.

A second exercise is to create an `InformationAgent` that reads a local CSV file and informs the cognitive agent about expected demand.

## Key takeaway

An LLM is **not required** for an agent to exist.

An agent is defined by its relationship with:

```text
environment
+ state
+ goals
+ decisions
+ actions
+ autonomy
```

Later modules can use an LLM as one possible reasoning mechanism inside an agent.
