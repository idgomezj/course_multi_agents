import os
from pathlib import Path

from mlx_lm import load

from config import MODEL_DIR


def get_weight_files(
    model_dir=MODEL_DIR
):

    model_dir = Path(
        model_dir
    )

    return sorted(
        model_dir.glob(
            "*.safetensors"
        )
    )


def is_complete_model(
    model_dir
):

    model_dir = Path(
        model_dir
    )

    if not (
        model_dir
        / "config.json"
    ).exists():

        return False

    weight_files = (
        get_weight_files(
            model_dir
        )
    )

    return bool(
        weight_files
    ) and all(
        path.stat().st_size > 0
        for path in weight_files
    )


def require_complete_model():

    if not is_complete_model(
        MODEL_DIR
    ):

        raise FileNotFoundError(
            "The BF16 base model is not ready.\n\n"
            f"Expected model directory:\n{MODEL_DIR}\n\n"
            "Run:\n"
            "python prepare_model.py"
        )

    return get_weight_files(
        MODEL_DIR
    )


def _load_from_directory(
    model_dir,
    adapter_path=None
):

    model_dir = Path(
        model_dir
    ).resolve()

    previous_directory = os.getcwd()

    try:

        # Loading from a relative path avoids the
        # square-bracket/glob issue discovered in
        # the earlier course chapters.
        os.chdir(
            model_dir
        )

        kwargs = {}

        if adapter_path is not None:

            adapter_path = Path(
                adapter_path
            ).resolve()

            kwargs[
                "adapter_path"
            ] = os.path.relpath(
                adapter_path,
                model_dir,
            )

        model, tokenizer = load(
            ".",
            **kwargs,
        )

    finally:

        os.chdir(
            previous_directory
        )

    return model, tokenizer


def load_base_model():

    require_complete_model()

    return _load_from_directory(
        MODEL_DIR
    )


def load_lora_model(
    adapter_path
):

    require_complete_model()

    return _load_from_directory(
        MODEL_DIR,
        adapter_path=adapter_path,
    )
