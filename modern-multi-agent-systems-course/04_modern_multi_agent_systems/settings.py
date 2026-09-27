import os
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def get_model_name(
    environment_variable: str = "LLM_MODEL",
) -> str:
    model = os.getenv(environment_variable)

    if model:
        return model

    fallback = os.getenv("LLM_MODEL")
    if fallback:
        return fallback

    raise RuntimeError(
        "Set LLM_MODEL in modern-multi-agent-systems-course/.env."
    )
