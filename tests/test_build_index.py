from __future__ import annotations

import unittest
from datetime import date

from app.rag.schemas import Chunk
from scripts.build_index import embedding_input


class BuildIndexTests(unittest.TestCase):
    def test_embedding_input_contains_title_section_and_text(self) -> None:
        chunk = Chunk(
            chunk_id="test:0001",
            source_id="test",
            title="Belge Başlığı",
            section="Başvuru",
            text="Başvuru il müdürlüğüne yapılır.",
            authority="Kurum",
            source_tier="A",
            retrieved_at=date(2026, 8, 20),
        )
        value = embedding_input(chunk)
        self.assertEqual(value, "Belge Başlığı\n\nBaşvuru\n\nBaşvuru il müdürlüğüne yapılır.")


if __name__ == "__main__":
    unittest.main()
