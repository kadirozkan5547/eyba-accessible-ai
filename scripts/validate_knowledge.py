"""Bilgi tabanı build çıktıları için çevrimdışı kalite kapısı."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.schemas import Source  # noqa: E402
from app.settings import settings  # noqa: E402
from scripts.build_chunks import parse_document  # noqa: E402

MIN_BODY_CHARS = 400
DIRECTORY_MIN_BODY_CHARS = 100
DIRECTORY_SOURCES = {"sanliurfa_engelsiz_yasam"}


def normalized_path(source: Source) -> Path:
    scope = "sanliurfa" if source.city else "national"
    return settings.normalized_dir / scope / f"{source.id}.md"


def raw_path(source: Source) -> Path | None:
    scope = "sanliurfa" if source.city else "national"
    matches = sorted((settings.raw_dir / scope).glob(f"{source.id}_*.html"))
    return matches[-1] if matches else None


def indexable_body(body: str) -> str:
    return body.split("\n## Kaynak", 1)[0].strip()


def validate() -> list[str]:
    errors: list[str] = []
    manifest = yaml.safe_load(settings.manifest_path.read_text(encoding="utf-8"))
    sources: list[Source] = []
    for item in manifest.get("sources", []):
        if not item.get("enabled", True):
            continue
        try:
            sources.append(Source.model_validate(item))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"manifest metadata: {item.get('id', '<id-yok>')}: {exc}")

    chunk_sources: set[str] = set()
    chunk_count = 0
    if settings.chunks_path.exists():
        from app.rag.retrieval import load_chunks

        chunks = load_chunks()
        chunk_count = len(chunks)
        chunk_sources = {chunk.source_id for chunk in chunks.values()}
    else:
        errors.append(f"chunk dosyası yok: {settings.chunks_path}")

    for source in sources:
        raw = raw_path(source)
        if raw is None:
            errors.append(f"{source.id}: ham arşiv yok")
        else:
            checksum = raw.with_suffix(".sha256")
            if not checksum.exists():
                errors.append(f"{source.id}: SHA-256 dosyası yok")
            else:
                expected = checksum.read_text(encoding="utf-8").split()[0]
                actual = hashlib.sha256(raw.read_bytes()).hexdigest()
                if actual != expected:
                    errors.append(f"{source.id}: SHA-256 uyuşmuyor")

        normalized = normalized_path(source)
        if not normalized.exists():
            errors.append(f"{source.id}: normalize Markdown yok")
            continue
        metadata, body = parse_document(normalized)
        if metadata.get("source_id") != source.id:
            errors.append(f"{source.id}: frontmatter source_id uyuşmuyor")
        minimum = DIRECTORY_MIN_BODY_CHARS if source.id in DIRECTORY_SOURCES else MIN_BODY_CHARS
        if len(indexable_body(body)) < minimum:
            errors.append(f"{source.id}: içerik çok ince (<{minimum} karakter)")
        if source.id not in chunk_sources:
            errors.append(f"{source.id}: chunk kapsamı yok")

    if settings.index_meta_path.exists():
        meta = json.loads(settings.index_meta_path.read_text(encoding="utf-8"))
        current_hash = hashlib.sha256(settings.chunks_path.read_bytes()).hexdigest()
        if meta.get("chunks_sha256") != current_hash:
            errors.append("embedding indexi mevcut chunks.jsonl ile güncel değil")
        if meta.get("chunk_count") != chunk_count:
            errors.append("embedding indexi chunk sayısı uyuşmuyor")
    else:
        errors.append("embedding index metadata dosyası yok")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Bilgi tabanı kalite kapısı: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Bilgi tabanı kalite kapısı: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
