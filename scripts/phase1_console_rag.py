"""Faz 1 kabul testi (plan §76): Microsoft tutorial akışının çalıştığını doğrular.

5 örnek metin → Foundry Local embedding → cosine similarity → Top-K → chat.
Gerçek bilgi tabanı kullanılmaz; yalnız pipeline doğrulamasıdır.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402

from app.rag.embeddings import embed_query, embed_texts  # noqa: E402
from app.rag.foundry import get_handles  # noqa: E402
from app.rag.retrieval import cosine_similarity  # noqa: E402

SAMPLE_TEXTS = [
    "Engelli kimlik kartı başvurusu Aile ve Sosyal Hizmetler İl Müdürlüklerine yapılır.",
    "Engelli sağlık kurulu raporu, Sağlık Bakanlığınca yetkilendirilmiş sağlık tesislerinden alınır.",
    "İŞKUR'a engelli kaydı, il müdürlükleri veya hizmet merkezleri üzerinden yapılabilir.",
    "EKPSS, engelli memur alımı için ÖSYM tarafından yapılan merkezi sınavdır.",
    "Afet çantası, en az üç günlük temel ihtiyaçları karşılayacak şekilde hazırlanır.",
]

QUESTION = "Engelli kimlik kartına nasıl başvurulur?"
TOP_K = 2


def main() -> int:
    started = time.perf_counter()
    get_handles()
    print(f"Model yükleme: {time.perf_counter() - started:.1f} s")

    doc_vectors = embed_texts(SAMPLE_TEXTS)
    print(f"Doküman embedding: {doc_vectors.shape}")

    query_vector = embed_query(QUESTION)
    scores = cosine_similarity(query_vector, doc_vectors)
    order = np.argsort(scores)[::-1][:TOP_K]

    print(f"\nSoru: {QUESTION}\nTop-{TOP_K}:")
    for rank, idx in enumerate(order, start=1):
        print(f"  {rank}. ({scores[idx]:.3f}) {SAMPLE_TEXTS[idx]}")

    context = "\n".join(f"- {SAMPLE_TEXTS[i]}" for i in order)
    reply = get_handles().chat_client.complete_chat(
        [
            {
                "role": "system",
                "content": (
                    "Yalnızca CONTEXT içindeki bilgilere dayan. Bilgi yoksa "
                    "bilmediğini söyle. Sade Türkçe yaz.\n\nCONTEXT:\n" + context
                ),
            },
            {"role": "user", "content": QUESTION},
        ]
    )
    print("\nCevap:\n" + reply.choices[0].message.content.strip())
    print(f"\nToplam süre: {time.perf_counter() - started:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
