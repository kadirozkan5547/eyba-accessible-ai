"""Önbellekteki bir chat modelini sabit resmî bağlamlarla hızlıca değerlendirir."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from foundry_local_sdk import Configuration, FoundryLocalManager  # noqa: E402

from app.rag.retrieval import load_chunks  # noqa: E402
from app.rag.schemas import RetrievedChunk  # noqa: E402
from app.services.rag_service import SYSTEM_PROMPT, build_context  # noqa: E402

CASES = (
    ("İŞKUR'a engelli olarak kayıt olmak için rapor oranı kaç olmalı?", "iskur_engelli_kaydi"),
    ("Afet çantasında hangi malzemeler bulunmalı?", "afad_afet_cantasi"),
    ("EKPSS başvuru ve sınav duyurularını hangi kurum yayımlar?", "osym_ekpss"),
    (
        "Şanlıurfa Engelliler Koordinasyon ve Yaşam Merkezi hangi hizmetleri sunuyor?",
        "sanliurfa_koordinasyon_merkezi",
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    args = parser.parse_args()

    FoundryLocalManager.initialize(Configuration(app_name="accessible_local_rag"))
    model = FoundryLocalManager.instance.catalog.get_model(args.model)
    if not model.is_cached:
        print(f"Model önbellekte değil: {args.model}")
        return 2
    model.load()
    client = model.get_chat_client()
    chunks = load_chunks()

    for number, (question, source_id) in enumerate(CASES, start=1):
        candidates = [
            RetrievedChunk(chunk=chunk, score=1.0)
            for chunk in chunks.values()
            if chunk.source_id == source_id
        ][:3]
        context = build_context(candidates)
        started = time.perf_counter()
        response = client.complete_chat(
            [
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context}"},
                {"role": "user", "content": f"/no_think\n{question}"},
            ]
        )
        elapsed = time.perf_counter() - started
        print(f"\n[{number}/{len(CASES)}] {question}")
        print(f"Süre: {elapsed:.1f} sn")
        print(response.choices[0].message.content.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
