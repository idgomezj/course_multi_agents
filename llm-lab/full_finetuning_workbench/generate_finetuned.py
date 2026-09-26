import argparse

from mlx_lm import (
    generate,
)

from mlx_lm.sample_utils import (
    make_sampler,
)

from config import (
    FULL_WEIGHTS_DIR,
)

from model_files import (
    load_finetuned_model,
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate with the fully fine-tuned "
            "model weights."
        )
    )

    parser.add_argument(
        "--prompt",
        default=(
            "What is gradient accumulation?"
        ),
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=160,
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
    )

    args = parser.parse_args()

    adapter_file = (
        FULL_WEIGHTS_DIR
        / "adapters.safetensors"
    )

    if not adapter_file.exists():

        raise FileNotFoundError(
            "Fine-tuned weights not found. "
            "Run python run_training.py first."
        )

    print(
        "Loading fine-tuned model..."
    )

    model, tokenizer = (
        load_finetuned_model(
            FULL_WEIGHTS_DIR
        )
    )

    messages = [
        {
            "role": "user",
            "content": args.prompt,
        }
    ]

    formatted_prompt = (
        tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_dict=False,
        )
    )

    sampler = make_sampler(
        temp=args.temperature
    )

    response = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=formatted_prompt,
        max_tokens=args.max_tokens,
        sampler=sampler,
        verbose=False,
    )

    print(
        "\nPrompt:"
    )

    print(
        args.prompt
    )

    print(
        "\nFine-tuned response:\n"
    )

    print(
        response
    )


if __name__ == "__main__":

    main()
