import json
import subprocess
import sys

from config import (
    BASE_DIR,
    QLORA_OUTPUT_DIR,
    TRAIN_FILE,
    VALID_FILE,
    TEST_FILE,
)

from model_files import require_complete_model


def validate_jsonl(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1
        ):

            if not line.strip():

                continue

            record = json.loads(
                line
            )

            if (
                "prompt" not in record
                or
                "completion" not in record
            ):

                raise ValueError(
                    f"{path.name}:{line_number} "
                    "must contain prompt and "
                    "completion."
                )


def count_rows(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return sum(
            1
            for line in file
            if line.strip()
        )


def main():

    require_complete_model()

    for path in [
        TRAIN_FILE,
        VALID_FILE,
        TEST_FILE,
    ]:

        validate_jsonl(path)

    print(
        "DATASET"
    )

    print(
        "-------"
    )

    print(
        "Train:",
        count_rows(TRAIN_FILE)
    )

    print(
        "Validation:",
        count_rows(VALID_FILE)
    )

    print(
        "Test:",
        count_rows(TEST_FILE)
    )

    print(
        "\nBase representation:"
    )

    print(
        "4-bit quantized"
    )

    print(
        "\nAdapter output:"
    )

    print(
        QLORA_OUTPUT_DIR
    )

    print(
        "\nStarting QLoRA..."
    )

    print(
        "MLX-LM detects QLoRA automatically "
        "because the base model is quantized."
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "mlx_lm",
            "lora",
            "--config",
            "qlora_finetune.yaml",
        ],
        cwd=BASE_DIR,
        check=True,
    )

    print(
        "\nQLoRA training finished."
    )

    print(
        "\nNext:"
    )

    print(
        "python test_qlora.py"
    )

    print(
        "python compare_before_after.py"
    )


if __name__ == "__main__":

    main()
