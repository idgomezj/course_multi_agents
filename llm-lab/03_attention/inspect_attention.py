import torch


from config import (
    DEVICE,
    CHECKPOINT_FILE,
)


from tokenizer import (
    CharacterTokenizer
)


from model import (
    AttentionLanguageModel
)


# --------------------------------------------------
# LOAD
# --------------------------------------------------

tokenizer = (
    CharacterTokenizer()
)


model = (
    AttentionLanguageModel(
        tokenizer.vocab_size
    )
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


# --------------------------------------------------
# TEXT
# --------------------------------------------------

text = (
    "language model"
)


tokens = (
    tokenizer.encode(
        text
    )
)


x = torch.tensor(
    [tokens],
    dtype=torch.long,
    device=DEVICE
)


# --------------------------------------------------
# ATTENTION
# --------------------------------------------------

with torch.no_grad():

    logits, loss, attention = (
        model(
            x,
            return_attention=True
        )
    )


attention = (
    attention[0]
    .cpu()
)


# --------------------------------------------------
# PRINT MATRIX
# --------------------------------------------------

print(
    "\nText:",
    repr(text)
)

print(
    "\nAttention Matrix:\n"
)


print(
    "     ",
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
            attention[
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