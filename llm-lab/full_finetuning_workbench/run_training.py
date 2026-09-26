import json
import subprocess
import sys

from config import (
    BASE_DIR,
    DATA_DIR,
    FULL_WEIGHTS_DIR,
    TRAIN_FILE,
    VALID_FILE,
    TEST_FILE,
    TRAINING_CONFIG_FILE,
)

from model_files import (
    require_complete_model,
)


def count_rows(
    path
):

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


def validate_jsonl(
    path
):

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


def main():

    require_complete_model()

    for path in [
        TRAIN_FILE,
        VALID_FILE,
        TEST_FILE,
    ]:

        validate_jsonl(
            path
        )

    print(
        "DATASET"
    )

    print(
        "-------"
    )

    print(
        "Train:",
        count_rows(
            TRAIN_FILE
        )
    )

    print(
        "Validation:",
        count_rows(
            VALID_FILE
        )
    )

    print(
        "Test:",
        count_rows(
            TEST_FILE
        )
    )

    print(
        "\nTraining config:"
    )

    print(
        TRAINING_CONFIG_FILE
    )

    print(
        "\nOutput:"
    )

    print(
        FULL_WEIGHTS_DIR
    )

    print(
        "\nStarting full fine-tuning..."
    )

    print(
        "The first run is intentionally small "
        "and educational. Watch train loss, "
        "validation loss, tokens/sec, and memory."
    )

    command = [
        sys.executable,
        "-m",
        "mlx_lm",
        "lora",
        "--config",
        TRAINING_CONFIG_FILE.name,
    ]

    subprocess.run(
        command,
        cwd=BASE_DIR,
        check=True,
    )

    print(
        "\nTraining finished."
    )

    print(
        "\nNext:"
    )

    print(
        "python test_finetuned.py"
    )

    print(
        "python compare_before_after.py"
    )


if __name__ == "__main__":

    main()
