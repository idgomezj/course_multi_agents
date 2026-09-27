from pydantic_ai import Agent

from settings import get_model_name


def main() -> None:
    model = get_model_name()

    agent = Agent(
        model,
        name="technical_tutor",
        instructions=(
            "You are a concise technical tutor. "
            "Explain agent-system concepts accurately."
        ),
    )

    result = agent.run_sync(
        "Explain in three short paragraphs why an agent is not the same thing as an LLM."
    )

    print("MODEL")
    print(model)

    print("\nOUTPUT")
    print(result.output)

    print("\nUSAGE")
    print(result.usage)

    print("\nRUN ID")
    print(result.run_id)

    print("\nCONVERSATION ID")
    print(result.conversation_id)


if __name__ == "__main__":
    main()
