"""Cosine similarity tabanlı yerel retrieval (plan §20, §21, §22.1)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np

from app.rag.schemas import Chunk, RetrievedChunk
from app.settings import settings


def cosine_similarity(query: np.ndarray, documents: np.ndarray) -> np.ndarray:
    """score = dot(q, d) / (||q|| * ||d||) — plan §20.2."""
    query_norm = np.linalg.norm(query)
    doc_norms = np.linalg.norm(documents, axis=1)
    denominator = query_norm * doc_norms
    denominator[denominator == 0] = np.finfo(np.float32).eps
    return (documents @ query) / denominator


def load_chunks(path: Path | None = None) -> dict[str, Chunk]:
    chunks_path = path or settings.chunks_path
    chunks: dict[str, Chunk] = {}
    with chunks_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            chunk = Chunk.model_validate(json.loads(line))
            chunks[chunk.chunk_id] = chunk
    return chunks


def is_valid_today(chunk: Chunk, today: date | None = None) -> bool:
    """Süresi geçmiş kaynak aktif bilgi gibi kullanılmaz (plan §22.1)."""
    if chunk.valid_until is None:
        return True
    return chunk.valid_until >= (today or date.today())


def city_mentioned(question: str, city: str) -> bool:
    """Soru metninde şehir açıkça geçiyor mu? (plan §21)"""
    normalized = question.casefold().replace("i̇", "i")
    return city.casefold().replace("i̇", "i") in normalized


def retrieve(
    query_vector: np.ndarray,
    embeddings: np.ndarray,
    chunk_ids: list[str],
    chunks: dict[str, Chunk],
    *,
    question: str = "",
    top_k: int | None = None,
    today: date | None = None,
) -> list[RetrievedChunk]:
    """Top-K ilgili chunk'ı döndürür; geçersiz kaynakları eler."""
    scores = cosine_similarity(query_vector, embeddings)
    k = top_k or settings.top_k

    candidates: list[RetrievedChunk] = []
    for chunk_id, score in zip(chunk_ids, scores):
        chunk = chunks.get(chunk_id)
        if chunk is None or not is_valid_today(chunk, today):
            continue
        # Şehirli kaynak yalnız soruda o şehir geçiyorsa öne çıkar; ulusal
        # sorularda şehir filtresi uygulanmaz (plan §21).
        if chunk.city and question and not city_mentioned(question, chunk.city):
            continue
        candidates.append(RetrievedChunk(chunk=chunk, score=float(score)))

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates[:k]


def sufficient_context(
    candidates: list[RetrievedChunk], threshold: float | None = None
) -> bool:
    """Yeterli bağlam yoksa cevap üretilmez (plan §24, §67)."""
    limit = settings.min_similarity if threshold is None else threshold
    return bool(candidates) and candidates[0].score >= limit
