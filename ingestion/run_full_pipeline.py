"""
Pipeline completo de scraping + persistência no banco.
Executa TODAS as 16 fontes, deduplica, enriquece e persiste.

Uso:  python -m ingestion.run_full_pipeline

Features:
  - Tracking de progresso em tempo real
  - Cada fonte é salva incrementalmente no banco (não perde dados se falhar)
  - Lida com rate limiting do Groq com retry/backoff
  - Usa cache de páginas já baixadas (791 em cache)
"""
from __future__ import annotations

import asyncio
import sys
import time

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from services.scraping.fetch import fetch_static
from services.scraping.smart_fetch import smart_fetch
from services.scraping.schema import StartupProfile
from services.scraping.directories import (
    ingest_ace,
    ingest_liga,
    ingest_distrito,
    ingest_startupsbr,
    ingest_startse,
    ingest_cubo,
    ingest_abstartups,
    ingest_endeavor,
    ingest_latitud,
    ingest_wow,
    ingest_braziljournal,
    ingest_neofeed,
    ingest_exame,
    ingest_pegn,
    ingest_mobiletime,
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
from services.scraping.directories.pegn import (
    INDEX_URL as PEGN_INDEX_URL,
    list_article_urls as pegn_list,
)
from services.scraping.directories.mobile_time import (
    INDEX_URL as MOBILETIME_INDEX_URL,
    list_article_urls as mobiletime_list,
)
from ingestion.runner import merge_profiles
from ingestion.spreadsheet import ingest_inovativa
from db.repository import save_profiles
from db.connection import get_cursor, close


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _get_existing_methods() -> set[str]:
    """Retorna set de extraction_methods já presentes no banco."""
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT extraction_method FROM startup_sources")
        return {row["extraction_method"] for row in cur.fetchall()}


def _save_batch(profiles: list[StartupProfile], source_name: str) -> int:
    """Salva batch no banco e retorna quantidade inserida."""
    if not profiles:
        return 0
    merged = merge_profiles(profiles)
    ids = save_profiles(merged)
    new_count = sum(1 for i in ids if i > 0)
    _log(f"  💾 [{source_name}] {new_count} novas startups salvas (de {len(merged)} únicas)")
    return new_count


async def _ingest_articles(
    source_name: str,
    index_url: str,
    list_fn,
    ingest_fn,
    *,
    use_smart_fetch: bool = False,
    list_fn_extra_args: tuple = (),
) -> list[StartupProfile]:
    """Helper genérico para fontes baseadas em artigos."""
    try:
        if use_smart_fetch:
            index_page = await smart_fetch(index_url)
        else:
            index_page = await fetch_static(index_url)

        articles = list_fn(index_page.raw_html, *list_fn_extra_args)
    except Exception as e:
        _log(f"  ⚠️  [{source_name}] Erro ao listar artigos: {e}")
        return []

    _log(f"  📄 [{source_name}] {len(articles)} artigos encontrados")

    profiles: list[StartupProfile] = []
    for i, url in enumerate(sorted(articles)):
        try:
            if use_smart_fetch:
                page = await smart_fetch(url)
            else:
                page = await fetch_static(url)
            extracted = ingest_fn(page)
            profiles.extend(extracted)
            slug = url.rstrip("/").split("/")[-1][:40]
            _log(f"    [{i+1}/{len(articles)}] +{len(extracted)} de {slug}")
        except Exception as e:
            _log(f"    [{i+1}/{len(articles)}] ✗ {url}: {e}")

    return profiles


# ---------------------------------------------------------------------------
# Ingestão por fonte
# ---------------------------------------------------------------------------

async def run_source_ace() -> list[StartupProfile]:
    _log("\n🔵 [1/16] ACE Ventures (BS4 puro)")
    page = await fetch_static(ACE_URL)
    profiles = ingest_ace(page)
    _log(f"  ✅ {len(profiles)} startups extraídas")
    return profiles


async def run_source_inovativa() -> list[StartupProfile]:
    _log("\n🔵 [2/16] InovAtiva Brasil (planilha XLSX)")
    profiles = ingest_inovativa()
    _log(f"  ✅ {len(profiles)} startups importadas")
    return profiles


async def run_source_wow() -> list[StartupProfile]:
    _log("\n🔵 [3/16] WOW Aceleradora (BS4 puro)")
    page = await fetch_static("https://www.wow.ac/portfolio")
    profiles = ingest_wow(page)
    _log(f"  ✅ {len(profiles)} startups extraídas")
    return profiles


async def run_source_startupsbr() -> list[StartupProfile]:
    _log("\n🟡 [4/16] Startups.com.br (trafilatura + LLM)")
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

    _log(f"  📄 {len(all_articles)} artigos encontrados")

    profiles: list[StartupProfile] = []
    for i, url in enumerate(sorted(all_articles)):
        try:
            page = await fetch_static(url)
            extracted = ingest_startupsbr(page)
            profiles.extend(extracted)
            slug = url.rstrip("/").split("/")[-1][:40]
            _log(f"    [{i+1}/{len(all_articles)}] +{len(extracted)} de {slug}")
        except Exception as e:
            _log(f"    [{i+1}/{len(all_articles)}] ✗ {url}: {e}")
    return profiles


async def run_source_distrito() -> list[StartupProfile]:
    _log("\n🟡 [5/16] Distrito Blog (trafilatura + LLM)")
    return await _ingest_articles("Distrito", DISTRITO_BLOG_URL, distrito_list, ingest_distrito)


async def run_source_liga() -> list[StartupProfile]:
    _log("\n🟡 [6/16] Liga Ventures (trafilatura + LLM)")
    return await _ingest_articles("Liga", LIGA_INDEX_URL, liga_list, ingest_liga)


async def run_source_startse() -> list[StartupProfile]:
    _log("\n🟡 [7/16] StartSe (trafilatura + LLM)")
    return await _ingest_articles(
        "StartSe", STARTSE_INDEX_URL, startse_list, ingest_startse,
        use_smart_fetch=True,
    )


async def run_source_cubo() -> list[StartupProfile]:
    _log("\n🟡 [8/16] Cubo Itaú (trafilatura + LLM)")
    return await _ingest_articles(
        "Cubo", CUBO_INDEX_URL, cubo_list, ingest_cubo,
        use_smart_fetch=True,
    )


async def run_source_abstartups() -> list[StartupProfile]:
    _log("\n🟡 [9/16] Abstartups (trafilatura + LLM)")
    return await _ingest_articles(
        "Abstartups", ABSTARTUPS_INDEX_URL, abstartups_list, ingest_abstartups,
    )


async def run_source_endeavor() -> list[StartupProfile]:
    _log("\n🟡 [10/16] Endeavor (trafilatura + LLM)")
    return await _ingest_articles(
        "Endeavor", ENDEAVOR_INDEX_URL, endeavor_list, ingest_endeavor,
    )


async def run_source_latitud() -> list[StartupProfile]:
    _log("\n🟡 [11/16] Latitud (trafilatura + LLM)")
    return await _ingest_articles(
        "Latitud", LATITUD_INDEX_URL, latitud_list, ingest_latitud,
        use_smart_fetch=True,
    )


async def run_source_braziljournal() -> list[StartupProfile]:
    _log("\n🟡 [12/16] Brazil Journal (trafilatura + LLM)")
    return await _ingest_articles(
        "BrazilJournal", BRAZILJOURNAL_INDEX_URL, braziljournal_list,
        ingest_braziljournal,
        list_fn_extra_args=(BRAZILJOURNAL_INDEX_URL,),
    )


async def run_source_neofeed() -> list[StartupProfile]:
    _log("\n🟡 [13/16] NeoFeed (trafilatura + LLM)")
    return await _ingest_articles(
        "NeoFeed", NEOFEED_INDEX_URL, neofeed_list, ingest_neofeed,
        list_fn_extra_args=(NEOFEED_INDEX_URL,),
    )


async def run_source_exame() -> list[StartupProfile]:
    _log("\n🟡 [14/16] Exame Startups (trafilatura + LLM)")
    return await _ingest_articles(
        "Exame", EXAME_INDEX_URL, exame_list, ingest_exame,
        list_fn_extra_args=(EXAME_INDEX_URL,),
    )


async def run_source_pegn() -> list[StartupProfile]:
    _log("\n🟡 [15/16] PEGN (trafilatura + LLM)")
    return await _ingest_articles(
        "PEGN", PEGN_INDEX_URL, pegn_list, ingest_pegn,
    )


async def run_source_mobiletime() -> list[StartupProfile]:
    _log("\n🟡 [16/16] Mobile Time (trafilatura + LLM)")
    return await _ingest_articles(
        "MobileTime", MOBILETIME_INDEX_URL, mobiletime_list, ingest_mobiletime,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    start = time.time()
    existing = _get_existing_methods()
    _log("=" * 60)
    _log("🚀 NVIDIA Startup Radar — Pipeline Completo de Scraping")
    _log("=" * 60)
    _log(f"Métodos já no banco: {existing}")

    all_profiles: list[StartupProfile] = []
    total_saved = 0

    # === FONTES SEM LLM (rápidas, BS4/planilha) ===
    _log("\n" + "━" * 50)
    _log("📦 FASE 1: Fontes sem LLM (BS4 + planilha)")
    _log("━" * 50)

    # 1. ACE
    profiles = await run_source_ace()
    total_saved += _save_batch(profiles, "ACE")
    all_profiles.extend(profiles)

    # 2. InovAtiva
    profiles = await run_source_inovativa()
    total_saved += _save_batch(profiles, "InovAtiva")
    all_profiles.extend(profiles)

    # 3. WOW
    profiles = await run_source_wow()
    total_saved += _save_batch(profiles, "WOW")
    all_profiles.extend(profiles)

    # === FONTES COM LLM (mais lentas, rate-limited) ===
    _log("\n" + "━" * 50)
    _log("🤖 FASE 2: Fontes com LLM (trafilatura + Groq)")
    _log("━" * 50)

    # Run each LLM source and save incrementally
    llm_sources = [
        ("Startups.com.br", run_source_startupsbr),
        ("Distrito", run_source_distrito),
        ("Liga", run_source_liga),
        ("StartSe", run_source_startse),
        ("Cubo", run_source_cubo),
        ("Abstartups", run_source_abstartups),
        ("Endeavor", run_source_endeavor),
        ("Latitud", run_source_latitud),
        ("BrazilJournal", run_source_braziljournal),
        ("NeoFeed", run_source_neofeed),
        ("Exame", run_source_exame),
        ("PEGN", run_source_pegn),
        ("MobileTime", run_source_mobiletime),
    ]

    for name, source_fn in llm_sources:
        try:
            profiles = await source_fn()
            total_saved += _save_batch(profiles, name)
            all_profiles.extend(profiles)
        except Exception as e:
            _log(f"  ❌ [{name}] Falha geral: {e}")

    # === REPORT FINAL ===
    _log("\n" + "=" * 60)
    _log("📊 RELATÓRIO FINAL")
    _log("=" * 60)

    elapsed = time.time() - start
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    merged = merge_profiles(all_profiles)
    _log(f"Total de perfis coletados: {len(all_profiles)}")
    _log(f"Total únicos (após dedup): {len(merged)}")
    _log(f"Total salvos nesta execução: {total_saved}")
    _log(f"Tempo total: {minutes}m {seconds}s")

    # Contagem final do banco
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM startups")
        db_count = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) as cnt FROM startup_sources")
        src_count = cur.fetchone()["cnt"]
        cur.execute("""
            SELECT extraction_method, COUNT(*) as cnt 
            FROM startup_sources 
            GROUP BY extraction_method 
            ORDER BY cnt DESC
        """)
        methods = cur.fetchall()

    _log(f"\n🏦 Estado do banco:")
    _log(f"   Startups totais: {db_count}")
    _log(f"   Sources totais:  {src_count}")
    _log(f"   Breakdown por método:")
    for m in methods:
        _log(f"     {m['extraction_method']}: {m['cnt']}")

    close()
    _log("\n✅ Pipeline finalizado com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())
