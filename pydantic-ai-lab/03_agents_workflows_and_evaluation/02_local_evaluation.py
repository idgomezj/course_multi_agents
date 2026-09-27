import json
from pathlib import Path

from pydantic import BaseModel, Field

from pydantic_ai import Agent

from settings import get_model_name


BASE_DIR = Path(
    __file__
).resolve().parent


class JudgeResult(BaseModel):

    score: int = Field(
        ge=0,
        le=5,
    )

    reason: str


answer_agent = Agent(
    get_model_name(),
    instructions=(
        "Answer accurately and concisely."
    ),
)


judge_agent = Agent(
    get_model_name(),
    output_type=JudgeResult,
    instructions=(
        "Grade the answer from 0 to 5 for "
        "correctness, relevance, and clarity."
    ),
)


def main():

    cases = json.loads(
        (
            BASE_DIR
            / "eval_cases.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    rows = []

    for case in cases:

        answer_result = (
            answer_agent.run_sync(
                case[
                    "prompt"
                ]
            )
        )

        answer = (
            answer_result.output
        )

        lower = answer.lower()

        deterministic_pass = all(
            term.lower()
            in lower
            for term in case[
                "required_terms"
            ]
        )

        judge_result = (
            judge_agent.run_sync(
                (
                    f"PROMPT:\n{case['prompt']}\n\n"
                    f"ANSWER:\n{answer}"
                )
            )
        )

        row = {
            "name":
                case[
                    "name"
                ],
            "answer":
                answer,
            "deterministic_pass":
                deterministic_pass,
            "judge":
                judge_result.output.model_dump(),
        }

        rows.append(
            row
        )

        print(
            "\n"
            + "=" * 60
        )

        print(
            case[
                "name"
            ]
        )

        print(
            answer
        )

        print(
            "deterministic_pass:",
            deterministic_pass,
        )

        print(
            "judge:",
            judge_result.output,
        )

    output = (
        BASE_DIR
        / "outputs"
        / "eval_results.json"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            rows,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "\nSaved:",
        output,
    )


if __name__ == "__main__":

    main()
