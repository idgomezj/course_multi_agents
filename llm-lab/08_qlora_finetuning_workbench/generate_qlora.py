import argparse

from mlx_lm import generate

from mlx_lm.sample_utils import make_sampler

from config import QLORA_OUTPUT_DIR

from model_files import load_qlora_model


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate with the 4-bit base plus "
            "the trained QLoRA adapter."
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
        QLORA_OUTPUT_DIR
        / "adapters.safetensors"
    )

    if not adapter_file.exists():

        raise FileNotFoundError(
            "QLoRA adapter not found. "
            "Run python run_training.py first."
        )

    print(
        "Loading 4-bit base + QLoRA adapter..."
    )

    model, tokenizer = load_qlora_model(
        QLORA_OUTPUT_DIR
    )

    formatted_prompt = (
        tokenizer.apply_chat_template(
            [
                {
                    "role": "user",
                    "content": args.prompt,
                }
            ],
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
        "\nQLoRA response:\n"
    )

    print(
        response
    )


if __name__ == "__main__":

    main()
