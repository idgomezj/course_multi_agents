from mlx.utils import tree_flatten

from mlx_lm.tuner.utils import (
    linear_to_lora_layers,
)

from config import (
    LORA_DROPOUT,
    LORA_KEYS,
    LORA_RANK,
    LORA_SCALE,
    NUM_LAYERS,
)

from model_files import (
    load_base_model,
)


def count_parameters(tree):

    return sum(
        value.size
        for _, value in tree_flatten(tree)
    )


def main():

    print(
        "Loading BF16 base model..."
    )

    model, _ = load_base_model()

    base_total = count_parameters(
        model.parameters()
    )

    model.freeze()

    lora_config = {
        "keys": LORA_KEYS,
        "rank": LORA_RANK,
        "scale": LORA_SCALE,
        "dropout": LORA_DROPOUT,
    }

    linear_to_lora_layers(
        model,
        NUM_LAYERS,
        lora_config,
        use_dora=False,
    )

    total_after_conversion = (
        count_parameters(
            model.parameters()
        )
    )

    trainable = list(
        tree_flatten(
            model.trainable_parameters()
        )
    )

    trainable_count = sum(
        value.size
        for _, value in trainable
    )

    added_lora_parameters = (
        total_after_conversion
        -
        base_total
    )

    percentage_of_base = (
        trainable_count
        /
        base_total
        *
        100
    )

    print(
        "\nLORA CONFIGURATION"
    )

    print(
        "------------------"
    )

    print(
        "Layers:",
        NUM_LAYERS,
        "(all Transformer layers)"
    )

    print(
        "Keys:"
    )

    for key in LORA_KEYS:

        print(
            " ",
            key
        )

    print(
        "Rank:",
        LORA_RANK
    )

    print(
        "Scale:",
        LORA_SCALE
    )

    print(
        "Dropout:",
        LORA_DROPOUT
    )

    print(
        "\nPARAMETER COUNTS"
    )

    print(
        "----------------"
    )

    print(
        "Original base parameters:",
        f"{base_total:,}"
    )

    print(
        "LoRA parameters added:",
        f"{added_lora_parameters:,}"
    )

    print(
        "Trainable parameters:",
        f"{trainable_count:,}"
    )

    print(
        "Trainable / base:",
        f"{percentage_of_base:.4f}%"
    )

    print(
        "\nFIRST TRAINABLE TENSORS"
    )

    print(
        "-----------------------"
    )

    for name, value in trainable[:24]:

        print(
            f"{name:70} "
            f"shape={tuple(value.shape)} "
            f"params={value.size:,}"
        )

    print(
        "\nKey observation:"
    )

    print(
        "The original Qwen weights are frozen. "
        "The trainable tensors are the small "
        "low-rank LoRA matrices introduced into "
        "the selected projections."
    )


if __name__ == "__main__":

    main()
