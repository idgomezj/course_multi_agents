import ast
import operator
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import (
    Agent,
    RunContext,
)

from memory import SQLiteMemory
from retrieval import LocalRetriever
from settings import get_model_name


BASE_DIR = Path(
    __file__
).resolve().parent


@dataclass
class Dependencies:

    retriever: LocalRetriever

    memory: SQLiteMemory


agent = Agent(
    get_model_name(),
    deps_type=Dependencies,
    instructions=(
        "You are an assistant for the local Atlas "
        "project. Use search_notes for project facts. "
        "Use remember/recall for persistent user or "
        "application memory. Never invent a local fact "
        "when the search tool can answer it."
    ),
)


@agent.tool
def search_notes(
    ctx: RunContext[Dependencies],
    query: str,
) -> str:
    """Search the local project notes and return the best matching passages."""

    results = ctx.deps.retriever.search(
        query,
        top_k=2,
    )

    return "\n\n".join(
        (
            f"[{item['name']}] "
            f"score={item['score']:.3f}\n"
            f"{item['text']}"
        )
        for item in results
    )


@agent.tool
def remember(
    ctx: RunContext[Dependencies],
    key: str,
    value: str,
) -> str:
    """Persist a short fact locally in SQLite."""

    ctx.deps.memory.set(
        key,
        value,
    )

    return (
        f"Saved memory '{key}'."
    )


@agent.tool
def recall(
    ctx: RunContext[Dependencies],
    key: str,
) -> str:
    """Read a previously stored fact from local SQLite memory."""

    value = ctx.deps.memory.get(
        key
    )

    if value is None:

        return (
            f"No memory found for '{key}'."
        )

    return value


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_calculate(
    expression
):

    node = ast.parse(
        expression,
        mode="eval",
    ).body

    def evaluate(current):

        if isinstance(
            current,
            ast.Constant,
        ) and isinstance(
            current.value,
            (
                int,
                float,
            ),
        ):

            return current.value

        if isinstance(
            current,
            ast.BinOp,
        ) and type(
            current.op
        ) in ALLOWED_OPERATORS:

            return ALLOWED_OPERATORS[
                type(
                    current.op
                )
            ](
                evaluate(
                    current.left
                ),
                evaluate(
                    current.right
                ),
            )

        if isinstance(
            current,
            ast.UnaryOp,
        ) and type(
            current.op
        ) in ALLOWED_OPERATORS:

            return ALLOWED_OPERATORS[
                type(
                    current.op
                )
            ](
                evaluate(
                    current.operand
                )
            )

        raise ValueError(
            "Unsupported expression."
        )

    return evaluate(
        node
    )


@agent.tool_plain
def calculator(
    expression: str
) -> float:
    """Calculate a basic arithmetic expression without using eval()."""

    return float(
        safe_calculate(
            expression
        )
    )


def main():

    deps = Dependencies(
        retriever=LocalRetriever(
            BASE_DIR
            / "knowledge"
        ),
        memory=SQLiteMemory(
            BASE_DIR
            / "data"
            / "memory.sqlite3"
        ),
    )

    result = agent.run_sync(
        (
            "Answer these tasks: "
            "1) find which database Atlas uses, "
            "2) calculate 25 * 12, and "
            "3) remember that answer_style=concise."
        ),
        deps=deps,
    )

    print(
        result.output
    )

    print(
        "\nLOCAL MEMORY"
    )

    print(
        deps.memory.all()
    )


if __name__ == "__main__":

    main()
