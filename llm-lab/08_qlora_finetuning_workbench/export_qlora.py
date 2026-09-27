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
            "QLoRA adapter not found. "
            "Run python run_training.py first."
        )

    print(
        "Fusing QLoRA into a quantized "
        "standalone model..."
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "mlx_lm",
            "fuse",
            "--model",
            "models/qwen3-0.6b-base-4bit",
            "--adapter-path",
            "outputs/qlora_adapter",
            "--save-path",
            "outputs/fused_qlora_model",
        ],
        cwd=BASE_DIR,
        check=True,
    )

    print(
        "\nSaved quantized fused model:"
    )

    print(
        BASE_DIR
        / "outputs"
        / "fused_qlora_model"
    )

    print(
        "\nOptional:"
    )

    print(
        "MLX-LM fuse also supports "
        "--dequantize if you intentionally want "
        "a dequantized fused export."
    )


if __name__ == "__main__":

    main()
