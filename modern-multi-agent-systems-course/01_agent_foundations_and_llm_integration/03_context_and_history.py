from pydantic_ai import Agent

from settings import get_model_name


def main() -> None:
    agent = Agent(
        get_model_name(),
        name="operations_agent",
        instructions=(
            "You are an operations assistant. "
            "Use prior messages only when they are explicitly supplied as history."
        ),
    )

    first = agent.run_sync(
        "The factory project is called Atlas. "
        "Its production target is 1,200 units per week."
    )

    second = agent.run_sync(
        "What is the project name and weekly target?",
        message_history=first.all_messages(),
    )

    third = agent.run_sync(
        "What is the project name and weekly target?"
    )

    print("WITH MESSAGE HISTORY")
    print(second.output)

    print("\nWITHOUT MESSAGE HISTORY")
    print(third.output)

    print("\nKEY IDEA")
    print(
        "Conversation context is application-managed input. "
        "It is not permanent model memory."
    )


if __name__ == "__main__":
    main()
