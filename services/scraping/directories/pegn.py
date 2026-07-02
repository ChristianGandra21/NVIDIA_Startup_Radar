"""
Ingestão do PEGN — Pequenas Empresas & Grandes Negócios.
https://revistapegn.globo.com/startups/

Estratégia: fetch_static + trafilatura + LLM Extractor.
Notícias sobre startups do ecossistema brasileiro.
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

INDEX_URL = "https://revistapegn.globo.com/startups/"
EXTRACTION_METHOD = "trafilatura+llm_pegn"


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


def list_article_urls(index_html: str) -> list[str]:
    soup = BeautifulSoup(index_html, "html.parser")
    urls: set[str] = set()
    domain = "https://revistapegn.globo.com"
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            href = f"{domain}{href}"
        if not href.startswith(domain):
            continue
        path = href.replace(domain, "")
        if any(x in path for x in ("/page/", "/feed/", "#", "?")):
            continue
        if path.strip("/").count("/") < 2:
            continue
        if "startups" in path:
            urls.add(href)
    return sorted(urls)
