from __future__ import annotations

from pathlib import Path

import logging

from app.observability import log_event

logger = logging.getLogger(__name__)


class SkillLibrary:
    def __init__(self, directory: Path):
        self.directory = directory
        log_event(logger, "skills.library.ready", directory=str(directory), exists=directory.exists())

    def list(self) -> list[dict[str, str]]:
        items = []
        for path in sorted(self.directory.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = next((line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("#")), path.stem)
            items.append({"name": path.stem, "title": title})
        log_event(logger, "skills.list.completed", directory=str(self.directory), count=len(items), skills=items)
        return items

    def load(self, name: str) -> str:
        safe = name.replace("..", "").replace("/", "")
        path = self.directory / f"{safe}.md"
        if not path.exists():
            log_event(logger, "skills.load.failed", level=logging.WARNING, requested=name, path=str(path))
            raise ValueError(f"Unknown skill: {name}")
        content = path.read_text(encoding="utf-8")
        log_event(logger, "skills.load.completed", requested=name, path=str(path), characters=len(content))
        return content
