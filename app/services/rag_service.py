"""Uçtan uca yerel RAG orkestrasyonu (retrieval -> guardrail -> chat)."""

from __future__ import annotations

import re
from functools import lru_cache

import numpy as np

from app.rag.embeddings import embed_query, load_index
from app.rag.foundry import get_handles
from app.rag.retrieval import load_chunks, retrieve, sufficient_context
from app.rag.schemas import Answer, AnswerSource, Chunk, RetrievedChunk
from app.settings import settings

INSUFFICIENT_ANSWER = (
    "Bu konuda doğrulanmış bilgi yerel bilgi tabanımda bulunmuyor. "
    "Yanlış yönlendirmemek için tahmin yürütmeyeceğim. "
    "Bulunduğunuz yerdeki ilgili kamu kurumunun resmî iletişim kanalından bilgi alın."
)

TAXI_INSUFFICIENT_ANSWER = (
    "Yerel bilgi tabanımda engelli taksi hizmeti için doğrulanmış kurum, telefon "
    "veya başvuru bilgisi bulunmuyor. Yanlış bir numara ya da hizmet adı vermeyeceğim. "
    "Bu hizmetler şehre göre değişebilir; bulunduğunuz il veya ilçeyi belirterek "
    "belediyenizin resmî ulaşım ya da engelli hizmetleri birimine danışın. "
    "Bu uygulamadaki yerel hizmet kapsamı şu anda Şanlıurfa ile sınırlıdır."
)

# Soru kalıbını ve tüm bilgi tabanında çok sık geçen genel ifadeleri ana konu
# kanıtı saymayız. En az bir ayırt edici terim kaynakta gerçekten bulunmalıdır.
QUESTION_STOPWORDS = {
    "acaba",
    "bilgi",
    "bana",
    "bir",
    "bu",
    "da",
    "de",
    "engelli",
    "engelliler",
    "engellilerin",
    "engelsiz",
    "erişilebilir",
    "erişilebilirlik",
    "hangi",
    "hakkında",
    "için",
    "ile",
    "ilgili",
    "mi",
    "mı",
    "mu",
    "mü",
    "nasıl",
    "ne",
    "neden",
    "nedir",
    "nerde",
    "nerden",
    "nereden",
    "var",
    "ve",
    "veya",
}
GENERIC_PREFIXES = ("hizmet", "ulaşabil", "öğren", "istiyor")
UNSUPPORTED_CHANNEL_MARKERS = (
    "telefon",
    "numara",
    "web sitesi",
    "mobil uygulama",
    "sosyal medya",
    "e-posta",
    "adres",
)
NUMERIC_INTENT_WORDS = {"kaç", "oran", "oranı", "yüzde", "ücret", "tutar", "süre"}

SYSTEM_PROMPT = """Sen engelli bireylerin hak ve kamu hizmetlerine erişimini kolaylaştıran Erişilebilir Yerel Bilgi Asistanısın.
Yalnızca CONTEXT içindeki resmî kaynak bilgilerine dayan. Ön bilgini kullanma.
Soruda adı geçen hizmet, kurum veya iletişim kanalı CONTEXT içinde açıkça yoksa yalnızca KAYNAKTA_YOK yaz.
CONTEXT içinde bulunmayan telefon, adres, web sitesi, mobil uygulama, kurum veya başvuru yolu ekleme.
Genel ve tekrar eden öneriler üretme. Tahmin yapma ve güncel canlı veri üretme.
Sağlık teşhisi veya kesin hukuki görüş verme.
İlk cümlede soruya doğrudan cevap ver. Sonra yalnız kaynakta varsa uygunluk şartını, yapılacak işlemi ve yetkili kurumu belirt.
En fazla 5 kısa cümleyle, sade ve uygulanabilir Türkçe yaz.
Kaynak adlarını cevap içine uydurma; kaynaklar arayüzde ayrıca gösterilecek.
"""


