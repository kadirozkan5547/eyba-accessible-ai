from __future__ import annotations

import json
import unittest

from app.rag.retrieval import load_chunks
from app.rag.schemas import RetrievedChunk
from app.services.rag_service import has_topic_evidence
from app.settings import BASE_DIR


class GroundingDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.chunks = load_chunks()

    def candidates_for(self, source_id: str) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(chunk=chunk, score=1.0)
            for chunk in self.chunks.values()
            if chunk.source_id == source_id
        ]

    def test_every_answerable_evaluation_question_has_literal_topic_evidence(self) -> None:
        path = BASE_DIR / "tests" / "rag" / "questions.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        for row in rows:
            if not row["answerable"]:
                continue
            with self.subTest(question=row["question"]):
                self.assertTrue(
                    has_topic_evidence(
                        row["question"], self.candidates_for(row["expected_source"])
                    )
                )

    def test_taxi_question_is_not_supported_by_current_top_sources(self) -> None:
        candidates = self.candidates_for("edevlet_engelsiz_hizmetler")
        candidates.extend(self.candidates_for("uab_erisilebilir_ulasim"))
        self.assertFalse(
            has_topic_evidence("Engelli taksi hizmetine nereden ulaşabilirim?", candidates)
        )


if __name__ == "__main__":
    unittest.main()
