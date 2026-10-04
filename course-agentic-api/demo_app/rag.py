from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import logging

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.observability import log_event

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    chunk_id: str
    source: str
    text: str


class RagIndex:
    """Case 0 RAG with solved source-authority weighting."""

    def __init__(
        self,
        documents: list[dict[str, str]],
        config_path: Path,
        document_priorities: dict[str, Any] | None = None,
        max_top_k: int | None = None,
    ):
        self.documents = documents
        self.config_path = config_path
        self.config = self._load_config()
        self.document_priorities = document_priorities or {
            "default_weight": 1.0,
            "authority_weights": {},
            "documents": {},
        }
        self.max_top_k = max_top_k
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
            document_priorities=self.document_priorities,
            max_top_k=self.max_top_k,
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
                chunks.append(Chunk(chunk_id=f"{stem}:{i // step}", source=source, text=" ".join(part)))
                if i + chunk_size >= len(words):
                    break
        return chunks

    def _source_weight(self, source: str) -> tuple[float, str]:
        default_weight = float(self.document_priorities.get("default_weight", 1.0))
        authorities = self.document_priorities.get("authority_weights", {}) or {}
        documents = self.document_priorities.get("documents", {}) or {}
        entry = documents.get(source, {})
        if not isinstance(entry, dict):
            entry = {}
        authority = str(entry.get("authority", "advisory")).lower()
        authority_weight = float(authorities.get(authority, 1.0))
        document_weight = float(entry.get("weight", default_weight))
        return max(0.01, authority_weight * document_weight), authority

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        if not self.chunks or self.matrix is None:
            log_event(logger, "rag.search.empty_index", query=query, requested_top_k=top_k)
            return []
        k = int(top_k or self.config.get("top_k", 4))
        if self.max_top_k is not None:
            k = min(k, int(self.max_top_k))
        k = max(1, k)
        min_score = float(self.config.get("min_score", 0.04))
        query_vec = self.vectorizer.transform([query])
        raw_scores = cosine_similarity(query_vec, self.matrix)[0]

        ranked = []
        for idx, raw_score in enumerate(raw_scores):
            chunk = self.chunks[idx]
            weight, authority = self._source_weight(chunk.source)
            ranked.append((idx, float(raw_score), float(raw_score) * weight, authority))
        ranked.sort(key=lambda x: x[2], reverse=True)

        results = []
        for idx, raw_score, score, authority in ranked[: max(k * 3, k)]:
            if score < min_score:
                continue
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "score": round(score, 4),
                "raw_score": round(raw_score, 4),
                "authority": authority,
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
                {"source": x["source"], "chunk_id": x["chunk_id"], "score": x["score"], "raw_score": x["raw_score"], "authority": x["authority"]}
                for x in results
            ],
        )
        return results
