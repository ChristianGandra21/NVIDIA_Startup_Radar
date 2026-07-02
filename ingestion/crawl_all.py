"""
Script único para crawlear e ingerir todas as fontes no banco.
Uso:  python -m ingestion.crawl_all

Fontes implementadas:
  - ACE Ventures (portfólio BS4)
  - Distrito Blog (trafilatura + LLM)
  - Liga Ventures Insights (trafilatura + LLM)
  - Startups.com.br (trafilatura + LLM)
  - InovAtiva Brasil (planilha XLSX)
  - StartSe (trafilatura + LLM)
  - Cubo Itaú (trafilatura + LLM)
  - Abstartups (trafilatura + LLM)
  - Endeavor Brasil (trafilatura + LLM)
  - Latitud (trafilatura + LLM)
  - Brazil Journal (trafilatura + LLM)
  - NeoFeed (trafilatura + LLM)
  - Exame Startups (trafilatura + LLM)
  + Enriquecimento via crawl dos sites individuais das startups
"""
from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from services.scraping.fetch import fetch_static
from services.scraping.smart_fetch import smart_fetch
from services.scraping.directories import (
    parse_portfolio,
    ingest_liga,
    ingest_distrito,
    ingest_startupsbr,
    ingest_startse,
    ingest_cubo,
    ingest_abstartups,
    ingest_endeavor,
    ingest_latitud,
    ingest_braziljournal,
    ingest_neofeed,
    ingest_exame,
)
from services.scraping.directories.ace_ventures import ACE_URL
from services.scraping.directories.liga_ventures import (
    LIGA_INDEX_URL,
    list_article_urls as liga_list,
)
from services.scraping.directories.distrito import (
    DISTRITO_BLOG_URL,
    list_article_urls as distrito_list,
)
from services.scraping.directories.startupsbr import (
    list_article_urls as startupsbr_list,
)
from services.scraping.directories.startse import (
    INDEX_URL as STARTSE_INDEX_URL,
    list_article_urls as startse_list,
)
from services.scraping.directories.cubo import (
    INDEX_URL as CUBO_INDEX_URL,
    list_article_urls as cubo_list,
)
from services.scraping.directories.abstartups import (
    INDEX_URL as ABSTARTUPS_INDEX_URL,
    list_article_urls as abstartups_list,
)
from services.scraping.directories.endeavor import (
    INDEX_URL as ENDEAVOR_INDEX_URL,
    list_article_urls as endeavor_list,
)
from services.scraping.directories.latitud import (
    INDEX_URL as LATITUD_INDEX_URL,
    list_article_urls as latitud_list,
)
from services.scraping.directories.brazil_journal import (
    INDEX_URL as BRAZILJOURNAL_INDEX_URL,
    list_article_urls as braziljournal_list,
)
from services.scraping.directories.neofeed import (
    INDEX_URL as NEOFEED_INDEX_URL,
    list_article_urls as neofeed_list,
)
from services.scraping.directories.exame import (
    INDEX_URL as EXAME_INDEX_URL,
    list_article_urls as exame_list,
)
from services.scraping.schema import StartupProfile
from services.scraping.startup_site import crawl_startup_site, enrich_profile
from ingestion.runner import merge_profiles
from ingestion.spreadsheet import ingest_inovativa
from db.repository import save_profiles


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


async def _ingest_articles(
    source_name: str,
    index_url: str,
    list_fn,
    ingest_fn,
    *,
    use_smart_fetch: bool = False,
    max_articles: int | None = None,
    list_fn_extra_args: tuple = (),
) -> list[StartupProfile]:
    """Helper genérico para fontes baseadas em artigos.

    1. Fetch da página-índice
    2. Extrai URLs de artigos
    3. Para cada artigo, fetch + ingest
    """
    try:
        if use_smart_fetch:
            index_page = await smart_fetch(index_url)
        else:
            index_page = await fetch_static(index_url)

        articles = list_fn(index_page.raw_html, *list_fn_extra_args)
    except Exception as e:
        _log(f"[{source_name}] Erro ao listar artigos: {e}")
        return []

    _log(f"[{source_name}] {len(articles)} artigos encontrados")

    if max_articles:
        articles = sorted(articles)[:max_articles]

    profiles: list[StartupProfile] = []
    for url in sorted(articles):
        try:
            if use_smart_fetch:
                page = await smart_fetch(url)
            else:
                page = await fetch_static(url)
            extracted = ingest_fn(page)
            profiles.extend(extracted)
            slug = url.rstrip("/").split("/")[-1][:40]
            _log(f"  +{len(extracted)} de {slug}")
        except Exception as e:
            _log(f"  Erro {url}: {e}")

    return profiles


# ---------------------------------------------------------------------------
# Ingestão por fonte
# ---------------------------------------------------------------------------

async def ingest_ace() -> list[StartupProfile]:
    _log("[ACE] Fetching portfolio...")
    page = await fetch_static(ACE_URL)
    profiles = parse_portfolio(page)
    _log(f"[ACE] {len(profiles)} startups")
    return profiles


