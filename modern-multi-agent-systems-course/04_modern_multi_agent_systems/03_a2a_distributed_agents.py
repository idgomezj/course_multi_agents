from fasta2a.pydantic_ai import agent_to_a2a
from pydantic_ai import Agent

from settings import get_model_name


inventory_service_agent = Agent(
    get_model_name(),
    name="inventory_service_agent",
    description=(
        "A remote inventory specialist that answers "
        "inventory-policy questions."
    ),
    instructions=(
        "You are an inventory specialist exposed as an A2A service. "
        "Explain inventory decisions concisely."
    ),
)

# FastA2A converts the Pydantic AI agent into an A2A-compatible ASGI app.
app = agent_to_a2a(
    inventory_service_agent
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
    )
