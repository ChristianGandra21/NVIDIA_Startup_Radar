"""
Ingestão do Mobile Time.
https://www.mobiletime.com.br/tag/startups/

Estratégia: fetch_static + trafilatura + LLM Extractor.
Notícias taggeadas com "startups".
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from services.scraping.schema import RawPage, StartupProfile
from services.scraping.extraction.clean_text import clean_text
from services.scraping.extraction.llm_extractor import extract_startups

INDEX_URL = "https://www.mobiletime.com.br/tag/startups/"
EXTRACTION_METHOD = "trafilatura+llm_mobiletime"


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


STATIC_PATHS = {
    "/", "/tag/startups/", "/anuncie-conosco/", "/fale-conosco/",
    "/politica-de-privacidade/", "/sobre/", "/equipe/",
    "/cartuns/", "/noticias/", "/colunistas/", "/especial/",
    "/pesquisas/", "/eventos/", "/premio/", "/latam/",
    "/super-bots/",
}


def list_article_urls(index_html: str) -> list[str]:
    soup = BeautifulSoup(index_html, "html.parser")
    urls: set[str] = set()
    domain = "https://www.mobiletime.com.br"
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            href = f"{domain}{href}"
        if not href.startswith(domain):
            continue
        path = href.replace(domain, "")
        if path in STATIC_PATHS or "/page/" in path:
            continue
        if path.strip("/").count("/") >= 1:
            urls.add(href)
    return sorted(urls)
