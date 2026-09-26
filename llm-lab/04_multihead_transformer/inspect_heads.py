import argparse

import torch

from config import (
    DEVICE,
    BLOCK_SIZE,
    N_HEADS,
    N_LAYERS,
    CHECKPOINT_FILE,
)

from tokenizer import CharacterTokenizer

from model import MiniGPT


def load_model():

    if not CHECKPOINT_FILE.exists():

        raise FileNotFoundError(
            f"Checkpoint not found: {CHECKPOINT_FILE}\n"
            "Train the model first with: python train.py"
        )

    tokenizer = (
        CharacterTokenizer()
    )

    model = MiniGPT(
        tokenizer.vocab_size
    )

    checkpoint = torch.load(
        CHECKPOINT_FILE,
        map_location=DEVICE
    )

    model.load_state_dict(
        checkpoint[
            "model_state_dict"
        ]
    )

    model = model.to(
        DEVICE
    )

    model.eval()

    return (
        tokenizer,
        model
    )


def print_attention_matrix(
    text,
    matrix,
    head_index
):

    print(
        f"\nHEAD {head_index + 1}\n"
    )

    print(
        "      ",
        end=""
    )

    for character in text:

        print(
            f"{character!r:>7}",
            end=""
        )

    print()

    for row_index, character in enumerate(
        text
    ):

        print(
            f"{character!r:>5}",
            end=""
        )

        for column_index in range(
            len(text)
        ):

            value = (
                matrix[
                    row_index,
                    column_index
                ]
                .item()
            )

            print(
                f"{value:7.2f}",
                end=""
            )

        print()


def print_top_connections(
    text,
    matrix,
    head_index
):

    print(
        f"\nHead {head_index + 1} "
        "strongest visible connections:"
    )

    for row_index in range(
        1,
        len(text)
    ):

        visible = matrix[
            row_index,
            :row_index + 1
        ]

        best_column = (
            torch.argmax(
                visible
            )
            .item()
        )

        print(
            f"  position {row_index:2d} "
            f"{text[row_index]!r} "
            f"attends most to "
            f"position {best_column:2d} "
            f"{text[best_column]!r} "
            f"({visible[best_column].item():.3f})"
        )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Inspect the learned attention "
            "weights of one Transformer block."
        )
    )

    parser.add_argument(
        "--text",
        default="language model",
        help="Text to inspect."
    )

    parser.add_argument(
        "--layer",
        type=int,
        default=0,
        help=(
            "Zero-based Transformer block index. "
            f"Valid values: 0 to {N_LAYERS - 1}."
        )
    )

    args = parser.parse_args()

    if not (
        0
        <= args.layer
        <
        N_LAYERS
    ):

        raise ValueError(
            f"--layer must be between "
            f"0 and {N_LAYERS - 1}"
        )

    if len(args.text) > BLOCK_SIZE:

        raise ValueError(
            f"Text has {len(args.text)} characters "
            f"but BLOCK_SIZE is {BLOCK_SIZE}."
        )

    tokenizer, model = (
        load_model()
    )

    tokens = tokenizer.encode(
        args.text
    )

    x = torch.tensor(
        [tokens],
        dtype=torch.long,
        device=DEVICE
    )

    with torch.no_grad():

        _, _, all_attention = model(
            x,
            return_attention=True
        )

    # One tensor per Transformer block.
    #
    # Selected tensor shape:
    #
    # (B, H, T, T)

    layer_attention = (
        all_attention[
            args.layer
        ][0]
        .cpu()
    )

    print(
        "\nText:",
        repr(args.text)
    )

    print(
        "Layer:",
        args.layer + 1,
        "of",
        N_LAYERS
    )

    print(
        "Heads:",
        N_HEADS
    )

    print(
        "Attention tensor shape:",
        tuple(
            layer_attention.shape
        )
    )

    for head_index in range(
        N_HEADS
    ):

        matrix = (
            layer_attention[
                head_index
            ]
        )

        print_attention_matrix(
            args.text,
            matrix,
            head_index
        )

        print_top_connections(
            args.text,
            matrix,
            head_index
        )


if __name__ == "__main__":

    main()
