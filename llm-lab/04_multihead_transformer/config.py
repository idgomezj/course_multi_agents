from pathlib import Path

import torch


BASE_DIR = Path(__file__).resolve().parent

TRAINING_FILE = BASE_DIR / "training.txt"

CHECKPOINT_DIR = BASE_DIR / "checkpoints"

CHECKPOINT_FILE = CHECKPOINT_DIR / "mini_gpt.pt"

TRAINING_PLOT_FILE = BASE_DIR / "training_loss.png"


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

BLOCK_SIZE = 64

BATCH_SIZE = 32


# --------------------------------------------------
# MODEL
# --------------------------------------------------

N_EMBD = 96

N_HEADS = 4

N_LAYERS = 4

DROPOUT = 0.10

FF_MULTIPLIER = 4


# --------------------------------------------------
# TRAINING
# --------------------------------------------------

LEARNING_RATE = 3e-4

WEIGHT_DECAY = 0.01

MAX_STEPS = 6000

EVAL_INTERVAL = 250

EVAL_BATCHES = 50

GRAD_CLIP = 1.0

RANDOM_SEED = 42
