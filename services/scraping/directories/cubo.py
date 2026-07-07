"""
Scraper for Cubo Itaú (cubo.network) – startup hub in São Paulo.

Extracts startup profiles from Cubo blog articles using trafilatura + LLM.
"""
from __future__ import annotations

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

INDEX_URL = "https://blog.cubo.network/"
EXTRACTION_METHOD = "trafilatura+llm_cubo"

# Known section pages to exclude from article listing
_SKIP_PATHS = {
    "/", "/corporates-portfolio", "/events-calendar",
    "/investors-portfolio", "/partners-portfolio",
    "/startups-portfolio", "/todos",
    "/corporates", "/investors", "/partners", "/startups",
}


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
    domain = "https://blog.cubo.network"
    urls: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            href = f"{domain}{href}"
        if not href.startswith(domain):
            continue

        # Skip URLs with fragments (section anchors)
        parsed = urlparse(href)
        if parsed.fragment:
            continue

        path = parsed.path.rstrip("/")
        if path in _SKIP_PATHS or not path:
            continue
        if path.startswith("/tag/"):
            continue

        # Article-like: single segment path (e.g., /proptechs)
        segments = [s for s in path.split("/") if s]
        if len(segments) == 1:
            urls.add(href)

    return sorted(urls)
