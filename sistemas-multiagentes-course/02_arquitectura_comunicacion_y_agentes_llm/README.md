# Module 2 — Agent Architecture, Communication, and Modern LLM Agents

## Objective

This module connects classical agent architecture and communication concepts with a modern implementation.

The theoretical part covers:

- internal agent architecture,
- beliefs/state, reasoning, capabilities and actions,
- structured agent communication,
- KQML,
- FIPA and ACL-style performatives,
- AgentSpeak/JASON,
- modern typed messages,
- LLMs as optional cognitive components,
- tools and local sources of truth.

## Example application

The code implements a procurement agent for a manufacturing environment.

A production agent sends a structured request:

```text
production-agent
      ↓
REQUEST
      ↓
procurement-agent
```

The procurement agent can use only explicitly registered tools:

```text
inventory_status()
search_procurement_policy()
calculate_reorder_quantity()
```

The inventory and policy are local files.

The only external runtime dependency is the configured LLM API.

The final decision is validated with the Pydantic model `ProcurementDecision`.

## Communication model

The example includes a simplified `ACLMessage`:

```text
sender
receiver
performative
conversation_id
content
```

The performatives are inspired by agent communication languages:

- REQUEST
- INFORM
- PROPOSE
- ACCEPT_PROPOSAL
- REJECT_PROPOSAL

This is a teaching abstraction, **not a complete FIPA ACL implementation**.

The goal is to make the student see that agent communication is more than passing arbitrary text.

## Theory-to-code mapping

| Theory | Code |
|---|---|
| Agent communication | `ACLMessage` |
| Communicative act | `Performative` |
| Conversation correlation | `conversation_id` |
| Capabilities | Pydantic AI tools |
| Local environment facts | `inventory.json` |
| Knowledge/policy | `procurement_policy.txt` |
| Reasoning mechanism | external LLM |
| Structured action recommendation | `ProcurementDecision` |
| Dependency injection | `Dependencies` + `RunContext` |

## Requirements

- Python 3.11+
- an API key for one Pydantic AI-supported LLM provider
- no database
- no hosted vector store
- no remote MCP server

Install:

```bash
python -m pip install -r requirements.txt
```

## Configuration

Copy:

```bash
cp .env.example .env
```

Edit `.env`:

```text
LLM_MODEL=openai:<model-you-can-access>
OPENAI_API_KEY=...
```

If using another provider, use the corresponding Pydantic AI model string and provider API key.

## Run

```bash
python app.py
```

The application prints:

1. the incoming structured agent message,
2. the validated procurement decision,
3. the outgoing proposal message,
4. LLM usage information.

## Classroom discussion

Ask students to compare:

### Classical approach

```text
KQML / FIPA ACL
+
explicit agent architecture
+
BDI / AgentSpeak
```

### Modern implementation

```text
typed Python messages
+
Pydantic validation
+
LLM reasoning
+
allowlisted tools
```

They solve related engineering concerns but should not be presented as identical standards.

## Suggested exercise

Add an `inventory-agent` that owns inventory data.

The procurement agent should no longer read inventory directly; it must request the information through an agent message.

That exercise prepares the transition to Module 3.
