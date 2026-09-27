import asyncio
import json
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from settings import get_model_name


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"


class Report(BaseModel):
    role: str
    facts: list[str] = Field(
        min_length=2,
        max_length=5,
    )
    recommendation: str


class Critique(BaseModel):
    approved: bool
    conflicts: list[str]
    missing_constraints: list[str]


class Decision(BaseModel):
    summary: str
    actions: list[str] = Field(
        min_length=2,
        max_length=6,
    )
    risks: list[str]
    requires_human_approval: bool


class SharedState(BaseModel):
    scenario: str
    inventory: Report
    production: Report
    logistics: Report
    critique: Critique
    decision: Decision


inventory_agent = Agent(
    get_model_name("RESEARCH_MODEL"),
    name="inventory_agent",
    output_type=Report,
    instructions=(
        "Analyze inventory only. "
        "Use only facts supplied in the scenario."
    ),
)

production_agent = Agent(
    get_model_name("RESEARCH_MODEL"),
    name="production_agent",
    output_type=Report,
    instructions=(
        "Analyze production capacity only. "
        "Use only facts supplied in the scenario."
    ),
)

logistics_agent = Agent(
    get_model_name("RESEARCH_MODEL"),
    name="logistics_agent",
    output_type=Report,
    instructions=(
        "Analyze inbound supply and logistics only. "
        "Use only facts supplied in the scenario."
    ),
)

critic_agent = Agent(
    get_model_name("VALIDATOR_MODEL"),
    name="critic_agent",
    output_type=Critique,
    instructions=(
        "Check specialist reports for contradictions, "
        "constraint violations, and missing information. "
        "Do not create new operational facts."
    ),
)

supervisor_agent = Agent(
    get_model_name("SUPERVISOR_MODEL"),
    name="supervisor_agent",
    output_type=Decision,
    instructions=(
        "Synthesize only the supplied reports and critique. "
        "Flag human approval when the final plan implies a new purchase "
        "or another consequential external action."
    ),
)


async def run_capstone(
    scenario: str,
) -> SharedState:
    inventory, production, logistics = await asyncio.gather(
        inventory_agent.run(
            scenario
        ),
        production_agent.run(
            scenario
        ),
        logistics_agent.run(
            scenario
        ),
    )

    critique = await critic_agent.run(
        (
            f"SCENARIO:\n{scenario}\n\n"
            f"INVENTORY:\n{inventory.output.model_dump_json(indent=2)}\n\n"
            f"PRODUCTION:\n{production.output.model_dump_json(indent=2)}\n\n"
            f"LOGISTICS:\n{logistics.output.model_dump_json(indent=2)}"
        )
    )

    decision = await supervisor_agent.run(
        (
            f"SCENARIO:\n{scenario}\n\n"
            f"INVENTORY:\n{inventory.output.model_dump_json(indent=2)}\n\n"
            f"PRODUCTION:\n{production.output.model_dump_json(indent=2)}\n\n"
            f"LOGISTICS:\n{logistics.output.model_dump_json(indent=2)}\n\n"
            f"CRITIQUE:\n{critique.output.model_dump_json(indent=2)}"
        )
    )

    state = SharedState(
        scenario=scenario,
        inventory=inventory.output,
        production=production.output,
        logistics=logistics.output,
        critique=critique.output,
        decision=decision.output,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        OUTPUT_DIR
        / "capstone_state.json"
    ).write_text(
        state.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    return state


async def main() -> None:
    scenario = (
        "Demand increased from 100 to 140 units per week. "
        "On-hand inventory is 70 units. "
        "20 inbound units are delayed by four days. "
        "The plant has at most 35 units of extra weekly production capacity. "
        "A new external purchase would require human approval."
    )

    state = await run_capstone(
        scenario
    )

    print(
        state.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
