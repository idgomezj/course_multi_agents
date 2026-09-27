from pydantic_ai import Agent


def main():

    agent = Agent(
        "test",
        instructions=(
            "This agent uses Pydantic AI's "
            "offline test model."
        ),
    )

    result = agent.run_sync(
        "This does not call an external LLM."
    )

    print(
        result.output
    )

    print(
        "\nThis script is useful for exercising "
        "agent plumbing without API cost."
    )


if __name__ == "__main__":

    main()
