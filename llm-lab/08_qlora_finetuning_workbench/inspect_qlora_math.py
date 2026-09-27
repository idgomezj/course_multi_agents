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


def main():

    model, _ = load_base_model()

    base_q = (
        model.layers[0]
        .self_attn
        .q_proj
    )

    print(
        "BEFORE QLoRA"
    )

    print(
        "------------"
    )

    print(
        "q_proj:",
        type(base_q).__name__
    )

    if hasattr(
        base_q,
        "bits"
    ):

        print(
            "bits:",
            base_q.bits
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

    wrapped_q = (
        model.layers[0]
        .self_attn
        .q_proj
    )

    print(
        "\nAFTER QLoRA CONVERSION"
    )

    print(
        "----------------------"
    )

    print(
        "wrapper:",
        type(
            wrapped_q
        ).__name__
    )

    print(
        "frozen base inside wrapper:",
        type(
            wrapped_q.linear
        ).__name__
    )

    print(
        "A shape:",
        tuple(
            wrapped_q.lora_a.shape
        )
    )

    print(
        "B shape:",
        tuple(
            wrapped_q.lora_b.shape
        )
    )

    print(
        "A parameters:",
        f"{wrapped_q.lora_a.size:,}"
    )

    print(
        "B parameters:",
        f"{wrapped_q.lora_b.size:,}"
    )

    print(
        "\nFORWARD"
    )

    print(
        "-------"
    )

    print(
        "base = QuantizedLinear(x)"
    )

    print(
        "delta = scale * ((x @ A) @ B)"
    )

    print(
        "output = base + delta"
    )

    print(
        "\nThe base branch stays quantized and "
        "frozen. A/B are ordinary trainable "
        "LoRA tensors."
    )

    trainable_names = [
        name
        for name, _ in tree_flatten(
            model.trainable_parameters()
        )
    ]

    print(
        "\nFirst trainable names:"
    )

    for name in trainable_names[:12]:

        print(
            " ",
            name
        )


if __name__ == "__main__":

    main()
