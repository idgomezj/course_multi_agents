from typing import Literal

from pydantic import BaseModel, Field

from pydantic_ai import Agent

from settings import get_model_name


class ConceptExplanation(BaseModel):

    concept: str

    definition: str

    key_points: list[str] = Field(
        min_length=2,
        max_length=4,
    )

    difficulty: Literal[
        "beginner",
        "intermediate",
        "advanced",
    ]

    example: str


def main():

    agent = Agent(
        get_model_name(),
        instructions=(
            "Teach AI concepts accurately and "
            "keep examples short."
        ),
        output_type=ConceptExplanation,
    )

    result = agent.run_sync(
        "Explain tool calling in an LLM application."
    )

    print(
        result.output
    )

    print(
        "\nAS JSON"
    )

    print(
        result.output.model_dump_json(
            indent=2
        )
    )

    print(
        "\nWhy this matters:"
    )

    print(
        "The application receives validated Python "
        "data, not a fragile block of free-form text."
    )


if __name__ == "__main__":

    main()
