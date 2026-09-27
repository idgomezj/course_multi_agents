import os
from pathlib import Path

from dotenv import load_dotenv


TRACK_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    TRACK_DIR / ".env"
)


def get_model_name():

    model = os.getenv(
        "LLM_MODEL"
    )

    if not model:

        raise RuntimeError(
            "LLM_MODEL is not configured.\n"
            "Copy pydantic-ai-lab/.env.example "
            "to pydantic-ai-lab/.env and set a "
            "model string your provider supports."
        )

    return model
