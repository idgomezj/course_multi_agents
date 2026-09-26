from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MODELS_DIR = BASE_DIR / "models"

OUTPUTS_DIR = BASE_DIR / "outputs"


# --------------------------------------------------
# MODEL
# --------------------------------------------------
#
# This is an MLX 4-bit conversion of the original
# Qwen/Qwen3-0.6B-Base model.
#
# We intentionally use the BASE model in this lab.
# It is pretrained, but it is not primarily tuned to
# behave like a chat assistant. That difference is
# educational and will matter when we fine-tune it.
# --------------------------------------------------

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


# --------------------------------------------------
# DOCUMENTED SOURCE MODEL FACTS
# --------------------------------------------------

SOURCE_PARAMETER_COUNT = 600_000_000

SOURCE_NON_EMBEDDING_PARAMETERS = 440_000_000

SOURCE_CONTEXT_LENGTH = 32_768


# --------------------------------------------------
# GENERATION DEFAULTS
# --------------------------------------------------

DEFAULT_MAX_TOKENS = 200

DEFAULT_TEMPERATURE = 0.7

DEFAULT_TOP_P = 0.95

DEFAULT_TOP_K = 20


# --------------------------------------------------
# BASELINE
# --------------------------------------------------

BASELINE_PROMPTS_FILE = (
    BASE_DIR
    / "baseline_prompts.json"
)

BASELINE_OUTPUT_FILE = (
    OUTPUTS_DIR
    / "baseline_results.json"
)
