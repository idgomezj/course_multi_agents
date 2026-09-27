from pydantic_ai import (
    Agent,
    ModelRequestContext,
    RunContext,
    UsageLimits,
)
from pydantic_ai.capabilities import Hooks

from settings import get_model_name


hooks = Hooks()


@hooks.on.before_model_request
async def log_model_request(
    ctx: RunContext,
    request_context: ModelRequestContext,
) -> ModelRequestContext:
    print(
        f"[TRACE] run_step={ctx.run_step} "
        f"messages={len(request_context.messages)}"
    )
    return request_context


agent = Agent(
    get_model_name(),
    name="bounded_operations_agent",
    capabilities=[hooks],
    instructions=(
        "Use the calculator tool for arithmetic. "
        "Never execute a quantity outside the tool's allowed range."
    ),
)


@agent.tool_plain
def calculate_reorder(
    target_stock: int,
    on_hand: int,
    open_orders: int,
) -> int:
    """Calculate replenishment quantity with deterministic guardrails."""

    values = {
        "target_stock": target_stock,
        "on_hand": on_hand,
        "open_orders": open_orders,
    }

    for name, value in values.items():
        if value < 0 or value > 100_000:
            raise ValueError(
                f"{name} is outside the allowed range."
            )

    return max(
        target_stock
        - on_hand
        - open_orders,
        0,
    )


def main() -> None:
    limits = UsageLimits(
        request_limit=4,
        total_tokens_limit=2000,
        tool_calls_limit=3,
    )

    result = agent.run_sync(
        (
            "Inventory target is 120 units, on-hand is 32, "
            "and 15 units are already on order. "
            "Use the calculator and report how many more units are required."
        ),
        usage_limits=limits,
    )

    print("\nOUTPUT")
    print(result.output)

    print("\nUSAGE")
    print(result.usage)

    print("\nLIMITS")
    print(limits)


if __name__ == "__main__":
    main()
