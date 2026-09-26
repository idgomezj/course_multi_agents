import subprocess
import sys

from config import (
    BASE_DIR,
    FULL_WEIGHTS_DIR,
)


def main():

    adapter_file = (
        FULL_WEIGHTS_DIR
        / "adapters.safetensors"
    )

    if not adapter_file.exists():

        raise FileNotFoundError(
            "Fine-tuned weights not found. "
            "Run python run_training.py first."
        )

    print(
        "Exporting a standalone fine-tuned model..."
    )

    command = [
        sys.executable,
        "-m",
        "mlx_lm",
        "fuse",
        "--model",
        "models/qwen3-0.6b-base-bf16",
        "--adapter-path",
        "outputs/full_weights",
        "--save-path",
        "outputs/fused_model",
    ]

    subprocess.run(
        command,
        cwd=BASE_DIR,
        check=True,
    )

    print(
        "\nStandalone model saved to:"
    )

    print(
        BASE_DIR
        / "outputs"
        / "fused_model"
    )


if __name__ == "__main__":

    main()
