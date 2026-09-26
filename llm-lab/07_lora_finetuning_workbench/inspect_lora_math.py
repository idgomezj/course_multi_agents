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


def main():

    model, _ = load_base_model()

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

    trainable = list(
        tree_flatten(
            model.trainable_parameters()
        )
    )

    groups = {}

    for name, value in trainable:

        if not (
            name.endswith(
                ".lora_a"
            )
            or
            name.endswith(
                ".lora_b"
            )
        ):

            continue

        module_name, matrix_name = (
            name.rsplit(
                ".",
                1
            )
        )

        groups.setdefault(
            module_name,
            {}
        )[
            matrix_name
        ] = value

    print(
        "LoRA changes a linear transformation "
        "from:\n"
    )

    print(
        "    y = xW"
    )

    print(
        "\nto approximately:\n"
    )

    print(
        "    y = xW + scale * xAB"
    )

    print(
        "\nW remains frozen."
    )

    print(
        "A and B are trainable."
    )

    print(
        "\nACTUAL MATRICES FROM THIS MODEL"
    )

    print(
        "-------------------------------"
    )

    shown = 0

    for module_name, matrices in groups.items():

        if (
            "lora_a" not in matrices
            or
            "lora_b" not in matrices
        ):

            continue

        a = matrices[
            "lora_a"
        ]

        b = matrices[
            "lora_b"
        ]

        count = (
            a.size
            +
            b.size
        )

        print(
            "\nModule:"
        )

        print(
            module_name
        )

        print(
            "A shape:",
            tuple(
                a.shape
            )
        )

        print(
            "B shape:",
            tuple(
                b.shape
            )
        )

        print(
            "A + B parameters:",
            f"{count:,}"
        )

        shown += 1

        if shown >= 4:

            break

    print(
        "\nRank controls the narrow inner "
        "dimension. A smaller rank means fewer "
        "trainable parameters and less adapter "
        "capacity."
    )


if __name__ == "__main__":

    main()
