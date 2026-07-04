"""
Search Planner Agent — transforma uma consulta do usuário em uma query
estruturada no banco de startups, definindo filtros e prioridades.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.agents.llm import call_llm
from db.connection import get_cursor

PLANNER_SYSTEM_PROMPT = """Você é um planejador de busca especializado em startups de IA.
Receba uma consulta do usuário e traduza em parâmetros de busca para consultar
um banco de dados de startups brasileiras.

Campos disponíveis para filtro:
  - sector: setor da startup (ex: "Fintech", "Healthtech", "Edtech", "Agritech", "Cibersegurança")
  - ai_label: classificação de IA ("ai_native", "ai_enabled", "non_ai")
  - funding_stage: estágio de investimento ("Seed", "Série A", "Série B", "Série C", "Bootstrapped")
  - state: estado (UF, ex: "SP", "RJ", "MG")
  - min_sources: número mínimo de fontes
  - has_description: se tem descrição preenchida (true/false)
  - has_website: se tem website (true/false)
  - has_ai_signals: se tem sinais de IA (true/false)
  - limit: máximo de resultados (padrão 20)

Responda APENAS com um JSON:
{
  "filters": { "campo": "valor", ... },
  "reason": "Explicação curta da estratégia de busca"
}

Se a consulta for ambígua ou genérica, aplique filtros mínimos e retorne
resultados variados. Prefira retornar resultados com sinais de IA quando
relevante."""


def plan_query(user_query: str) -> dict[str, Any]:
    result = call_llm(PLANNER_SYSTEM_PROMPT, user_query, json_mode=True)
    if not isinstance(result, dict):
        return {"filters": {"limit": 20}, "reason": "Não foi possível interpretar a consulta"}
    filters = result.get("filters", {})
    if "limit" not in filters:
        filters["limit"] = 20
    return {"filters": filters, "reason": result.get("reason", "")}


def execute_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    filters = plan.get("filters", {})
    limit = filters.pop("limit", 20)

    conditions: list[str] = []
    params: list[Any] = []
    param_idx = 1

    for field, value in filters.items():
        if field == "sector" and value:
            conditions.append(f"LOWER(s.sector) LIKE LOWER(%s)")
            params.append(f"%{value}%")
        elif field == "ai_label" and value:
            conditions.append("""
                EXISTS (SELECT 1 FROM startup_classifications sc
                WHERE sc.startup_id = s.id AND sc.label = %s)
            """)
            params.append(value)
        elif field == "funding_stage" and value:
            conditions.append(f"LOWER(s.funding_stage) = LOWER(%s)")
            params.append(value)
        elif field == "state" and value:
            conditions.append(f"LOWER(s.state) = LOWER(%s)")
            params.append(value)
        elif field == "min_sources":
            conditions.append("""
                (SELECT COUNT(*) FROM startup_sources ss
                WHERE ss.startup_id = s.id) >= %s
            """)
            params.append(int(value))
        elif field == "has_description" and value:
            conditions.append("s.description IS NOT NULL AND s.description != ''")
        elif field == "has_website" and value:
            conditions.append("s.website IS NOT NULL")
        elif field == "has_ai_signals" and value:
            conditions.append("s.ai_signals IS NOT NULL AND array_length(s.ai_signals, 1) > 0")

    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    sql = f"""
        SELECT s.id, s.name, s.sector, s.funding_stage, s.state,
               s.ai_signals IS NOT NULL AND array_length(s.ai_signals, 1) > 0 AS has_ai
        FROM startups s
        WHERE {where_clause}
        ORDER BY has_ai DESC, s.id
        LIMIT %s
    """
    params.append(limit)

    with get_cursor() as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def search_startups(user_query: str) -> dict[str, Any]:
    plan = plan_query(user_query)
    results = execute_plan(plan)
    return {
        "query": user_query,
        "plan": plan,
        "total": len(results),
        "results": results,
    }
