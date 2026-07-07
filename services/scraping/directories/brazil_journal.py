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

    Filters out non-article links such as category, tag, pagination and
    section-page URLs.
    """
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse

    soup = BeautifulSoup(category_html, "html.parser")
    urls: set[str] = set()

    parsed_base = urlparse(base_url)
    domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

    skip_prefixes = (
        "/hot-topic/", "/author/", "/brands", "/anuncie",
        "/newsletter", "/podcasts", "/videos", "/eventos",
        "/institucional", "/ultimas",
    )

    for anchor in soup.find_all("a", href=True):
        href: str = anchor["href"]

        # Normalise relative URLs
        if href.startswith("/"):
            href = domain + href
        elif not href.startswith(domain):
            continue

        # Exclude category, tag and pagination paths
        if "/categoria/" in href or "/tag/" in href or "/page/" in href:
            continue

        # Exclude the bare domain / homepage and the index page itself
        clean = href.rstrip("/")
        if clean == domain.rstrip("/") or clean == base_url.rstrip("/"):
            continue

        # Exclude known section-page prefixes
        path = urlparse(href).path.rstrip("/")
        if path.startswith(skip_prefixes):
            continue

        # Only keep paths whose last segment looks like an article slug
        # (at least 2 hyphens and >15 chars — filters out section pages)
        last_seg = path.split("/")[-1] if path else ""
        if last_seg.count("-") < 2 or len(last_seg) <= 15:
            continue

        urls.add(href)

    return sorted(urls)
