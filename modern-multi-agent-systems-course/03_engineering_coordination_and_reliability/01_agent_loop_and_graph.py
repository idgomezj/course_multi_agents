from __future__ import annotations

import asyncio
from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_graph import (
    BaseNode,
    End,
    GraphBuilder,
    GraphRunContext,
    StepContext,
)

from settings import get_model_name


worker = Agent(
    get_model_name(),
    name="worker",
    instructions=(
        "Produce a concise technical answer. "
        "If the task is about agents, explicitly mention tools and control flow."
    ),
)


@dataclass
class Draft(BaseNode[None]):
    goal: str
    attempt: int = 1
    feedback: str = ""

    async def run(
        self,
        ctx: GraphRunContext[None],
    ) -> Review:
        prompt = self.goal

        if self.feedback:
            prompt += (
                "\n\nREVISION FEEDBACK:\n"
                + self.feedback
            )

        result = await worker.run(prompt)

        return Review(
            goal=self.goal,
            answer=result.output,
            attempt=self.attempt,
        )


@dataclass
class Review(BaseNode[None, object, str]):
    goal: str
    answer: str
    attempt: int

    async def run(
        self,
        ctx: GraphRunContext[None],
    ) -> Revise | End[str]:
        lower = self.answer.lower()

        checks = {
            "mentions_agent":
                "agent" in lower,
            "mentions_tools":
                "tool" in lower,
            "mentions_control":
                (
                    "control" in lower
                    or "workflow" in lower
                    or "orchestration" in lower
                ),
            "reasonable_length":
                120 <= len(self.answer) <= 1600,
        }

        failed = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        if not failed:
            return End(self.answer)

        if self.attempt >= 2:
            return End(
                self.answer
                + "\n\n[Stopped after maximum revision attempts.]"
            )

        return Revise(
            goal=self.goal,
            previous=self.answer,
            attempt=self.attempt + 1,
            failed_checks=failed,
        )


@dataclass
class Revise(BaseNode[None]):
    goal: str
    previous: str
    attempt: int
    failed_checks: list[str]

    async def run(
        self,
        ctx: GraphRunContext[None],
    ) -> Draft:
        feedback = (
            "The previous answer failed these deterministic checks: "
            + ", ".join(self.failed_checks)
            + ". Revise it without adding unsupported claims."
        )

        return Draft(
            goal=self.goal,
            attempt=self.attempt,
            feedback=feedback,
        )


builder = GraphBuilder(
    input_type=str,
    output_type=str,
)


@builder.step
async def start(
    ctx: StepContext[None, None, str],
) -> Draft:
    return Draft(ctx.inputs)


builder.add(
    builder.node(Draft),
    builder.node(Review),
    builder.node(Revise),
    builder.edge_from(
        builder.start_node
    ).to(start),
)

workflow = builder.build()


async def main() -> None:
    result = await workflow.run(
        inputs=(
            "Explain the difference between a plain LLM call "
            "and a controlled agent workflow."
        )
    )

    print(result)

    print("\nGRAPH")
    print(workflow)


if __name__ == "__main__":
    asyncio.run(main())
