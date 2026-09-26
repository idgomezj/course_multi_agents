import random

import matplotlib.pyplot as plt
import numpy as np
import torch

from config import (
    BASE_DIR,
    DEVICE,
    RANDOM_SEED,
    LEARNING_RATE,
    WEIGHT_DECAY,
    MAX_STEPS,
    EVAL_INTERVAL,
    EVAL_BATCHES,
    GRAD_CLIP,
    CHECKPOINT_DIR,
    CHECKPOINT_FILE,
    TRAINING_PLOT_FILE,
    BLOCK_SIZE,
    BATCH_SIZE,
    N_EMBD,
    N_HEADS,
    N_LAYERS,
    DROPOUT,
    FF_MULTIPLIER,
)

from tokenizer import CharacterTokenizer

from data import get_batch

from model import MiniGPT


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
# TOKENIZER AND MODEL
# --------------------------------------------------

tokenizer = (
    CharacterTokenizer()
)

model = MiniGPT(
    tokenizer.vocab_size
)

model = model.to(
    DEVICE
)


parameter_count = sum(
    parameter.numel()
    for parameter
    in model.parameters()
)


print(
    "Device:",
    DEVICE
)

print(
    "Vocabulary size:",
    tokenizer.vocab_size
)

print(
    "Parameters:",
    f"{parameter_count:,}"
)

print(
    "Transformer blocks:",
    N_LAYERS
)

print(
    "Attention heads per block:",
    N_HEADS
)

print(
    "Embedding dimension:",
    N_EMBD
)

print(
    "Context length:",
    BLOCK_SIZE
)


# --------------------------------------------------
# OPTIMIZER
# --------------------------------------------------

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY
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
# TRAINING
# --------------------------------------------------

steps_history = []

train_history = []

validation_history = []


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

    if step == MAX_STEPS:

        break

    xb, yb = get_batch(
        "train"
    )

    _, loss = model(
        xb,
        yb
    )

    optimizer.zero_grad(
        set_to_none=True
    )

    loss.backward()

    torch.nn.utils.clip_grad_norm_(
        model.parameters(),
        max_norm=GRAD_CLIP
    )

    optimizer.step()


# --------------------------------------------------
# SAVE CHECKPOINT
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

        "parameter_count":
            parameter_count,

        "architecture": {
            "block_size":
                BLOCK_SIZE,
            "batch_size":
                BATCH_SIZE,
            "n_embd":
                N_EMBD,
            "n_heads":
                N_HEADS,
            "n_layers":
                N_LAYERS,
            "dropout":
                DROPOUT,
            "ff_multiplier":
                FF_MULTIPLIER,
        },
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
# SAVE TRAINING GRAPH
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
    "Cross-Entropy Loss"
)

plt.title(
    "04 Multi-Head Transformer Training"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    TRAINING_PLOT_FILE,
    dpi=150
)

plt.close()


print(
    "\nTraining graph saved:"
)

print(
    TRAINING_PLOT_FILE
)
