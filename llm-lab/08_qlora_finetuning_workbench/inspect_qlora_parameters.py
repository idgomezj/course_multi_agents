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

from model_files import load_base_model


def count_parameters(tree):

    return sum(
        value.size
        for _, value in tree_flatten(tree)
    )


def main():

    print(
        "Loading 4-bit base model..."
    )

    model, _ = load_base_model()

    first_before = (
        model.layers[0]
        .self_attn
        .q_proj
    )

    print(
        "q_proj before LoRA:",
        type(
            first_before
        ).__name__
    )

    model.freeze()

    linear_to_lora_layers(
        model,
        NUM_LAYERS,
        {
            "keys": LORA_KEYS,
            "rank": LORA_RANK,
            "scale": LORA_SCALE,
            "dropout": LORA_DROPOUT,
        },
        use_dora=False,
    )

    first_after = (
        model.layers[0]
        .self_attn
        .q_proj
    )

    print(
        "q_proj after LoRA:",
        type(
            first_after
        ).__name__
    )

    print(
        "wrapped base type:",
        type(
            first_after.linear
        ).__name__
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

    print(
        "\nQLORA CONFIGURATION"
    )

    print(
        "-------------------"
    )

    print(
        "Base: 4-bit quantized"
    )

    print(
        "Layers:",
        NUM_LAYERS,
        "(all Transformer layers)"
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
        "Targets:"
    )

    for key in LORA_KEYS:

        print(
            " ",
            key
        )

    print(
        "\nTRAINABLE PARAMETERS"
    )

    print(
        "--------------------"
    )

    print(
        "LoRA trainable parameters:",
        f"{trainable_count:,}"
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
        "The quantized base weights remain "
        "frozen. The optimizer only receives "
        "the low-rank LoRA tensors."
    )


if __name__ == "__main__":

    main()
