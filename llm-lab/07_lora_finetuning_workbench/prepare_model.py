import argparse
import os
import shutil

from huggingface_hub import (
    snapshot_download,
)

from config import (
    MODEL_REPO,
    MODEL_DIR,
    CHAPTER_06_MODEL_DIR,
    LEGACY_CHAPTER_06_MODEL_DIR,
)

from model_files import (
    get_weight_files,
    is_complete_model,
)


def remove_existing_destination():

    if MODEL_DIR.is_symlink():

        MODEL_DIR.unlink()

    elif MODEL_DIR.exists():

        shutil.rmtree(
            MODEL_DIR
        )


def try_reuse_chapter_06():

    candidates = [
        CHAPTER_06_MODEL_DIR,
        LEGACY_CHAPTER_06_MODEL_DIR,
    ]

    for candidate in candidates:

        if not is_complete_model(
            candidate
        ):

            continue

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
                    "Model already ready:"
                )

                print(
                    MODEL_DIR
                )

                return True

            remove_existing_destination()

        relative_target = os.path.relpath(
            candidate,
            MODEL_DIR.parent,
        )

        MODEL_DIR.symlink_to(
            relative_target,
            target_is_directory=True,
        )

        print(
            "Reusing chapter 06 BF16 model "
            "through a local symlink:"
        )

        print(
            MODEL_DIR
        )

        print(
            " -> "
            + str(candidate)
        )

        return True

    return False


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Prepare the same BF16 Qwen base "
            "model used in chapter 06."
        )
    )

    parser.add_argument(
        "--force-download",
        action="store_true",
        help=(
            "Download a separate local copy "
            "instead of reusing chapter 06."
        ),
    )

    args = parser.parse_args()

    if (
        not args.force_download
        and
        try_reuse_chapter_06()
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

        remove_existing_destination()

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

    print(
        "\nDestination:"
    )

    print(
        MODEL_DIR
    )

    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_DIR,
        force_download=args.force_download,
    )

    weight_files = (
        get_weight_files(
            MODEL_DIR
        )
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
        "\nModel ready."
    )

    print(
        "Safetensors size:",
        f"{total / (1024 ** 3):.3f} GiB"
    )


if __name__ == "__main__":

    main()
