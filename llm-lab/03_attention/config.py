from pathlib import Path

import torch


BASE_DIR = Path(__file__).resolve().parent

TRAINING_FILE = BASE_DIR / "training.txt"

CHECKPOINT_DIR = BASE_DIR / "checkpoints"

CHECKPOINT_FILE = (
    CHECKPOINT_DIR
    / "attention_model.pt"
)


# --------------------------------------------------
# DEVICE
# --------------------------------------------------

DEVICE = (
    "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)


# --------------------------------------------------
# DATA
# --------------------------------------------------

TRAIN_SPLIT = 0.90

BLOCK_SIZE = 32

BATCH_SIZE = 32


# --------------------------------------------------
# MODEL
# --------------------------------------------------

N_EMBD = 64


# --------------------------------------------------
# TRAINING
# --------------------------------------------------

LEARNING_RATE = 0.003

MAX_STEPS = 5000

EVAL_INTERVAL = 250

EVAL_BATCHES = 50

RANDOM_SEED = 42