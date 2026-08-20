from __future__ import annotations

import unittest
from datetime import date

from app.rag.schemas import Chunk, RetrievedChunk
from app.services.rag_service import (
    INSUFFICIENT_ANSWER,
    answer_sources,
    build_context,
    validate_question,
)


def candidate(source_id: str, score: float) -> RetrievedChunk:
    return RetrievedChunk(
        chunk=Chunk(
            chunk_id=f"{source_id}:0001",
            source_id=source_id,
            title=f"{source_id} başlığı",
            section="Başvuru",
            text="Resmî içerik.",
            authority="Kurum",
            source_tier="A",
            retrieved_at=date(2026, 8, 20),
        ),
        score=score,
    )


class RagServiceTests(unittest.TestCase):
    def test_question_validation(self) -> None:
        self.assertEqual(validate_question("  Nasıl   başvururum? "), "Nasıl başvururum?")
        with self.assertRaises(ValueError):
            validate_question("   ")

    def test_source_cards_are_deduplicated_with_best_score(self) -> None:
        items = [candidate("a", 0.5), candidate("a", 0.7), candidate("b", 0.6)]
        sources = answer_sources(items)
        self.assertEqual([source.source_id for source in sources], ["a", "b"])
        self.assertEqual(sources[0].score, 0.7)

    def test_context_has_visible_provenance(self) -> None:
        context = build_context([candidate("a", 0.7)])
        self.assertIn("Kaynak: a başlığı", context)
        self.assertIn("Kurum: Kurum", context)

    def test_insufficient_message_is_plain_turkish(self) -> None:
        self.assertIn("yerel bilgi tabanımda bulunmuyor", INSUFFICIENT_ANSWER)


if __name__ == "__main__":
    unittest.main()
