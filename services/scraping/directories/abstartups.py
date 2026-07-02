"""
Scraper for Abstartups (abstartups.com.br) – Brazilian Startup Association.

Extracts startup profiles from Abstartups news articles using trafilatura + LLM.
"""
from __future__ import annotations

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

INDEX_URL = "https://abstartups.com.br/category/noticias/"
EXTRACTION_METHOD = "trafilatura+llm_abstartups"


def _extract_from_page(page: RawPage) -> list[StartupProfile]:
    text = clean_text(page)
    if not text:
        return []
    return extract_startups(text, source_url=page.url, extraction_method=EXTRACTION_METHOD)


def ingest_article(page: RawPage) -> list[StartupProfile]:
    return _extract_from_page(page)


def list_article_urls(index_html: str) -> list[str]:
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse

    soup = BeautifulSoup(index_html, "html.parser")
    domain = "https://abstartups.com.br"
    urls: set[str] = set()
    skip_prefixes = ("/category/", "/tag/", "/page/", "/author/", "/wp-")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Normalize relative URLs
        if href.startswith("/"):
            href = f"{domain}{href}"
        if not href.startswith(domain):
            continue
        path = urlparse(href).path.rstrip("/")
        if not path or path == "":
            continue
        if any(path.startswith(p) for p in skip_prefixes):
            continue
        # Only include paths with at least some depth (articles)
        if path.strip("/").count("/") == 0 and len(path.strip("/")) > 3:
            urls.add(href)
        elif path.strip("/").count("/") >= 1:
            urls.add(href)
    return sorted(urls)
