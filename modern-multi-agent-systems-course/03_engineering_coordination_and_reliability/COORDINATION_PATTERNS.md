# Cooperation, Coordination, Control, and MAS Organization

## Social Organization

A MAS is not only a collection of agents.

The organization defines:

- roles,
- responsibilities,
- authority,
- information boundaries,
- interaction rules.

## Cooperation

Agents cooperate when their combined actions contribute to a common objective.

Examples:

- two agents contribute different analyses,
- one agent produces data another needs,
- agents share workload.

## Coordination

Coordination orders interdependent behavior.

Common coordination problems include:

- task allocation,
- scheduling,
- synchronization,
- resource contention,
- dependency management.

## Control

Control verifies that agent behavior remains inside allowed constraints.

Modern examples include:

- usage limits,
- policy checks,
- graph transitions,
- approval gates,
- validators,
- deterministic business rules.

Control does not necessarily remove autonomy. It defines the boundaries inside which autonomy is allowed.

## Common MAS Architectures

### Supervisor / Worker

```text
       Supervisor
       /   |   \
      A    B    C
```

### Hierarchical

```text
          Manager
         /       \
      Lead A    Lead B
      /   \      /   \
     A1   A2    B1   B2
```

### Peer-to-Peer

```text
A <-> B
^     ^
|     |
C <-> D
```

### Sequential

```text
A -> B -> C
```

### Parallel + Aggregator

```text
       ┌-> A --┐
Input -├-> B --├-> Aggregator
       └-> C --┘
```

### Critic / Validator

```text
Worker
  ↓
Critic
  ↓
pass? -- yes --> final
  |
  no
  ↓
revise
```

## Negotiation

Negotiation occurs when agents have:

- different local information,
- competing resource needs,
- different utility functions,
- multiple feasible task assignments.

Contract Net is one structured task-allocation pattern.

## Classical Concept to Modern Mechanism

| MAS concept | Modern mechanism |
|---|---|
| Cooperation | parallel specialists |
| Coordination | Python orchestration / graph |
| Control | validators, budgets, approvals |
| Organization | agent roster / roles |
| Negotiation | bidding / scoring / model-mediated proposal |
| Commitment | persisted task assignment |
