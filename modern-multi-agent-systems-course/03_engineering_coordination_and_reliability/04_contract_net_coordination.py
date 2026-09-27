from dataclasses import dataclass, field


@dataclass(frozen=True)
class Job:
    job_id: str
    capability: str
    processing_hours: float
    due_in_hours: float


@dataclass
class Bid:
    agent: str
    accepted: bool
    completion_hours: float | None
    cost: float | None
    reason: str


@dataclass
class MachineAgent:
    name: str
    capabilities: set[str]
    queued_hours: float
    hourly_cost: float
    commitments: list[str] = field(default_factory=list)

    def evaluate(self, job: Job) -> Bid:
        if job.capability not in self.capabilities:
            return Bid(
                agent=self.name,
                accepted=False,
                completion_hours=None,
                cost=None,
                reason="Required capability is unavailable.",
            )

        return Bid(
            agent=self.name,
            accepted=True,
            completion_hours=(
                self.queued_hours
                + job.processing_hours
            ),
            cost=(
                self.hourly_cost
                * job.processing_hours
            ),
            reason="Capability available.",
        )

    def commit(self, job: Job) -> None:
        self.queued_hours += job.processing_hours
        self.commitments.append(
            job.job_id
        )


class Coordinator:
    def __init__(
        self,
        machines: list[MachineAgent],
    ) -> None:
        self.machines = machines

    def call_for_proposals(
        self,
        job: Job,
    ) -> list[Bid]:
        return [
            machine.evaluate(job)
            for machine in self.machines
        ]

    def select(
        self,
        job: Job,
        bids: list[Bid],
    ) -> Bid:
        valid = [
            bid
            for bid in bids
            if bid.accepted
        ]

        if not valid:
            raise RuntimeError(
                "No agent can execute the job."
            )

        def score(bid: Bid) -> float:
            assert bid.completion_hours is not None
            assert bid.cost is not None

            lateness = max(
                bid.completion_hours
                - job.due_in_hours,
                0,
            )

            return (
                0.7 * (
                    bid.completion_hours
                    + 4 * lateness
                )
                + 0.3 * (
                    bid.cost / 100
                )
            )

        return min(
            valid,
            key=score,
        )

    def award(
        self,
        job: Job,
        winner: Bid,
    ) -> None:
        machine = next(
            item
            for item in self.machines
            if item.name == winner.agent
        )

        machine.commit(job)


def main() -> None:
    machines = [
        MachineAgent(
            name="CNC-A",
            capabilities={"turning", "drilling"},
            queued_hours=2,
            hourly_cost=80,
        ),
        MachineAgent(
            name="CNC-B",
            capabilities={"turning", "milling"},
            queued_hours=7,
            hourly_cost=60,
        ),
        MachineAgent(
            name="MILL-C",
            capabilities={"milling", "drilling"},
            queued_hours=1,
            hourly_cost=55,
        ),
    ]

    job = Job(
        job_id="JOB-1042",
        capability="turning",
        processing_hours=5,
        due_in_hours=10,
    )

    coordinator = Coordinator(
        machines
    )

    bids = coordinator.call_for_proposals(
        job
    )

    print("CALL FOR PROPOSALS")
    for bid in bids:
        print(bid)

    winner = coordinator.select(
        job,
        bids,
    )

    print("\nWINNER")
    print(winner)

    coordinator.award(
        job,
        winner,
    )

    print("\nCOMMITMENTS")
    for machine in machines:
        print(
            machine.name,
            machine.commitments,
        )


if __name__ == "__main__":
    main()
