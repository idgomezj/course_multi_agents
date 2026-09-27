from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import (
    Evaluator,
    EvaluatorContext,
)

from settings import get_model_name


answer_agent = Agent(
    get_model_name(),
    name="course_answer_agent",
    instructions=(
        "Answer accurately in one short paragraph. "
        "Use standard multi-agent terminology."
    ),
)


@dataclass
class ExpectedConcepts(Evaluator):
    """Deterministic concept-coverage evaluator."""

    async def evaluate(
        self,
        ctx: EvaluatorContext[str, str],
    ) -> float:
        expected = (
            ctx.expected_output
            or ""
        )

        required_terms = [
            term.strip().lower()
            for term in expected.split("|")
            if term.strip()
        ]

        if not required_terms:
            return 1.0

        output = str(ctx.output).lower()

        hits = sum(
            term in output
            for term in required_terms
        )

        return hits / len(required_terms)


dataset = Dataset(
    name="agent_concepts",
    cases=[
        Case(
            name="tool_calling",
            inputs=(
                "What is tool calling in an LLM agent?"
            ),
            expected_output="tool|function|action",
        ),
        Case(
            name="semantic_rag",
            inputs=(
                "What does semantic RAG do?"
            ),
            expected_output="retriev|embedding|context",
        ),
        Case(
            name="multi_agent_delegation",
            inputs=(
                "What is delegation in a multi-agent system?"
            ),
            expected_output="agent|delegate|task",
        ),
    ],
)

dataset.add_evaluator(
    ExpectedConcepts()
)


def task(prompt: str) -> str:
    return answer_agent.run_sync(
        prompt
    ).output


def main() -> None:
    report = dataset.evaluate_sync(
        task
    )

    print(report)


if __name__ == "__main__":
    main()
