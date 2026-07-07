"""
Smart fetch — decide automaticamente entre fetch_static e fetch_rendered
com base no domínio. Inclui fallback: se fetch_static retornar HTML
muito curto, tenta fetch_rendered.
"""
from __future__ import annotations

from urllib.parse import urlparse

from services.scraping.schema import RawPage
from services.scraping.fetch import fetch_static, fetch_rendered

# Domínios conhecidos por exigir JavaScript rendering
DYNAMIC_DOMAINS = {
    "startse.com",
    "www.startse.com",
    "cubo.network",
    "www.cubo.network",
    "endeavor.org.br",
    "www.endeavor.org.br",
    "latitud.com",
    "www.latitud.com",
    "bossainvest.com",
    "www.bossainvest.com",
    "abstartups.com.br",
    "www.abstartups.com.br",
    "brasil.endeavor.org",
    "blog.cubo.network",
}

# Limiar mínimo de conteúdo HTML para considerar fetch_static suficiente
MIN_HTML_LENGTH = 500


def _extract_domain(url: str) -> str:
    return urlparse(url).netloc.lower()


def _is_dynamic(url: str) -> bool:
    domain = _extract_domain(url)
    return any(d in domain for d in DYNAMIC_DOMAINS)


async def smart_fetch(
    url: str,
    *,
    use_cache: bool = True,
    force_rendered: bool = False,
    fallback_to_rendered: bool = True,
) -> RawPage:
    """Coleta uma página decidindo automaticamente o método.

    1. Se o domínio é conhecido como dinâmico → fetch_rendered
    2. Caso contrário → fetch_static
    3. Se fetch_static retornar HTML muito curto e fallback_to_rendered=True,
       tenta fetch_rendered como fallback.
    """
    if force_rendered or _is_dynamic(url):
        return await fetch_rendered(url, use_cache=use_cache)

    page = await fetch_static(url, use_cache=use_cache)

    if (
        fallback_to_rendered
        and page.raw_html
        and len(page.raw_html) < MIN_HTML_LENGTH
    ):
        return await fetch_rendered(url, use_cache=False)

    return page
