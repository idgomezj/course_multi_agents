import asyncio

from pydantic_ai import (
    Agent,
    RunContext,
    UsageLimits,
)
from pydantic_ai_harness import (
    SubAgent,
    SubAgents,
)

from settings import get_model_name


model = get_model_name()

manual_specialist = Agent(
    model,
    name="manual_specialist",
    description="Answers focused Python implementation questions.",
    instructions=(
        "Answer only the delegated technical subtask. "
        "Keep the response concise."
    ),
)

manual_manager = Agent(
    model,
    name="manual_manager",
    instructions=(
        "For Python implementation details, call the specialist tool. "
        "Then integrate the specialist's result into your answer."
    ),
)


@manual_manager.tool
async def delegate_python_task(
    ctx: RunContext,
    task: str,
) -> str:
    """Delegate a self-contained task and propagate parent usage."""

    result = await manual_specialist.run(
        task,
        usage=ctx.usage,
    )

    return result.output


researcher = Agent(
    model,
    name="researcher",
    description="Extracts relevant facts from a supplied problem statement.",
    instructions=(
        "Work only from the supplied task. "
        "Return concise factual findings."
    ),
)

validator = Agent(
    model,
    name="validator",
    description="Checks a proposed solution for contradictions and missing constraints.",
    instructions=(
        "Validate the supplied proposal. "
        "Identify contradictions and missing constraints."
    ),
)

harness_manager = Agent(
    model,
    name="harness_manager",
    capabilities=[
        SubAgents(
            agents=[
                SubAgent(
                    researcher,
                    max_calls=2,
                ),
                SubAgent(
                    validator,
                    max_calls=2,
                ),
            ],
            contain_errors=True,
        )
    ],
    instructions=(
        "Delegate focused subtasks when useful. "
        "Use the researcher for fact extraction and the validator "
        "for quality control before the final answer."
    ),
)


async def main() -> None:
    limits = UsageLimits(
        request_limit=10,
        total_tokens_limit=5000,
        tool_calls_limit=8,
    )

    print("MANUAL DELEGATION")
    manual = await manual_manager.run(
        (
            "Recommend a simple way to persist small agent state locally. "
            "Delegate the concrete Python choice to the specialist."
        ),
        usage_limits=limits,
    )

    print(manual.output)
    print("Aggregated usage:", manual.usage)

    print("\nHARNESS SUBAGENTS")
    harness = await harness_manager.run(
        (
            "A production plan proposes using 50 units of extra capacity, "
            "but the stated maximum extra capacity is 35 units. "
            "Analyze the facts, validate the proposal, and give a corrected conclusion."
        ),
        usage_limits=limits,
    )

    print(harness.output)
    print("Tree usage:", harness.usage)


if __name__ == "__main__":
    asyncio.run(main())
