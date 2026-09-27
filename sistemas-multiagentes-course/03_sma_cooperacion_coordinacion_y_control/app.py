from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Performative(str, Enum):
    CFP = "call_for_proposal"
    PROPOSE = "propose"
    REFUSE = "refuse"
    ACCEPT = "accept_proposal"
    REJECT = "reject_proposal"
    INFORM = "inform"


@dataclass(frozen=True)
class ProductionJob:
    job_id: str
    capability: str
    processing_hours: float
    due_in_hours: float


@dataclass
class Bid:
    agent_name: str
    performative: Performative
    estimated_completion_hours: float | None
    estimated_cost: float | None
    reason: str


@dataclass
class MachineAgent:
    name: str
    capabilities: set[str]
    queued_hours: float
    hourly_cost: float
    commitments: list[str] = field(default_factory=list)

    def evaluate_cfp(self, job: ProductionJob) -> Bid:
        if job.capability not in self.capabilities:
            return Bid(
                agent_name=self.name,
                performative=Performative.REFUSE,
                estimated_completion_hours=None,
                estimated_cost=None,
                reason=(
                    f"Missing capability '{job.capability}'."
                ),
            )

        completion = self.queued_hours + job.processing_hours
        cost = job.processing_hours * self.hourly_cost

        return Bid(
            agent_name=self.name,
            performative=Performative.PROPOSE,
            estimated_completion_hours=completion,
            estimated_cost=cost,
            reason=(
                f"Can execute after {self.queued_hours:.1f} h "
                f"of existing workload."
            ),
        )

    def accept(self, job: ProductionJob) -> str:
        self.queued_hours += job.processing_hours

        commitment = (
            f"{self.name} commits to {job.job_id}; "
            f"new queued load={self.queued_hours:.1f} h."
        )

        self.commitments.append(commitment)
        return commitment


@dataclass
class Award:
    winner: str
    score: float
    rationale: str


class ProductionCoordinator:
    """Simplified Contract Net manager.

    The score combines completion time and cost. Lower is better.
    """

    def __init__(
        self,
        machines: Iterable[MachineAgent],
        time_weight: float = 0.7,
        cost_weight: float = 0.3,
    ):
        self.machines = list(machines)
        self.time_weight = time_weight
        self.cost_weight = cost_weight

    def call_for_proposals(self, job: ProductionJob) -> list[Bid]:
        return [
            machine.evaluate_cfp(job)
            for machine in self.machines
        ]

    def _score(self, bid: Bid, job: ProductionJob) -> float:
        assert bid.estimated_completion_hours is not None
        assert bid.estimated_cost is not None

        lateness = max(
            bid.estimated_completion_hours - job.due_in_hours,
            0.0,
        )

        normalized_time = (
            bid.estimated_completion_hours
            + 4.0 * lateness
        )

        normalized_cost = bid.estimated_cost / 100.0

        return (
            self.time_weight * normalized_time
            + self.cost_weight * normalized_cost
        )

    def select(self, job: ProductionJob, bids: list[Bid]) -> Award:
        proposals = [
            bid
            for bid in bids
            if bid.performative == Performative.PROPOSE
        ]

        if not proposals:
            raise RuntimeError(
                f"No agent can execute job {job.job_id}."
            )

        ranked = sorted(
            (
                (self._score(bid, job), bid)
                for bid in proposals
            ),
            key=lambda item: item[0],
        )

        score, winner_bid = ranked[0]

        return Award(
            winner=winner_bid.agent_name,
            score=score,
            rationale=(
                "Selected using weighted completion time, "
                "lateness penalty, and processing cost."
            ),
        )

    def award(self, job: ProductionJob, award: Award) -> str:
        winner = next(
            machine
            for machine in self.machines
            if machine.name == award.winner
        )

        return winner.accept(job)


def print_bids(bids: list[Bid]) -> None:
    print("\nBIDS")
    print("-" * 78)

    for bid in bids:
        if bid.performative == Performative.REFUSE:
            print(
                f"{bid.agent_name:12} REFUSE | {bid.reason}"
            )
            continue

        print(
            f"{bid.agent_name:12} PROPOSE | "
            f"completion={bid.estimated_completion_hours:5.1f} h | "
            f"cost=$ {bid.estimated_cost:7.2f} | "
            f"{bid.reason}"
        )


def main() -> None:
    machines = [
        MachineAgent(
            name="CNC-A",
            capabilities={"turning", "drilling"},
            queued_hours=2.0,
            hourly_cost=80.0,
        ),
        MachineAgent(
            name="CNC-B",
            capabilities={"turning", "milling"},
            queued_hours=7.0,
            hourly_cost=60.0,
        ),
        MachineAgent(
            name="MILL-C",
            capabilities={"milling", "drilling"},
            queued_hours=1.0,
            hourly_cost=55.0,
        ),
    ]

    job = ProductionJob(
        job_id="JOB-1042",
        capability="turning",
        processing_hours=5.0,
        due_in_hours=10.0,
    )

    coordinator = ProductionCoordinator(
        machines,
        time_weight=0.7,
        cost_weight=0.3,
    )

    print("CALL FOR PROPOSAL")
    print(job)

    bids = coordinator.call_for_proposals(job)
    print_bids(bids)

    award = coordinator.select(job, bids)

    print("\nAWARD")
    print(award)

    commitment = coordinator.award(job, award)

    print("\nCOMMITMENT")
    print(commitment)

    print("\nFINAL MACHINE STATES")
    for machine in machines:
        print(
            f"{machine.name:12} "
            f"queued_hours={machine.queued_hours:5.1f} "
            f"commitments={len(machine.commitments)}"
        )


if __name__ == "__main__":
    main()
