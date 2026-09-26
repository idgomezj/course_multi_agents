import argparse

from mlx_lm import (
    generate,
)

from mlx_lm.sample_utils import (
    make_sampler
)

from config import (
    MODEL_DIR,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_TOP_K,
)


from model_files import (
    require_complete_model,
    load_local_mlx_model,
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate text with the downloaded "
            "pretrained base LLM."
        )
    )

    parser.add_argument(
        "--prompt",
        default=(
            "Artificial intelligence is"
        ),
        help=(
            "Raw text that the base model "
            "should continue."
        )
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help="Maximum new tokens."
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=(
            "0 gives greedy decoding. Higher "
            "values increase randomness."
        )
    )

    parser.add_argument(
        "--top-p",
        type=float,
        default=DEFAULT_TOP_P,
        help="Nucleus sampling threshold."
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=(
            "Restrict sampling to the top-k "
            "tokens. Use 0 to disable."
        )
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "Let MLX-LM print generation "
            "performance metrics."
        )
    )

    args = parser.parse_args()

    require_complete_model()

    print(
        "Loading model..."
    )

    model, tokenizer = (
        load_local_mlx_model()
    )

    sampler = make_sampler(
        temp=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
    )

    print(
        "\nPrompt:"
    )

    print(
        args.prompt
    )

    print(
        "\nCompletion:\n"
    )

    response = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=args.prompt,
        max_tokens=args.max_tokens,
        sampler=sampler,
        verbose=args.verbose,
    )

    if not args.verbose:

        print(
            response
        )


if __name__ == "__main__":

    main()
