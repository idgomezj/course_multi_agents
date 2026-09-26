from mlx.utils import (
    tree_flatten,
)

from model_files import (
    load_base_model,
)


def count_parameters(
    tree
):

    return sum(
        value.size
        for _, value
        in tree_flatten(
            tree
        )
    )


def main():

    print(
        "Loading BF16 base model..."
    )

    model, _ = (
        load_base_model()
    )

    total_parameters = (
        count_parameters(
            model.parameters()
        )
    )

    model.freeze()

    for layer in model.layers:

        layer.unfreeze()

    trainable_parameters = (
        count_parameters(
            model.trainable_parameters()
        )
    )

    percentage = (
        trainable_parameters
        /
        total_parameters
        *
        100
    )

    all_parameters = dict(
        tree_flatten(
            model.parameters()
        )
    )

    trainable = dict(
        tree_flatten(
            model.trainable_parameters()
        )
    )

    frozen_names = [
        name
        for name
        in all_parameters
        if name not in trainable
    ]

    print(
        "\nMLX-LM FULL MODE WITH "
        "num_layers = -1"
    )

    print(
        "------------------------------"
    )

    print(
        "Total parameters:",
        f"{total_parameters:,}"
    )

    print(
        "Trainable parameters:",
        f"{trainable_parameters:,}"
    )

    print(
        "Trainable percentage:",
        f"{percentage:.3f}%"
    )

    print(
        "\nTransformer layers:",
        len(
            model.layers
        )
    )

    print(
        "\nImportant nuance:"
    )

    print(
        "Current MLX-LM full mode first freezes "
        "the model and then unfreezes the "
        "selected Transformer layers. With "
        "num_layers=-1, all Transformer layers "
        "are trainable, but some top-level "
        "parameters can remain frozen."
    )

    print(
        "\nFirst frozen parameter groups:"
    )

    for name in frozen_names[:20]:

        print(
            " ",
            name
        )

    print(
        "\nThis exact measurement is more "
        "useful than assuming that 'full' means "
        "100.000% of every top-level tensor."
    )


if __name__ == "__main__":

    main()
