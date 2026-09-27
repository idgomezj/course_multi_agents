from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MODELS_DIR = BASE_DIR / "models"

DATA_DIR = BASE_DIR / "data"

OUTPUTS_DIR = BASE_DIR / "outputs"


# Quantized base. MLX-LM automatically performs
# QLoRA when LoRA training points at a quantized
# model.
MODEL_REPO = (
    "mlx-community/Qwen3-0.6B-Base-4bit"
)

SOURCE_MODEL_REPO = (
    "Qwen/Qwen3-0.6B-Base"
)

MODEL_DIR = (
    MODELS_DIR
    / "qwen3-0.6b-base-4bit"
)


# Reuse the model already downloaded in chapter 05.
CHAPTER_05_MODEL_DIR = (
    BASE_DIR.parent
    / "05_pretrained_llm_workbench"
    / "models"
    / "qwen3-0.6b-base-4bit"
)


TRAIN_FILE = DATA_DIR / "train.jsonl"

VALID_FILE = DATA_DIR / "valid.jsonl"

TEST_FILE = DATA_DIR / "test.jsonl"

EVAL_PROMPTS_FILE = (
    BASE_DIR
    / "evaluation_prompts.json"
)


QLORA_OUTPUT_DIR = (
    OUTPUTS_DIR
    / "qlora_adapter"
)

COMPARISON_FILE = (
    OUTPUTS_DIR
    / "before_after_qlora.json"
)

THREE_WAY_COMPARISON_FILE = (
    OUTPUTS_DIR
    / "06_full_vs_07_lora_vs_08_qlora.json"
)


# Keep LoRA settings aligned with chapter 07.
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
