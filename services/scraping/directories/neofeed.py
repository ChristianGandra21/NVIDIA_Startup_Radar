"""
NeoFeed – tech, startups and venture-capital news scraper.

Source: https://neofeed.com.br
Index:  https://neofeed.com.br/blog/startups/

NeoFeed is a prominent Brazilian digital outlet focused on technology,
startups, venture capital and innovation.
"""

from __future__ import annotations

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

# ── constants ────────────────────────────────────────────────────────────────
INDEX_URL = "https://neofeed.com.br/blog/startups/"
EXTRACTION_METHOD = "trafilatura+llm_neofeed"


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
    """Ingest a single NeoFeed article and return extracted profiles."""
    return _extract_from_page(page)


def list_article_urls(category_html: str, base_url: str) -> list[str]:
    """Return sorted article URLs found in a NeoFeed category page.

    Filters out non-article links such as pagination URLs.
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

        # Exclude pagination paths (e.g. /page/2/)
        if "/page/" in href:
            continue

        # Exclude the bare index / category landing page
        if href.rstrip("/") == INDEX_URL.rstrip("/"):
            continue

        # Exclude the bare domain / homepage
        if href.rstrip("/") == base_url.rstrip("/"):
            continue

        urls.add(href)

    return sorted(urls)
