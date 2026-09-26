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
# LOAD DATA
# --------------------------------------------------

with open(
    TRAINING_FILE,
    "r",
    encoding="utf-8"
) as file:

    text = file.read()


# --------------------------------------------------
# TOKENIZE
# --------------------------------------------------

data = torch.tensor(
    tokenizer.encode(text),
    dtype=torch.long
)


# --------------------------------------------------
# TRAIN / VALIDATION
# --------------------------------------------------

split_index = int(
    len(data)
    * TRAIN_SPLIT
)


train_data = (
    data[:split_index]
)

val_data = (
    data[split_index:]
)


# --------------------------------------------------
# BATCH
# --------------------------------------------------

def get_batch(split):

    source = (
        train_data
        if split == "train"
        else val_data
    )


    positions = torch.randint(

        0,

        len(source)
        - BLOCK_SIZE
        - 1,

        (BATCH_SIZE,)
    )


    x = torch.stack([

        source[
            position:
            position + BLOCK_SIZE
        ]

        for position
        in positions
    ])


    y = torch.stack([

        source[
            position + 1:
            position + BLOCK_SIZE + 1
        ]

        for position
        in positions
    ])


    return (
        x.to(DEVICE),
        y.to(DEVICE)
    )


# --------------------------------------------------
# TEST
# --------------------------------------------------

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
        "\nExamples:\n"
    )


    for i in range(3):

        input_text = (
            tokenizer.decode(
                xb[i].tolist()
            )
        )

        target_text = (
            tokenizer.decode(
                yb[i].tolist()
            )
        )


        print(
            "INPUT :",
            repr(input_text)
        )

        print(
            "TARGET:",
            repr(target_text)
        )

        print()