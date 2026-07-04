from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.agents.llm import call_llm
from db.connection import get_cursor

CLASSIFIER_SYSTEM_PROMPT = """Você é um classificador de maturidade AI-native para startups brasileiras.
Analise as informações fornecidas e classifique a startup em UMA das seguintes categorias:

1. "ai_native": A startup TEM a inteligência artificial como parte CENTRAL e INDISSOCIÁVEL do seu produto ou serviço. O modelo de negócio depende de IA/ML para funcionar. Exemplos: plataformas de LLM, visão computacional, agentes de IA, NLP como produto principal.

2. "ai_enabled": A startup USA inteligência artificial para MELHORAR ou OTIMIZAR seu produto/serviço, mas a IA não é o core business. Exemplos: fintech que usa ML para scoring, healthtech que usa IA para diagnóstico, SaaS que adicionou features de IA.

3. "non_ai": A startup NÃO apresenta evidências claras de uso de inteligência artificial no seu produto, serviço ou operação. Pode ser uma empresa tradicional ou digital que não utiliza IA.

Responda APENAS com um JSON:
{"label": "ai_native" | "ai_enabled" | "non_ai", "confidence": 0.0-1.0, "justification": "Resumo curto da decisão (1-2 frases)"}"""


def classify_startup(startup_id: int) -> dict[str, Any]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.id, s.name, s.description, s.sector, s.ai_signals,
                   s.tech_stack_mentions, s.funding_stage, s.website
            FROM startups s WHERE s.id = %s
        """, (startup_id,))
        row = cur.fetchone()

    if not row:
        return {"label": "non_ai", "confidence": 0.0, "justification": "Startup não encontrada"}

    signals = row["ai_signals"] or []
    tech = row["tech_stack_mentions"] or []

    prompt_parts = [
        f"Nome: {row['name']}",
        f"Setor: {row['sector'] or 'N/A'}",
        f"Descrição: {row['description'] or 'N/A'}",
        f"Sinais de IA: {', '.join(signals) if signals else 'Nenhum'}",
        f"Tecnologias mencionadas: {', '.join(tech) if tech else 'N/A'}",
        f"Estágio de funding: {row['funding_stage'] or 'N/A'}",
        f"Website: {row['website'] or 'N/A'}",
    ]
    prompt = "\n".join(prompt_parts)

    result = call_llm(CLASSIFIER_SYSTEM_PROMPT, prompt, json_mode=True)
    if not isinstance(result, dict):
        result = {}
    label = result.get("label", "non_ai")
    confidence = float(result.get("confidence", 0.0))
    justification = result.get("justification", "")

    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO startup_classifications
                (startup_id, label, confidence, justification)
            VALUES (%s, %s, %s, %s)
        """, (startup_id, label, confidence, justification))

    return {"label": label, "confidence": confidence, "justification": justification, "startup_name": row["name"]}
