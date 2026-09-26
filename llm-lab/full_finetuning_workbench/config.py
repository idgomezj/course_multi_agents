from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MODELS_DIR = BASE_DIR / "models"

DATA_DIR = BASE_DIR / "data"

OUTPUTS_DIR = BASE_DIR / "outputs"


# --------------------------------------------------
# MODEL
# --------------------------------------------------
#
# Non-quantized BF16 MLX conversion of the same
# Qwen3-0.6B-Base family used in the previous lab.
#
# We deliberately do NOT use the 4-bit model here:
# this lab teaches full-weight fine-tuning before
# introducing LoRA and QLoRA.
# --------------------------------------------------

MODEL_REPO = (
    "mlx-community/Qwen3-0.6B-Base"
)

SOURCE_MODEL_REPO = (
    "Qwen/Qwen3-0.6B-Base"
)

MODEL_DIR = (
    MODELS_DIR
    / "qwen3-0.6b-base-bf16"
)


# --------------------------------------------------
# TRAINING OUTPUT
# --------------------------------------------------

FULL_WEIGHTS_DIR = (
    OUTPUTS_DIR
    / "full_weights"
)

COMPARISON_FILE = (
    OUTPUTS_DIR
    / "before_after.json"
)


# --------------------------------------------------
# DATA
# --------------------------------------------------

TRAIN_FILE = DATA_DIR / "train.jsonl"

VALID_FILE = DATA_DIR / "valid.jsonl"

TEST_FILE = DATA_DIR / "test.jsonl"

EVAL_PROMPTS_FILE = (
    BASE_DIR
    / "evaluation_prompts.json"
)


# --------------------------------------------------
# TRAINING CONFIGURATION
# --------------------------------------------------

TRAINING_CONFIG_FILE = (
    BASE_DIR
    / "full_finetune.yaml"
)

MAX_SEQUENCE_LENGTH = 256

TRAINING_ITERATIONS = 80

LEARNING_RATE = 5e-6

BATCH_SIZE = 1

GRAD_ACCUMULATION_STEPS = 4

RANDOM_SEED = 42
