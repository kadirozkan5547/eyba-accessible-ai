from __future__ import annotations

import unittest

from scripts.build_chunks import (
    Section,
    chunk_sections,
    heading_directory,
    parse_document_text,
    split_sections,
)


class ChunkingTests(unittest.TestCase):
    def test_parse_document_reads_frontmatter(self) -> None:
        metadata, body = parse_document_text(
            "---\nsource_id: test\n---\n\n# Başlık\n\nMetin"
        )
        self.assertEqual(metadata["source_id"], "test")
        self.assertIn("Metin", body)

    def test_source_footer_is_not_indexed(self) -> None:
        sections = split_sections("# Belge\n\nAsıl içerik.\n\n## Kaynak\n\nKurum — https://example")
        self.assertEqual([section.text for section in sections], ["Asıl içerik."])

    def test_windows_have_requested_overlap(self) -> None:
        words = [f"w{i}" for i in range(12)]
        chunks = chunk_sections([Section("Bölüm", " ".join(words))], target=6, overlap=2)
        self.assertEqual(chunks[0].text.split()[-2:], chunks[1].text.split()[:2])
        self.assertLessEqual(max(len(chunk.text.split()) for chunk in chunks), 6)

    def test_heading_only_page_becomes_directory(self) -> None:
        section = heading_directory("# Engelsiz Yaşam\n## Kurslar\n## Spor\n## Kaynak")
        self.assertIsNotNone(section)
        self.assertEqual(section.text, "- Kurslar\n- Spor")


if __name__ == "__main__":
    unittest.main()
