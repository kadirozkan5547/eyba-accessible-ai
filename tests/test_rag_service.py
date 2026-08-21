from __future__ import annotations

import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from app.rag.schemas import Chunk, RetrievedChunk
from app.services.rag_service import (
    INSUFFICIENT_ANSWER,
    TAXI_INSUFFICIENT_ANSWER,
    answer_question,
    answer_satisfies_question,
    answer_sources,
    build_context,
    has_topic_evidence,
    is_grounded_answer,
    topic_terms,
    validate_question,
    verified_fallback,
)


def candidate(source_id: str, score: float, text: str = "Resmî içerik.") -> RetrievedChunk:
    return RetrievedChunk(
        chunk=Chunk(
            chunk_id=f"{source_id}:0001",
            source_id=source_id,
            title=f"{source_id} başlığı",
            section="Başvuru",
            text=text,
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

    def test_taxi_question_requires_taxi_evidence(self) -> None:
        question = "Engelli taksi hizmetine nereden ulaşabilirim?"
        generic_transport = candidate(
            "ulasim",
            0.51,
            "Engelli bireyler için erişilebilir ulaşım projeleri geliştirilmektedir.",
        )
        taxi_source = candidate(
            "taksi",
            0.51,
            "Engelsiz taksi hizmeti belediyenin ulaşım birimi tarafından sunulur.",
        )
        self.assertEqual(topic_terms(question), ["taksi"])
        self.assertFalse(has_topic_evidence(question, [generic_transport]))
        self.assertTrue(has_topic_evidence(question, [taxi_source]))

    def test_model_is_not_called_when_topic_is_absent(self) -> None:
        generic_transport = candidate(
            "ulasim",
            0.51,
            "Engelli bireyler için erişilebilir ulaşım projeleri geliştirilmektedir.",
        )
        with (
            patch("app.services.rag_service.retrieval_assets", return_value=(np.zeros((1, 2)), ["x"], {})),
            patch("app.services.rag_service.embed_query", return_value=np.zeros(2)),
            patch("app.services.rag_service.retrieve", return_value=[generic_transport]),
            patch("app.services.rag_service.get_handles") as mocked_handles,
        ):
            response = answer_question("Engelli taksi hizmetine nereden ulaşabilirim?")
        self.assertEqual(response.status, "insufficient_context")
        self.assertEqual(response.answer, TAXI_INSUFFICIENT_ANSWER)
        self.assertEqual(response.sources, [])
        mocked_handles.assert_not_called()

    def test_incomplete_numeric_model_answer_uses_verified_fallback(self) -> None:
        source = candidate(
            "iskur",
            0.71,
            "Kayıt şartları - Tüm vücut fonksiyon kaybının en az %40 olduğunu "
            "belirten engelli sağlık kurulu raporu gerekir.",
        )
        chat_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Raporın ibraz edilmesi gerekir."))]
        )
        handles = SimpleNamespace(
            chat_client=SimpleNamespace(complete_chat=lambda _messages: chat_response)
        )
        with (
            patch("app.services.rag_service.retrieval_assets", return_value=(np.zeros((1, 2)), ["x"], {})),
            patch("app.services.rag_service.embed_query", return_value=np.zeros(2)),
            patch("app.services.rag_service.retrieve", return_value=[source]),
            patch("app.services.rag_service.get_handles", return_value=handles),
        ):
            response = answer_question("İŞKUR engelli kaydı için rapor oranı kaç olmalı?")
        self.assertEqual(response.status, "ok")
        self.assertIn("%40", response.answer)

    def test_unsupported_contact_channel_rejects_generated_answer(self) -> None:
        context = "Engelli ulaşımında indirim uygulanır."
        self.assertFalse(
            is_grounded_answer("Telefon numarasını web sitesinden öğrenin.", context)
        )
        self.assertTrue(
            is_grounded_answer(
                "Başvuru için 123 numaralı telefonu arayın.",
                "Başvuru için 123 numaralı telefon aranır.",
            )
        )

    def test_repeated_generated_advice_is_rejected(self) -> None:
        text = "Kurumun resmî kanalına başvurun. Kurumun resmî kanalına başvurun."
        self.assertFalse(is_grounded_answer(text, "Kurumun resmî kanalı kullanılır."))

    def test_numeric_question_requires_number_in_answer(self) -> None:
        question = "İŞKUR engelli kaydı için rapor oranı kaç olmalı?"
        self.assertFalse(answer_satisfies_question(question, "Rapor ibraz edilmelidir."))
        self.assertTrue(answer_satisfies_question(question, "Oran en az %40 olmalıdır."))

    def test_numeric_question_has_verified_source_fallback(self) -> None:
        question = "İŞKUR engelli kaydı için rapor oranı kaç olmalı?"
        source = candidate(
            "iskur",
            0.7,
            "Kayıt şartları - Tüm vücut fonksiyon kaybının en az %40 olduğunu "
            "belirten engelli sağlık kurulu raporu gerekir. - 14 yaşını doldurmak gerekir.",
        )
        answer = verified_fallback(question, [source])
        self.assertIsNotNone(answer)
        answer_text, supporting_candidate = answer
        self.assertIn("%40", answer_text)
        self.assertIn("Resmî kaynağa göre", answer_text)
        self.assertEqual(supporting_candidate.chunk.source_id, "iskur")

    def test_invented_number_is_rejected(self) -> None:
        self.assertFalse(
            is_grounded_answer(
                "Başvuru için oran en az %50 olmalıdır.",
                "Başvuru için oran en az %40 olmalıdır.",
            )
        )


if __name__ == "__main__":
    unittest.main()
