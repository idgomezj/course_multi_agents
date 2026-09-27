# Classical Foundations — Distributed AI and Agents

## Distributed Artificial Intelligence

Distributed Artificial Intelligence studies systems in which knowledge, control, decision-making, or action are distributed across multiple computational entities.

Typical reasons to distribute intelligence include:

- information is physically distributed,
- resources belong to different subsystems,
- decisions must happen concurrently,
- local autonomy is valuable,
- no single component has complete knowledge,
- the system should tolerate partial failure.

## Agent vs. Object

A software object typically responds when another component invokes one of its methods.

An agent may also:

- observe its environment,
- maintain beliefs or state,
- pursue goals,
- initiate actions,
- choose among alternatives,
- communicate or negotiate,
- make commitments.

The important distinction is **autonomous decision behavior**, not syntax or programming language.

## Internal Agent Concepts

### Beliefs

What the agent currently assumes or knows about the environment.

Beliefs may be:

- incomplete,
- uncertain,
- stale,
- local to one agent.

### Goals

States the agent tries to achieve.

### Capabilities

Actions the agent is able or authorized to perform.

### Decisions

Selections among available actions or plans.

### Commitments

Actions or obligations the agent has accepted, often creating expectations for other agents.

## Common Agent Types

### Reactive Agent

Responds directly to observations or events.

Example:

```text
temperature > safety threshold
        ↓
stop machine
```

### Cognitive / Deliberative Agent

Uses internal state, goals, plans, or reasoning before acting.

### Hybrid Agent

Combines fast reactive behavior with deliberate planning.

### Interface Agent

Mediates between users and other systems.

### Information Agent

Searches, filters, aggregates, or transforms information.

### Mobile Agent

Can migrate or move execution between computational environments.

### Autonomous Agent

Operates with limited direct supervision.

### Adaptive Agent

Changes behavior according to experience or environmental feedback.

## Where an LLM Fits

An LLM can implement part of the cognitive layer:

```text
perception
   ↓
state / context
   ↓
LLM reasoning
   ↓
typed decision
   ↓
policy validation
   ↓
action
```

But an LLM does not automatically provide:

- authorization,
- persistent state,
- tools,
- organizational roles,
- communication protocols,
- global coordination,
- safety policies.

Those remain application and system-design responsibilities.
