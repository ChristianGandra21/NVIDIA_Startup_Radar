"""
Scraper for Cubo Itaú (cubo.network) – startup hub in São Paulo.

Extracts startup profiles from Cubo blog articles using trafilatura + LLM.
"""
from __future__ import annotations

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

INDEX_URL = "https://cubo.network/blog/"
EXTRACTION_METHOD = "trafilatura+llm_cubo"


def _extract_from_page(page: RawPage) -> list[StartupProfile]:
    text = clean_text(page)
    if not text:
        return []
    return extract_startups(text, source_url=page.url, extraction_method=EXTRACTION_METHOD)


def ingest_article(page: RawPage) -> list[StartupProfile]:
    return _extract_from_page(page)


def list_article_urls(index_html: str) -> list[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(index_html, "html.parser")
    urls: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/blog/") and href != "/blog/":
            urls.add(f"https://cubo.network{href}")
    return sorted(urls)
