import torch
import torch.nn.functional as F

from config import (
    DEVICE,
    BLOCK_SIZE,
    CHECKPOINT_FILE,
)

from tokenizer import CharacterTokenizer

from model import ContextLanguageModel


# --------------------------------------------------
# TOKENIZER
# --------------------------------------------------

tokenizer = CharacterTokenizer()


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = ContextLanguageModel(
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


# --------------------------------------------------
# GENERATION
# --------------------------------------------------

@torch.no_grad()
def generate(
    prompt,
    max_new_tokens=300,
    temperature=1.0
):

    generated = tokenizer.encode(
        prompt
    )


    space_token = (
        tokenizer.stoi[" "]
    )


    for _ in range(
        max_new_tokens
    ):


        # ------------------------------------------
        # KEEP LAST BLOCK_SIZE TOKENS
        # ------------------------------------------

        context = generated[
            -BLOCK_SIZE:
        ]


        # ------------------------------------------
        # LEFT PAD IF CONTEXT IS TOO SHORT
        # ------------------------------------------

        if (
            len(context)
            < BLOCK_SIZE
        ):

            missing = (
                BLOCK_SIZE
                - len(context)
            )

            context = (
                [space_token] * missing
                +
                context
            )


        x = torch.tensor(
            [context],
            dtype=torch.long,
            device=DEVICE
        )


        # ------------------------------------------
        # MODEL PREDICTION
        # ------------------------------------------

        logits, _ = model(x)


        logits = (
            logits[0]
            /
            temperature
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


# --------------------------------------------------
# RUN
# --------------------------------------------------

prompt = (
    "artificial intel"
)


text = generate(
    prompt,
    max_new_tokens=300,
    temperature=0.8
)


print(
    "\nGenerated text:\n"
)

print(text)