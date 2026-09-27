from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    chunk_id: str
    source: str
    text: str


class RagIndex:
    """Small local RAG baseline.

    Students are allowed to improve the RAG configuration and retrieval strategy.
    The enterprise documents themselves are case inputs and should not be rewritten.
    """

    def __init__(self, documents_dir: Path, config_path: Path):
        self.documents_dir = documents_dir
        self.config_path = config_path
        self.config = self._load_config()
        self.chunks = self._load_chunks()
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, int(self.config.get("ngram_max", 2))),
            stop_words="english",
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform([c.text for c in self.chunks]) if self.chunks else None

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            return {"chunk_size": 180, "overlap": 30, "top_k": 4, "min_score": 0.04, "ngram_max": 2}
        with self.config_path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def _load_chunks(self) -> list[Chunk]:
        chunk_size = max(40, int(self.config.get("chunk_size", 180)))
        overlap = max(0, min(chunk_size - 1, int(self.config.get("overlap", 30))))
        step = max(1, chunk_size - overlap)
        chunks: list[Chunk] = []
        for path in sorted(self.documents_dir.glob("*.md")):
            words = path.read_text(encoding="utf-8").split()
            for i in range(0, len(words), step):
                part = words[i : i + chunk_size]
                if not part:
                    break
                chunks.append(
                    Chunk(
                        chunk_id=f"{path.stem}:{i // step}",
                        source=path.name,
                        text=" ".join(part),
                    )
                )
                if i + chunk_size >= len(words):
                    break
        return chunks

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        if not self.chunks or self.matrix is None:
            return []
        k = top_k or int(self.config.get("top_k", 4))
        min_score = float(self.config.get("min_score", 0.04))
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in ranked[: max(k * 2, k)]:
            if float(score) < min_score:
                continue
            chunk = self.chunks[idx]
            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.source,
                    "score": round(float(score), 4),
                    "text": chunk.text,
                }
            )
            if len(results) >= k:
                break
        return results
