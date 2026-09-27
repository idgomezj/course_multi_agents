import asyncio

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from settings import get_model_name


class SpecialistReport(BaseModel):
    specialist: str
    findings: list[str] = Field(
        min_length=1,
        max_length=4,
    )
    recommendation: str


class FinalSynthesis(BaseModel):
    summary: str
    priorities: list[str] = Field(
        min_length=2,
        max_length=5,
    )


model = get_model_name()

inventory_agent = Agent(
    model,
    name="inventory_agent",
    output_type=SpecialistReport,
    instructions=(
        "Analyze only inventory implications. "
        "Use the facts supplied in the prompt."
    ),
)

production_agent = Agent(
    model,
    name="production_agent",
    output_type=SpecialistReport,
    instructions=(
        "Analyze only production-capacity implications. "
        "Use the facts supplied in the prompt."
    ),
)

logistics_agent = Agent(
    model,
    name="logistics_agent",
    output_type=SpecialistReport,
    instructions=(
        "Analyze only inbound/logistics implications. "
        "Use the facts supplied in the prompt."
    ),
)

supervisor = Agent(
    model,
    name="supervisor",
    output_type=FinalSynthesis,
    instructions=(
        "Synthesize specialist reports. "
        "Do not invent facts that are absent from the reports."
    ),
)


async def parallel_pattern(
    scenario: str,
) -> FinalSynthesis:
    inventory, production, logistics = await asyncio.gather(
        inventory_agent.run(scenario),
        production_agent.run(scenario),
        logistics_agent.run(scenario),
    )

    result = await supervisor.run(
        (
            "Synthesize these independent specialist reports:\n\n"
            f"INVENTORY:\n{inventory.output.model_dump_json(indent=2)}\n\n"
            f"PRODUCTION:\n{production.output.model_dump_json(indent=2)}\n\n"
            f"LOGISTICS:\n{logistics.output.model_dump_json(indent=2)}"
        )
    )

    return result.output


async def sequential_pattern(
    scenario: str,
) -> FinalSynthesis:
    inventory = await inventory_agent.run(
        scenario
    )

    production = await production_agent.run(
        (
            f"{scenario}\n\n"
            "Inventory agent already reported:\n"
            f"{inventory.output.model_dump_json(indent=2)}"
        )
    )

    result = await supervisor.run(
        (
            "Build a final sequential synthesis from these reports:\n\n"
            f"INVENTORY:\n{inventory.output.model_dump_json(indent=2)}\n\n"
            f"PRODUCTION:\n{production.output.model_dump_json(indent=2)}"
        )
    )

    return result.output


async def main() -> None:
    scenario = (
        "Weekly demand increased from 100 to 140 units. "
        "There are 70 units on hand, 20 inbound units delayed by four days, "
        "and 35 units of extra production capacity."
    )

    print("PARALLEL PATTERN")
    parallel = await parallel_pattern(
        scenario
    )
    print(
        parallel.model_dump_json(
            indent=2
        )
    )

    print("\nSEQUENTIAL PATTERN")
    sequential = await sequential_pattern(
        scenario
    )
    print(
        sequential.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
