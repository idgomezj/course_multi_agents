from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Performative(str, Enum):
    """Simplified ACL-like performatives for teaching.

    This is inspired by FIPA-style communication but is not
    a complete FIPA ACL implementation.
    """

    REQUEST = "request"
    INFORM = "inform"
    PROPOSE = "propose"
    ACCEPT_PROPOSAL = "accept_proposal"
    REJECT_PROPOSAL = "reject_proposal"


class ACLMessage(BaseModel):
    sender: str
    receiver: str
    performative: Performative
    conversation_id: str
    content: str


class ProcurementDecision(BaseModel):
    sku: str
    current_stock: int
    reorder_quantity: int = Field(ge=0)
    action: str
    rationale: list[str] = Field(min_length=2, max_length=5)


@dataclass
class Dependencies:
    inventory: dict[str, dict[str, int]]
    policy_text: str


def get_model_name() -> str:
    model = os.getenv("LLM_MODEL")
    if not model:
        raise RuntimeError(
            "Set LLM_MODEL in .env, for example "
            "openai:<model-you-can-access>."
        )
    return model


agent = Agent(
    get_model_name(),
    deps_type=Dependencies,
    output_type=ProcurementDecision,
    instructions=(
        "You are a procurement agent in a manufacturing company. "
        "Use tools to obtain inventory and policy facts. "
        "Never invent stock values or policy rules. "
        "Return a conservative, operational recommendation."
    ),
)


@agent.tool
def inventory_status(
    ctx: RunContext[Dependencies],
    sku: str,
) -> dict[str, int]:
    """Return local inventory facts for one SKU."""

    key = sku.upper()

    if key not in ctx.deps.inventory:
        raise ValueError(f"Unknown SKU: {sku}")

    return ctx.deps.inventory[key]


@agent.tool
def search_procurement_policy(
    ctx: RunContext[Dependencies],
    query: str,
) -> str:
    """Return relevant local procurement-policy lines."""

    terms = {
        token.lower().strip(".,:;!?")
        for token in query.split()
        if len(token) >= 4
    }

    scored: list[tuple[int, str]] = []

    for line in ctx.deps.policy_text.splitlines():
        clean = line.strip()
        if not clean:
            continue

        lower = clean.lower()
        score = sum(term in lower for term in terms)
        scored.append((score, clean))

    scored.sort(key=lambda item: item[0], reverse=True)

    best = [line for score, line in scored if score > 0][:3]

    if not best:
        return ctx.deps.policy_text

    return "\n".join(best)


@agent.tool_plain
def calculate_reorder_quantity(
    target_stock: int,
    current_stock: int,
    open_purchase_orders: int = 0,
) -> int:
    """Calculate units still required to reach target stock."""

    return max(
        target_stock
        - current_stock
        - open_purchase_orders,
        0,
    )


def load_dependencies() -> Dependencies:
    inventory = json.loads(
        (BASE_DIR / "data" / "inventory.json").read_text(
            encoding="utf-8"
        )
    )

    policy = (
        BASE_DIR / "data" / "procurement_policy.txt"
    ).read_text(encoding="utf-8")

    return Dependencies(
        inventory=inventory,
        policy_text=policy,
    )


def main() -> None:
    incoming = ACLMessage(
        sender="production-agent",
        receiver="procurement-agent",
        performative=Performative.REQUEST,
        conversation_id="PO-2026-001",
        content=(
            "Evaluate whether SKU BEARING-6205 should be reordered. "
            "Production expects 75 units of demand next week."
        ),
    )

    deps = load_dependencies()

    prompt = (
        "INCOMING AGENT MESSAGE\n"
        f"{incoming.model_dump_json(indent=2)}\n\n"
        "Evaluate the request. Use the inventory and policy tools. "
        "The expected demand is 75 units."
    )

    result = agent.run_sync(
        prompt,
        deps=deps,
    )

    outgoing = ACLMessage(
        sender="procurement-agent",
        receiver=incoming.sender,
        performative=Performative.PROPOSE,
        conversation_id=incoming.conversation_id,
        content=result.output.model_dump_json(),
    )

    print("INCOMING MESSAGE")
    print(incoming.model_dump_json(indent=2))

    print("\nPROCUREMENT DECISION")
    print(result.output.model_dump_json(indent=2))

    print("\nOUTGOING MESSAGE")
    print(outgoing.model_dump_json(indent=2))

    print("\nUSAGE")
    print(result.usage)


if __name__ == "__main__":
    main()
