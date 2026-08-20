"""BUILD MODE: ham HTML'i frontmatter'lı Markdown'a normalize eder (plan §16).

Kaldırılan: script, style, nav, header, footer, aside, form, iframe, cookie
banner, paylaşım/sosyal medya blokları, erişilebilirlik overlay'leri.
Korunan: başlıklar, paragraflar, listeler, tablolar (metne çevrilir).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.settings import settings  # noqa: E402

DROP_TAGS = (
    "script", "style", "noscript", "nav", "header", "footer", "aside",
    "iframe", "svg", "button", "select", "input", "template",
)
# ASP.NET WebForms sayfalarında tüm gövde tek bir <form> içindedir; bu yüzden
# form koşulsuz silinmez, yoğunluk kuralına tabi tutulur.
DENSITY_GUARDED_TAGS = ("form",)
DROP_PATTERN = re.compile(
    r"cookie|cerez|çerez|navbar|main-menu|breadcrumb|social-|-social|sosyal-medya|"
    r"paylas|paylaş|share-|footer|site-header|sidebar|banner|popup|"
    r"erisilebilirlik-arac|accessibility-widget|skip-link|search-box",
    re.IGNORECASE,
)
# Bir kapsayıcı gürültü desenine uysa bile sayfanın metninin büyük bölümünü
# taşıyorsa silinmez — aksi hâlde asıl içerik (ör. modal içindeki hastane
# listesi) kaybolur.
KEEP_IF_TEXT_OVER = 1200
KEEP_IF_TEXT_RATIO = 0.25
BLOCK_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "dt", "dd")
MIN_TEXT_LENGTH = 25
MIN_USABLE_CHARS = 400


def strip_noise(soup: BeautifulSoup) -> None:
    for tag in soup(list(DROP_TAGS)):
        tag.decompose()
    body_length = len(soup.get_text(" ", strip=True))

    def carries_content(tag: Tag) -> bool:
        text_length = len(tag.get_text(" ", strip=True))
        return text_length > KEEP_IF_TEXT_OVER or text_length > body_length * KEEP_IF_TEXT_RATIO

    for tag in soup.find_all(list(DENSITY_GUARDED_TAGS)):
        if tag.attrs is not None and not carries_content(tag):
            tag.decompose()

    for tag in soup.find_all(True):
        if tag.attrs is None:  # üst öğesiyle birlikte zaten kaldırılmış
            continue
        identifier = " ".join(
            filter(None, [tag.get("id", ""), " ".join(tag.get("class", []) or [])])
        )
        if not identifier or not DROP_PATTERN.search(identifier):
            continue
        if carries_content(tag):
            continue
        tag.decompose()


def pick_content_root(soup: BeautifulSoup) -> Tag:
    """Metin yoğunluğu en yüksek kapsayıcıyı seçer."""
    # Kurum sitelerinin bilinen semantik içerik kapsayıcıları, genel yoğunluk
    # hesabından daha güvenilirdir. Menü ağaçları çoğu zaman asıl yazıdan daha
    # uzun olduğu için önce bu dar kökler denenir.
    for selector in (
        ".detail-content-container",  # AFAD
        ".contentAreaForPages",  # İŞKUR
        "#main_contents",       # Sağlık Bakanlığı
        "#duyuru-kartlar",      # ÖSYM sınav duyuruları
        "main.page-content",    # Şanlıurfa Büyükşehir Belediyesi
    ):
        root = soup.select_one(selector)
        if root is not None:
            return root

    candidates = soup.find_all(["main", "article", "section", "div"])
    best, best_score = soup.body or soup, 0
    for tag in candidates:
        text_length = len(tag.get_text(" ", strip=True))
        block_count = len(tag.find_all(BLOCK_TAGS))
        score = text_length * (1 + block_count)
        if block_count >= 3 and score > best_score:
            best, best_score = tag, score
    return best


def to_markdown(root: Tag) -> str:
    if root.get("id") == "duyuru-kartlar":
        items = []
        for tag in root.select(".duyuru-list-item"):
            text = " ".join(tag.get_text(" ", strip=True).split())
            if text:
                items.append(f"- {text}")
        return "\n".join(items)

    lines: list[str] = []
    seen: set[str] = set()
    for tag in root.find_all(BLOCK_TAGS):
        text = " ".join(tag.get_text(" ", strip=True).split())
        is_heading = tag.name in ("h1", "h2", "h3", "h4", "h5", "h6")
        if (len(text) < MIN_TEXT_LENGTH and not is_heading) or not text or text in seen:
            continue
        seen.add(text)
        if tag.name in ("h1", "h2", "h3", "h4"):
            level = "#" * (int(tag.name[1]) + 1)  # H1 belgede tek kalsın diye kaydırılır
            lines.append(f"\n{level} {text}\n")
        elif tag.name in ("h5", "h6"):
            lines.append(f"\n###### {text}\n")
        elif tag.name in ("li", "dt", "dd"):
            lines.append(f"- {text}")
        else:
            lines.append(text + "\n")
    return "\n".join(lines).strip()


def extract_lines(raw_file: Path) -> list[str]:
    """Ham HTML'den Markdown satırlarını çıkarır (henüz dosyaya yazmadan)."""
    soup = BeautifulSoup(raw_file.read_text(encoding="utf-8", errors="replace"), "html.parser")
    strip_noise(soup)
    return to_markdown(pick_content_root(soup)).splitlines()


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower()