@lru_cache(maxsize=1)
def retrieval_assets() -> tuple[np.ndarray, list[str], dict[str, Chunk]]:
    embeddings, chunk_ids, _meta = load_index()
    return embeddings, chunk_ids, load_chunks()


def build_context(candidates: list[RetrievedChunk]) -> str:
    blocks = []
    for item in candidates:
        chunk = item.chunk
        section = f" | Bölüm: {chunk.section}" if chunk.section else ""
        blocks.append(
            f"[Kaynak: {chunk.title} | Kurum: {chunk.authority}{section}]\n{chunk.text}"
        )
    return "\n\n---\n\n".join(blocks)


def answer_sources(candidates: list[RetrievedChunk]) -> list[AnswerSource]:
    """Aynı belgeden gelen birden çok chunk'ı tek kaynak kartında birleştirir."""
    best: dict[str, RetrievedChunk] = {}
    for item in candidates:
        current = best.get(item.chunk.source_id)
        if current is None or item.score > current.score:
            best[item.chunk.source_id] = item
    return [
        AnswerSource(
            source_id=item.chunk.source_id,
            title=item.chunk.title,
            authority=item.chunk.authority,
            retrieved_at=item.chunk.retrieved_at,
            score=item.score,
        )
        for item in best.values()
    ]


def validate_question(question: str) -> str:
    cleaned = " ".join(question.split())
    if not cleaned:
        raise ValueError("Soru boş olamaz.")
    if len(cleaned) > settings.max_question_chars:
        raise ValueError(f"Soru en fazla {settings.max_question_chars} karakter olabilir.")
    return cleaned


def normalized_words(text: str) -> list[str]:
    """Türkçe karakterleri koruyarak arama/kanıt karşılaştırma sözcükleri üretir."""
    normalized = text.casefold().replace("i̇", "i")
    return re.findall(r"[a-zçğıöşü0-9]+", normalized)


def topic_terms(question: str) -> list[str]:
    """Soru kalıbından ayırt edici ana konu terimlerini çıkarır."""
    return [
        word
        for word in normalized_words(question)
        if len(word) >= 3
        and word not in QUESTION_STOPWORDS
        and not any(word.startswith(prefix) for prefix in GENERIC_PREFIXES)
    ]


def words_match(first: str, second: str) -> bool:
    """Basit Türkçe ek farklılıklarında kök benzerliğini kabul eder."""
    if first == second:
        return True
    shorter, longer = sorted((first, second), key=len)
    return len(shorter) >= 5 and len(longer) - len(shorter) <= 6 and longer.startswith(shorter)


def has_topic_evidence(question: str, candidates: list[RetrievedChunk]) -> bool:
    """Sorunun en az bir ayırt edici terimi getirilen resmî metinde geçiyor mu?"""
    terms = topic_terms(question)
    if not terms:
        return False
    evidence_words: set[str] = set()
    for item in candidates:
        chunk = item.chunk
        evidence_words.update(
            normalized_words(
                " ".join(
                    [
                        chunk.title,
                        chunk.section or "",
                        chunk.text,
                        " ".join(chunk.topic),
                        chunk.city or "",
                    ]
                )
            )
        )
    return any(words_match(term, evidence) for term in terms for evidence in evidence_words)


def insufficient_answer(question: str) -> str:
    words = set(normalized_words(question))
    if "taksi" in words:
        return TAXI_INSUFFICIENT_ANSWER
    return INSUFFICIENT_ANSWER


