from dataclasses import dataclass

from pydantic_ai import Agent, FunctionToolset, RunContext

from settings import get_model_name


@dataclass
class OperationsContext:
    plant_name: str
    inventory: dict[str, int]
    reorder_points: dict[str, int]


inventory_tools = FunctionToolset[OperationsContext](
    instructions=(
        "Use these tools for inventory facts. "
        "Never invent stock levels."
    )
)


@inventory_tools.tool
def get_inventory(
    ctx: RunContext[OperationsContext],
    sku: str,
) -> dict[str, int | str]:
    """Return current stock and reorder point for one SKU."""

    key = sku.upper()

    if key not in ctx.deps.inventory:
        return {
            "sku": key,
            "status": "unknown",
        }

    return {
        "sku": key,
        "on_hand": ctx.deps.inventory[key],
        "reorder_point": ctx.deps.reorder_points[key],
    }


@inventory_tools.tool
def plant_status(
    ctx: RunContext[OperationsContext],
) -> str:
    """Return the plant name from typed run dependencies."""

    return ctx.deps.plant_name


def main() -> None:
    deps = OperationsContext(
        plant_name="Atlas Plant",
        inventory={
            "BEARING-6205": 18,
            "MOTOR-2HP": 12,
        },
        reorder_points={
            "BEARING-6205": 25,
            "MOTOR-2HP": 5,
        },
    )

    agent = Agent(
        get_model_name(),
        name="inventory_agent",
        deps_type=OperationsContext,
        toolsets=[inventory_tools],
        instructions=(
            "Answer inventory questions using the registered toolset. "
            "State whether the item is below its reorder point."
        ),
    )

    result = agent.run_sync(
        "At which plant are you operating, and should BEARING-6205 be reordered?",
        deps=deps,
    )

    print(result.output)
    print("\nUSAGE")
    print(result.usage)


if __name__ == "__main__":
    main()
