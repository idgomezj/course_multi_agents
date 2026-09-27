import os
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def get_model_name() -> str:
    model = os.getenv("LLM_MODEL")
    if not model:
        raise RuntimeError(
            "LLM_MODEL is not configured. Copy .env.example to .env "
            "in modern-multi-agent-systems-course and set a model string."
        )
    return model
