import os
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def get_model_name() -> str:
    model = os.getenv("LLM_MODEL")
    if not model:
        raise RuntimeError(
            "Set LLM_MODEL in modern-multi-agent-systems-course/.env."
        )
    return model
