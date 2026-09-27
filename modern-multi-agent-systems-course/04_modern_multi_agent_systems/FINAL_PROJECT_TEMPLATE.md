# Final Project Template — Modern Multi-Agent System

## 1. Problem Definition

Describe:

- operational context,
- users/stakeholders,
- environment,
- constraints,
- available data,
- global objective.

## 2. Why a Multi-Agent System?

Explain why one agent or one centralized procedure is insufficient.

Consider:

- distributed information,
- specialized capabilities,
- independent decisions,
- parallel work,
- organizational boundaries.

## 3. Global and Local Goals

### Global Goal

...

### Agent Goals

| Agent | Local Goal |
|---|---|
| | |

## 4. Agent Architecture

For each agent specify:

- name,
- role,
- model or deterministic decision mechanism,
- state/memory,
- tools,
- knowledge sources,
- output schema,
- permissions.

## 5. GAIA-Inspired Role Model

| Field | Description |
|---|---|
| Role | |
| Responsibilities | |
| Permissions | |
| Activities | |
| Protocols | |

## 6. MaSE-Inspired Design

Define:

1. system goals,
2. roles,
3. concurrent tasks,
4. conversations,
5. agent classes,
6. deployment.

## 7. MAS-CommonKADS-Inspired Design

Define:

- agent model,
- task model,
- knowledge/expertise model,
- coordination model.

## 8. Communication

For each important interaction define:

- sender,
- receiver,
- intention/performative,
- schema,
- conversation/task identifier.

Indicate whether the interaction is:

- in-process,
- MCP agent-to-tool,
- A2A agent-to-agent.

## 9. Knowledge and Memory

Document:

- RAG sources,
- embedding model,
- memory data,
- what enters the LLM context,
- what is considered untrusted data.

## 10. Cooperation, Coordination, and Control

### Cooperation

...

### Coordination

...

### Control

...

## 11. Human Approval

Identify consequential actions that require approval.

Examples:

- purchases,
- deletions,
- financial actions,
- external communications,
- production changes.

## 12. Budgets and Stopping Conditions

Define:

- maximum requests,
- maximum tokens,
- maximum tool calls,
- retry limits,
- timeout strategy.

## 13. Evaluation

Evaluate both:

### Final Output

- correctness,
- relevance,
- groundedness.

### Agent Trajectory

- correct tool selection,
- correct handoff,
- correct agent selection,
- approval compliance,
- request/tool-call counts,
- latency/cost.

## 14. Test Scenarios

Include at least:

1. normal scenario,
2. missing-information scenario,
3. conflicting-agent scenario,
4. tool failure,
5. approval rejected,
6. budget exhausted.

## 15. Results

Include:

- traces/logs,
- outputs,
- evaluation report,
- usage,
- failure observations.

## 16. Conclusion

Answer:

- Did multi-agent decomposition improve the solution?
- What complexity did it introduce?
- What would you change for production?
- Could a simpler single-agent design solve the same problem?
