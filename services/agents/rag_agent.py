from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.agents.llm import call_llm

_store = None
_retriever = None


def _get_retriever():
    global _store, _retriever
    if _retriever is None:
        from services.rag.vector_store import NVIDIAVectorStore
        from services.rag.retriever import HybridRetriever
        _store = NVIDIAVectorStore()
        _retriever = HybridRetriever(_store)
    return _retriever


RAG_SYSTEM_PROMPT = """Você é um especialista em tecnologias NVIDIA para startups.
Com base no perfil da startup e nos trechos de documentação NVIDIA abaixo,
selecione as tecnologias NVIDIA MAIS RELEVANTES.

Documentação NVIDIA relevante:
{context}

Para cada tecnologia recomendada, explique POR QUE ela é relevante para a startup.
Retorne APENAS um JSON com a lista de recomendações:
{{"relevant_technologies": [
    {{
        "technology": "Nome da tecnologia",
        "relevance": "Explicação curta de por que é relevante",
        "priority": "high/medium/low",
        "use_case": "Caso de uso específico para a startup"
    }}
]}}

Máximo de 5 tecnologias. Se nenhuma for relevante, retorne lista vazia."""


def query_nvidia_kb(
    startup_name: str,
    sector: str | None,
    description: str | None,
    ai_signals: list[str],
    tech_stack: list[str],
    ai_label: str,
) -> list[dict[str, Any]]:
    query_parts = [
        f"Startup {startup_name} in {sector or 'general'} sector",
        description or "",
        f"AI signals: {', '.join(ai_signals[-3:])}" if ai_signals else "",
        f"Tech stack: {', '.join(tech_stack)}" if tech_stack else "",
        f"AI maturity: {ai_label}",
    ]
    query = " ".join(q for q in query_parts if q)

    retriever = _get_retriever()
    chunks = retriever.retrieve(query, n_final=5) if retriever.vector_store.count() > 0 else []

    context = "\n\n".join(
        f"[{c.get('metadata', {}).get('topic', 'NVIDIA')}] {c.get('text', '')[:500]}"
        for c in chunks
    ) if chunks else "NVIDIA technologies available for startups."

    prompt_parts = [
        f"Startup: {startup_name}",
        f"Setor: {sector or 'N/A'}",
        f"Descrição: {description or 'N/A'}",
        f"Classificação AI: {ai_label}",
        f"Sinais de IA: {', '.join(ai_signals) if ai_signals else 'Nenhum'}",
        f"Stack tecnológica: {', '.join(tech_stack) if tech_stack else 'N/A'}",
    ]
    prompt = "\n".join(prompt_parts)
    system = RAG_SYSTEM_PROMPT.format(context=context)

    result = call_llm(system, prompt, json_mode=True)
    if isinstance(result, dict):
        return result.get("relevant_technologies", [])
    return []
