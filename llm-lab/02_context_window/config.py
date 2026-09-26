from pathlib import Path
import torch


BASE_DIR = Path(__file__).resolve().parent

TRAINING_FILE = BASE_DIR / "training.txt"

CHECKPOINT_DIR = BASE_DIR / "checkpoints"

CHECKPOINT_FILE = CHECKPOINT_DIR / "context_model.pt"


# --------------------------------------------------
# DEVICE
# --------------------------------------------------

DEVICE = (
    "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

BLOCK_SIZE = 16

N_EMBD = 32

HIDDEN_SIZE = 128


# --------------------------------------------------
# TRAINING
# --------------------------------------------------

BATCH_SIZE = 32

LEARNING_RATE = 0.003

MAX_STEPS = 5000

EVAL_INTERVAL = 250

EVAL_BATCHES = 50

TRAIN_SPLIT = 0.90

RANDOM_SEED = 42