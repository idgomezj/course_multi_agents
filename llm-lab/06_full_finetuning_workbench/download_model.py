import argparse

from huggingface_hub import (
    snapshot_download,
)

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
            "Download the non-quantized BF16 "
            "model used for full fine-tuning."
        )
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Force every file to be downloaded "
            "again."
        )
    )

    args = parser.parse_args()

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "Model:"
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

    print(
        "\nThis is the BF16 model, not the "
        "4-bit model from the previous lab."
    )

    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_DIR,
        force_download=args.force,
    )

    weight_files = (
        require_complete_model()
    )

    total_bytes = 0

    print(
        "\nVerified weight files:"
    )

    for path in weight_files:

        size = (
            path.stat().st_size
        )

        total_bytes += size

        print(
            f"  {path.name}: "
            f"{size / (1024 ** 3):.3f} GiB"
        )

    print(
        "\nTotal safetensors size:",
        f"{total_bytes / (1024 ** 3):.3f} GiB"
    )

    print(
        "\nDownload complete."
    )

    print(
        "\nNext:"
    )

    print(
        "python inspect_trainable_parameters.py"
    )


if __name__ == "__main__":

    main()
