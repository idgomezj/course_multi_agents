from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from settings import get_model_name


class AgentDesign(BaseModel):
    role: str
    goal: str
    agent_type: Literal["reactive", "cognitive", "hybrid"]
    capabilities: list[str] = Field(min_length=2, max_length=5)
    requires_memory: bool
    requires_tools: bool
    rationale: str


def main() -> None:
    agent = Agent(
        get_model_name(),
        name="agent_architect",
        output_type=AgentDesign,
        instructions=(
            "Design small software agents. "
            "Return only facts supported by the user scenario."
        ),
    )

    result = agent.run_sync(
        "Design an agent that monitors factory machine temperature, "
        "stops production when the temperature becomes dangerous, "
        "and can also plan routine maintenance."
    )

    print("VALIDATED PYTHON OBJECT")
    print(result.output)

    print("\nJSON")
    print(result.output.model_dump_json(indent=2))

    print("\nTYPE")
    print(type(result.output).__name__)


if __name__ == "__main__":
    main()
