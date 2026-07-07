"""
Script rápido: salva no banco as fontes que NÃO dependem de LLM.
  - ACE Ventures (BS4 puro)
  - InovAtiva Brasil (planilha XLSX)

As demais fontes dependem do LLM extractor (Groq) que está com
o limite diário esgotado (500k TPD).
"""
from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from ingestion.crawl_all import ingest_ace_portfolio as ingest_ace, ingest_inovativa_all
from ingestion.runner import merge_profiles
from db.repository import save_profiles
from services.scraping.schema import StartupProfile


def _log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


async def main():
    all_profiles: list[StartupProfile] = []

    # --- Fontes SEM dependência de LLM ---
    all_profiles.extend(await ingest_ace())
    all_profiles.extend(ingest_inovativa_all())

    # --- Deduplicação ---
    merged = merge_profiles(all_profiles)
    _log(f"\nTotal únicas: {len(merged)}")

    # --- Persistência ---
    _log("Salvando no banco...")
    ids = save_profiles(merged)
    _log(f"✅ Persistidas: {len(ids)} startups no banco")

    from db.connection import close
    close()


if __name__ == "__main__":
    asyncio.run(main())
