"""
Ingestão do Startups.com.br.
https://startups.com.br

Estratégia: fetch_static + trafilatura + LLM Extractor.
Artigos de notícias sobre startups brasileiras (investimentos, IA, etc.).
"""
from __future__ import annotations

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

STARTUPSBR_URL = "https://startups.com.br"
EXTRACTION_METHOD = "trafilatura+llm_startupsbr"


def _extract_from_page(page: RawPage) -> list[StartupProfile]:
    text = clean_text(page)
    if not text:
        return []

    return extract_startups(
        text,
        source_url=page.url,
        extraction_method=EXTRACTION_METHOD,
    )


def ingest_article(page: RawPage) -> list[StartupProfile]:
    return _extract_from_page(page)


def list_article_urls(category_html: str, base_url: str) -> list[str]:
    """Extrai URLs de artigos de uma página de categoria."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(category_html, "html.parser")
    urls: set[str] = set()
    domain = "https://startups.com.br"
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(domain) and "/negocios/" in href:
            urls.add(href)
        elif href.startswith("/negocios/"):
            urls.add(f"{domain}{href}")
    return sorted(urls)
