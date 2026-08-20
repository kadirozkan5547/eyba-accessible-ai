"""Retrieval isabetini ölçer ve eşik kalibrasyonu için skorları raporlar."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.embeddings import embed_texts, load_index  # noqa: E402
from app.rag.retrieval import load_chunks, retrieve  # noqa: E402
from app.settings import BASE_DIR  # noqa: E402

QUESTIONS_PATH = BASE_DIR / "tests" / "rag" / "questions.jsonl"
REPORT_PATH = BASE_DIR / "tests" / "rag" / "retrieval_report.json"


def load_questions() -> list[dict]:
    return [
        json.loads(line)
        for line in QUESTIONS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    questions = load_questions()
    vectors = embed_texts([item["question"] for item in questions])
    embeddings, chunk_ids, meta = load_index()
    chunks = load_chunks()
    rows = []
    top1_hits = top3_hits = answerable_count = 0

    for item, vector in zip(questions, vectors):
        candidates = retrieve(
            vector,
            embeddings,
            chunk_ids,
            chunks,
            question=item["question"],
            top_k=4,
        )
        source_ids = [candidate.chunk.source_id for candidate in candidates]
        score = candidates[0].score if candidates else None
        if item["answerable"]:
            answerable_count += 1
            top1_hits += int(bool(source_ids) and source_ids[0] == item["expected_source"])
            top3_hits += int(item["expected_source"] in source_ids[:3])
        rows.append(
            {
                **item,
                "top_sources": source_ids,
                "top_score": score,
                "hit_top1": item["answerable"] and bool(source_ids) and source_ids[0] == item["expected_source"],
                "hit_top3": item["answerable"] and item["expected_source"] in source_ids[:3],
            }
        )
        label = "IN " if item["answerable"] else "OUT"
        print(f"[{label}] {score or 0:.4f} {item['question']} -> {source_ids[:3]}")

    in_scores = [row["top_score"] for row in rows if row["answerable"] and row["top_score"]]
    out_scores = [row["top_score"] for row in rows if not row["answerable"] and row["top_score"]]
    summary = {
        "index_meta": meta,
        "answerable_count": answerable_count,
        "top1_accuracy": top1_hits / answerable_count,
        "top3_accuracy": top3_hits / answerable_count,
        "min_answerable_top_score": min(in_scores),
        "max_out_of_scope_top_score": max(out_scores),
    }
    REPORT_PATH.write_text(
        json.dumps({"summary": summary, "results": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Rapor -> {REPORT_PATH}")
    return 0 if top3_hits == answerable_count else 1


if __name__ == "__main__":
    raise SystemExit(main())
