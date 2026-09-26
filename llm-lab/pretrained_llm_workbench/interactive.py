from mlx_lm import (
    generate,
    load,
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

    print(
        "Loading pretrained base model..."
    )

    model, tokenizer = load(
        str(
            MODEL_DIR
        )
    )

    sampler = make_sampler(
        temp=DEFAULT_TEMPERATURE,
        top_p=DEFAULT_TOP_P,
        top_k=DEFAULT_TOP_K,
    )

    print(
        "\nInteractive continuation mode."
    )

    print(
        "This is a BASE model, not an "
        "instruction-tuned assistant."
    )

    print(
        "Give it text to continue rather than "
        "expecting perfect chat behavior."
    )

    print(
        "Type /exit to finish.\n"
    )

    while True:

        prompt = input(
            "Prompt> "
        ).strip()

        if prompt.lower() in {
            "/exit",
            "/quit",
        }:

            break

        if not prompt:

            continue

        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            max_tokens=DEFAULT_MAX_TOKENS,
            sampler=sampler,
            verbose=False,
        )

        print(
            "\nModel continuation:"
        )

        print(
            response
        )

        print()


if __name__ == "__main__":

    main()
