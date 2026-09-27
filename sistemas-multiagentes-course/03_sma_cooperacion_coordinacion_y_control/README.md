# Module 3 — Multi-Agent Cooperation, Coordination, and Control

## Objective

This module moves from individual agents to a complete Multi-Agent System.

Students learn how:

- agents are organized into roles,
- cooperation combines local capabilities,
- coordination manages dependencies,
- control enforces system rules,
- tasks can be allocated through negotiation,
- local agent decisions produce global system behavior.

## Example application

The example implements a simplified **Contract Net-style** production allocation protocol.

A production coordinator needs to assign a job requiring a specific manufacturing capability.

The system contains three machine agents.

Each machine knows only its own:

- capabilities,
- current workload,
- hourly cost,
- commitments.

The coordinator knows the job and applies a common selection rule.

## Interaction protocol

```text
Coordinator
    │
    ├── CFP ──► CNC-A
    ├── CFP ──► CNC-B
    └── CFP ──► MILL-C

Machine agents evaluate local state.

CNC-A ──► PROPOSE
CNC-B ──► PROPOSE
MILL-C ─► REFUSE

Coordinator ranks proposals.

Coordinator ──► ACCEPT ──► winner
            └─► REJECT ──► others

Winner records a commitment.
```

The code is inspired by the Contract Net family of agent interaction protocols, but it is intentionally simplified for teaching and is not a complete FIPA protocol implementation.

## Theory-to-code mapping

| Theory | Code |
|---|---|
| Social organization | coordinator + machine roles |
| Cooperation | machines participate in solving the allocation problem |
| Coordination | call-for-proposal sequence |
| Control | coordinator validates and ranks proposals |
| Local autonomy | each `MachineAgent` calculates its own bid |
| Communication acts | `Performative` |
| Proposal | `Bid` |
| Commitment | `MachineAgent.commitments` |
| Global objective | coordinator scoring function |

## Requirements

- Python 3.11+
- standard library only
- no LLM
- no external API
- no database

## Run

```bash
python app.py
```

The output shows:

1. the call for proposal,
2. bids and refusals,
3. the selected winner,
4. the winner's commitment,
5. the final machine workloads.

## Experiments for class

### Experiment 1 — Change the objective

Modify:

```python
time_weight=0.7
cost_weight=0.3
```

Try prioritizing cost instead of speed.

Observe that the same autonomous agents can produce a different global allocation when the coordination policy changes.

### Experiment 2 — Create a deadline conflict

Reduce `due_in_hours` and inspect the lateness penalty.

### Experiment 3 — Remove the coordinator

Ask students to design a peer-to-peer negotiation where machines exchange proposals directly.

This creates a useful discussion about centralized versus distributed coordination.

## Key takeaway

A Multi-Agent System is not simply:

```text
many LLM calls
```

It is a system with:

```text
multiple autonomous entities
+
roles
+
interaction protocols
+
coordination rules
+
commitments
+
global behavior
```

LLM-based agents can participate in these structures, but the MAS concepts exist independently of LLM technology.
