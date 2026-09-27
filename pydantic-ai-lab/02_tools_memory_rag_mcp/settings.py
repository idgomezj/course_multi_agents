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
            "Set LLM_MODEL in pydantic-ai-lab/.env "
            "before running the LLM examples."
        )

    return model
