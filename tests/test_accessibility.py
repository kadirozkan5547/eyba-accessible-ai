from __future__ import annotations

import re
import unittest

from app.settings import BASE_DIR

TEMPLATE_PATH = BASE_DIR / "app" / "templates" / "index.html"


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    first_luminance = relative_luminance(first.removeprefix("#"))
    second_luminance = relative_luminance(second.removeprefix("#"))
    lighter, darker = sorted((first_luminance, second_luminance), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class AccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = TEMPLATE_PATH.read_text(encoding="utf-8")
        cls.colors = dict(
            re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", cls.template)
        )

    def test_text_colors_meet_wcag_aa(self) -> None:
        surface = self.colors["surface"]
        for token in ("text", "muted", "primary", "danger"):
            with self.subTest(token=token):
                self.assertGreaterEqual(contrast_ratio(self.colors[token], surface), 4.5)
        self.assertGreaterEqual(contrast_ratio("#ffffff", self.colors["primary"]), 4.5)

    def test_focus_and_control_boundaries_have_three_to_one_contrast(self) -> None:
        surface = self.colors["surface"]
        self.assertGreaterEqual(contrast_ratio(self.colors["focus"], surface), 3.0)
        self.assertGreaterEqual(contrast_ratio(self.colors["border"], surface), 3.0)

    def test_controls_and_live_regions_have_accessible_contract(self) -> None:
        self.assertIn("min-height: 3rem", self.template)
        self.assertIn("min-width: 3rem", self.template)
        self.assertIn('role="status"', self.template)
        self.assertIn('aria-live="polite"', self.template)
        self.assertIn('aria-describedby="question-hint question-count"', self.template)
        self.assertIn('tabindex="-1">Yanıt', self.template)

    def test_reflow_styles_do_not_require_fixed_page_width(self) -> None:
        self.assertIn("width: min(70rem, calc(100% - 2rem))", self.template)
        self.assertIn("flex-wrap: wrap", self.template)
        self.assertNotRegex(self.template, r"width:\s*[4-9][0-9]{2,}px")

    def test_scenarios_are_keyboard_native_buttons(self) -> None:
        self.assertEqual(self.template.count('class="scenario-card"'), 6)
        self.assertEqual(self.template.count('data-question="'), 6)
        self.assertNotIn('role="button"', self.template)


if __name__ == "__main__":
    unittest.main()
