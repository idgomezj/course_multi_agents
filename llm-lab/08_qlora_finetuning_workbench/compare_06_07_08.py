import json
from pathlib import Path

import mlx.core as mx

from config import (
    BASE_DIR,
    MODEL_DIR,
    QLORA_OUTPUT_DIR,
    THREE_WAY_COMPARISON_FILE,
)


SOURCE_PARAMETER_COUNT = 600_000_000


def first_existing(
    paths
):

    for path in paths:

        if path.exists():

            return path

    return None


def file_size(
    path
):

    if (
        path is None
        or
        not path.exists()
    ):

        return None

    return path.stat().st_size


def safetensor_directory_size(
    directory
):

    if (
        directory is None
        or
        not directory.exists()
    ):

        return None

    files = list(
        directory.glob(
            "*.safetensors"
        )
    )

    if not files:

        return None

    return sum(
        file.stat().st_size
        for file in files
    )


def tensor_element_count(
    path
):

    if (
        path is None
        or
        not path.exists()
    ):

        return None

    tensors = mx.load(
        str(path)
    )

    return sum(
        tensor.size
        for tensor in tensors.values()
    )


def load_json(
    path
):

    if (
        path is None
        or
        not path.exists()
    ):

        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def mib(
    value
):

    if value is None:

        return None

    return value / (1024 ** 2)


def main():

    chapter_06 = first_existing([
        (
            BASE_DIR.parent
            / "06_full_finetuning_workbench"
        ),
        (
            BASE_DIR.parent
            / "full_finetuning_workbench"
        ),
    ])

    chapter_07 = (
        BASE_DIR.parent
        / "07_lora_finetuning_workbench"
    )

    full_checkpoint = (
        chapter_06
        / "outputs"
        / "full_weights"
        / "adapters.safetensors"
        if chapter_06
        else None
    )

    lora_checkpoint = (
        chapter_07
        / "outputs"
        / "lora_adapter"
        / "adapters.safetensors"
    )

    qlora_checkpoint = (
        QLORA_OUTPUT_DIR
        / "adapters.safetensors"
    )

    bf16_model_dir = (
        chapter_06
        / "models"
        / "qwen3-0.6b-base-bf16"
        if chapter_06
        else None
    )

    if (
        bf16_model_dir is None
        or
        not bf16_model_dir.exists()
    ):

        candidate = (
            chapter_07
            / "models"
            / "qwen3-0.6b-base-bf16"
        )

        if candidate.exists():

            bf16_model_dir = candidate.resolve()

    four_bit_model_dir = (
        MODEL_DIR.resolve()
        if MODEL_DIR.exists()
        else None
    )

    full_before_after = (
        chapter_06
        / "outputs"
        / "before_after.json"
        if chapter_06
        else None
    )

    lora_before_after = (
        chapter_07
        / "outputs"
        / "before_after_lora.json"
    )

    qlora_before_after = (
        BASE_DIR
        / "outputs"
        / "before_after_qlora.json"
    )

    full_elements = tensor_element_count(
        full_checkpoint
    )

    lora_elements = tensor_element_count(
        lora_checkpoint
    )

    qlora_elements = tensor_element_count(
        qlora_checkpoint
    )

    bf16_bytes = safetensor_directory_size(
        bf16_model_dir
    )

    four_bit_bytes = (
        safetensor_directory_size(
            four_bit_model_dir
        )
    )

    report = {
        "source_model_nominal_parameters":
            SOURCE_PARAMETER_COUNT,
        "base_storage_bytes": {
            "bf16":
                bf16_bytes,
            "4bit":
                four_bit_bytes,
        },
        "base_storage_reduction_factor":
            (
                bf16_bytes
                / four_bit_bytes
                if (
                    bf16_bytes
                    and
                    four_bit_bytes
                )
                else None
            ),
        "checkpoint_bytes": {
            "06_full":
                file_size(
                    full_checkpoint
                ),
            "07_lora":
                file_size(
                    lora_checkpoint
                ),
            "08_qlora":
                file_size(
                    qlora_checkpoint
                ),
        },
        "checkpoint_tensor_elements": {
            "06_full":
                full_elements,
            "07_lora":
                lora_elements,
            "08_qlora":
                qlora_elements,
        },
        "behavior": {
            "06_full":
                load_json(
                    full_before_after
                ),
            "07_lora":
                load_json(
                    lora_before_after
                ),
            "08_qlora":
                load_json(
                    qlora_before_after
                ),
        },
    }

    THREE_WAY_COMPARISON_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        THREE_WAY_COMPARISON_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\nBASE MODEL STORAGE"
    )

    print(
        "------------------"
    )

    print(
        "BF16:",
        (
            f"{mib(bf16_bytes):.2f} MiB"
            if bf16_bytes
            else "not found"
        )
    )

    print(
        "4-bit:",
        (
            f"{mib(four_bit_bytes):.2f} MiB"
            if four_bit_bytes
            else "not found"
        )
    )

    if (
        bf16_bytes
        and
        four_bit_bytes
    ):

        print(
            "Storage reduction:",
            f"{bf16_bytes / four_bit_bytes:.2f}x"
        )

    print(
        "\nTRAINED CHECKPOINTS"
    )

    print(
        "-------------------"
    )

    methods = [
        (
            "06 Full",
            full_checkpoint,
            full_elements,
        ),
        (
            "07 LoRA",
            lora_checkpoint,
            lora_elements,
        ),
        (
            "08 QLoRA",
            qlora_checkpoint,
            qlora_elements,
        ),
    ]

    for label, path, elements in methods:

        size = file_size(
            path
        )

        if size is None:

            print(
                f"{label:10}: not found"
            )

            continue

        print(
            f"{label:10}: "
            f"{mib(size):8.2f} MiB | "
            f"{elements:,} saved tensor elements"
        )

    if (
        lora_elements
        and
        qlora_elements
    ):

        print(
            "\nLoRA vs QLoRA adapter "
            "parameter equality:"
        )

        print(
            lora_elements
            ==
            qlora_elements
        )

        print(
            "With the same rank, target modules, "
            "and layer count, the adapters should "
            "have the same trainable parameter "
            "count even though the base storage "
            "precision is different."
        )

    print(
        "\nBEHAVIOR FILES"
    )

    print(
        "--------------"
    )

    print(
        "06:",
        (
            "available"
            if report[
                "behavior"
            ][
                "06_full"
            ]
            is not None
            else "missing"
        )
    )

    print(
        "07:",
        (
            "available"
            if report[
                "behavior"
            ][
                "07_lora"
            ]
            is not None
            else "missing"
        )
    )

    print(
        "08:",
        (
            "available"
            if report[
                "behavior"
            ][
                "08_qlora"
            ]
            is not None
            else "missing"
        )
    )

    print(
        "\nSaved report:"
    )

    print(
        THREE_WAY_COMPARISON_FILE
    )

    print(
        "\nPeak training memory is not inferred "
        "from checkpoint files. Record the actual "
        "runtime value from each training run "
        "instead of inventing it."
    )


if __name__ == "__main__":

    main()
