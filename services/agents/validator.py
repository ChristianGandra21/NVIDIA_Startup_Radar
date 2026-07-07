from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.agents.llm import call_llm
from db.connection import get_cursor

VALIDATOR_SYSTEM_PROMPT = """Você é um validador de evidências para perfis de startups.
Analise as fontes de informação disponíveis sobre uma startup e identifique possíveis problemas:

1. Fontes insuficientes: a startup tem menos de 2 fontes de informação.
2. Informação não sustentada: alegações sobre a startup que não têm fonte específica.
3. Conflito entre fontes: informações contraditórias em diferentes fontes.
4. Informação desatualizada: fontes com mais de 1 ano.

Retorne APENAS um JSON:
{"valid": true/false, "issues": ["descrição do problema 1", "descrição do problema 2", ...]}"""


def validate_evidence(startup_id: int) -> dict[str, Any]:
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.name, s.description, s.sector, s.ai_signals,
                   s.funding_stage, s.funding_amount_usd
            FROM startups s WHERE s.id = %s
        """, (startup_id,))
        startup = cur.fetchone()

        cur.execute("""
            SELECT url, extraction_method, raw_excerpt, fetched_at
            FROM startup_sources WHERE startup_id = %s
            ORDER BY fetched_at DESC
        """, (startup_id,))
        sources = cur.fetchall()

    if not startup:
        return {"valid": False, "issues": ["Startup não encontrada"]}

    issues = []

    if len(sources) < 2:
        issues.append(f"Apenas {len(sources)} fonte(s) de informação — mínimo recomendado: 2")

    if not startup["description"]:
        issues.append("Descrição da startup não preenchida")

    if not startup["sector"]:
        issues.append("Setor não preenchido")

    if not startup["ai_signals"]:
        issues.append("Nenhum sinal de IA identificado")

    prompt_parts = [
        f"Startup: {startup['name']}",
        f"Setor: {startup['sector'] or 'N/A'}",
        f"Descrição: {startup['description'] or 'N/A'}",
        f"Sinais de IA: {', '.join(startup['ai_signals'] or []) or 'Nenhum'}",
        f"Funding: {startup['funding_stage'] or 'N/A'} - {startup['funding_amount_usd'] or 'N/A'}",
        f"\nFontes ({len(sources)}):",
    ]
    for s in sources:
        prompt_parts.append(f"  - {s['url']} (via {s['extraction_method']}, em {s['fetched_at']})")

    prompt = "\n".join(prompt_parts)
    llm_result = call_llm(VALIDATOR_SYSTEM_PROMPT, prompt, json_mode=True)
    if isinstance(llm_result, dict):
        issues.extend(llm_result.get("issues", []))

    is_valid = len(issues) == 0
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO startup_validations
                (startup_id, is_valid, issues, source_count)
            VALUES (%s, %s, %s, %s)
        """, (startup_id, is_valid, issues if issues else None, len(sources)))

    return {"valid": is_valid, "issues": issues, "source_count": len(sources)}
