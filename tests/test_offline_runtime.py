from __future__ import annotations

import ast
import unittest
from pathlib import Path

from app.settings import BASE_DIR

BANNED_IMPORTS = {"aiohttp", "httpx", "requests", "socket", "urllib"}


class OfflineRuntimeTests(unittest.TestCase):
    def test_app_has_no_external_network_imports(self) -> None:
        violations: list[str] = []
        for path in (BASE_DIR / "app").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    if name.split(".", 1)[0] in BANNED_IMPORTS:
                        violations.append(f"{path.relative_to(BASE_DIR)}:{node.lineno} {name}")
        self.assertEqual(violations, [])

    def test_web_template_has_no_external_asset_url(self) -> None:
        template = (BASE_DIR / "app" / "templates" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("https://", template)
        self.assertNotIn("http://", template)


if __name__ == "__main__":
    unittest.main()
