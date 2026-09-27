import logging
from pathlib import Path

from pydantic import BaseModel, Field

from pydantic_ai import Agent

from settings import get_model_name


BASE_DIR = Path(
    __file__
).resolve().parent

OUTPUT_DIR = (
    BASE_DIR
    / "outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | %(message)s"
    ),
    handlers=[
        logging.FileHandler(
            OUTPUT_DIR
            / "workflow.log"
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(
    "agent-workflow"
)


class Plan(BaseModel):

    objective: str

    steps: list[str] = Field(
        min_length=1,
        max_length=4,
    )


class Validation(BaseModel):

    passed: bool

    issues: list[str]

    improvement: str


planner = Agent(
    get_model_name(),
    output_type=Plan,
    instructions=(
        "Create a small executable plan. "
        "Use at most four concrete steps."
    ),
)


worker = Agent(
    get_model_name(),
    instructions=(
        "Execute the requested task concisely. "
        "Do not claim to have used tools, files, "
        "or external facts that were not supplied."
    ),
)


validator = Agent(
    get_model_name(),
    output_type=Validation,
    instructions=(
        "Validate whether the candidate actually "
        "satisfies the user's goal. Be strict but "
        "practical. Pass good concise work."
    ),
)


def validate_goal(
    goal
):

    clean = goal.strip()

    if not clean:

        raise ValueError(
            "Goal cannot be empty."
        )

    if len(clean) > 1500:

        raise ValueError(
            "Goal is too long for this teaching demo."
        )

    return clean


def run_workflow(
    goal,
    max_attempts=2,
):

    goal = validate_goal(
        goal
    )

    logger.info(
        "Planning goal: %s",
        goal,
    )

    plan_result = planner.run_sync(
        goal
    )

    plan = plan_result.output

    logger.info(
        "Plan: %s",
        plan.model_dump(),
    )

    candidate = None

    validation = None

    for attempt in range(
        1,
        max_attempts + 1,
    ):

        revision_context = ""

        if (
            validation is not None
            and
            not validation.passed
        ):

            revision_context = (
                "\nPrevious validation issues:\n- "
                + "\n- ".join(
                    validation.issues
                )
                + "\nRequested improvement:\n"
                + validation.improvement
            )

        candidate_result = worker.run_sync(
            (
                f"USER GOAL:\n{goal}\n\n"
                f"PLAN:\n"
                + "\n".join(
                    (
                        f"{index}. {step}"
                        for index, step in enumerate(
                            plan.steps,
                            start=1,
                        )
                    )
                )
                + revision_context
            )
        )

        candidate = (
            candidate_result.output
        )

        logger.info(
            "Attempt %s candidate created.",
            attempt,
        )

        validation_result = (
            validator.run_sync(
                (
                    f"GOAL:\n{goal}\n\n"
                    f"CANDIDATE:\n{candidate}"
                )
            )
        )

        validation = (
            validation_result.output
        )

        logger.info(
            "Attempt %s validation: %s",
            attempt,
            validation.model_dump(),
        )

        if validation.passed:

            break

    return {
        "plan":
            plan,
        "answer":
            candidate,
        "validation":
            validation,
        "attempts":
            attempt,
    }


def main():

    result = run_workflow(
        (
            "Explain in under 180 words how an "
            "LLM agent differs from a normal LLM "
            "API call. Include tool use and the "
            "agent loop."
        )
    )

    print(
        "\nFINAL ANSWER\n"
    )

    print(
        result[
            "answer"
        ]
    )

    print(
        "\nVALIDATION\n"
    )

    print(
        result[
            "validation"
        ]
    )

    print(
        "\nATTEMPTS"
    )

    print(
        result[
            "attempts"
        ]
    )


if __name__ == "__main__":

    main()
