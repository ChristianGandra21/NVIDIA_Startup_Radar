"""
Orquestrador de ingestão — executa todas as fontes e persiste
os resultados no banco.
"""
from __future__ import annotations

from services.scraping.schema import StartupProfile
from services.scraping.fetch import fetch_static
from services.scraping.directories import ingest_ace
from services.scraping.directories.ace_ventures import ACE_URL


def merge_profiles(profiles: list[StartupProfile]) -> list[StartupProfile]:
    """Deduplica por nome — mesma startup pode aparecer em múltiplas fontes."""
    seen: dict[str, StartupProfile] = {}
    for p in profiles:
        key = p.name.lower().strip()
        if key in seen:
            existing = seen[key]
            for s in p.sources:
                if s.url not in {ev.url for ev in existing.sources}:
                    existing.sources.append(s)
            if p.sector and not existing.sector:
                existing.sector = p.sector
            if p.website and not existing.website:
                existing.website = p.website
            if p.description and not existing.description:
                existing.description = p.description
            existing.ai_signals.extend(
                s for s in p.ai_signals if s not in existing.ai_signals
            )
            if p.funding_stage and not existing.funding_stage:
                existing.funding_stage = p.funding_stage
            if p.funding_amount_usd and not existing.funding_amount_usd:
                existing.funding_amount_usd = p.funding_amount_usd
        else:
            seen[key] = p
    return list(seen.values())


async def ingest_ace_ventures() -> list[StartupProfile]:
    page = await fetch_static(ACE_URL)
    return ingest_ace(page)


async def run_all() -> list[StartupProfile]:
    """Executa todas as fontes e retorna lista consolidada (sem persistir)."""
    all_profiles: list[StartupProfile] = []
    all_profiles.extend(await ingest_ace_ventures())
    return merge_profiles(all_profiles)


async def run_and_persist() -> list[int]:
    """Executa todas as fontes e persiste os resultados no banco."""
    from db.repository import save_profiles

    profiles = await run_all()
    ids = save_profiles(profiles)
    return ids
