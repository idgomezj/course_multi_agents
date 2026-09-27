from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import logging

from app.observability import current_trace_id, log_event, new_span_id, reset_span_id, set_span_id
from .model_registry import StudentModelRegistry
from .rag import RagIndex
from .skills import SkillLibrary

logger = logging.getLogger(__name__)


@dataclass
class RuntimeDeps:
    team_id: str
    case: dict[str, Any]
    scenario: dict[str, Any]
    rag: RagIndex
    skills: SkillLibrary
    models: StudentModelRegistry
    trace: list[dict[str, Any]] = field(default_factory=list)
    rag_hits: set[str] = field(default_factory=set)

    def record(self, tool: str, inputs: dict[str, Any], output: Any) -> Any:
        trace_id = current_trace_id()
        span_id = new_span_id()
        entry = {
            "tool": tool,
            "inputs": inputs,
            "output": output,
            "trace_id": trace_id,
            "span_id": span_id,
        }
        self.trace.append(entry)
        span_token = set_span_id(span_id)
        try:
            log_event(
                logger,
                "tool.completed",
                tool=tool,
                team_id=self.team_id,
                scenario_id=self.scenario.get("id"),
                tool_inputs=inputs,
                tool_output=output,
                tool_call_index=len(self.trace),
            )
        finally:
            reset_span_id(span_token)
        return output
