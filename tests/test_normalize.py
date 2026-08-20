from __future__ import annotations

import unittest

from bs4 import BeautifulSoup

from scripts.normalize_sources import pick_content_root, to_markdown


class NormalizeTests(unittest.TestCase):
    def test_known_content_root_beats_large_menu(self) -> None:
        html = """
        <div class="menu"><p>Menü metni Menü metni Menü metni Menü metni</p></div>
        <div class="contentAreaForPages"><p>Gerçek içerik burada bulunur.</p></div>
        """
        soup = BeautifulSoup(html, "html.parser")
        root = pick_content_root(soup)
        self.assertIn("Gerçek içerik", root.get_text())

    def test_osym_cards_are_converted_to_list_items(self) -> None:
        html = """
        <div id="duyuru-kartlar">
          <a class="duyuru-list-item"><span>3 Şubat 2026</span><span>Başvurular alındı</span></a>
        </div>
        """
        root = BeautifulSoup(html, "html.parser").select_one("#duyuru-kartlar")
        self.assertIn("- 3 Şubat 2026 Başvurular alındı", to_markdown(root))


if __name__ == "__main__":
    unittest.main()
