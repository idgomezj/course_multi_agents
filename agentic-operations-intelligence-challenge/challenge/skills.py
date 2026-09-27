from __future__ import annotations

from pathlib import Path


class SkillLibrary:
    def __init__(self, directory: Path):
        self.directory = directory

    def list(self) -> list[dict[str, str]]:
        items = []
        for path in sorted(self.directory.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = next((line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("#")), path.stem)
            items.append({"name": path.stem, "title": title})
        return items

    def load(self, name: str) -> str:
        safe = name.replace("..", "").replace("/", "")
        path = self.directory / f"{safe}.md"
        if not path.exists():
            raise ValueError(f"Unknown skill: {name}")
        return path.read_text(encoding="utf-8")
