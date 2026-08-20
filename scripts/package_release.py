"""Doğrulanmış EYBA kaynak paketini ve SHA-256 dosyasını üretir."""

from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.settings import BASE_DIR, settings  # noqa: E402

RELEASE_FILES = (
    "VERSION",
    "README.md",
    "PROJECT_SPEC.md",
    "DEVAM_DURUMU.md",
    "requirements.txt",
    "requirements-dev.txt",
    "baslat.bat",
    "app",
    "knowledge/chunks",
    "knowledge/index",
    "knowledge/manifest",
    "docs",
    "scripts/prepare_models.py",
    "scripts/run_offline_acceptance.py",
    "scripts/validate_knowledge.py",
)


def included_files() -> list[Path]:
    files: list[Path] = []
    for relative in RELEASE_FILES:
        path = BASE_DIR / relative
        if not path.exists():
            raise FileNotFoundError(f"Paket için zorunlu yol eksik: {relative}")
        candidates = path.rglob("*") if path.is_dir() else (path,)
        files.extend(
            candidate
            for candidate in candidates
            if candidate.is_file()
            and "__pycache__" not in candidate.parts
            and candidate.suffix not in {".pyc", ".pyo"}
        )
    return sorted(set(files))


def main() -> int:
    version = (BASE_DIR / "VERSION").read_text(encoding="utf-8").strip()
    if version != settings.app_version:
        raise ValueError("VERSION ile settings.app_version aynı olmalıdır.")

    dist_dir = BASE_DIR / "dist"
    dist_dir.mkdir(exist_ok=True)
    archive = dist_dir / f"eyba-{version}.zip"
    prefix = f"eyba-{version}"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in included_files():
            bundle.write(path, Path(prefix) / path.relative_to(BASE_DIR))

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(".zip.sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    print(f"Paket: {archive}")
    print(f"SHA-256: {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
