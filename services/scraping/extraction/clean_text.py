"""
Extração de texto limpo a partir de HTML bruto, via trafilatura com fallback bs4.
Usado para conteúdo "corrido" (sites institucionais, blogs, notícias) --
diretórios estruturados (listagens) usam parser dedicado, feito depois.
"""
from __future__ import annotations

import trafilatura
from bs4 import BeautifulSoup

from services.scraping.schema import RawPage


def _bs4_fallback(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return "\n".join(lines) if lines else None


def clean_text(page: RawPage) -> str | None:
    if not page.raw_html:
        return None

    text = trafilatura.extract(
        page.raw_html,
        include_comments=False,
        include_tables=True,
        favor_precision=False,
    )

    if text and len(text) > 200:
        return text

    return _bs4_fallback(page.raw_html)