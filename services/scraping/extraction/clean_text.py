"""
Extração de texto limpo a partir de HTML bruto, via trafilatura.
Usado para conteúdo "corrido" (sites institucionais, blogs, notícias) --
diretórios estruturados (listagens) usam parser dedicado, feito depois.
"""
from __future__ import annotations

import trafilatura

from services.scraping.schema import RawPage


def clean_text(page: RawPage) -> str | None:
    """Extrai o texto principal da página, descartando menu/footer/ads."""
    if not page.raw_html:
        return None

    return trafilatura.extract(
        page.raw_html,
        include_comments=False,
        include_tables=True,
        favor_precision=True,  # prioriza precisão sobre recall -- menos ruído
    )