import torch

from config import (
    TRAINING_FILE,
    BLOCK_SIZE,
    BATCH_SIZE,
    TRAIN_SPLIT,
    DEVICE,
)

from tokenizer import CharacterTokenizer


tokenizer = CharacterTokenizer()


# --------------------------------------------------
# LOAD TEXT
# --------------------------------------------------

with open(
    TRAINING_FILE,
    "r",
    encoding="utf-8"
) as f:

    text = f.read()


# --------------------------------------------------
# ENCODE TEXT
# --------------------------------------------------

data = torch.tensor(
    tokenizer.encode(text),
    dtype=torch.long
)


# --------------------------------------------------
# TRAIN / VALIDATION SPLIT
# --------------------------------------------------

split_index = int(
    len(data) * TRAIN_SPLIT
)

train_data = data[:split_index]

val_data = data[split_index:]


# --------------------------------------------------
# CREATE BATCH
# --------------------------------------------------

def get_batch(split):

    source = (
        train_data
        if split == "train"
        else val_data
    )

    max_start = (
        len(source)
        - BLOCK_SIZE
        - 1
    )

    positions = torch.randint(
        0,
        max_start,
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
            position + BLOCK_SIZE
        ]

        for position in positions
    ])


    return (
        x.to(DEVICE),
        y.to(DEVICE)
    )

if __name__ == "__main__":

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


    xb, yb = get_batch("train")


    print(
        "\nX shape:",
        xb.shape
    )

    print(
        "Y shape:",
        yb.shape
    )


    print(
        "\nFirst batch examples:\n"
    )


    for i in range(5):

        context = tokenizer.decode(
            xb[i].tolist()
        )

        target = tokenizer.decode(
            [yb[i].item()]
        )

        print(
            repr(context),
            "->",
            repr(target)
        )