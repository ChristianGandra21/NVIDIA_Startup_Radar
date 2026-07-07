"""
Executa apenas as fontes que ainda não foram registradas no banco.
Uso:  python -m ingestion.run_missing
"""
from __future__ import annotations

import asyncio
import sys
import time

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from db.connection import get_cursor, close
from db.repository import save_profiles
from ingestion.runner import merge_profiles
from ingestion.run_full_pipeline import (
    run_source_cubo,
    run_source_abstartups,
    run_source_endeavor,
    run_source_latitud,
    run_source_braziljournal,
    run_source_neofeed,
    run_source_exame,
    run_source_mobiletime,
)


def _log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _get_existing_methods() -> set[str]:
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT extraction_method FROM startup_sources")
        return {row["extraction_method"] for row in cur.fetchall()}


def _save_batch(profiles, source_name: str) -> int:
    if not profiles:
        return 0
    merged = merge_profiles(profiles)
    ids = save_profiles(merged)
    new_count = sum(1 for i in ids if i > 0)
    _log(f"  💾 [{source_name}] {new_count} novas startups salvas (de {len(merged)} únicas)")
    return new_count


async def main():
    start = time.time()
    existing = _get_existing_methods()
    _log("=" * 60)
    _log("🚀 NVIDIA Startup Radar — Fontes faltantes")
    _log("=" * 60)
    _log(f"Métodos já no banco: {existing}")

    all_sources = [
        ("Cubo", run_source_cubo, "trafilatura+llm_cubo"),
        ("Abstartups", run_source_abstartups, "trafilatura+llm_abstartups"),
        ("Endeavor", run_source_endeavor, "trafilatura+llm_endeavor"),
        ("Latitud", run_source_latitud, "trafilatura+llm_latitud"),
        ("BrazilJournal", run_source_braziljournal, "trafilatura+llm_braziljournal"),
        ("NeoFeed", run_source_neofeed, "trafilatura+llm_neofeed"),
        ("Exame", run_source_exame, "trafilatura+llm_exame"),
        ("MobileTime", run_source_mobiletime, "trafilatura+llm_mobiletime"),
    ]

    total_saved = 0
    for name, source_fn, method in all_sources:
        if method in existing:
            _log(f"\n⏭️  Pulando {name} (já registrado: {method})")
            continue
        _log(f"\n▶️  Executando {name}...")
        try:
            profiles = await source_fn()
            total_saved += _save_batch(profiles, name)
        except Exception as e:
            _log(f"  ❌ [{name}] Falha: {e}")

    elapsed = time.time() - start
    _log(f"\n✅ Concluído em {int(elapsed//60)}m {int(elapsed%60)}s")
    _log(f"Total salvo nesta execução: {total_saved}")

    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM startups")
        _log(f"Total startups no banco: {cur.fetchone()['cnt']}")
        cur.execute("SELECT extraction_method, COUNT(*) as cnt FROM startup_sources GROUP BY extraction_method ORDER BY cnt DESC")
        for r in cur.fetchall():
            _log(f"  {r['extraction_method']}: {r['cnt']}")

    close()


if __name__ == "__main__":
    asyncio.run(main())
