import importlib.metadata
import platform
import sys


def package_version(
    package
):

    try:

        return (
            importlib.metadata.version(
                package
            )
        )

    except (
        importlib.metadata.PackageNotFoundError
    ):

        return "not installed"


def main():

    print(
        "Python:",
        sys.version.split()[0]
    )

    print(
        "Executable:",
        sys.executable
    )

    print(
        "Platform:",
        platform.platform()
    )

    print(
        "Machine:",
        platform.machine()
    )

    print(
        "\nPackages:"
    )

    print(
        "  mlx:",
        package_version(
            "mlx"
        )
    )

    print(
        "  mlx-lm:",
        package_version(
            "mlx-lm"
        )
    )

    print(
        "  huggingface-hub:",
        package_version(
            "huggingface-hub"
        )
    )

    print(
        "  transformers:",
        package_version(
            "transformers"
        )
    )

    if platform.system() != "Darwin":

        print(
            "\nWARNING: This lab is designed "
            "for macOS."
        )

    if platform.machine() != "arm64":

        print(
            "\nWARNING: This lab is designed "
            "for Apple Silicon."
        )

    try:

        import mlx.core as mx

        test = (
            mx.array(
                [1.0, 2.0, 3.0]
            )
            *
            2
        )

        mx.eval(
            test
        )

        print(
            "\nMLX test:",
            test.tolist()
        )

        print(
            "MLX default device:",
            mx.default_device()
        )

    except Exception as exc:

        print(
            "\nMLX test failed:"
        )

        print(exc)

    if (
        ".venv" in sys.executable
        and
        "conda" in sys.executable.lower()
    ):

        print(
            "\nWARNING: Python appears to mix "
            "virtual-environment paths."
        )

    print(
        "\nRecommendation:"
    )

    print(
        "Use ONE environment only. Check with:"
    )

    print(
        "which python"
    )

    print(
        'python -c "import sys; print(sys.executable)"'
    )


if __name__ == "__main__":

    main()
