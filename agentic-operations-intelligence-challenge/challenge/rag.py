from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import logging

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .observability import log_event

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    chunk_id: str
    source: str
    text: str


class RagIndex:
    """Student-editable RAG over documents delivered by the Data API."""

    def __init__(self, documents: list[dict[str, str]], config_path: Path):
        self.documents = documents
        self.config_path = config_path
        self.config = self._load_config()
        self.chunks = self._load_chunks()
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, int(self.config.get("ngram_max", 2))),
            stop_words="english",
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform([c.text for c in self.chunks]) if self.chunks else None
        log_event(
            logger,
            "rag.index.ready",
            config_path=str(self.config_path),
            document_count=len(self.documents),
            sources=[d.get("name") for d in self.documents],
            chunk_count=len(self.chunks),
            config=self.config,
        )

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
        for document in sorted(self.documents, key=lambda x: x["name"]):
            words = document["content"].split()
            source = document["name"]
            stem = source.rsplit(".", 1)[0]
            for i in range(0, len(words), step):
                part = words[i : i + chunk_size]
                if not part:
                    break
                chunks.append(
                    Chunk(
                        chunk_id=f"{stem}:{i // step}",
                        source=source,
                        text=" ".join(part),
                    )
                )
                if i + chunk_size >= len(words):
                    break
        return chunks

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        if not self.chunks or self.matrix is None:
            log_event(logger, "rag.search.empty_index", query=query, requested_top_k=top_k)
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
            results.append({
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "score": round(float(score), 4),
                "text": chunk.text,
            })
            if len(results) >= k:
                break
        log_event(
            logger,
            "rag.search.completed",
            query=query,
            requested_top_k=top_k,
            effective_top_k=k,
            min_score=min_score,
            result_count=len(results),
            hits=[
                {"source": x["source"], "chunk_id": x["chunk_id"], "score": x["score"]}
                for x in results
            ],
        )
        return results