def boilerplate_lines(per_source: dict[str, list[str]], hosts: dict[str, str]) -> set[str]:
    """Aynı alan adındaki birden fazla sayfada geçen satırlar menü/footer sayılır.

    Sağlık Bakanlığı ve AFAD sayfalarında asıl içeriğin yanına devasa kenar menüsü
    geliyor; tek sayfaya bakarak bunu ayırmak güvenilir değil, alan içi tekrar ise
    güvenilir bir sinyal (ölçüm: saglik ortak/toplam = 0.99, aile = 0.00).
    """
    counts: dict[tuple[str, str], int] = {}
    source_counts: dict[str, int] = {}
    for source_id, lines in per_source.items():
        host = hosts[source_id]
        source_counts[host] = source_counts.get(host, 0) + 1
        for line in {l.strip() for l in lines if len(l.strip()) > MIN_TEXT_LENGTH}:
            counts[(host, line)] = counts.get((host, line), 0) + 1
    # İki sayfalı alanlarda aynı satır gerçek içerik de olabilir (ör. bir
    # kategori sayfasındaki hizmet adı ve o hizmetin detay sayfası). En az üç
    # örnek olmadan ortak satırı menü saymak güvenli değildir.
    return {
        line
        for (host, line), count in counts.items()
        if source_counts[host] >= 3 and count >= 2
    }


def normalize_one(source: dict, lines: list[str], drop: set[str]) -> tuple[Path, int]:
    body = "\n".join(line for line in lines if line.strip() not in drop).strip()

    frontmatter = {
        "source_id": source["id"],
        "title": source["title"],
        "authority": source["authority"],
        "source_tier": source["source_tier"],
        "url": source["url"],
        "retrieved_at": source["retrieved_at"],
        "language": source["language"],
        "topic": source["topic"],
        "country": source["country"],
        "city": source["city"],
    }
    document = (
        "---\n"
        + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
        + "---\n\n"
        + f"# {source['title']}\n\n"
        + body
        + f"\n\n## Kaynak\n\n{source['authority']} — {source['url']}\n"
    )

    scope = "sanliurfa" if source.get("city") else "national"
    target = settings.normalized_dir / scope / f"{source['id']}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")
    return target, len(body)


def latest_raw_file(source: dict) -> Path | None:
    scope = "sanliurfa" if source.get("city") else "national"
    matches = sorted((settings.raw_dir / scope).glob(f"{source['id']}_*.html"))
    return matches[-1] if matches else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Ham HTML'i Markdown'a normalize eder.")
    parser.add_argument("--id", action="append", dest="ids")
    args = parser.parse_args()

    manifest = yaml.safe_load(settings.manifest_path.read_text(encoding="utf-8"))
    sources = [s for s in manifest["sources"] if s.get("enabled", True)]
    if args.ids:
        sources = [s for s in sources if s["id"] in set(args.ids)]

    extracted: dict[str, list[str]] = {}
    hosts: dict[str, str] = {}
    source_by_id: dict[str, dict] = {}
    for source in sources:
        raw_file = latest_raw_file(source)
        if raw_file is None:
            print(f"[SKIP] {source['id']:38s} ham dosya yok")
            continue
        source_id = source["id"]
        extracted[source_id] = extract_lines(raw_file)
        hosts[source_id] = host_of(source["url"])
        source_by_id[source_id] = source

    drop = boilerplate_lines(extracted, hosts)
    print(f"Alan içi tekrar eden {len(drop)} boilerplate satırı elenecek.\n")

    done = 0
    for source_id, lines in extracted.items():
        source = source_by_id[source_id]
        target, length = normalize_one(source, lines, drop)
        flag = "OK  " if length >= 400 else "THIN"
        print(f"[{flag}] {source['id']:38s} {length:>7,} karakter -> {target.name}")
        done += 1
    print(f"\n{done} kaynak normalize edildi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
