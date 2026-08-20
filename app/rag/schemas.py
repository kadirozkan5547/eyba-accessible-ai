"""Veri sözleşmeleri (plan §14, §18.3, §25)."""

from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

SourceTier = Literal["A", "B", "C", "D"]


class Source(BaseModel):
    """sources.yaml içindeki bir kaynak kaydı (plan §14.1)."""

    id: str
    title: str
    authority: str
    source_tier: SourceTier
    url: str
    retrieved_at: date
    language: str = "tr"
    topic: list[str] = Field(default_factory=list)
    country: str = "TR"
    city: Optional[str] = None
    publication_date: Optional[date] = None
    last_updated: Optional[date] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    enabled: bool = True


class Chunk(BaseModel):
    """chunks.jsonl içindeki bir parça (plan §18.3)."""

    chunk_id: str
    source_id: str
    title: str
    section: Optional[str] = None
    text: str
    authority: str
    source_tier: SourceTier
    country: str = "TR"
    city: Optional[str] = None
    topic: list[str] = Field(default_factory=list)
    retrieved_at: date
    valid_until: Optional[date] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None


class RetrievedChunk(BaseModel):
    chunk: Chunk
    score: float


class AnswerSource(BaseModel):
    """UI'da gösterilen kaynak (plan §25)."""

    source_id: str
    title: str
    authority: str
    retrieved_at: date
    score: float


class Answer(BaseModel):
    answer: str
    sources: list[AnswerSource] = Field(default_factory=list)
    status: Literal["ok", "insufficient_context", "error"] = "ok"
