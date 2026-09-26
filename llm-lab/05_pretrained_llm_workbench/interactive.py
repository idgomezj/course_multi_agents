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

    require_complete_model()

    print(
        "Loading pretrained base model..."
    )

    model, tokenizer = (
        load_local_mlx_model()
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
