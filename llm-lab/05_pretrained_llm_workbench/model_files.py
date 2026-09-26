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
            "Download the model first with:\n"
            "python download_model.py"
        )

    weight_files = (
        get_weight_files()
    )

    if not weight_files:

        raise FileNotFoundError(
            "The model directory exists, but no "
            ".safetensors weights were found.\n\n"
            f"Model directory:\n{MODEL_DIR}\n\n"
            "Resume the download with:\n"
            "python download_model.py\n\n"
            "If it still fails, force a clean "
            "re-download with:\n"
            "python download_model.py --force"
        )

    empty_files = [
        path
        for path in weight_files
        if path.stat().st_size == 0
    ]

    if empty_files:

        raise FileNotFoundError(
            "One or more model weight files are "
            "empty. Re-download with:\n"
            "python download_model.py --force"
        )

    return weight_files


def load_local_mlx_model():

    require_complete_model()

    previous_directory = os.getcwd()

    try:

        # MLX-LM currently discovers model weights
        # with glob.glob("model*.safetensors").
        #
        # Square brackets in an absolute parent
        # directory are interpreted by glob as a
        # pattern. The course repository may live
        # in a path such as:
        #
        #   curso [Sistemas Multiagentes ...]
        #
        # Loading from "." while temporarily inside
        # MODEL_DIR avoids passing those brackets to
        # glob and still loads the exact same files.

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
