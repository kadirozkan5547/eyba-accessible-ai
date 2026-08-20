from __future__ import annotations

import unittest

from app.settings import BASE_DIR, settings
from scripts.package_release import included_files


class ReleaseTests(unittest.TestCase):
    def test_version_file_matches_application_version(self) -> None:
        version = (BASE_DIR / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, settings.app_version)

    def test_release_contains_runtime_assets(self) -> None:
        relative_files = {path.relative_to(BASE_DIR).as_posix() for path in included_files()}
        for required in (
            "baslat.bat",
            "app/main.py",
            "app/templates/index.html",
            "knowledge/chunks/chunks.jsonl",
            "knowledge/index/embeddings.npy",
            "knowledge/index/chunk_ids.json",
        ):
            with self.subTest(required=required):
                self.assertIn(required, relative_files)


if __name__ == "__main__":
    unittest.main()
