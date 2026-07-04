from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.agents.llm import call_llm
from db.connection import get_cursor

RECOMMENDER_SYSTEM_PROMPT = """Você é um motor de recomendação de tecnologias NVIDIA para startups.
Com base no perfil da startup, na classificação AI-native e nas tecnologias NVIDIA pré-selecionadas,
gere recomendações detalhadas.

Para cada tecnologia recomendada, forneça:
- technology: Nome da tecnologia NVIDIA
- technical_justification: Por que tecnicamente ela é relevante para o stack da startup
- business_justification: Qual o benefício de negócio (redução de custo, aumento de performance, etc.)
- priority: "high", "medium" ou "low"
- implementation_complexity: "low", "medium" ou "high"
- suggested_next_action: Qual o próximo passo concreto que o time NVIDIA deveria tomar

Retorne APENAS um JSON com a lista:
{"recommendations": [
    {
        "technology": "...",
        "technical_justification": "...",
        "business_justification": "...",
        "priority": "high/medium/low",
        "implementation_complexity": "low/medium/high",
        "suggested_next_action": "..."
    }
]}"""


def generate_recommendations(
    startup_id: int,
    startup_name: str,
    ai_label: str,
    ai_justification: str,
    nvidia_context: list[dict[str, Any]],
    evidence_issues: list[str],
) -> list[dict[str, Any]]:
    prompt_parts = [
        f"Startup: {startup_name}",
        f"Classificação: {ai_label}",
        f"Justificativa da classificação: {ai_justification}",
        f"Issues de evidência: {'; '.join(evidence_issues) if evidence_issues else 'Nenhum'}",
        "\nTecnologias NVIDIA pré-selecionadas:",
    ]
    for t in nvidia_context:
        prompt_parts.append(f"  - {t.get('technology', '?')}: {t.get('relevance', '')}")

    prompt = "\n".join(prompt_parts)
    result = call_llm(RECOMMENDER_SYSTEM_PROMPT, prompt, json_mode=True)
    recommendations = []
    if isinstance(result, dict):
        recommendations = result.get("recommendations", [])

    with get_cursor() as cur:
        for rec in recommendations:
            cur.execute("""
                INSERT INTO nvidia_recommendations
                    (startup_id, nvidia_technology, technical_justification,
                     business_justification, priority, implementation_complexity,
                     suggested_next_action, evidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                startup_id,
                rec.get("technology", ""),
                rec.get("technical_justification", ""),
                rec.get("business_justification", ""),
                rec.get("priority", "medium"),
                rec.get("implementation_complexity", "medium"),
                rec.get("suggested_next_action", ""),
                evidence_issues if evidence_issues else None,
            ))

    return recommendations
