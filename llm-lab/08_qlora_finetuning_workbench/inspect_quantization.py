import json

from config import MODEL_DIR

from model_files import (
    load_base_model,
    require_complete_model,
)


def directory_weight_size(path):

    return sum(
        item.stat().st_size
        for item in path.glob(
            "*.safetensors"
        )
    )


def main():

    require_complete_model()

    config_file = (
        MODEL_DIR
        / "config.json"
    )

    with open(
        config_file,
        "r",
        encoding="utf-8"
    ) as file:

        config = json.load(file)

    quantization = (
        config.get(
            "quantization"
        )
        or
        config.get(
            "quantization_config"
        )
    )

    print(
        "MODEL QUANTIZATION"
    )

    print(
        "------------------"
    )

    print(
        "Model directory:",
        MODEL_DIR
    )

    print(
        "Quantization config:",
        quantization
    )

    print(
        "Weight files on disk:",
        f"{directory_weight_size(MODEL_DIR) / (1024 ** 2):.2f} MiB"
    )

    print(
        "\nLoading model to inspect real modules..."
    )

    model, _ = load_base_model()

    first = model.layers[0]

    print(
        "\nFIRST TRANSFORMER LAYER"
    )

    print(
        "-----------------------"
    )

    print(
        "q_proj type:",
        type(
            first.self_attn.q_proj
        ).__name__
    )

    print(
        "k_proj type:",
        type(
            first.self_attn.k_proj
        ).__name__
    )

    print(
        "v_proj type:",
        type(
            first.self_attn.v_proj
        ).__name__
    )

    print(
        "o_proj type:",
        type(
            first.self_attn.o_proj
        ).__name__
    )

    q_proj = first.self_attn.q_proj

    for attribute in [
        "bits",
        "group_size",
        "mode",
    ]:

        if hasattr(
            q_proj,
            attribute
        ):

            print(
                f"q_proj {attribute}:",
                getattr(
                    q_proj,
                    attribute
                )
            )

    print(
        "\nKey observation:"
    )

    print(
        "The base attention projection is a "
        "quantized layer. QLoRA will keep this "
        "base layer frozen and add floating-point "
        "LoRA matrices around it."
    )


if __name__ == "__main__":

    main()
