import argparse

from transformers import AutoTokenizer

from config import MODEL_DIR


def require_model():

    if not MODEL_DIR.exists():

        raise FileNotFoundError(
            f"Model directory not found: {MODEL_DIR}\n\n"
            "Download it first with:\n"
            "python download_model.py"
        )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Inspect how a real pretrained LLM "
            "tokenizes text."
        )
    )

    parser.add_argument(
        "--text",
        default=(
            "Artificial intelligence is changing "
            "how software is built."
        ),
        help="Text to tokenize."
    )

    args = parser.parse_args()

    require_model()

    tokenizer = (
        AutoTokenizer.from_pretrained(
            MODEL_DIR,
            use_fast=True
        )
    )

    token_ids = tokenizer.encode(
        args.text,
        add_special_tokens=False
    )

    token_strings = (
        tokenizer.convert_ids_to_tokens(
            token_ids
        )
    )

    decoded_pieces = [
        tokenizer.decode(
            [token_id],
            skip_special_tokens=False
        )
        for token_id in token_ids
    ]

    print(
        "Text:"
    )

    print(
        repr(args.text)
    )

    print(
        "\nVocabulary size:",
        len(tokenizer)
    )

    print(
        "Characters:",
        len(args.text)
    )

    print(
        "Tokens:",
        len(token_ids)
    )

    if token_ids:

        print(
            "Characters per token:",
            f"{len(args.text) / len(token_ids):.2f}"
        )

    print(
        "\nTokenization:\n"
    )

    for index, (
        token_id,
        token_string,
        decoded_piece
    ) in enumerate(
        zip(
            token_ids,
            token_strings,
            decoded_pieces
        )
    ):

        print(
            f"{index:3d} | "
            f"id={token_id:6d} | "
            f"token={token_string!r:24} | "
            f"decoded={decoded_piece!r}"
        )

    print(
        "\nToken IDs:"
    )

    print(
        token_ids
    )

    print(
        "\nRound-trip decode:"
    )

    print(
        repr(
            tokenizer.decode(
                token_ids
            )
        )
    )

    print(
        "\nCompare this with our previous "
        "character tokenizer:"
    )

    print(
        f"Character tokenizer would need "
        f"approximately {len(args.text)} tokens."
    )

    print(
        f"This tokenizer used "
        f"{len(token_ids)} tokens."
    )


if __name__ == "__main__":

    main()
