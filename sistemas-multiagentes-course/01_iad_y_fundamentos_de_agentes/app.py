from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Action(str, Enum):
    CONTINUE = "continue_production"
    SLOW_DOWN = "slow_down"
    STOP = "emergency_stop"
    PROCESS_URGENT = "process_urgent_order"
    PROCESS_NORMAL = "process_normal_order"
    IDLE = "idle"


@dataclass
class Perception:
    temperature_c: float
    queue_size: int
    urgent_orders: int
    machine_available: bool = True


@dataclass
class Decision:
    action: Action
    reason: str


@dataclass
class AgentState:
    beliefs: dict[str, object] = field(default_factory=dict)
    capabilities: set[str] = field(default_factory=set)
    commitments: list[str] = field(default_factory=list)


class BaseAgent:
    def __init__(self, name: str, capabilities: Iterable[str]):
        self.name = name
        self.state = AgentState(
            capabilities=set(capabilities)
        )

    def perceive(self, perception: Perception) -> None:
        self.state.beliefs.update(
            {
                "temperature_c": perception.temperature_c,
                "queue_size": perception.queue_size,
                "urgent_orders": perception.urgent_orders,
                "machine_available": perception.machine_available,
            }
        )

    def decide(self) -> Decision:
        raise NotImplementedError


class ReactiveAgent(BaseAgent):
    """Fast stimulus-response policy with no planning."""

    def decide(self) -> Decision:
        temperature = float(
            self.state.beliefs["temperature_c"]
        )

        if temperature >= 90:
            return Decision(
                Action.STOP,
                "Temperature reached the emergency threshold.",
            )

        if temperature >= 75:
            return Decision(
                Action.SLOW_DOWN,
                "Temperature is high; reduce load immediately.",
            )

        return Decision(
            Action.CONTINUE,
            "No safety threshold is active.",
        )


class CognitiveAgent(BaseAgent):
    """Uses beliefs, capabilities and commitments to select a goal-oriented action."""

    def decide(self) -> Decision:
        available = bool(
            self.state.beliefs["machine_available"]
        )
        urgent = int(
            self.state.beliefs["urgent_orders"]
        )
        queue_size = int(
            self.state.beliefs["queue_size"]
        )

        if not available:
            return Decision(
                Action.IDLE,
                "The machine is not available.",
            )

        if urgent > 0 and "process_urgent" in self.state.capabilities:
            commitment = (
                f"Complete one urgent order; "
                f"{urgent - 1} urgent orders will remain."
            )
            self.state.commitments.append(commitment)

            return Decision(
                Action.PROCESS_URGENT,
                commitment,
            )

        if queue_size > 0 and "process_normal" in self.state.capabilities:
            commitment = (
                f"Process one normal order from queue of {queue_size}."
            )
            self.state.commitments.append(commitment)

            return Decision(
                Action.PROCESS_NORMAL,
                commitment,
            )

        return Decision(
            Action.IDLE,
            "No executable production goal is available.",
        )


class HybridAgent(BaseAgent):
    """Combines a reactive safety layer with cognitive planning."""

    def __init__(
        self,
        name: str,
        capabilities: Iterable[str],
    ):
        super().__init__(name, capabilities)
        self.reactive = ReactiveAgent(
            f"{name}-safety",
            capabilities={"stop", "slow_down"},
        )
        self.cognitive = CognitiveAgent(
            f"{name}-planner",
            capabilities=capabilities,
        )

    def perceive(self, perception: Perception) -> None:
        super().perceive(perception)
        self.reactive.perceive(perception)
        self.cognitive.perceive(perception)

    def decide(self) -> Decision:
        safety_decision = self.reactive.decide()

        if safety_decision.action in {
            Action.STOP,
            Action.SLOW_DOWN,
        }:
            return safety_decision

        cognitive_decision = self.cognitive.decide()
        self.state.commitments.extend(
            self.cognitive.state.commitments[
                len(self.state.commitments):
            ]
        )
        return cognitive_decision


def run_scenario(
    title: str,
    perception: Perception,
    agents: list[BaseAgent],
) -> None:
    print(f"\n=== {title} ===")
    print(f"Perception: {perception}")

    for agent in agents:
        agent.perceive(perception)
        decision = agent.decide()

        print(
            f"{agent.name:18} -> "
            f"{decision.action.value:24} | "
            f"{decision.reason}"
        )


def main() -> None:
    capabilities = {
        "process_urgent",
        "process_normal",
        "stop",
        "slow_down",
    }

    agents: list[BaseAgent] = [
        ReactiveAgent(
            "reactive-agent",
            capabilities,
        ),
        CognitiveAgent(
            "cognitive-agent",
            capabilities,
        ),
        HybridAgent(
            "hybrid-agent",
            capabilities,
        ),
    ]

    scenarios = [
        (
            "Normal production",
            Perception(
                temperature_c=55,
                queue_size=6,
                urgent_orders=1,
            ),
        ),
        (
            "High temperature",
            Perception(
                temperature_c=82,
                queue_size=8,
                urgent_orders=2,
            ),
        ),
        (
            "Emergency",
            Perception(
                temperature_c=96,
                queue_size=3,
                urgent_orders=1,
            ),
        ),
    ]

    for title, perception in scenarios:
        run_scenario(
            title,
            perception,
            agents,
        )


if __name__ == "__main__":
    main()
