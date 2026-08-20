"""On resmî soruyla gerçek embedding -> retrieval -> chat kabul turu."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.foundry import is_cached  # noqa: E402
from app.services.rag_service import answer_question  # noqa: E402
from app.settings import BASE_DIR, settings  # noqa: E402

CASES = [
    ("Afet çantasında hangi malzemeler bulunmalı?", "afad_afet_cantasi"),
    ("Deprem sırasında binadaysam ne yapmalıyım?", "afad_deprem_onlemler"),
    ("Engellilere şehirlerarası otobüslerde indirim var mı?", "aile_indirim_muafiyetler"),
    ("Engellilerin Haklarına İlişkin Sözleşme'nin amacı nedir?", "aile_engelli_haklari_sozlesme"),
    ("e-Devlet'te engelli kimlik kartı başvurusu yapılabilir mi?", "edevlet_engelsiz_hizmetler"),
    ("İŞKUR'a engelli olarak kayıt olmak için rapor oranı kaç olmalı?", "iskur_engelli_kaydi"),
    ("Özel sektör işyerlerinde engelli çalıştırma kotası yüzde kaç?", "iskur_engelli_istihdami"),
    ("EKPSS başvuru ve sınav duyurularını hangi kurum yayımlar?", "osym_ekpss"),
    ("Engelli sağlık kurulu raporu vermeye yetkili hastane listesine nereden ulaşılır?", "saglik_yetkili_tesisler"),
    ("Şanlıurfa Engelliler Koordinasyon ve Yaşam Merkezi hangi hizmetleri sunuyor?", "sanliurfa_koordinasyon_merkezi"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--network-condition",
        choices=("unspecified", "restricted", "wifi-off-manual"),
        default="unspecified",
        help="Test sırasında doğrulanan ağ koşulu.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "tests" / "acceptance" / "offline_acceptance_report.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cached = {
        settings.embedding_model: is_cached(settings.embedding_model),
        settings.chat_model: is_cached(settings.chat_model),
    }
    rows: list[dict] = []
    started = time.perf_counter()

    if not all(cached.values()):
        print("FAIL: Yerel modellerden en az biri önbellekte değil.")
    else:
        for number, (question, expected_source) in enumerate(CASES, start=1):
            case_started = time.perf_counter()
            try:
                response = answer_question(question)
                source_ids = [source.source_id for source in response.sources]
                passed = (
                    response.status == "ok"
                    and bool(response.answer.strip())
                    and expected_source in source_ids
                )
                row = {
                    "number": number,
                    "question": question,
                    "expected_source": expected_source,
                    "status": response.status,
                    "source_ids": source_ids,
                    "answer": response.answer,
                    "elapsed_seconds": round(time.perf_counter() - case_started, 2),
                    "passed": passed,
                }
            except Exception as exc:  # kabul raporunda tek vaka tüm turu kesmemeli
                row = {
                    "number": number,
                    "question": question,
                    "expected_source": expected_source,
                    "error": f"{type(exc).__name__}: {exc}",
                    "elapsed_seconds": round(time.perf_counter() - case_started, 2),
                    "passed": False,
                }
            rows.append(row)
            print(f"[{number:02d}/10] {'PASS' if row['passed'] else 'FAIL'} - {question}")

    passed_count = sum(bool(row.get("passed")) for row in rows)
    report = {
        "result": "PASS" if passed_count == len(CASES) and all(cached.values()) else "FAIL",
        "run_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "network_condition": args.network_condition,
        "platform": platform.platform(),
        "app_version": settings.app_version,
        "knowledge_version": settings.knowledge_version,
        "models_cached": cached,
        "passed_count": passed_count,
        "case_count": len(CASES),
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "cases": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sonuç: {report['result']} ({passed_count}/{len(CASES)})")
    print(f"Rapor: {args.output}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
