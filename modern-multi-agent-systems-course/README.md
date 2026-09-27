# Modern Multi-Agent Systems with LLMs

This is the main compact course for teaching modern LLM-based agent systems in four modules.

It intentionally combines two perspectives:

1. **Multi-Agent Systems foundations** — autonomy, roles, coordination, communication, control, and distributed problem solving.
2. **Current LLM-agent engineering** — structured outputs, tools, semantic RAG, memory, MCP, approval, graph orchestration, evaluation, sub-agents, A2A, and deep-agent concepts.

The goal is not to teach one framework in isolation. Pydantic AI is used as the main implementation framework because it provides typed agents, tools, capabilities, structured output, MCP integration, evaluation, graph orchestration, sub-agents, and distributed-agent integration.

Existing directories in this repository remain untouched and can be used as supplementary material:

- `llm-lab/` — how LLMs work and how they are trained/adapted.
- `pydantic-ai-lab/` — earlier focused Pydantic AI experiments.
- `sistemas-multiagentes-course/` — academic MAS material in the earlier course structure.

## Course Structure

```text
modern-multi-agent-systems-course/
│
├── 01_agent_foundations_and_llm_integration/
├── 02_capabilities_knowledge_and_communication/
├── 03_engineering_coordination_and_reliability/
└── 04_modern_multi_agent_systems/
```

## Learning Progression

```text
MODULE 1
What is an agent?
How can an LLM become one reasoning component?
        ↓
MODULE 2
What can the agent know, access, and do?
        ↓
MODULE 3
How do we coordinate, control, secure, and evaluate it?
        ↓
MODULE 4
How do multiple specialized agents collaborate locally and across services?
```

## Module 1 — Agent Foundations and LLM Integration

Core topics:

- Distributed AI and agent fundamentals
- agent vs. passive software object
- reactive, cognitive, and hybrid agents
- beliefs, goals, capabilities, decisions, commitments
- external LLM API
- provider/model abstraction
- instructions vs. user prompts
- typed structured output
- context and message history
- usage and cost awareness

## Module 2 — Capabilities, Knowledge, and Communication

Core topics:

- tools
- `RunContext` and dependencies
- toolsets
- reusable capabilities
- short-term vs. persistent memory
- embeddings
- semantic RAG
- local vector similarity
- structured agent communication
- MCP
- human approval
- deferred tools
- prompt-injection and tool-security boundaries

## Module 3 — Engineering, Coordination, and Reliability

Core topics:

- agent loops
- planning
- deterministic vs. model-controlled workflows
- Pydantic Graph
- cooperation, coordination, and control
- retries and stopping conditions
- usage/token/tool-call budgets
- hooks
- tracing concepts
- deterministic evaluation
- LLM-as-judge
- trajectory evaluation
- persistence vs. durable execution

## Module 4 — Modern Multi-Agent Systems

Core topics:

- sequential orchestration
- parallel orchestration
- delegation
- programmatic handoff
- supervisor/worker
- critic/validator
- shared typed state
- Pydantic AI Harness `SubAgents`
- dynamic workflow concept
- heterogeneous models
- usage propagation
- MCP vs. A2A
- A2A distributed agents
- agent discovery
- deep-agent concept
- capstone

## Infrastructure Philosophy

The course is designed to stay local wherever practical.

Required external runtime resource:

- one LLM provider API for LLM-backed examples

Local components:

- SQLite
- local files
- NumPy arrays
- local semantic embedding model
- local FastMCP server
- local graph orchestration
- local evaluation data
- local A2A server demo

### Important note about local embeddings

The semantic RAG example uses a small `sentence-transformers` model. The first run normally downloads the model once. After it is cached, embedding generation runs locally and does not require an embedding API or vector database.

## Suggested Teaching Schedule

### Day 1
Module 1 — agent foundations + external LLM + typed outputs

### Day 2
Module 2 — tools + embeddings + semantic RAG + memory + MCP + approval

### Day 3
Module 3 — graph orchestration + reliability + coordination + evals

### Day 4
Module 4 — orchestration patterns + SubAgents + A2A + capstone

## What Is Practical vs. Conceptual

Practical code:

- structured outputs
- context/history
- tools/dependencies
- toolsets
- semantic embeddings and RAG
- SQLite memory
- MCP
- approval gates
- graph workflows
- usage limits
- hooks
- evaluations
- parallel agents
- delegation
- SubAgents
- A2A
- capstone

Conceptual / short demo:

- hosted observability platforms
- durable execution engines such as Temporal/DBOS/Prefect/Restate
- deep agents
- realtime voice
- AG-UI
- agent specs
- production vector databases

## Setup

Create an environment and install:

```bash
python -m pip install -r requirements.txt
```

Copy:

```bash
cp .env.example .env
```

Then configure a model string and provider key:

```text
LLM_MODEL=openai:<model-you-can-access>
OPENAI_API_KEY=...
```

The exact provider can be changed without redesigning the course architecture.
