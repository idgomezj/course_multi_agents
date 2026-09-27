# MAS Design Methodologies

The final module includes the methodologies named in the academic MAS curriculum.

The purpose is not to spend days implementing every historical artifact. The goal is to understand what each methodology contributes to system design.

## MAS-CommonKADS

MAS-CommonKADS extends knowledge-engineering ideas into multi-agent analysis.

Useful design questions:

- Which agents exist?
- Which tasks do they perform?
- What knowledge does each task require?
- How do agents coordinate?
- What expertise is distributed across the system?

Useful artifacts:

- agent model,
- task model,
- expertise/knowledge model,
- coordination model.

## GAIA

GAIA treats the multi-agent system as an organization.

Core design questions:

- What roles exist?
- What responsibilities belong to each role?
- What permissions are needed?
- What activities can the role perform?
- Which interaction protocols connect roles?

A compact role template:

| Field | Description |
|---|---|
| Role | organizational role name |
| Responsibilities | what must be achieved or maintained |
| Permissions | information/resources the role may access |
| Activities | private actions |
| Protocols | interactions with other roles |

## MaSE

MaSE connects system goals to agent implementation.

A useful simplified flow:

```text
System Goals
    ↓
Use Cases / Scenarios
    ↓
Roles
    ↓
Concurrent Tasks
    ↓
Conversations
    ↓
Agent Classes
    ↓
Deployment
```

## Combining the Methodologies in This Course

The final project does not need three separate complete designs.

Instead, reuse the strongest artifact from each perspective:

### From MAS-CommonKADS

Document:

- agents,
- tasks,
- knowledge,
- coordination.

### From GAIA

Document:

- roles,
- responsibilities,
- permissions,
- protocols.

### From MaSE

Document:

- system goals,
- conversations,
- agent classes,
- deployment.

## Modern Mapping

| Design concern | Modern implementation |
|---|---|
| Agent role | named Pydantic AI Agent |
| Responsibility | instructions + output schema |
| Permission | tool/toolset/capability access |
| Knowledge | RAG / local state / dependencies |
| Interaction protocol | explicit orchestration / A2A |
| Coordination | Python / graph / supervisor |
| Control | limits / approval / validators |
| Deployment | process / service / A2A endpoint |

The methodology describes the architecture.

The framework implements it.
