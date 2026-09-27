import json

import mlx.core as mx

from mlx_lm import generate

from mlx_lm.sample_utils import make_sampler

from config import (
    COMPARISON_FILE,
    EVAL_PROMPTS_FILE,
    QLORA_OUTPUT_DIR,
)

from model_files import (
    load_base_model,
    load_qlora_model,
)


MAX_TOKENS = 160


def format_prompt(
    tokenizer,
    prompt
):

    return tokenizer.apply_chat_template(
        [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        add_generation_prompt=True,
        return_dict=False,
    )


def run_prompts(
    model,
    tokenizer,
    prompts
):

    sampler = make_sampler(
        temp=0.0
    )

    results = []

    for item in prompts:

        results.append(
            generate(
                model=model,
                tokenizer=tokenizer,
                prompt=format_prompt(
                    tokenizer,
                    item["prompt"],
                ),
                max_tokens=MAX_TOKENS,
                sampler=sampler,
                verbose=False,
            )
        )

    return results


def main():

    adapter_file = (
        QLORA_OUTPUT_DIR
        / "adapters.safetensors"
    )

    if not adapter_file.exists():

        raise FileNotFoundError(
            "QLoRA adapter not found. "
            "Run python run_training.py first."
        )

    with open(
        EVAL_PROMPTS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        prompts = json.load(file)

    print(
        "Running 4-bit BASE model..."
    )

    base_model, base_tokenizer = (
        load_base_model()
    )

    before = run_prompts(
        base_model,
        base_tokenizer,
        prompts,
    )

    del base_model
    del base_tokenizer

    mx.clear_cache()

    print(
        "Running 4-bit BASE + QLoRA..."
    )

    tuned_model, tuned_tokenizer = (
        load_qlora_model(
            QLORA_OUTPUT_DIR
        )
    )

    after = run_prompts(
        tuned_model,
        tuned_tokenizer,
        prompts,
    )

    rows = []

    for item, base_text, qlora_text in zip(
        prompts,
        before,
        after,
    ):

        row = {
            "id": item["id"],
            "prompt": item["prompt"],
            "base_4bit": base_text,
            "qlora": qlora_text,
        }

        rows.append(row)

        print(
            "\n"
            + "=" * 72
        )

        print(
            "PROMPT:"
        )

        print(
            item["prompt"]
        )

        print(
            "\n4-BIT BASE:"
        )

        print(
            base_text
        )

        print(
            "\nQLoRA:"
        )

        print(
            qlora_text
        )

    COMPARISON_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        COMPARISON_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            rows,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\nSaved:"
    )

    print(
        COMPARISON_FILE
    )


if __name__ == "__main__":

    main()
