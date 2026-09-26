import argparse

import torch
import torch.nn.functional as F

from config import (
    DEVICE,
    BLOCK_SIZE,
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


@torch.no_grad()
def generate(
    tokenizer,
    model,
    prompt,
    max_new_tokens=300,
    temperature=0.8,
    top_k=None
):

    generated = (
        tokenizer.encode(
            prompt
        )
    )

    for _ in range(
        max_new_tokens
    ):

        context = generated[
            -BLOCK_SIZE:
        ]

        x = torch.tensor(
            [context],
            dtype=torch.long,
            device=DEVICE
        )

        logits, _ = model(
            x
        )

        logits = logits[
            0,
            -1,
            :
        ]

        if temperature <= 0:

            next_token = (
                torch.argmax(
                    logits
                )
                .item()
            )

        else:

            logits = (
                logits
                /
                temperature
            )

            if (
                top_k is not None
                and
                top_k > 0
            ):

                top_k = min(
                    top_k,
                    logits.numel()
                )

                threshold = (
                    torch.topk(
                        logits,
                        top_k
                    )
                    .values[-1]
                )

                logits = logits.masked_fill(
                    logits < threshold,
                    float("-inf")
                )

            probabilities = (
                F.softmax(
                    logits,
                    dim=-1
                )
            )

            next_token = (
                torch.multinomial(
                    probabilities,
                    num_samples=1
                )
                .item()
            )

        generated.append(
            next_token
        )

    return tokenizer.decode(
        generated
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate text with the trained "
            "04_multihead_transformer model."
        )
    )

    parser.add_argument(
        "--prompt",
        default="artificial intelligence",
        help="Text used to start generation."
    )

    parser.add_argument(
        "--tokens",
        type=int,
        default=300,
        help="Number of new characters to generate."
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help=(
            "0 uses greedy decoding. "
            "Higher values increase randomness."
        )
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=0,
        help=(
            "If greater than zero, sample only "
            "from the top-k logits."
        )
    )

    args = parser.parse_args()

    tokenizer, model = (
        load_model()
    )

    result = generate(
        tokenizer=tokenizer,
        model=model,
        prompt=args.prompt,
        max_new_tokens=args.tokens,
        temperature=args.temperature,
        top_k=(
            args.top_k
            if args.top_k > 0
            else None
        )
    )

    print(
        "\nGenerated text:\n"
    )

    print(result)


if __name__ == "__main__":

    main()
