from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ["challenge", "frontend", "run.py", "requirements.txt", ".env.example", "schemas", "student-package"]


def copy_item(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", required=True, choices=[f"team_{i}" for i in range(1, 6)])
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    out = Path(args.out or f"{args.team}_student_package.zip").resolve()
    with tempfile.TemporaryDirectory() as td:
        stage = Path(td) / "agentic-operations-challenge"
        stage.mkdir()
        for item in SHARED:
            copy_item(ROOT / item, stage / item)

        # No business data is copied into the package. It is delivered by the Data API.
        (stage / "student").mkdir(exist_ok=True)
        copy_item(ROOT / "student" / "train_pytorch.py", stage / "student" / "train_pytorch.py")
        copy_item(ROOT / "student" / "README.md", stage / "student" / "README.md")
        copy_item(ROOT / "student" / args.team, stage / "student" / args.team)

        env_path = stage / ".env.example"
        with env_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\nASSIGNED_TEAM_ID={args.team}\n")

        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in stage.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(stage.parent))
    print(out)


if __name__ == "__main__":
    main()
