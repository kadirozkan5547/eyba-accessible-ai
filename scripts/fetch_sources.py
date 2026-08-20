"""BUILD MODE: resmî kaynakları indirir ve ham arşive yazar (plan §8.1, §15).

İnternet **yalnız** bu betikte kullanılır; `app/` içinde dış ağ çağrısı yasaktır
(plan §53). Her indirilen dosyanın yanına SHA-256 özeti yazılır ve manifestteki
`retrieved_at` alanı güncellenir.

Kullanım:
    python scripts/fetch_sources.py            # tüm etkin kaynaklar
    python scripts/fetch_sources.py --id afad_afet_cantasi
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import date
from pathlib import Path

import httpx
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.settings import settings  # noqa: E402

USER_AGENT = (
    "AccessibleLocalRAG/1.0 (Microsoft Foundry Local staj projesi; "
    "resmi kaynak arsivleme; build-time)"
)
TIMEOUT_SECONDS = 30.0
MIN_CONTENT_BYTES = 500


def raw_path_for(source: dict, today: date) -> Path:
    scope = "sanliurfa" if source.get("city") else "national"
    return settings.raw_dir / scope / f"{source['id']}_{today.isoformat()}.html"


def fetch_one(client: httpx.Client, source: dict, today: date) -> dict:
    """Tek kaynağı indirir; sonuç sözlüğü döndürür (plan §69)."""
    result = {"id": source["id"], "status": "ok", "note": ""}
    try:
        response = client.get(source["url"])
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001 — rapor edilip devam edilir
        result.update(status="fetch_failed", note=f"{type(exc).__name__}: {exc}")
        return result

    content = response.content
    if len(content) < MIN_CONTENT_BYTES:
        result.update(status="too_short", note=f"{len(content)} bayt")
        return result

    target = raw_path_for(source, today)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)

    digest = hashlib.sha256(content).hexdigest()
    target.with_suffix(".sha256").write_text(f"{digest}  {target.name}\n", encoding="utf-8")

    result.update(
        path=str(target.relative_to(settings.raw_dir.parent)),
        bytes=len(content),
        sha256=digest,
        http_status=response.status_code,
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Resmî kaynakları ham arşive indirir.")
    parser.add_argument("--id", action="append", dest="ids", help="Yalnız bu kaynak id'si")
    args = parser.parse_args()

    manifest = yaml.safe_load(settings.manifest_path.read_text(encoding="utf-8"))
    sources = [s for s in manifest["sources"] if s.get("enabled", True)]
    if args.ids:
        sources = [s for s in sources if s["id"] in set(args.ids)]

    today = date.today()
    results = []
    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
        follow_redirects=True,
    ) as client:
        for source in sources:
            outcome = fetch_one(client, source, today)
            results.append(outcome)
            if outcome["status"] == "ok":
                print(f"[OK]   {outcome['id']:38s} {outcome['bytes']:>8,} bayt")
                source["retrieved_at"] = today.isoformat()
            else:
                print(f"[FAIL] {outcome['id']:38s} {outcome['status']}: {outcome['note']}")

    manifest["version"] = today.isoformat()
    settings.manifest_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{ok}/{len(results)} kaynak indirildi. Manifest güncellendi.")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
