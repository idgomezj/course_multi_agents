import asyncio

from fastmcp import FastMCP

from pydantic_ai import Agent

from pydantic_ai.mcp import MCPToolset

from settings import get_model_name


server = FastMCP(
    "local-course-server"
)


@server.tool()
def course_status() -> dict:
    """Return the locally defined status of the compressed course."""

    return {
        "llm_labs_complete":
            8,
        "pydantic_ai_modules":
            4,
        "current_module":
            2,
        "external_services":
            [
                "configured LLM provider"
            ],
    }


@server.tool()
def multiply(
    a: float,
    b: float,
) -> float:
    """Multiply two numbers locally."""

    return (
        a
        *
        b
    )


async def main():

    toolset = MCPToolset(
        server
    )

    agent = Agent(
        get_model_name(),
        toolsets=[
            toolset
        ],
        instructions=(
            "Use the local MCP tools when they "
            "contain the requested information."
        ),
    )

    result = await agent.run(
        (
            "Using MCP, tell me the current module "
            "and multiply 17 by 9."
        )
    )

    print(
        result.output
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