def is_grounded_answer(text: str, context: str) -> bool:
    """Küçük modelin kaynaksız kanal/iletişim uydurmasını ve tekrarını engeller."""
    if not text or len(text) > 1500 or "KAYNAKTA_YOK" in text.upper():
        return False

    answer_normalized = " ".join(normalized_words(text))
    context_normalized = " ".join(normalized_words(context))
    for marker in UNSUPPORTED_CHANNEL_MARKERS:
        marker_normalized = " ".join(normalized_words(marker))
        if marker_normalized in answer_normalized and marker_normalized not in context_normalized:
            return False

    answer_without_list_numbers = re.sub(r"(?m)^\s*\d+[.)]\s*", "", text)
    answer_numbers = set(re.findall(r"%?\d+(?:[.,]\d+)?", answer_without_list_numbers))
    context_numbers = set(re.findall(r"%?\d+(?:[.,]\d+)?", context))
    if answer_numbers - context_numbers:
        return False

    sentences = [
        " ".join(normalized_words(sentence))
        for sentence in re.split(r"[.!?\n]+", text)
        if len(normalized_words(sentence)) >= 4
    ]
    return len(sentences) == len(set(sentences))


def question_requires_number(question: str) -> bool:
    words = set(normalized_words(question))
    return bool(words & NUMERIC_INTENT_WORDS)


def answer_satisfies_question(question: str, text: str) -> bool:
    """Sorunun istediği zorunlu bilgi türü yanıtta gerçekten var mı?"""
    if question_requires_number(question):
        return bool(re.search(r"%?\d+(?:[.,]\d+)?", text))
    return True


def evidence_units(candidates: list[RetrievedChunk]) -> list[str]:
    """Kaynak metnini kısa cümle ve madde birimlerine ayırır."""
    units: list[str] = []
    for item in candidates:
        for unit in re.split(r"\s+-\s+|(?<=[.!?])\s+|[\r\n]+", item.chunk.text):
            cleaned = " ".join(unit.split()).strip(" -")
            if 15 <= len(cleaned) <= 500 and cleaned not in units:
                units.append(cleaned)
    return units


def verified_fallback(
    question: str, candidates: list[RetrievedChunk]
) -> tuple[str, RetrievedChunk] | None:
    """Model zorunlu olguyu atladığında kısa bir kaynak cümlesi döndürür."""
    if not question_requires_number(question):
        return None

    terms = topic_terms(question)
    def score(unit: str) -> int:
        words = normalized_words(unit)
        return sum(
            1 for term in terms if any(words_match(term, evidence) for evidence in words)
        )

    selected: tuple[str, RetrievedChunk] | None = None
    for candidate in candidates:
        numbered = [
            unit for unit in evidence_units([candidate]) if re.search(r"%?\d", unit)
        ]
        relevant = [unit for unit in numbered if score(unit) > 0]
        if relevant:
            selected = (max(relevant, key=score), candidate)
            break
    if selected is None:
        return None

    best, supporting_candidate = selected
    if len(best) > 360:
        best = best[:357].rsplit(" ", 1)[0] + "…"
    return f"Resmî kaynağa göre: {best}", supporting_candidate


def answer_question(question: str) -> Answer:
    cleaned = validate_question(question)
    embeddings, chunk_ids, chunks = retrieval_assets()
    candidates = retrieve(
        embed_query(cleaned),
        embeddings,
        chunk_ids,
        chunks,
        question=cleaned,
    )
    if not sufficient_context(candidates) or not has_topic_evidence(cleaned, candidates):
        return Answer(answer=insufficient_answer(cleaned), status="insufficient_context")

    context = build_context(candidates)
    response = get_handles().chat_client.complete_chat(
        [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context}"},
            {"role": "user", "content": cleaned},
        ]
    )
    text = response.choices[0].message.content.strip()
    if not is_grounded_answer(text, context) or not answer_satisfies_question(cleaned, text):
        fallback = verified_fallback(cleaned, candidates)
        if fallback:
            fallback_text, supporting_candidate = fallback
            return Answer(
                answer=fallback_text,
                sources=answer_sources([supporting_candidate]),
                status="ok",
            )
        return Answer(answer=insufficient_answer(cleaned), status="insufficient_context")
    return Answer(answer=text, sources=answer_sources(candidates), status="ok")
