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
            "Fine-tuned weights not found.\n"
            "Run first:\n"
            "python run_training.py"
        )

    print(
        "Evaluating the held-out test set..."
    )

    command = [
        sys.executable,
        "-m",
        "mlx_lm",
        "lora",
        "--config",
        "test_finetuned.yaml",
    ]

    subprocess.run(
        command,
        cwd=BASE_DIR,
        check=True,
    )


if __name__ == "__main__":

    main()
