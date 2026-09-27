from pydantic_ai import Agent

from settings import get_model_name


def main():

    model = get_model_name()

    agent = Agent(
        model,
        instructions=(
            "You are a concise technical tutor. "
            "Explain concepts clearly."
        ),
    )

    result = agent.run_sync(
        "In two paragraphs, explain the difference "
        "between an LLM model and an LLM application."
    )

    print(
        "MODEL"
    )

    print(
        model
    )

    print(
        "\nOUTPUT"
    )

    print(
        result.output
    )

    print(
        "\nUSAGE"
    )

    print(
        result.usage
    )

    print(
        "\nRUN ID"
    )

    print(
        result.run_id
    )

    print(
        "\nCONVERSATION ID"
    )

    print(
        result.conversation_id
    )


if __name__ == "__main__":

    main()
