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

from tokenizer import CharacterTokenizer

from data import get_batch

from model import ContextLanguageModel


# --------------------------------------------------
# RANDOM SEEDS
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

tokenizer = CharacterTokenizer()


print(
    "Device:",
    DEVICE
)

print(
    "Vocabulary size:",
    tokenizer.vocab_size
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = ContextLanguageModel(
    tokenizer.vocab_size
)

model = model.to(
    DEVICE
)


# --------------------------------------------------
# PARAMETERS
# --------------------------------------------------

number_parameters = sum(
    parameter.numel()
    for parameter
    in model.parameters()
)


print(
    "Number of parameters:",
    f"{number_parameters:,}"
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
            / len(losses)
        )


    model.train()

    return results


# --------------------------------------------------
# TRAINING
# --------------------------------------------------

training_history = []

validation_history = []

steps_history = []


print(
    "\nStarting training...\n"
)


for step in range(
    MAX_STEPS + 1
):


    # ----------------------------------------------
    # EVALUATE
    # ----------------------------------------------

    if (
        step % EVAL_INTERVAL == 0
        or
        step == MAX_STEPS
    ):

        losses = estimate_loss()


        train_loss = (
            losses["train"]
        )

        val_loss = (
            losses["val"]
        )


        print(
            f"Step {step:5d} | "
            f"Train {train_loss:.4f} | "
            f"Validation {val_loss:.4f}"
        )


        steps_history.append(
            step
        )

        training_history.append(
            train_loss
        )

        validation_history.append(
            val_loss
        )


    # ----------------------------------------------
    # GET BATCH
    # ----------------------------------------------

    xb, yb = get_batch(
        "train"
    )


    # ----------------------------------------------
    # FORWARD
    # ----------------------------------------------

    logits, loss = model(
        xb,
        yb
    )


    # ----------------------------------------------
    # BACKPROPAGATION
    # ----------------------------------------------

    optimizer.zero_grad(
        set_to_none=True
    )

    loss.backward()


    # ----------------------------------------------
    # UPDATE PARAMETERS
    # ----------------------------------------------

    optimizer.step()


# --------------------------------------------------
# SAVE MODEL
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
    "\nCheckpoint saved:"
)

print(
    CHECKPOINT_FILE
)


# --------------------------------------------------
# TRAINING GRAPH
# --------------------------------------------------

plt.figure()

plt.plot(
    steps_history,
    training_history,
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
    "Context Language Model"
)

plt.legend()

plt.show()