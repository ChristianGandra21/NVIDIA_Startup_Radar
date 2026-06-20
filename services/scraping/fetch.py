"""
Camada de coleta bruta (fetch). Decide a estratégia de coleta por
fonte: Playwright para sites JS-heavy, requests para HTML estático.
Implementa cache simples em disco para evitar rescraping durante dev.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
from pathlib import Path

import httpx
from playwright.async_api import async_playwright

from services.scraping.schema import RawPage

CACHE_DIR = Path(".cache/raw_pages")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(url: str) -> Path:
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    return CACHE_DIR / f"{url_hash}.json"


def _load_from_cache(url: str) -> RawPage | None:
    path = _cache_path(url)
    if path.exists():
        return RawPage.model_validate_json(path.read_text())
    return None


def _save_to_cache(page: RawPage) -> None:
    _cache_path(page.url).write_text(page.model_dump_json())


async def fetch_static(url: str, use_cache: bool = True) -> RawPage:
    """Coleta páginas que não dependem de JS (diretórios, notícias)."""
    if use_cache and (cached := _load_from_cache(url)):
        return cached

    async with httpx.AsyncClient(
        timeout=20.0,
        headers={"User-Agent": "Mozilla/5.0 (compatible; AIRadarBot/1.0)"},
        follow_redirects=True,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    page = RawPage(url=url, fetch_method="requests", raw_html=response.text)
    _save_to_cache(page)
    return page


async def fetch_rendered(url: str, use_cache: bool = True, wait_ms: int = 2000) -> RawPage:
    """Coleta páginas JS-heavy (sites institucionais, careers pages)."""
    if use_cache and (cached := _load_from_cache(url)):
        return cached

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page_ctx = await browser.new_page(
            user_agent="Mozilla/5.0 (compatible; AIRadarBot/1.0)"
        )
        await page_ctx.goto(url, wait_until="networkidle", timeout=30000)
        await page_ctx.wait_for_timeout(wait_ms)
        html = await page_ctx.content()
        await browser.close()

    page = RawPage(url=url, fetch_method="playwright", raw_html=html)
    _save_to_cache(page)
    return page


async def fetch_batch(urls: list[str], rendered: bool = False, concurrency: int = 5) -> list[RawPage]:
    """Coleta em lote com limite de concorrência (evita martelar os sites)."""
    semaphore = asyncio.Semaphore(concurrency)
    fetch_fn = fetch_rendered if rendered else fetch_static

    async def _bounded_fetch(url: str) -> RawPage | None:
        async with semaphore:
            try:
                return await fetch_fn(url)
            except Exception as exc:  # noqa: BLE001
                print(f"[fetch_batch] falhou em {url}: {exc}")
                return None

    results = await asyncio.gather(*[_bounded_fetch(u) for u in urls])
    return [r for r in results if r is not None]