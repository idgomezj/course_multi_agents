import json
from datetime import (
    datetime,
    timezone,
)

from mlx_lm import (
    generate,
    load,
)

from mlx_lm.sample_utils import (
    make_sampler
)

from config import (
    MODEL_REPO,
    MODEL_DIR,
    BASELINE_PROMPTS_FILE,
    BASELINE_OUTPUT_FILE,
)


BASELINE_MAX_TOKENS = 120


def main():

    if not (
        MODEL_DIR
        / "config.json"
    ).exists():

        raise FileNotFoundError(
            f"Model not found at: {MODEL_DIR}\n\n"
            "Download it first with:\n"
            "python download_model.py"
        )

    with open(
        BASELINE_PROMPTS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        prompts = json.load(
            file
        )

    print(
        "Loading model once for baseline evaluation..."
    )

    model, tokenizer = load(
        str(
            MODEL_DIR
        )
    )

    # Greedy decoding makes this baseline
    # reproducible and easier to compare after
    # fine-tuning.
    sampler = make_sampler(
        temp=0.0
    )

    results = []

    for index, item in enumerate(
        prompts,
        start=1
    ):

        print(
            f"[{index}/{len(prompts)}] "
            f"{item['id']}"
        )

        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=item["prompt"],
            max_tokens=BASELINE_MAX_TOKENS,
            sampler=sampler,
            verbose=False,
        )

        results.append({
            "id":
                item["id"],
            "prompt":
                item["prompt"],
            "response":
                response,
        })

    BASELINE_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    payload = {
        "created_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),
        "model_repo":
            MODEL_REPO,
        "decoding":
            "greedy",
        "max_new_tokens":
            BASELINE_MAX_TOKENS,
        "results":
            results,
    }

    with open(
        BASELINE_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        "\nBaseline saved:"
    )

    print(
        BASELINE_OUTPUT_FILE
    )

    print(
        "\nKeep this file. Later we will run "
        "the same prompts after fine-tuning."
    )


if __name__ == "__main__":

    main()