async def ingest_startupsbr_ia() -> list[StartupProfile]:
    category_urls = [
        "https://startups.com.br/negocios/inteligencia-artificial/",
        "https://startups.com.br/negocios/rodada-de-investimento/",
    ]
    all_articles: set[str] = set()
    for list_url in category_urls:
        try:
            page = await fetch_static(list_url)
            articles = startupsbr_list(page.raw_html, list_url)
            all_articles.update(articles)
        except Exception as e:
            _log(f"  Erro listing {list_url}: {e}")

    _log(f"[Startups.com.br] {len(all_articles)} artigos encontrados")

    profiles: list[StartupProfile] = []
    for url in sorted(all_articles):
        try:
            page = await fetch_static(url)
            extracted = ingest_startupsbr(page)
            profiles.extend(extracted)
            slug = url.rstrip("/").split("/")[-1]
            _log(f"  +{len(extracted)} de {slug[:40]}")
        except Exception as e:
            _log(f"  Erro {url}: {e}")
    return profiles


async def ingest_distrito_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "Distrito", DISTRITO_BLOG_URL, distrito_list, ingest_distrito,
    )


async def ingest_liga_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "Liga Ventures", LIGA_INDEX_URL, liga_list, ingest_liga,
    )


async def ingest_startse_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "StartSe", STARTSE_INDEX_URL, startse_list, ingest_startse,
        use_smart_fetch=True,
    )


async def ingest_cubo_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "Cubo Itaú", CUBO_INDEX_URL, cubo_list, ingest_cubo,
        use_smart_fetch=True,
    )


async def ingest_abstartups_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "Abstartups", ABSTARTUPS_INDEX_URL, abstartups_list, ingest_abstartups,
    )


async def ingest_endeavor_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "Endeavor", ENDEAVOR_INDEX_URL, endeavor_list, ingest_endeavor,
    )


async def ingest_latitud_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "Latitud", LATITUD_INDEX_URL, latitud_list, ingest_latitud,
        use_smart_fetch=True,
    )


async def ingest_braziljournal_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "Brazil Journal", BRAZILJOURNAL_INDEX_URL, braziljournal_list,
        ingest_braziljournal,
        list_fn_extra_args=(BRAZILJOURNAL_INDEX_URL,),
    )


async def ingest_neofeed_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "NeoFeed", NEOFEED_INDEX_URL, neofeed_list, ingest_neofeed,
        list_fn_extra_args=(NEOFEED_INDEX_URL,),
    )


async def ingest_exame_all() -> list[StartupProfile]:
    return await _ingest_articles(
        "Exame", EXAME_INDEX_URL, exame_list, ingest_exame,
        list_fn_extra_args=(EXAME_INDEX_URL,),
    )


def ingest_inovativa_all() -> list[StartupProfile]:
    _log("[InovAtiva] Importando planilha...")
    profiles = ingest_inovativa()
    _log(f"[InovAtiva] {len(profiles)} startups importadas")
    return profiles


# ---------------------------------------------------------------------------
# Enriquecimento via crawl dos sites individuais
# ---------------------------------------------------------------------------

async def enrich_all(profiles: list[StartupProfile]) -> list[StartupProfile]:
    """Crawlea o site de cada startup para enriquecer o perfil."""
    enriched: list[StartupProfile] = []
    with_site = [p for p in profiles if p.website]
    _log(f"\n[Enrichment] {len(with_site)}/{len(profiles)} startups com site para crawlear")

    for i, profile in enumerate(profiles):
        if not profile.website:
            enriched.append(profile)
            continue

        try:
            pages = await crawl_startup_site(profile.website, max_pages=3)
            profile = await enrich_profile(profile, pages)
            _log(f"  [{i+1}/{len(with_site)}] ✓ {profile.name} — {len(pages)} páginas")
        except Exception as e:
            _log(f"  [{i+1}/{len(with_site)}] ✗ {profile.name}: {e}")

        enriched.append(profile)

    return enriched


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    all_profiles: list[StartupProfile] = []

    # --- Fontes já existentes ---
    all_profiles.extend(await ingest_ace())
    all_profiles.extend(await ingest_startupsbr_ia())
    all_profiles.extend(await ingest_distrito_all())
    all_profiles.extend(await ingest_liga_all())

    # --- Novas fontes de plataformas ---
    all_profiles.extend(await ingest_startse_all())
    all_profiles.extend(await ingest_cubo_all())
    all_profiles.extend(await ingest_abstartups_all())
    all_profiles.extend(await ingest_endeavor_all())
    all_profiles.extend(await ingest_latitud_all())

    # --- Fontes de notícias ---
    all_profiles.extend(await ingest_braziljournal_all())
    all_profiles.extend(await ingest_neofeed_all())
    all_profiles.extend(await ingest_exame_all())

    # --- Planilha InovAtiva ---
    all_profiles.extend(ingest_inovativa_all())

    # --- Deduplicação ---
    merged = merge_profiles(all_profiles)
    _log(f"\nTotal únicas: {len(merged)}")

    # --- Enriquecimento via sites das startups ---
    merged = await enrich_all(merged)

    # --- Persistência ---
    ids = save_profiles(merged)
    _log(f"Persistidas: {len(ids)} startups no banco")

    from db.connection import close
    close()


if __name__ == "__main__":
    asyncio.run(main())
