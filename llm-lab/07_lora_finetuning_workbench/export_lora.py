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
            "LoRA adapter not found. "
            "Run python run_training.py first."
        )

    print(
        "Fusing LoRA into a standalone model..."
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "mlx_lm",
            "fuse",
            "--model",
            "models/qwen3-0.6b-base-bf16",
            "--adapter-path",
            "outputs/lora_adapter",
            "--save-path",
            "outputs/fused_lora_model",
        ],
        cwd=BASE_DIR,
        check=True,
    )

    print(
        "\nSaved:"
    )

    print(
        BASE_DIR
        / "outputs"
        / "fused_lora_model"
    )


if __name__ == "__main__":

    main()
