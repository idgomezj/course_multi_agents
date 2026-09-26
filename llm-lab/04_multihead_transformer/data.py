import torch

from config import (
    TRAINING_FILE,
    TRAIN_SPLIT,
    BLOCK_SIZE,
    BATCH_SIZE,
    DEVICE,
)

from tokenizer import CharacterTokenizer


tokenizer = CharacterTokenizer()


# --------------------------------------------------
# LOAD AND TOKENIZE DATA
# --------------------------------------------------

with open(
    TRAINING_FILE,
    "r",
    encoding="utf-8"
) as file:

    text = file.read()


data = torch.tensor(
    tokenizer.encode(text),
    dtype=torch.long
)


# --------------------------------------------------
# TRAIN / VALIDATION SPLIT
# --------------------------------------------------

split_index = int(
    len(data)
    * TRAIN_SPLIT
)

train_data = data[:split_index]

val_data = data[split_index:]


# --------------------------------------------------
# BATCHES
# --------------------------------------------------

def get_batch(split):

    if split not in {
        "train",
        "val"
    }:

        raise ValueError(
            "split must be 'train' or 'val'"
        )

    source = (
        train_data
        if split == "train"
        else val_data
    )

    if len(source) <= BLOCK_SIZE:

        raise ValueError(
            f"{split} split has {len(source)} tokens, "
            f"but BLOCK_SIZE is {BLOCK_SIZE}."
        )

    positions = torch.randint(
        0,
        len(source) - BLOCK_SIZE,
        (BATCH_SIZE,)
    )

    x = torch.stack([
        source[
            position:
            position + BLOCK_SIZE
        ]
        for position in positions
    ])

    y = torch.stack([
        source[
            position + 1:
            position + BLOCK_SIZE + 1
        ]
        for position in positions
    ])

    return (
        x.to(DEVICE),
        y.to(DEVICE)
    )


# --------------------------------------------------
# MANUAL INSPECTION
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "Device:",
        DEVICE
    )

    print(
        "Vocabulary size:",
        tokenizer.vocab_size
    )

    print(
        "Total tokens:",
        len(data)
    )

    print(
        "Training tokens:",
        len(train_data)
    )

    print(
        "Validation tokens:",
        len(val_data)
    )

    xb, yb = get_batch(
        "train"
    )

    print(
        "\nX shape:",
        xb.shape
    )

    print(
        "Y shape:",
        yb.shape
    )

    print(
        "\nFirst two examples:\n"
    )

    for index in range(2):

        print(
            "INPUT :",
            repr(
                tokenizer.decode(
                    xb[index].tolist()
                )
            )
        )

        print(
            "TARGET:",
            repr(
                tokenizer.decode(
                    yb[index].tolist()
                )
            )
        )

        print()
