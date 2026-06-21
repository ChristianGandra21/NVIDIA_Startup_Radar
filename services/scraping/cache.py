"""
Cache simples em disco para RawPage, baseado em hash da URL.
Evita rescraping ao testar/reprocessar durante o desenvolvimento.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from services.scraping.schema import RawPage

CACHE_DIR = Path(".cache/raw_pages")


def _cache_path(url: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    return CACHE_DIR / f"{url_hash}.json"


def load_from_cache(url: str) -> RawPage | None:
    path = _cache_path(url)
    if path.exists():
        return RawPage.model_validate_json(path.read_text())
    return None


def save_to_cache(page: RawPage) -> None:
    _cache_path(page.url).write_text(page.model_dump_json())