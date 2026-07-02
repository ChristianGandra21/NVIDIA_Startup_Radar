"""
Ingestão da Liga Ventures Insights.
https://liga.ventures/insights/startups/

Estratégia: fetch_static + trafilatura + LLM Extractor.
Os artigos são corridos (texto), sem cards estruturados no HTML.
"""
from __future__ import annotations

from services.scraping.schema import RawPage, StartupProfile, SourceEvidence
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

LIGA_INDEX_URL = "https://liga.ventures/insights/startups/"
EXTRACTION_METHOD = "trafilatura+llm_liga"


def _extract_from_page(page: RawPage) -> list[StartupProfile]:
    """Extrai startups do texto limpo de um artigo."""
    text = clean_text(page)
    if not text:
        return []

    return extract_startups(
        text,
        source_url=page.url,
        extraction_method=EXTRACTION_METHOD,
    )


def ingest_article(page: RawPage) -> list[StartupProfile]:
    """Processa um artigo individual da Liga Ventures."""
    return _extract_from_page(page)


def list_article_urls(index_html: str) -> list[str]:
    """Extrai URLs de artigos da página de listagem (filtra paginação)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(index_html, "html.parser")
    urls: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/insights/artigos/" in href:
            urls.add(href)
    return sorted(urls)
