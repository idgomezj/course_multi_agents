from huggingface_hub import snapshot_download

from config import (
    MODEL_REPO,
    MODEL_DIR,
)


def main():

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

    print(
        "\nThis download contains the model "
        "weights, tokenizer, and configuration."
    )

    downloaded_path = snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_DIR,
    )

    print(
        "\nDownload complete:"
    )

    print(
        downloaded_path
    )

    print(
        "\nNext:"
    )

    print(
        "python inspect_architecture.py"
    )

    print(
        "python inspect_tokenizer.py "
        '--text "Artificial intelligence is"'
    )

    print(
        "python generate.py "
        '--prompt "Artificial intelligence is"'
    )


if __name__ == "__main__":

    main()
