import argparse
import json

from safetensors import safe_open

from config import (
    MODEL_DIR,
    SOURCE_MODEL_REPO,
    SOURCE_PARAMETER_COUNT,
    SOURCE_NON_EMBEDDING_PARAMETERS,
    SOURCE_CONTEXT_LENGTH,
)


def require_model():

    config_file = (
        MODEL_DIR
        / "config.json"
    )

    if not config_file.exists():

        raise FileNotFoundError(
            f"Model not found at: {MODEL_DIR}\n\n"
            "Run first:\n"
            "python download_model.py"
        )


def human_size(
    number_bytes
):

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    ]

    value = float(
        number_bytes
    )

    for unit in units:

        if (
            value < 1024
            or
            unit == units[-1]
        ):

            return (
                f"{value:.2f} {unit}"
            )

        value /= 1024

    return (
        f"{value:.2f} TB"
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Inspect the architecture and local "
            "files of the downloaded model."
        )
    )

    parser.add_argument(
        "--show-tensors",
        action="store_true",
        help=(
            "Print tensor names and shapes "
            "from the safetensors files."
        )
    )

    parser.add_argument(
        "--tensor-limit",
        type=int,
        default=25,
        help=(
            "Maximum tensors to display with "
            "--show-tensors."
        )
    )

    args = parser.parse_args()

    require_model()

    config_file = (
        MODEL_DIR
        / "config.json"
    )

    with open(
        config_file,
        "r",
        encoding="utf-8"
    ) as file:

        config = json.load(
            file
        )

    hidden_size = (
        config.get(
            "hidden_size"
        )
    )

    query_heads = (
        config.get(
            "num_attention_heads"
        )
    )

    kv_heads = (
        config.get(
            "num_key_value_heads"
        )
    )

    head_dim = (
        config.get(
            "head_dim"
        )
    )

    if (
        head_dim is None
        and
        hidden_size
        and
        query_heads
    ):

        head_dim = (
            hidden_size
            //
            query_heads
        )

    print(
        "SOURCE MODEL"
    )

    print(
        "------------"
    )

    print(
        "Repository:",
        SOURCE_MODEL_REPO
    )

    print(
        "Nominal parameters:",
        f"{SOURCE_PARAMETER_COUNT:,}"
    )

    print(
        "Non-embedding parameters:",
        f"{SOURCE_NON_EMBEDDING_PARAMETERS:,}"
    )

    print(
        "Documented context length:",
        f"{SOURCE_CONTEXT_LENGTH:,}"
    )

    print(
        "\nLOCAL MLX CONFIG"
    )

    print(
        "----------------"
    )

    fields = [
        (
            "Architecture",
            config.get(
                "architectures"
            )
        ),
        (
            "Model type",
            config.get(
                "model_type"
            )
        ),
        (
            "Vocabulary size",
            config.get(
                "vocab_size"
            )
        ),
        (
            "Hidden size",
            hidden_size
        ),
        (
            "Intermediate size",
            config.get(
                "intermediate_size"
            )
        ),
        (
            "Layers",
            config.get(
                "num_hidden_layers"
            )
        ),
        (
            "Query heads",
            query_heads
        ),
        (
            "Key/value heads",
            kv_heads
        ),
        (
            "Head dimension",
            head_dim
        ),
        (
            "Max position embeddings",
            config.get(
                "max_position_embeddings"
            )
        ),
        (
            "Activation",
            config.get(
                "hidden_act"
            )
        ),
        (
            "RMSNorm epsilon",
            config.get(
                "rms_norm_eps"
            )
        ),
        (
            "RoPE theta",
            config.get(
                "rope_theta"
            )
        ),
        (
            "Tie word embeddings",
            config.get(
                "tie_word_embeddings"
            )
        ),
    ]

    for label, value in fields:

        print(
            f"{label:24}: {value}"
        )

    if (
        query_heads
        and
        kv_heads
    ):

        print(
            f"{'Q heads per KV head':24}: "
            f"{query_heads / kv_heads:.2f}"
        )

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
        "\nQUANTIZATION"
    )

    print(
        "------------"
    )

    print(
        quantization
    )

    print(
        "\nLOCAL FILES"
    )

    print(
        "-----------"
    )

    total_disk_size = 0

    files = sorted([
        path
        for path in MODEL_DIR.iterdir()
        if path.is_file()
    ])

    for path in files:

        size = (
            path.stat().st_size
        )

        total_disk_size += size

        print(
            f"{path.name:40} "
            f"{human_size(size):>12}"
        )

    print(
        "\nTotal local file size:",
        human_size(
            total_disk_size
        )
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "The local model is quantized to 4 bits. "
        "Its on-disk storage size is therefore "
        "not the same thing as the original "
        "parameter count."
    )

    if args.show_tensors:

        print(
            "\nSAFETENSORS"
        )

        print(
            "-----------"
        )

        tensor_count = 0

        for model_file in sorted(
            MODEL_DIR.glob(
                "*.safetensors"
            )
        ):

            print(
                "\nFile:",
                model_file.name
            )

            with safe_open(
                model_file,
                framework="np"
            ) as file:

                for key in file.keys():

                    tensor_slice = (
                        file.get_slice(
                            key
                        )
                    )

                    shape = (
                        tensor_slice.get_shape()
                    )

                    print(
                        f"{key:70} "
                        f"shape={str(shape):18}"
                    )

                    tensor_count += 1

                    if (
                        tensor_count
                        >= args.tensor_limit
                    ):

                        print(
                            "\nTensor display limit reached."
                        )

                        return


if __name__ == "__main__":

    main()
