"""
Exame – business magazine startup news scraper.

Source: https://exame.com
Index:  https://exame.com/bussola/startups/

Exame is one of Brazil's most influential business magazines, with a
dedicated section covering startups and innovation.
"""

from __future__ import annotations

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

# ── constants ────────────────────────────────────────────────────────────────
INDEX_URL = "https://exame.com/tag/startups/"
EXTRACTION_METHOD = "trafilatura+llm_exame"


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
    """Ingest a single Exame article and return extracted profiles."""
    return _extract_from_page(page)


def list_article_urls(category_html: str, base_url: str) -> list[str]:
    """Return sorted article URLs found in an Exame category page.

    Filters out the category landing page itself and pagination URLs.
    """
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse

    soup = BeautifulSoup(category_html, "html.parser")
    urls: set[str] = set()

    parsed_base = urlparse(base_url)
    domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

    skip_prefixes = (
        "/newsletters", "/edicoes", "/colunistas",
        "/ultimas-noticias", "/institucional",
    )

    for anchor in soup.find_all("a", href=True):
        href: str = anchor["href"]

        # Normalise relative URLs
        if href.startswith("/"):
            href = domain + href
        elif not href.startswith(domain):
            continue

        # Exclude pagination paths (e.g. /page/2/ or ./2/)
        if "/page/" in href or href.startswith("./"):
            continue

        # Exclude the index page itself and the bare domain
        clean = href.rstrip("/")
        if clean == base_url.rstrip("/") or clean == domain.rstrip("/"):
            continue

        # Exclude known section-page prefixes
        path = urlparse(href).path.rstrip("/")
        if path.startswith(skip_prefixes):
            continue

        # Only keep paths whose last segment looks like an article slug
        last_seg = path.split("/")[-1] if path else ""
        if last_seg.count("-") < 2 or len(last_seg) <= 15:
            continue

        urls.add(href)

    return sorted(urls)
