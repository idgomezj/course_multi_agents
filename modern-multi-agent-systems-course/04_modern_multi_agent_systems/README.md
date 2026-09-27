# Module 4 — Modern Multi-Agent Systems

## Objective

This module is the culmination of the course.

Students move from one bounded agent to systems in which multiple specialized agents collaborate.

The progression is:

```text
single agent
    ↓
sequential agents
    ↓
parallel agents
    ↓
delegation
    ↓
programmatic handoff
    ↓
supervisor / critic
    ↓
SubAgents
    ↓
distributed A2A agents
    ↓
deep-agent concepts
```

## 1. Orchestration Patterns

Run:

```bash
python 01_orchestration_patterns.py
```

The example demonstrates two important patterns.

### Sequential

```text
Agent A
   ↓
Agent B
   ↓
Supervisor
```

Use sequential execution when later work depends on earlier output.

### Parallel

```text
             ┌── Inventory Agent ──┐
Scenario ────┼── Production Agent ─┼── Supervisor
             └── Logistics Agent ──┘
```

Use parallel execution when specialist tasks are independent.

Parallelism can reduce latency, but it also increases simultaneous model requests and makes global usage controls more important.

## 2. Manual Delegation and Harness SubAgents

Run:

```bash
python 02_delegation_and_subagents.py
```

### Manual delegation

The manager exposes a tool that calls another agent.

```text
Manager Agent
     ↓
delegate_python_task()
     ↓
Specialist Agent
     ↓
tool result
     ↓
Manager continues
```

The implementation explicitly propagates:

```python
usage=ctx.usage
```

so delegated work contributes to the parent run's usage accounting.

### Harness SubAgents

Pydantic AI Harness provides `SubAgents`.

Instead of writing one delegation tool per specialist:

```text
Orchestrator
   │
   └── delegate_task(agent_name, task)
           ├── researcher
           └── validator
```

Each child receives its own message history.

The parent controls the roster, budgets, maximum calls, and failure behavior.

This is a modern implementation of specialized-agent delegation.

## 3. Heterogeneous Models

An agent is not the model.

A production system may use:

```text
Supervisor
  powerful reasoning model

Research Agent
  fast/general model

Validator
  different model or deterministic code

Embedding Model
  local semantic model
```

The capstone supports optional environment variables:

```text
SUPERVISOR_MODEL
RESEARCH_MODEL
VALIDATOR_MODEL
```

If they are not configured, all roles fall back to `LLM_MODEL`.

## 4. MCP vs. A2A

This distinction should be memorized.

```text
MCP
Agent <-> Tool / Resource
```

```text
A2A
Agent <-> Agent
```

MCP extends what an agent can access or do.

A2A lets independently served agents communicate across an agent-oriented protocol.

## 5. Distributed Agent with A2A

Run the A2A server:

```bash
python 03_a2a_distributed_agents.py
```

or:

```bash
uvicorn 03_a2a_distributed_agents:app --port 8001
```

The example converts a normal Pydantic AI agent into an A2A-compatible ASGI application using FastA2A.

Conceptually:

```text
Process / Service A
Inventory Agent
       │
       │ A2A
       ▼
Process / Service B
Another Agent
```

This is different from keeping all agents as Python objects inside one process.

### Agent discovery

Distributed systems need a way to describe what an agent is and what it can do.

A2A uses agent metadata/cards so clients can discover agent capabilities rather than relying only on hard-coded Python references.

## 6. Dynamic Workflow

Pydantic AI Harness also provides a **Dynamic Workflow** capability.

It lets the model orchestrate named sub-agents through a bounded workflow program, supporting patterns such as:

- fan-out,
- chaining,
- voting,
- task decomposition.

For a short course, understand the architectural role rather than building a large dynamic workflow.

Start with explicit orchestration and `SubAgents` first.

## 7. Deep Agents

A deep agent combines several capabilities:

```text
planning
+ tools
+ files/workspace
+ memory
+ sub-agents
+ context management
+ long-horizon execution
```

Deep agents are useful for tasks that may run for many steps and require their own working environment.

They should not be the starting point for every agent application.

A simpler agent with good tools is usually easier to control, evaluate, and operate.

## 8. Capstone

Run:

```bash
python 04_capstone.py
```

Architecture:

```text
                    SCENARIO
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   Inventory        Production       Logistics
     Agent             Agent           Agent
        └───────────────┼───────────────┘
                        ▼
                      Critic
                        │
                        ▼
                    Supervisor
                        │
                        ▼
                 Typed Shared State
                        │
                        ▼
              outputs/capstone_state.json
```

The capstone demonstrates:

- specialist roles,
- parallel execution,
- typed reports,
- critic/validator pattern,
- supervisor synthesis,
- heterogeneous model configuration,
- shared typed state,
- local persistence,
- explicit human-approval flag for consequential actions.

## When Not to Use Multiple Agents

Multi-agent architecture introduces:

- more latency,
- more requests,
- more cost,
- more failure modes,
- more state,
- more difficult evaluation.

Decision rule:

```text
Can one agent + good tools solve it?
          │
        yes
          ↓
      use one agent

          no
          ↓
Does specialization/decomposition provide real value?
          │
        yes
          ↓
    consider multi-agent
```

Multi-agent is an architectural choice, not a default.

## Learning Check

Students should be able to:

1. distinguish sequential from parallel orchestration,
2. explain delegation vs. programmatic handoff,
3. explain supervisor and critic roles,
4. propagate usage across delegated runs,
5. use Harness `SubAgents`,
6. explain why different roles may use different models,
7. distinguish MCP from A2A,
8. explain the difference between in-process agents and distributed agent services,
9. describe what makes an agent "deep",
10. justify when a multi-agent design is or is not appropriate.


## MAS Design Methodologies

Review:

```text
DESIGN_METHODOLOGIES.md
```

It provides a compact treatment of:

- MAS-CommonKADS,
- GAIA,
- MaSE,

and maps their design artifacts to modern Pydantic AI implementations.

## Final Project

Use:

```text
FINAL_PROJECT_TEMPLATE.md
```

The project requires students to design, implement, and evaluate a complete MAS, including roles, communication, RAG/memory, coordination, control, approval boundaries, budgets, output evaluation, and trajectory evaluation.
