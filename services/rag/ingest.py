"""
Ingestão de documentos NVIDIA — fetch, limpeza, chunking e armazenamento.
Fontes definidas no tapi.md seção 8.
"""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime
from typing import Any

import httpx

from services.rag.vector_store import NVIDIAVectorStore

NVIDIA_DOC_SOURCES = [
    # Programas e plataformas
    {"url": "https://www.nvidia.com/en-us/startups/", "topic": "NVIDIA Inception", "lang": "en"},
    {"url": "https://build.nvidia.com/", "topic": "NVIDIA API Catalog", "lang": "en"},
    {"url": "https://www.nvidia.com/en-us/ai-data-science/products/nim-microservices/", "topic": "NVIDIA NIM", "lang": "en"},
    {"url": "https://www.nvidia.com/en-us/ai-data-science/products/nemo/", "topic": "NVIDIA NeMo", "lang": "en"},
    {"url": "https://github.com/NVIDIA/NeMo-Guardrails", "topic": "NeMo Guardrails", "lang": "en"},
    {"url": "https://developer.nvidia.com/triton-inference-server", "topic": "NVIDIA Triton", "lang": "en"},
    {"url": "https://github.com/NVIDIA/TensorRT-LLM", "topic": "TensorRT-LLM", "lang": "en"},
    {"url": "https://rapids.ai/", "topic": "NVIDIA RAPIDS", "lang": "en"},
    {"url": "https://developer.nvidia.com/cuda-toolkit", "topic": "CUDA Toolkit", "lang": "en"},
    {"url": "https://developer.nvidia.com/riva", "topic": "NVIDIA Riva", "lang": "en"},
    {"url": "https://www.nvidia.com/en-us/omniverse/", "topic": "NVIDIA Omniverse", "lang": "en"},
    {"url": "https://developer.nvidia.com/isaac", "topic": "NVIDIA Isaac", "lang": "en"},
    {"url": "https://www.nvidia.com/en-us/clara/", "topic": "NVIDIA Clara", "lang": "en"},
    {"url": "https://developer.nvidia.com/morpheus-cybersecurity", "topic": "NVIDIA Morpheus", "lang": "en"},
    {"url": "https://www.nvidia.com/en-us/data-center/products/ai-enterprise/", "topic": "NVIDIA AI Enterprise", "lang": "en"},
    # Materiais de apoio
    {"url": "https://sequoiacap.com/article/services-the-new-software/", "topic": "AI-native services", "lang": "en"},
    {"url": "https://blogs.nvidia.com/blog/ai-5-layer-cake/", "topic": "NVIDIA AI 5-layer cake", "lang": "en"},
    # Documentação técnica adicional
    {"url": "https://docs.nvidia.com/nim/large-language-models/latest/introduction.html", "topic": "NVIDIA NIM docs", "lang": "en"},
    {"url": "https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/", "topic": "NVIDIA NeMo docs", "lang": "en"},
    {"url": "https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html", "topic": "NVIDIA Triton docs", "lang": "en"},
    {"url": "https://docs.rapids.ai/api/cudf/stable/", "topic": "cuDF docs", "lang": "en"},
]

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def fetch_page(url: str) -> str | None:
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=20,
                         headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  ✗ {url}: {e}", file=sys.stderr)
        return None


def clean_html(html: str) -> str | None:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return "\n".join(lines) if lines else None


def chunk_text(text: str, source_url: str, topic: str) -> list[dict[str, Any]]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk_words = words[i:i + CHUNK_SIZE]
        if len(chunk_words) < 30:
            continue
        chunk_text = " ".join(chunk_words)
        chunk_id = hashlib.md5(f"{source_url}#chunk{i}".encode()).hexdigest()
        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "metadata": {
                "source": source_url,
                "topic": topic,
                "chunk_index": i // (CHUNK_SIZE - CHUNK_OVERLAP),
                "ingested_at": datetime.utcnow().isoformat(),
            },
        })
    return chunks


def ingest_nvidia_docs(
    vector_store: NVIDIAVectorStore | None = None,
    sources: list[dict[str, Any]] | None = None,
) -> int:
    if vector_store is None:
        vector_store = NVIDIAVectorStore()
    if sources is None:
        sources = NVIDIA_DOC_SOURCES

    total_chunks = 0
    for src in sources:
        url = src["url"]
        topic = src["topic"]
        print(f"  Fetching {topic}...", end=" ", flush=True)

        html = fetch_page(url)
        if not html:
            print("skipped")
            continue

        text = clean_html(html)
        if not text or len(text) < 100:
            print("too short")
            continue

        chunks = chunk_text(text, url, topic)
        if chunks:
            vector_store.add_documents(chunks)
            total_chunks += len(chunks)
            print(f"{len(chunks)} chunks")
        else:
            print("no chunks")

    print(f"\nTotal: {total_chunks} chunks de {len(sources)} fontes")
    return total_chunks


def list_sources() -> list[dict[str, Any]]:
    return NVIDIA_DOC_SOURCES
