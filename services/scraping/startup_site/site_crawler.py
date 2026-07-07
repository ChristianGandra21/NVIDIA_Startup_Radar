"""
Site Crawler — crawls an individual startup's website to discover and
fetch relevant sub-pages (about, team, product, blog, etc.).

This runs AFTER discovery (directories / news).  Its output is a list
of RawPage objects that the enricher can consume.
"""
from __future__ import annotations

import logging
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from services.scraping.schema import RawPage
from services.scraping.smart_fetch import smart_fetch

logger = logging.getLogger(__name__)

# URL path patterns that typically contain enrichment-worthy content.
# Ordered roughly by value — the crawler will try higher-priority
# patterns first when it needs to respect *max_pages*.
PRIORITY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"/(about|sobre)", re.I),
    re.compile(r"/(team|equipe)", re.I),
    re.compile(r"/(careers|vagas)", re.I),
    re.compile(r"/(product|produto)", re.I),
    re.compile(r"/(technology|tecnologia)", re.I),
    re.compile(r"/(blog)", re.I),
]


def _same_domain(base_url: str, candidate_url: str) -> bool:
    """Return True if *candidate_url* belongs to the same domain as *base_url*."""
    return urlparse(base_url).netloc.lower() == urlparse(candidate_url).netloc.lower()


def _priority_score(url: str) -> int:
    """Lower value == higher priority.  Unmatched URLs get a high score."""
    path = urlparse(url).path
    for idx, pat in enumerate(PRIORITY_PATTERNS):
        if pat.search(path):
            return idx
    return len(PRIORITY_PATTERNS)


def _discover_links(html: str, base_url: str) -> list[str]:
    """Extract unique internal links from *html*, resolved against *base_url*."""
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    links: list[str] = []

    for anchor in soup.find_all("a", href=True):
        href: str = anchor["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue

        absolute = urljoin(base_url, href)
        # Strip fragment / query for dedup purposes
        parsed = urlparse(absolute)
        clean = parsed._replace(fragment="", query="").geturl()

        if clean in seen:
            continue
        if not _same_domain(base_url, clean):
            continue

        seen.add(clean)
        links.append(clean)

    return links


async def crawl_startup_site(
    website_url: str,
    max_pages: int = 5,
) -> list[RawPage]:
    """Crawl a startup's website and return up to *max_pages* RawPage objects.

    1. Fetch the main page.
    2. Discover internal links from the main page HTML.
    3. Prioritise links that match enrichment-relevant URL patterns.
    4. Fetch sub-pages (best-effort — a single failure does not abort).

    Returns
    -------
    list[RawPage]
        The main page followed by the most relevant sub-pages.
    """
    pages: list[RawPage] = []

    # --- 1. Main page ---
    try:
        main_page = await smart_fetch(website_url)
        pages.append(main_page)
    except Exception:
        logger.exception("Failed to fetch main page: %s", website_url)
        return pages  # nothing else to do without the main page

    if max_pages <= 1 or not main_page.raw_html:
        return pages

    # --- 2. Discover & prioritise sub-page links ---
    candidates = _discover_links(main_page.raw_html, website_url)
    candidates.sort(key=_priority_score)

    # Only keep pages that match at least one priority pattern (unless we
    # have very few candidates, in which case we take what we can get).
    relevant = [c for c in candidates if _priority_score(c) < len(PRIORITY_PATTERNS)]
    if not relevant:
        relevant = candidates

    # Cap at (max_pages - 1) because the main page already counts.
    relevant = relevant[: max_pages - 1]

    # --- 3. Fetch sub-pages (best-effort) ---
    for url in relevant:
        try:
            page = await smart_fetch(url)
            pages.append(page)
        except Exception:
            logger.warning("Skipping failed sub-page: %s", url, exc_info=True)
            continue

    return pages
