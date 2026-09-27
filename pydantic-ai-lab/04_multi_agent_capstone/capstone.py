import asyncio
import json
from pathlib import Path

from pydantic import BaseModel, Field

from pydantic_ai import Agent

from settings import get_model_name


BASE_DIR = Path(
    __file__
).resolve().parent


class SpecialistReport(BaseModel):

    summary: str

    findings: list[str] = Field(
        min_length=2,
        max_length=5,
    )

    recommendations: list[str] = Field(
        min_length=1,
        max_length=4,
    )


class Critique(BaseModel):

    conflicts: list[str]

    missing_items: list[str]

    approved: bool


class FinalDecision(BaseModel):

    architecture: list[str] = Field(
        min_length=3,
        max_length=7,
    )

    priorities: list[str] = Field(
        min_length=2,
        max_length=5,
    )

    risks: list[str]

    final_summary: str


class SharedState(BaseModel):

    goal: str

    architecture_report: SpecialistReport

    reliability_report: SpecialistReport

    critique: Critique

    final: FinalDecision


architecture_agent = Agent(
    get_model_name(),
    output_type=SpecialistReport,
    instructions=(
        "You are the architecture specialist. "
        "Use only the supplied project brief. "
        "Focus on simple local architecture and "
        "clear component boundaries."
    ),
)


reliability_agent = Agent(
    get_model_name(),
    output_type=SpecialistReport,
    instructions=(
        "You are the reliability specialist. "
        "Use only the supplied project brief. "
        "Focus on validation, failures, security, "
        "cost control, testing, and observability."
    ),
)


critic_agent = Agent(
    get_model_name(),
    output_type=Critique,
    instructions=(
        "Compare two specialist reports. Identify "
        "real conflicts and important omissions. "
        "Approve when they are compatible enough "
        "for a small teaching project."
    ),
)


supervisor_agent = Agent(
    get_model_name(),
    output_type=FinalDecision,
    instructions=(
        "You are the supervisor. Synthesize the "
        "specialist reports and critique into one "
        "small actionable architecture. Prefer "
        "local components and avoid unnecessary "
        "infrastructure."
    ),
)


def load_brief():

    return (
        BASE_DIR
        / "local_context"
        / "project_brief.txt"
    ).read_text(
        encoding="utf-8"
    )


async def run_capstone(
    goal
):

    brief = load_brief()

    specialist_prompt = (
        f"GOAL:\n{goal}\n\n"
        f"PROJECT BRIEF:\n{brief}"
    )

    architecture_result, reliability_result = (
        await asyncio.gather(
            architecture_agent.run(
                specialist_prompt
            ),
            reliability_agent.run(
                specialist_prompt
            ),
        )
    )

    architecture_report = (
        architecture_result.output
    )

    reliability_report = (
        reliability_result.output
    )

    critique_result = await critic_agent.run(
        (
            f"GOAL:\n{goal}\n\n"
            "ARCHITECTURE REPORT:\n"
            f"{architecture_report.model_dump_json(indent=2)}"
            "\n\nRELIABILITY REPORT:\n"
            f"{reliability_report.model_dump_json(indent=2)}"
        )
    )

    critique = (
        critique_result.output
    )

    final_result = await supervisor_agent.run(
        (
            f"GOAL:\n{goal}\n\n"
            "ARCHITECTURE REPORT:\n"
            f"{architecture_report.model_dump_json(indent=2)}"
            "\n\nRELIABILITY REPORT:\n"
            f"{reliability_report.model_dump_json(indent=2)}"
            "\n\nCRITIQUE:\n"
            f"{critique.model_dump_json(indent=2)}"
        )
    )

    state = SharedState(
        goal=goal,
        architecture_report=architecture_report,
        reliability_report=reliability_report,
        critique=critique,
        final=final_result.output,
    )

    output_path = (
        BASE_DIR
        / "outputs"
        / "capstone_state.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        state.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    return state


async def main():

    state = await run_capstone(
        (
            "Design a small teaching application "
            "that demonstrates a useful multi-agent "
            "system using only a remote LLM API and "
            "local application resources."
        )
    )

    print(
        state.final.model_dump_json(
            indent=2
        )
    )

    print(
        "\nSaved shared state to:"
    )

    print(
        BASE_DIR
        / "outputs"
        / "capstone_state.json"
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
