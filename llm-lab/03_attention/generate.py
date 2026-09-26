import torch

import torch.nn.functional as F


from config import (
    DEVICE,
    BLOCK_SIZE,
    CHECKPOINT_FILE,
)


from tokenizer import (
    CharacterTokenizer
)


from model import (
    AttentionLanguageModel
)


# --------------------------------------------------
# TOKENIZER
# --------------------------------------------------

tokenizer = (
    CharacterTokenizer()
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

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
# GENERATE
# --------------------------------------------------

@torch.no_grad()
def generate(
    prompt,
    max_new_tokens=300,
    temperature=0.8
):


    generated = (
        tokenizer.encode(
            prompt
        )
    )


    for _ in range(
        max_new_tokens
    ):


        context = (
            generated[
                -BLOCK_SIZE:
            ]
        )


        x = torch.tensor(
            [context],
            dtype=torch.long,
            device=DEVICE
        )


        logits, _ = (
            model(x)
        )


        # Only prediction
        # from final position

        logits = (
            logits[
                0,
                -1,
                :
            ]
        )


        logits = (
            logits
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
    "artificial intelligence"
)


result = generate(
    prompt,
    max_new_tokens=300,
    temperature=0.7
)


print(
    "\nGenerated text:\n"
)

print(result)