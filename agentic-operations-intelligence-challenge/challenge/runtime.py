from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .model_registry import StudentModelRegistry
from .rag import RagIndex
from .skills import SkillLibrary


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
        self.trace.append({"tool": tool, "inputs": inputs, "output": output})
        return output
