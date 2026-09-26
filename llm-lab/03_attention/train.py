import random

import numpy as np

import torch

import matplotlib.pyplot as plt


from config import (
    DEVICE,
    RANDOM_SEED,
    LEARNING_RATE,
    MAX_STEPS,
    EVAL_INTERVAL,
    EVAL_BATCHES,
    CHECKPOINT_DIR,
    CHECKPOINT_FILE,
)


from tokenizer import (
    CharacterTokenizer
)

from data import (
    get_batch
)

from model import (
    AttentionLanguageModel
)


# --------------------------------------------------
# REPRODUCIBILITY
# --------------------------------------------------

random.seed(
    RANDOM_SEED
)

np.random.seed(
    RANDOM_SEED
)

torch.manual_seed(
    RANDOM_SEED
)


# --------------------------------------------------
# TOKENIZER
# --------------------------------------------------

tokenizer = (
    CharacterTokenizer()
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = (
    AttentionLanguageModel(
        tokenizer.vocab_size
    )
)

model = model.to(
    DEVICE
)


print(
    "Device:",
    DEVICE
)

print(
    "Vocabulary size:",
    tokenizer.vocab_size
)


parameter_count = sum(

    parameter.numel()

    for parameter
    in model.parameters()
)


print(
    "Parameters:",
    f"{parameter_count:,}"
)


# --------------------------------------------------
# OPTIMIZER
# --------------------------------------------------

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE
)


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

@torch.no_grad()
def estimate_loss():

    model.eval()

    results = {}


    for split in [
        "train",
        "val"
    ]:

        losses = []


        for _ in range(
            EVAL_BATCHES
        ):

            xb, yb = get_batch(
                split
            )


            _, loss = model(
                xb,
                yb
            )


            losses.append(
                loss.item()
            )


        results[split] = (

            sum(losses)
            /
            len(losses)
        )


    model.train()

    return results


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

steps_history = []

train_history = []

validation_history = []


# --------------------------------------------------
# TRAIN
# --------------------------------------------------

print(
    "\nTraining...\n"
)


for step in range(
    MAX_STEPS + 1
):


    if (
        step % EVAL_INTERVAL == 0
        or
        step == MAX_STEPS
    ):

        losses = (
            estimate_loss()
        )


        print(
            f"Step {step:5d} | "
            f"Train {losses['train']:.4f} | "
            f"Validation {losses['val']:.4f}"
        )


        steps_history.append(
            step
        )

        train_history.append(
            losses["train"]
        )

        validation_history.append(
            losses["val"]
        )


    xb, yb = get_batch(
        "train"
    )


    logits, loss = model(
        xb,
        yb
    )


    optimizer.zero_grad(
        set_to_none=True
    )


    loss.backward()


    optimizer.step()


# --------------------------------------------------
# SAVE
# --------------------------------------------------

CHECKPOINT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


torch.save(

    {

        "model_state_dict":
            model.state_dict(),

        "vocab_size":
            tokenizer.vocab_size,

        "characters":
            tokenizer.characters,

    },

    CHECKPOINT_FILE
)


print(
    "\nSaved:",
    CHECKPOINT_FILE
)


# --------------------------------------------------
# GRAPH
# --------------------------------------------------

plt.figure()

plt.plot(
    steps_history,
    train_history,
    label="Training"
)

plt.plot(
    steps_history,
    validation_history,
    label="Validation"
)

plt.xlabel(
    "Training Step"
)

plt.ylabel(
    "Loss"
)

plt.title(
    "Single-Head Self-Attention"
)

plt.legend()

plt.show()