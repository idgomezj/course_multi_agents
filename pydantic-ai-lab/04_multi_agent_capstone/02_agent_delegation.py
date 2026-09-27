import asyncio

from pydantic_ai import Agent

from settings import get_model_name


specialist = Agent(
    get_model_name(),
    instructions=(
        "You are a Python specialist. "
        "Answer delegated technical questions "
        "in no more than three sentences."
    ),
)


manager = Agent(
    get_model_name(),
    instructions=(
        "You are a manager. If the question is "
        "about Python implementation details, "
        "delegate that part to the specialist tool "
        "before producing your final answer."
    ),
)


@manager.tool_plain
async def ask_python_specialist(
    question: str
) -> str:
    """Delegate a Python-specific question to a specialist agent."""

    result = await specialist.run(
        question
    )

    return result.output


async def main():

    result = await manager.run(
        (
            "Explain how I should persist a small "
            "agent's state locally in Python. Ask "
            "the Python specialist for the concrete "
            "implementation recommendation."
        )
    )

    print(
        result.output
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
