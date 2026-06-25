"""
Repositório — operações CRUD para as tabelas do AIRadar.
Mapeia StartupProfile → linhas em startups + startup_sources.
"""
from __future__ import annotations

from services.scraping.schema import StartupProfile
from db.connection import get_cursor


def _find_existing(name: str) -> int | None:
    """Busca startup pelo nome exato (case-insensitive). Retorna id ou None."""
    with get_cursor() as cur:
        cur.execute("SELECT id FROM startups WHERE LOWER(name) = LOWER(%s)", (name,))
        row = cur.fetchone()
        return row["id"] if row else None


def _insert_startup(p: StartupProfile) -> int:
    """Insere uma startup e retorna o id gerado."""
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO startups
                (name, website, sector, description, founders,
                 funding_stage, funding_amount_usd, employee_count_estimate,
                 ai_signals, tech_stack_mentions,
                 state, business_area, program, cohort_year, cohort_cycle,
                 inovativa_status)
            VALUES
                (%s, %s, %s, %s, %s,
                 %s, %s, %s,
                 %s, %s,
                 %s, %s, %s, %s, %s,
                 %s)
            RETURNING id
            """,
            (
                p.name, p.website, p.sector, p.description,
                p.founders if p.founders else None,
                p.funding_stage, p.funding_amount_usd,
                p.employee_count_estimate,
                p.ai_signals if p.ai_signals else None,
                p.tech_stack_mentions if p.tech_stack_mentions else None,
                p.state, p.business_area, p.program,
                p.cohort_year, p.cohort_cycle,
                p.inovativa_status,
            ),
        )
        return cur.fetchone()["id"]


def _update_startup(startup_id: int, p: StartupProfile) -> None:
    """Atualiza campos não-nulos de uma startup existente."""
    fields = []
    values = []
    for field, value in [
        ("website", p.website),
        ("sector", p.sector),
        ("description", p.description),
        ("funding_stage", p.funding_stage),
        ("funding_amount_usd", p.funding_amount_usd),
        ("employee_count_estimate", p.employee_count_estimate),
        ("state", p.state),
        ("business_area", p.business_area),
        ("program", p.program),
        ("cohort_year", p.cohort_year),
        ("cohort_cycle", p.cohort_cycle),
        ("inovativa_status", p.inovativa_status),
    ]:
        if value is not None:
            fields.append(f"{field} = %s")
            values.append(value)

    for field, value in [
        ("founders", p.founders),
        ("ai_signals", p.ai_signals),
        ("tech_stack_mentions", p.tech_stack_mentions),
    ]:
        if value:
            fields.append(f"{field} = %s")
            values.append(value)

    if not fields:
        return

    fields.append("updated_at = NOW()")
    values.append(startup_id)

    with get_cursor() as cur:
        cur.execute(
            f"UPDATE startups SET {', '.join(fields)} WHERE id = %s",
            values,
        )


def _insert_sources(startup_id: int, p: StartupProfile) -> None:
    """Insere as fontes de uma startup (evita duplicatas por URL)."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT url FROM startup_sources WHERE startup_id = %s",
            (startup_id,),
        )
        existing = {row["url"] for row in cur.fetchall()}

        for src in p.sources:
            if src.url in existing:
                continue
            cur.execute(
                """
                INSERT INTO startup_sources
                    (startup_id, url, extraction_method, raw_excerpt, fetched_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (startup_id, src.url, src.extraction_method,
                 src.raw_excerpt, src.fetched_at),
            )


def save_profile(p: StartupProfile) -> int:
    """Faz upsert de um StartupProfile. Retorna o id da startup."""
    existing_id = _find_existing(p.name)
    if existing_id is not None:
        _update_startup(existing_id, p)
        startup_id = existing_id
    else:
        startup_id = _insert_startup(p)

    _insert_sources(startup_id, p)
    return startup_id


def save_profiles(profiles: list[StartupProfile]) -> list[int]:
    """Persiste múltiplos perfis em uma transação."""
    from db.connection import get_connection

    ids: list[int] = []
    conn = get_connection()

    for p in profiles:
        existing_id = _find_existing(p.name)
        if existing_id is not None:
            _update_startup(existing_id, p)
            startup_id = existing_id
        else:
            startup_id = _insert_startup(p)
        _insert_sources(startup_id, p)
        ids.append(startup_id)

    conn.commit()
    return ids
