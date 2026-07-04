"""
Script de ingestão — busca documentações NVIDIA, limpa, chunkifica e armazena.

Uso:  python -m services.rag.run_ingest
      python -m services.rag.run_ingest --force   # recria a base do zero
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.rag.vector_store import NVIDIAVectorStore
from services.rag.ingest import ingest_nvidia_docs


def main():
    force = "--force" in sys.argv
    store = NVIDIAVectorStore()

    before = store.count()
    print(f"Chunks antes: {before}")

    if force and before > 0:
        print("Forçando recriação da base...")
        store.delete_all()
        before = 0

    if before == 0:
        total = ingest_nvidia_docs(store)
        print(f"\n✅ Ingestão concluída: {total} chunks")
    else:
        print(f"Base já populada ({before} chunks). Use --force para recriar.")

    after = store.count()
    print(f"Chunks depois: {after}")


if __name__ == "__main__":
    main()
