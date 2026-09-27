import subprocess
import sys

from config import (
    BASE_DIR,
    QLORA_OUTPUT_DIR,
)


def main():

    adapter_file = (
        QLORA_OUTPUT_DIR
        / "adapters.safetensors"
    )

    if not adapter_file.exists():

        raise FileNotFoundError(
            "QLoRA adapter not found.\n"
            "Run first:\n"
            "python run_training.py"
        )

    print(
        "Evaluating QLoRA on held-out test data..."
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "mlx_lm",
            "lora",
            "--config",
            "test_qlora.yaml",
        ],
        cwd=BASE_DIR,
        check=True,
    )


if __name__ == "__main__":

    main()
