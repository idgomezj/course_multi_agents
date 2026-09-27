# Agent Communication — Classical and Modern Views

## Why Agent Communication Needs Structure

In a MAS, communication is not only text transmission.

A message may communicate an intention such as:

- request an action,
- inform another agent,
- propose a solution,
- accept a proposal,
- reject a proposal.

A useful teaching message schema is:

```text
sender
receiver
performative
conversation_id
content
```

## KQML

KQML was an influential agent communication language focused on knowledge exchange.

A key idea was the **performative**: the message specifies the communicative intention separately from the payload.

Examples include concepts such as:

- ask,
- tell,
- achieve.

The historical value for this course is the separation:

```text
intent
!=
content
```

## FIPA

FIPA worked toward interoperability between agent systems and platforms.

Important teaching areas include:

- agent communication language (ACL),
- communicative acts,
- interaction protocols,
- agent-management concepts,
- message transport.

Useful ACL-style performatives include:

- REQUEST,
- INFORM,
- PROPOSE,
- ACCEPT_PROPOSAL,
- REJECT_PROPOSAL.

## Contract Net as an Interaction Protocol

Contract Net organizes task allocation:

```text
Manager
  ↓ CFP
Contractors
  ↓ proposals/refusals
Manager
  ↓ accept/reject
Winner
  ↓ commitment/result
```

A simplified local implementation appears in Module 3.

## AgentSpeak and JASON

AgentSpeak represents agent reasoning using BDI-oriented concepts:

- beliefs,
- goals,
- plans,
- intentions.

JASON is a well-known implementation environment for AgentSpeak-style agents.

The modern Python/Pydantic AI approach is not equivalent to AgentSpeak/JASON, but useful conceptual mappings exist:

| Classical concept | Modern implementation idea |
|---|---|
| Belief base | typed state / memory / context |
| Plan/action | application workflow / tool |
| Goal | task / instruction / desired output |
| Communication act | typed agent message |
| Agent platform | application runtime / services |

## MCP Is Not FIPA

MCP is primarily used to connect an agent/application to tools, resources, and external capabilities.

```text
MCP
Agent <-> Tool / Resource
```

FIPA/KQML focus more directly on agent communication semantics.

## A2A Is Closer to Agent-to-Agent Distribution

A2A addresses communication between independently served agents.

```text
A2A
Agent <-> Agent
```

The modern course therefore teaches:

```text
FIPA / KQML
historical communication foundations

MCP
agent-to-capability integration

A2A
distributed agent-to-agent integration
```
