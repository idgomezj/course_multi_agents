import subprocess
import sys

from config import (
    BASE_DIR,
    LORA_OUTPUT_DIR,
)


def main():

    adapter_file = (
        LORA_OUTPUT_DIR
        / "adapters.safetensors"
    )

    if not adapter_file.exists():

        raise FileNotFoundError(
            "LoRA adapter not found.\n"
            "Run first:\n"
            "python run_training.py"
        )

    print(
        "Evaluating LoRA on held-out test data..."
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "mlx_lm",
        "lora",
            "--config",
            "test_lora.yaml",
        ],
        cwd=BASE_DIR,
        check=True,
    )


if __name__ == "__main__":

    main()
