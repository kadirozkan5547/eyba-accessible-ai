"""BUILD MODE: normalize Markdown belgelerini metadata'lı JSONL chunk'lara böler.

Çalışma zamanında ağ kullanmaz. Üretilen ``chunks.jsonl`` dosyası embedding
indexinin tek metin/metadata kaynağıdır.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.schemas import Chunk  # noqa: E402
from app.settings import settings  # noqa: E402

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOKEN = re.compile(r"\S+")


@dataclass(frozen=True)
class Section:
    title: str | None
    text: str


def token_count(text: str) -> int:
    """Bağımlılıksız ve deterministik yaklaşık token sayısı."""
    return len(TOKEN.findall(text))


def parse_document_text(content: str, source: str = "<memory>") -> tuple[dict, str]:
    match = FRONTMATTER.match(content)
    if not match:
        raise ValueError(f"YAML frontmatter bulunamadı: {source}")
    metadata = yaml.safe_load(match.group(1)) or {}
    return metadata, content[match.end() :].strip()


def parse_document(path: Path) -> tuple[dict, str]:
    return parse_document_text(path.read_text(encoding="utf-8"), str(path))


def split_sections(body: str) -> list[Section]:
    """Başlık sınırlarını korur; yapay kaynak dipnotunu indexe almaz."""
    sections: list[Section] = []
    title: str | None = None
    lines: list[str] = []

    def flush() -> None:
        text = "\n".join(lines).strip()
        if text:
            sections.append(Section(title=title, text=text))

    for line in body.splitlines():
        heading = HEADING.match(line)
        if heading:
            flush()
            lines = []
            title = heading.group(2).strip()
            if title.casefold() == "kaynak":
                break
            continue
        lines.append(line)
    else:
        flush()
    return sections


def heading_directory(body: str) -> Section | None:
    """Yalnız başlıklardan oluşan kategori sayfalarını tek dizin parçası yapar."""
    headings: list[str] = []
    for line in body.splitlines():
        match = HEADING.match(line)
        if not match:
            continue
        title = match.group(2).strip()
        if title.casefold() == "kaynak":
            break
        if title not in headings:
            headings.append(title)
    if len(headings) <= 1:
        return None
    return Section(title="Hizmet başlıkları", text="\n".join(f"- {title}" for title in headings[1:]))


def _windows(words: list[str], target: int, overlap: int) -> list[str]:
    if target <= 0:
        raise ValueError("target sıfırdan büyük olmalı")
    if overlap < 0 or overlap >= target:
        raise ValueError("overlap, 0 ile target arasında olmalı")
    step = target - overlap
    return [" ".join(words[start : start + target]) for start in range(0, len(words), step)]


def chunk_sections(sections: list[Section], target: int, overlap: int) -> list[Section]:
    """Her bölümü hedef boyutta böler; komşu parçalar arasında örtüşme bırakır."""
    result: list[Section] = []
    for section in sections:
        words = TOKEN.findall(section.text)
        if not words:
            continue
        for text in _windows(words, target, overlap):
            result.append(Section(title=section.title, text=text))
    return result


def build_chunks(normalized_dir: Path | None = None) -> list[Chunk]:
    root = normalized_dir or settings.normalized_dir
    chunks: list[Chunk] = []
    for path in sorted(root.rglob("*.md")):
        metadata, body = parse_document(path)
        required = ("source_id", "title", "authority", "source_tier", "retrieved_at")
        missing = [key for key in required if not metadata.get(key)]
        if missing:
            raise ValueError(f"{path}: zorunlu metadata eksik: {', '.join(missing)}")

        sections = split_sections(body)
        if not sections:
            directory = heading_directory(body)
            sections = [directory] if directory else []
        parts = chunk_sections(
            sections,
            target=settings.chunk_target_tokens,
            overlap=settings.chunk_overlap_tokens,
        )
        for index, part in enumerate(parts, start=1):
            chunks.append(
                Chunk(
                    chunk_id=f"{metadata['source_id']}:{index:04d}",
                    source_id=metadata["source_id"],
                    title=metadata["title"],
                    section=part.title,
                    text=part.text,
                    authority=metadata["authority"],
                    source_tier=metadata["source_tier"],
                    country=metadata.get("country", "TR"),
                    city=metadata.get("city"),
                    topic=metadata.get("topic") or [],
                    retrieved_at=metadata["retrieved_at"],
                    valid_until=metadata.get("valid_until"),
                )
            )
    return chunks


def write_chunks(chunks: list[Chunk], output: Path | None = None) -> Path:
    target = output or settings.chunks_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        for chunk in chunks:
            handle.write(chunk.model_dump_json() + "\n")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize belgelerden chunks.jsonl üretir.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    chunks = build_chunks()
    target = write_chunks(chunks, args.output)
    print(f"{len(chunks)} chunk üretildi -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
