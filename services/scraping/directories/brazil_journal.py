"""
Brazil Journal – startup and business news scraper.

Source: https://braziljournal.com
Index:  https://braziljournal.com/categoria/startups/

Brazil Journal is one of Brazil's leading business-news outlets, covering
startups, venture capital, M&A and the broader tech ecosystem.
"""

from __future__ import annotations

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

# ── constants ────────────────────────────────────────────────────────────────
INDEX_URL = "https://braziljournal.com/categoria/startups/"
EXTRACTION_METHOD = "trafilatura+llm_braziljournal"


# ── helpers ──────────────────────────────────────────────────────────────────
def _extract_from_page(page: RawPage) -> list[StartupProfile]:
    """Clean the raw page and run LLM-based startup extraction."""
    text = clean_text(page)
    if not text:
        return []
    return extract_startups(
        text,
        source_url=page.url,
        extraction_method=EXTRACTION_METHOD,
    )


# ── public API ───────────────────────────────────────────────────────────────
def ingest_article(page: RawPage) -> list[StartupProfile]:
    """Ingest a single Brazil Journal article and return extracted profiles."""
    return _extract_from_page(page)


def list_article_urls(category_html: str, base_url: str) -> list[str]:
    """Return sorted article URLs found in a Brazil Journal category page.

    Filters out non-article links such as category, tag and pagination URLs.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(category_html, "html.parser")
    urls: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href: str = anchor["href"]

        # Ensure the link belongs to the same domain
        if not href.startswith(base_url) and not href.startswith("/"):
            continue

        # Normalise relative URLs
        if href.startswith("/"):
            href = base_url.rstrip("/") + href

        # Exclude category, tag and pagination paths
        if "/categoria/" in href or "/tag/" in href or "/page/" in href:
            continue

        # Exclude the bare domain / homepage
        if href.rstrip("/") == base_url.rstrip("/"):
            continue

        urls.add(href)

    return sorted(urls)
