"""
Camada de coleta bruta (fetch). Duas estratégias:
- fetch_static: requests, para HTML que não depende de JS.
- fetch_rendered: Playwright, para sites JS-heavy (React/Next.js, etc.).

Agora integrado com cache.py: antes de coletar, checa se já existe
RawPage salvo para a URL.
"""
from __future__ import annotations

import httpx
from playwright.async_api import async_playwright

from services.scraping.schema import RawPage
from services.scraping.cache import load_from_cache, save_to_cache

USER_AGENT = "Mozilla/5.0 (compatible; AIRadarBot/1.0)"


async def fetch_static(url: str, use_cache: bool = True) -> RawPage:
    """Coleta páginas que não dependem de JS (diretórios, notícias)."""
    if use_cache and (cached := load_from_cache(url)):
        return cached

    async with httpx.AsyncClient(
        timeout=20.0,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    page = RawPage(url=url, fetch_method="requests", raw_html=response.text)
    save_to_cache(page)
    return page


async def fetch_rendered(url: str, use_cache: bool = True, wait_ms: int = 2000) -> RawPage:
    """Coleta páginas JS-heavy (sites institucionais, careers pages)."""
    if use_cache and (cached := load_from_cache(url)):
        return cached

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=USER_AGENT)
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(wait_ms)
        html = await page.content()
        await browser.close()

    raw_page = RawPage(url=url, fetch_method="playwright", raw_html=html)
    save_to_cache(raw_page)
    return raw_page