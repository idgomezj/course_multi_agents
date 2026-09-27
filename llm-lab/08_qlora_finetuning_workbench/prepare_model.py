import argparse
import os
import shutil

from huggingface_hub import snapshot_download

from config import (
    CHAPTER_05_MODEL_DIR,
    MODEL_DIR,
    MODEL_REPO,
)

from model_files import (
    get_weight_files,
    is_complete_model,
)


def remove_destination():

    if MODEL_DIR.is_symlink():

        MODEL_DIR.unlink()

    elif MODEL_DIR.exists():

        shutil.rmtree(
            MODEL_DIR
        )


def try_reuse_chapter_05():

    if not is_complete_model(
        CHAPTER_05_MODEL_DIR
    ):

        return False

    MODEL_DIR.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if (
        MODEL_DIR.exists()
        or
        MODEL_DIR.is_symlink()
    ):

        if is_complete_model(
            MODEL_DIR
        ):

            print(
                "4-bit model already ready:"
            )

            print(
                MODEL_DIR
            )

            return True

        remove_destination()

    relative_target = os.path.relpath(
        CHAPTER_05_MODEL_DIR,
        MODEL_DIR.parent,
    )

    MODEL_DIR.symlink_to(
        relative_target,
        target_is_directory=True,
    )

    print(
        "Reusing chapter 05 4-bit model:"
    )

    print(
        MODEL_DIR
    )

    print(
        " -> "
        + str(
            CHAPTER_05_MODEL_DIR
        )
    )

    return True


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Prepare the 4-bit Qwen base used "
            "for the QLoRA experiment."
        )
    )

    parser.add_argument(
        "--force-download",
        action="store_true",
        help=(
            "Download a separate copy instead "
            "of reusing chapter 05."
        ),
    )

    args = parser.parse_args()

    if (
        not args.force_download
        and
        try_reuse_chapter_05()
    ):

        return

    if (
        MODEL_DIR.is_symlink()
        or
        (
            MODEL_DIR.exists()
            and
            not is_complete_model(
                MODEL_DIR
            )
        )
    ):

        remove_destination()

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Downloading:"
    )

    print(
        MODEL_REPO
    )

    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_DIR,
        force_download=args.force_download,
    )

    weight_files = get_weight_files(
        MODEL_DIR
    )

    if not weight_files:

        raise FileNotFoundError(
            "Download finished without "
            ".safetensors weights."
        )

    total = sum(
        path.stat().st_size
        for path in weight_files
    )

    print(
        "\n4-bit model ready."
    )

    print(
        "Safetensors size:",
        f"{total / (1024 ** 2):.2f} MiB"
    )


if __name__ == "__main__":

    main()
