import argparse

from huggingface_hub import snapshot_download

from config import (
    MODEL_REPO,
    MODEL_DIR,
)

from model_files import (
    require_complete_model,
)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Download the pretrained MLX model "
            "from Hugging Face."
        )
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Force all model files to be "
            "downloaded again."
        )
    )

    args = parser.parse_args()

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "Downloading model:"
    )

    print(
        MODEL_REPO
    )

    print(
        "\nDestination:"
    )

    print(
        MODEL_DIR
    )

    if args.force:

        print(
            "\nForce download enabled."
        )

    print(
        "\nThis download contains the model "
        "weights, tokenizer, and configuration."
    )

    downloaded_path = snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_DIR,
        force_download=args.force,
    )

    print(
        "\nDownload operation finished:"
    )

    print(
        downloaded_path
    )

    weight_files = (
        require_complete_model()
    )

    print(
        "\nVerified model weight files:"
    )

    total_size = 0

    for path in weight_files:

        size = (
            path.stat().st_size
        )

        total_size += size

        print(
            f"  {path.name}: "
            f"{size / (1024 ** 2):.1f} MB"
        )

    print(
        "\nTotal safetensors size:",
        f"{total_size / (1024 ** 2):.1f} MB"
    )

    print(
        "\nModel download is complete."
    )

    print(
        "\nNext:"
    )

    print(
        "python inspect_architecture.py"
    )

    print(
        "python generate.py "
        '--prompt "Artificial intelligence is"'
    )


if __name__ == "__main__":

    main()
