"""Uçtan uca yerel RAG orkestrasyonu (retrieval -> guardrail -> chat)."""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from app.rag.embeddings import embed_query, load_index
from app.rag.foundry import get_handles
from app.rag.retrieval import load_chunks, retrieve, sufficient_context
from app.rag.schemas import Answer, AnswerSource, Chunk, RetrievedChunk
from app.settings import settings

INSUFFICIENT_ANSWER = (
    "Bu bilgi yerel bilgi tabanımda bulunmuyor. "
    "Güncel ve kesin bilgi için ilgili resmî kuruma başvurun."
)

SYSTEM_PROMPT = """Sen Erişilebilir Yerel Bilgi Asistanısın.
Yalnızca CONTEXT içindeki resmî kaynak bilgilerine dayan.
CONTEXT dışında bilgi ekleme, tahmin yapma ve güncel canlı veri üretme.
Bilgi yetersizse bunu açıkça söyle.
Sağlık teşhisi veya kesin hukuki görüş verme.
Kısa cümlelerle, sade ve anlaşılır Türkçe yaz.
Kaynak adlarını cevap içine uydurma; kaynaklar arayüzde ayrıca gösterilecek.
"""


@lru_cache(maxsize=1)
def retrieval_assets() -> tuple[np.ndarray, list[str], dict[str, Chunk]]:
    embeddings, chunk_ids, _meta = load_index()
    return embeddings, chunk_ids, load_chunks()


def build_context(candidates: list[RetrievedChunk]) -> str:
    blocks = []
    for item in candidates:
        chunk = item.chunk
        section = f" | Bölüm: {chunk.section}" if chunk.section else ""
        blocks.append(
            f"[Kaynak: {chunk.title} | Kurum: {chunk.authority}{section}]\n{chunk.text}"
        )
    return "\n\n---\n\n".join(blocks)


def answer_sources(candidates: list[RetrievedChunk]) -> list[AnswerSource]:
    """Aynı belgeden gelen birden çok chunk'ı tek kaynak kartında birleştirir."""
    best: dict[str, RetrievedChunk] = {}
    for item in candidates:
        current = best.get(item.chunk.source_id)
        if current is None or item.score > current.score:
            best[item.chunk.source_id] = item
    return [
        AnswerSource(
            source_id=item.chunk.source_id,
            title=item.chunk.title,
            authority=item.chunk.authority,
            retrieved_at=item.chunk.retrieved_at,
            score=item.score,
        )
        for item in best.values()
    ]


def validate_question(question: str) -> str:
    cleaned = " ".join(question.split())
    if not cleaned:
        raise ValueError("Soru boş olamaz.")
    if len(cleaned) > settings.max_question_chars:
        raise ValueError(f"Soru en fazla {settings.max_question_chars} karakter olabilir.")
    return cleaned


def answer_question(question: str) -> Answer:
    cleaned = validate_question(question)
    embeddings, chunk_ids, chunks = retrieval_assets()
    candidates = retrieve(
        embed_query(cleaned),
        embeddings,
        chunk_ids,
        chunks,
        question=cleaned,
    )
    if not sufficient_context(candidates):
        return Answer(answer=INSUFFICIENT_ANSWER, status="insufficient_context")

    context = build_context(candidates)
    response = get_handles().chat_client.complete_chat(
        [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context}"},
            {"role": "user", "content": cleaned},
        ]
    )
    text = response.choices[0].message.content.strip()
    return Answer(answer=text, sources=answer_sources(candidates), status="ok")
