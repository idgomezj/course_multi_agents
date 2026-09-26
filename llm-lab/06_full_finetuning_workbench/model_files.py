import os

from mlx_lm import load

from config import MODEL_DIR


def get_weight_files():

    return sorted(
        MODEL_DIR.glob(
            "*.safetensors"
        )
    )


def require_complete_model():

    config_file = (
        MODEL_DIR
        / "config.json"
    )

    if not config_file.exists():

        raise FileNotFoundError(
            f"Model configuration not found at:\n"
            f"{config_file}\n\n"
            "Download the BF16 model first with:\n"
            "python download_model.py"
        )

    weight_files = (
        get_weight_files()
    )

    if not weight_files:

        raise FileNotFoundError(
            "No .safetensors model weights were "
            "found. Run:\n"
            "python download_model.py"
        )

    empty_files = [
        path
        for path in weight_files
        if path.stat().st_size == 0
    ]

    if empty_files:

        raise FileNotFoundError(
            "One or more weight files are empty. "
            "Run:\n"
            "python download_model.py --force"
        )

    return weight_files


def load_base_model():

    require_complete_model()

    previous_directory = os.getcwd()

    try:

        # The user's course path contains square
        # brackets. MLX-LM may use glob-based local
        # weight discovery, where brackets have
        # special pattern meaning. Loading from "."
        # inside MODEL_DIR avoids that problem.

        os.chdir(
            MODEL_DIR
        )

        model, tokenizer = load(
            "."
        )

    finally:

        os.chdir(
            previous_directory
        )

    return (
        model,
        tokenizer
    )


def load_finetuned_model(
    adapter_path
):

    require_complete_model()

    adapter_path = (
        adapter_path.resolve()
    )

    previous_directory = os.getcwd()

    try:

        os.chdir(
            MODEL_DIR
        )

        relative_adapter_path = os.path.relpath(
            adapter_path,
            MODEL_DIR
        )

        model, tokenizer = load(
            ".",
            adapter_path=relative_adapter_path
        )

    finally:

        os.chdir(
            previous_directory
        )

    return (
        model,
        tokenizer
    )
