from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.agents.llm import call_llm
from db.connection import get_cursor

BRIEFER_SYSTEM_PROMPT = """Você é um analista de inteligência de startups. Gere um briefing executivo 
profissional em português para o gerente de Startups & VCs da NVIDIA.

O briefing deve conter:
1. **Resumo Executivo**: visão geral da startup (2-3 frases)
2. **Classificação AI-native**: nível de maturidade em IA
3. **Tecnologias NVIDIA Recomendadas**: lista priorizada com justificativas
4. **Próximas Ações**: o que o time NVIDIA deve fazer (entrar em contato, oferecer Inception, etc.)

Formato: markdown limpo, sem JSON."""


def generate_briefing(
    startup_id: int,
    startup_name: str,
    classification: dict[str, Any],
    evidence_valid: bool,
    evidence_issues: list[str],
    recommendations: list[dict[str, Any]],
    nvidia_context: list[dict[str, Any]],
) -> str:
    prompt_parts = [
        f"Startup: {startup_name}",
        f"\nClassificação: {classification.get('label', 'N/A')}",
        f"Confiança: {classification.get('confidence', 0):.0%}",
        f"Justificativa: {classification.get('justification', 'N/A')}",
        f"\nEvidências válidas: {'Sim' if evidence_valid else 'Não'}",
        f"Issues de evidência: {'; '.join(evidence_issues) if evidence_issues else 'Nenhuma'}",
        "\nTecnologias pré-selecionadas:",
    ]
    for t in nvidia_context:
        prompt_parts.append(f"  - {t.get('technology', '?')}: {t.get('relevance', '')} (prioridade: {t.get('priority', 'N/A')})")

    prompt_parts.append("\nRecomendações detalhadas:")
    for r in recommendations:
        prompt_parts.append(f"  - {r.get('technology', '?')}")
        prompt_parts.append(f"    Justificativa técnica: {r.get('technical_justification', 'N/A')}")
        prompt_parts.append(f"    Justificativa de negócio: {r.get('business_justification', 'N/A')}")
        prompt_parts.append(f"    Prioridade: {r.get('priority', 'N/A')}")
        prompt_parts.append(f"    Complexidade: {r.get('implementation_complexity', 'N/A')}")
        prompt_parts.append(f"    Próxima ação: {r.get('suggested_next_action', 'N/A')}")

    prompt = "\n".join(prompt_parts)
    result = call_llm(BRIEFER_SYSTEM_PROMPT, prompt, json_mode=False)
    briefing = str(result) if result else "Erro ao gerar briefing."

    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO startup_briefings (startup_id, briefing_text)
            VALUES (%s, %s)
        """, (startup_id, briefing))

    return briefing
