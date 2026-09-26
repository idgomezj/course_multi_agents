from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MODELS_DIR = BASE_DIR / "models"

DATA_DIR = BASE_DIR / "data"

OUTPUTS_DIR = BASE_DIR / "outputs"


# Same BF16 base family used by chapter 06.
MODEL_REPO = "mlx-community/Qwen3-0.6B-Base"

SOURCE_MODEL_REPO = "Qwen/Qwen3-0.6B-Base"

MODEL_DIR = (
    MODELS_DIR
    / "qwen3-0.6b-base-bf16"
)


# Optional sibling model locations.
CHAPTER_06_MODEL_DIR = (
    BASE_DIR.parent
    / "06_full_finetuning_workbench"
    / "models"
    / "qwen3-0.6b-base-bf16"
)

LEGACY_CHAPTER_06_MODEL_DIR = (
    BASE_DIR.parent
    / "full_finetuning_workbench"
    / "models"
    / "qwen3-0.6b-base-bf16"
)


TRAIN_FILE = DATA_DIR / "train.jsonl"

VALID_FILE = DATA_DIR / "valid.jsonl"

TEST_FILE = DATA_DIR / "test.jsonl"

EVAL_PROMPTS_FILE = (
    BASE_DIR
    / "evaluation_prompts.json"
)


LORA_OUTPUT_DIR = (
    OUTPUTS_DIR
    / "lora_adapter"
)

COMPARISON_FILE = (
    OUTPUTS_DIR
    / "before_after_lora.json"
)

METHOD_COMPARISON_FILE = (
    OUTPUTS_DIR
    / "06_full_vs_07_lora.json"
)


LORA_RANK = 8

LORA_SCALE = 20.0

LORA_DROPOUT = 0.0

LORA_KEYS = [
    "self_attn.q_proj",
    "self_attn.v_proj",
]

NUM_LAYERS = -1

BATCH_SIZE = 1

GRAD_ACCUMULATION_STEPS = 4

TRAINING_ITERATIONS = 80

LEARNING_RATE = 1e-5

MAX_SEQUENCE_LENGTH = 256

RANDOM_SEED = 42
