from pydantic_ai import Agent

from settings import get_model_name


def main():

    agent = Agent(
        get_model_name(),
        instructions=(
            "You are a short, precise AI tutor."
        ),
    )

    first = agent.run_sync(
        "My project is called Atlas. "
        "It uses a local SQLite database."
    )

    print(
        "TURN 1"
    )

    print(
        first.output
    )

    second = agent.run_sync(
        "What is the project called and what "
        "database does it use?",
        message_history=first.all_messages(),
    )

    print(
        "\nTURN 2"
    )

    print(
        second.output
    )

    print(
        "\nSAME CONVERSATION?"
    )

    print(
        first.conversation_id
        ==
        second.conversation_id
    )

    print(
        "\nNEW MESSAGES IN TURN 2"
    )

    print(
        len(
            second.new_messages()
        )
    )

    print(
        "\nImportant:"
    )

    print(
        "The LLM itself did not gain permanent "
        "memory. The application supplied previous "
        "messages as context."
    )


if __name__ == "__main__":

    main()
