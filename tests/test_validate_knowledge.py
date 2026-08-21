from __future__ import annotations

import os
import subprocess
import sys
import unittest

from app.settings import BASE_DIR


class KnowledgeValidationTests(unittest.TestCase):
    def test_cli_uses_utf8_on_legacy_windows_console(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "cp1252"

        result = subprocess.run(
            [sys.executable, "scripts/validate_knowledge.py"],
            cwd=BASE_DIR,
            env=environment,
            capture_output=True,
            check=False,
        )

        diagnostics = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        self.assertEqual(result.returncode, 0, diagnostics)
        self.assertIn(
            "Bilgi tabanı kalite kapısı: PASS",
            result.stdout.decode("utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
