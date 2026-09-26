import json
import subprocess
import sys

from config import (
    BASE_DIR,
    TRAIN_FILE,
    VALID_FILE,
    TEST_FILE,
    LORA_OUTPUT_DIR,
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
        "\nAdapter output:"
    )

    print(
        LORA_OUTPUT_DIR
    )

    print(
        "\nStarting LoRA fine-tuning..."
    )

    command = [
        sys.executable,
        "-m",
        "mlx_lm.lora",
        "--config",
        "lora_finetune.yaml",
    ]

    subprocess.run(
        command,
        cwd=BASE_DIR,
        check=True,
    )

    print(
        "\nLoRA training finished."
    )

    print(
        "\nNext:"
    )

    print(
        "python test_lora.py"
    )

    print(
        "python compare_before_after.py"
    )


if __name__ == "__main__":

    main()
