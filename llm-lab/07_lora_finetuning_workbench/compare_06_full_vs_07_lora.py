import json
from pathlib import Path

import mlx.core as mx

from mlx.utils import tree_flatten

from mlx_lm.tuner.utils import (
    linear_to_lora_layers,
)

from config import (
    BASE_DIR,
    LORA_DROPOUT,
    LORA_KEYS,
    LORA_OUTPUT_DIR,
    LORA_RANK,
    LORA_SCALE,
    METHOD_COMPARISON_FILE,
    NUM_LAYERS,
)

from model_files import load_base_model


def count_parameters(tree):

    return sum(
        value.size
        for _, value in tree_flatten(tree)
    )


def find_chapter_06():

    candidates = [
        (
            BASE_DIR.parent
            / "06_full_finetuning_workbench"
        ),
        (
            BASE_DIR.parent
            / "full_finetuning_workbench"
        ),
    ]

    # Prefer the location that actually contains
    # chapter-06 local training artifacts. This
    # matters after the repository directory was
    # renamed: ignored model/output files may still
    # live under the legacy path.

    for candidate in candidates:

        if (
            (
                candidate
                / "outputs"
                / "full_weights"
                / "adapters.safetensors"
            ).exists()
            or
            (
                candidate
                / "outputs"
                / "before_after.json"
            ).exists()
        ):

            return candidate

    for candidate in candidates:

        if candidate.exists():

            return candidate

    return None


def calculate_parameter_counts():

    print(
        "Measuring chapter 06 full-mode "
        "trainable parameters..."
    )

    full_model, _ = load_base_model()

    total_base = count_parameters(
        full_model.parameters()
    )

    full_model.freeze()

    for layer in full_model.layers:

        layer.unfreeze()

    full_trainable = count_parameters(
        full_model.trainable_parameters()
    )

    del full_model
    mx.clear_cache()

    print(
        "Measuring chapter 07 LoRA "
        "trainable parameters..."
    )

    lora_model, _ = load_base_model()

    lora_model.freeze()

    linear_to_lora_layers(
        lora_model,
        NUM_LAYERS,
        {
            "keys": LORA_KEYS,
            "rank": LORA_RANK,
            "scale": LORA_SCALE,
            "dropout": LORA_DROPOUT,
        },
        use_dora=False,
    )

    lora_trainable = count_parameters(
        lora_model.trainable_parameters()
    )

    return {
        "base_parameters":
            total_base,
        "full_trainable_parameters":
            full_trainable,
        "lora_trainable_parameters":
            lora_trainable,
        "full_trainable_percent":
            full_trainable
            / total_base
            * 100,
        "lora_trainable_percent":
            lora_trainable
            / total_base
            * 100,
        "trainable_reduction_factor":
            full_trainable
            / lora_trainable,
    }


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


def load_json_if_exists(
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


def main():

    counts = (
        calculate_parameter_counts()
    )

    chapter_06 = (
        find_chapter_06()
    )

    full_adapter = None
    full_comparison = None

    if chapter_06 is not None:

        full_adapter = (
            chapter_06
            / "outputs"
            / "full_weights"
            / "adapters.safetensors"
        )

        full_comparison = (
            chapter_06
            / "outputs"
            / "before_after.json"
        )

    lora_adapter = (
        LORA_OUTPUT_DIR
        / "adapters.safetensors"
    )

    lora_comparison = (
        BASE_DIR
        / "outputs"
        / "before_after_lora.json"
    )

    full_size = file_size(
        full_adapter
    )

    lora_size = file_size(
        lora_adapter
    )

    report = {
        "parameter_comparison":
            counts,
        "checkpoint_bytes": {
            "06_full":
                full_size,
            "07_lora":
                lora_size,
        },
        "checkpoint_reduction_factor":
            (
                full_size / lora_size
                if (
                    full_size
                    and
                    lora_size
                )
                else None
            ),
        "chapter_06_path":
            (
                str(chapter_06)
                if chapter_06
                else None
            ),
        "06_before_after":
            load_json_if_exists(
                full_comparison
            ),
        "07_before_after":
            load_json_if_exists(
                lora_comparison
            ),
    }

    METHOD_COMPARISON_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        METHOD_COMPARISON_FILE,
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
        "\nPARAMETERS"
    )

    print(
        "----------"
    )

    print(
        "Base:",
        f"{counts['base_parameters']:,}"
    )

    print(
        "06 Full trainable:",
        f"{counts['full_trainable_parameters']:,}",
        f"({counts['full_trainable_percent']:.3f}%)"
    )

    print(
        "07 LoRA trainable:",
        f"{counts['lora_trainable_parameters']:,}",
        f"({counts['lora_trainable_percent']:.3f}%)"
    )

    print(
        "Trainable reduction:",
        f"{counts['trainable_reduction_factor']:.1f}x"
    )

    print(
        "\nCHECKPOINTS"
    )

    print(
        "-----------"
    )

    if full_size:

        print(
            "06 Full:",
            f"{full_size / (1024 ** 2):.2f} MiB"
        )

    else:

        print(
            "06 Full: not found"
        )

    if lora_size:

        print(
            "07 LoRA:",
            f"{lora_size / (1024 ** 2):.2f} MiB"
        )

    else:

        print(
            "07 LoRA: not found"
        )

    if (
        full_size
        and
        lora_size
    ):

        print(
            "Checkpoint reduction:",
            f"{full_size / lora_size:.1f}x"
        )

    print(
        "\nSaved report:"
    )

    print(
        METHOD_COMPARISON_FILE
    )

    if (
        report[
            "06_before_after"
        ]
        is None
    ):

        print(
            "\nNote: Run chapter 06 "
            "compare_before_after.py to include "
            "its generated responses."
        )

    if (
        report[
            "07_before_after"
        ]
        is None
    ):

        print(
            "Note: Run chapter 07 "
            "compare_before_after.py to include "
            "its generated responses."
        )


if __name__ == "__main__":

    main()
