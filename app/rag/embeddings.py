"""Foundry Local embedding üretimi ve yerel index G/Ç (plan §19)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from app.rag.foundry import get_handles
from app.settings import settings


def embed_texts(texts: Sequence[str], *, allow_download: bool = False) -> np.ndarray:
    """Metinleri cihaz üzerinde vektöre çevirir; (n, d) float32 dizi döndürür."""
    client = get_handles(allow_download=allow_download).embedding_client
    response = client.generate_embeddings(list(texts))
    return np.asarray([item.embedding for item in response.data], dtype=np.float32)


def embed_query(text: str) -> np.ndarray:
    """Tek bir sorgu için embedding (plan §20.1)."""
    client = get_handles().embedding_client
    response = client.generate_embedding(text)
    return np.asarray(response.data[0].embedding, dtype=np.float32)


def save_index(
    embeddings: np.ndarray, chunk_ids: Iterable[str], meta: dict, index_dir: Path | None = None
) -> None:
    directory = index_dir or settings.index_dir
    directory.mkdir(parents=True, exist_ok=True)
    np.save(directory / "embeddings.npy", embeddings)
    (directory / "chunk_ids.json").write_text(
        json.dumps(list(chunk_ids), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (directory / "index_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_index(index_dir: Path | None = None) -> tuple[np.ndarray, list[str], dict]:
    directory = index_dir or settings.index_dir
    embeddings = np.load(directory / "embeddings.npy")
    chunk_ids = json.loads((directory / "chunk_ids.json").read_text(encoding="utf-8"))
    meta = json.loads((directory / "index_meta.json").read_text(encoding="utf-8"))
    return embeddings, chunk_ids, meta
