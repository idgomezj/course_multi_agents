import platform
import sys


def main():

    print(
        "Python:",
        sys.version.split()[0]
    )

    print(
        "Platform:",
        platform.platform()
    )

    print(
        "Machine:",
        platform.machine()
    )

    if platform.system() != "Darwin":

        print(
            "\nWARNING: This lab is designed "
            "primarily for macOS + Apple Silicon."
        )

    if platform.machine() != "arm64":

        print(
            "\nWARNING: MLX requires Apple Silicon "
            "for the intended workflow."
        )

    try:

        import mlx.core as mx

        print(
            "\nMLX imported successfully."
        )

        print(
            "MLX default device:",
            mx.default_device()
        )

        a = mx.array(
            [1.0, 2.0, 3.0]
        )

        b = a * 2

        mx.eval(b)

        print(
            "MLX test result:",
            b.tolist()
        )

    except Exception as exc:

        print(
            "\nMLX check failed:"
        )

        print(exc)

        print(
            "\nInstall dependencies with:"
        )

        print(
            "pip install -r requirements.txt"
        )


if __name__ == "__main__":

    main()
