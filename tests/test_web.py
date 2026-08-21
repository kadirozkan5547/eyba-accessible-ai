from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.rag.schemas import Answer


class WebTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_home_has_accessible_landmarks(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('lang="tr"', response.text)
        self.assertIn('href="#main-content"', response.text)
        self.assertIn('label for="question"', response.text)
        self.assertIn('aria-busy="false"', response.text)
        self.assertIn("Uygulama sürümü: 1.1.1", response.text)
        self.assertEqual(response.text.count('class="scenario-card"'), 6)
        self.assertIn('id="character-count"', response.text)
        self.assertIn('id="copy-answer"', response.text)

    @patch("app.main.is_cached", return_value=True)
    def test_health_reports_app_and_knowledge_versions(self, _mocked_cached) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["app_version"], "1.1.1")
        self.assertEqual(payload["knowledge_version"], "2026-08-20")

    @patch("app.main.answer_question")
    def test_ask_returns_answer_contract(self, mocked_answer) -> None:
        mocked_answer.return_value = Answer(answer="Yerel yanıt", status="ok")
        response = self.client.post("/api/ask", json={"question": "Nasıl başvururum?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "Yerel yanıt")

    def test_empty_question_is_rejected(self) -> None:
        response = self.client.post("/api/ask", json={"question": ""})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
