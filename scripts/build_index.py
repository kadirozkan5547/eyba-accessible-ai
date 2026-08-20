"""BUILD MODE: chunks.jsonl içeriğinden yerel embedding indexi üretir."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.embeddings import embed_texts, save_index  # noqa: E402
from app.rag.retrieval import load_chunks  # noqa: E402
from app.rag.schemas import Chunk  # noqa: E402
from app.settings import settings  # noqa: E402

DEFAULT_BATCH_SIZE = 16


def embedding_input(chunk: Chunk) -> str:
    fields = [chunk.title]
    if chunk.section and chunk.section.casefold() != chunk.title.casefold():
        fields.append(chunk.section)
    fields.append(chunk.text)
    return "\n\n".join(fields)


def embed_in_batches(texts: list[str], batch_size: int, allow_download: bool) -> np.ndarray:
    if batch_size <= 0:
        raise ValueError("batch_size sıfırdan büyük olmalı")
    batches = []
    for start in range(0, len(texts), batch_size):
        stop = min(start + batch_size, len(texts))
        print(f"Embedding {start + 1}-{stop}/{len(texts)}")
        batches.append(embed_texts(texts[start:stop], allow_download=allow_download))
    if not batches:
        raise ValueError("Indexlenecek chunk yok")
    return np.vstack(batches).astype(np.float32, copy=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Yerel embedding indexi üretir.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Model cache'te yoksa indir (yalnız internet bağlı build modunda)",
    )
    args = parser.parse_args()

    chunks = load_chunks()
    ordered = list(chunks.values())
    vectors = embed_in_batches(
        [embedding_input(chunk) for chunk in ordered],
        batch_size=args.batch_size,
        allow_download=args.allow_download,
    )
    if vectors.shape[0] != len(ordered):
        raise RuntimeError("Embedding sayısı chunk sayısıyla uyuşmuyor")

    manifest = yaml.safe_load(settings.manifest_path.read_text(encoding="utf-8"))
    chunks_sha256 = hashlib.sha256(settings.chunks_path.read_bytes()).hexdigest()
    meta = {
        "embedding_model": settings.embedding_model,
        "knowledge_version": manifest["version"],
        "chunk_count": len(ordered),
        "dimensions": int(vectors.shape[1]),
        "chunks_sha256": chunks_sha256,
    }
    save_index(vectors, [chunk.chunk_id for chunk in ordered], meta)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"Index kaydedildi -> {settings.index_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
