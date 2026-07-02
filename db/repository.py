"""
Repositório — operações CRUD para as tabelas do AIRadar.
Versão otimizada com batch operations via execute_values.
"""
from __future__ import annotations

from psycopg2.extras import execute_values

from services.scraping.schema import StartupProfile
from db.connection import get_connection, get_cursor

BATCH_SIZE = 500


def save_profile(p: StartupProfile) -> int:
    """Persiste um único perfil."""
    return save_profiles([p])[0]


def save_profiles(profiles: list[StartupProfile]) -> list[int]:
    """Persiste múltiplos perfis em uma única transação (batch)."""
    if not profiles:
        return []

    conn = get_connection()
    cur = conn.cursor()
    ids: list[int] = [0] * len(profiles)

    try:
        names_lower = [p.name.lower().strip() for p in profiles]

        # 1. Descobrir quais já existem no banco
        cur.execute(
            "SELECT id, LOWER(name) as name FROM startups WHERE LOWER(name) = ANY(%s)",
            (names_lower,),
        )
        existing_map: dict[str, int] = {}
        for row in cur.fetchall():
            existing_map[row["name"]] = row["id"]

        # 2. Separar novos × existentes
        insert_profiles: list[StartupProfile] = []
        insert_indices: list[int] = []  # posição original em `profiles`
        for i, p in enumerate(profiles):
            key = names_lower[i]
            if key in existing_map:
                ids[i] = existing_map[key]
            else:
                insert_profiles.append(p)
                insert_indices.append(i)

        # 3. Batch INSERT de novas startups
        if insert_profiles:
            for chunk_start in range(0, len(insert_profiles), BATCH_SIZE):
                chunk = insert_profiles[chunk_start:chunk_start + BATCH_SIZE]
                chunk_indices = insert_indices[chunk_start:chunk_start + BATCH_SIZE]
                vals = [_startup_values(p) for p in chunk]

                execute_values(
                    cur,
                    """
                    INSERT INTO startups
                        (name, website, sector, description, founders,
                         funding_stage, funding_amount_usd, employee_count_estimate,
                         ai_signals, tech_stack_mentions,
                         state, business_area, program, cohort_year, cohort_cycle,
                         inovativa_status)
                    VALUES %s
                    RETURNING id
                    """,
                    vals,
                    fetch=True,
                )
                for row_idx, row in enumerate(cur.fetchall()):
                    ids[chunk_indices[row_idx]] = row["id"]

        # 4. Atualizar startups existentes (individual, mas geralmente poucas)
        for i, p in enumerate(profiles):
            if ids[i] and names_lower[i] in existing_map:
                _update_startup_in_txn(cur, ids[i], p)

        # 5. Batch INSERT de sources (com ON CONFLICT para ignorar duplicatas)
        all_sources: list[tuple] = []
        for i, p in enumerate(profiles):
            sid = ids[i]
            if not sid or not p.sources:
                continue
            for src in p.sources:
                all_sources.append((
                    sid, src.url, src.extraction_method,
                    src.raw_excerpt, src.fetched_at,
                ))

        if all_sources:
            for chunk_start in range(0, len(all_sources), BATCH_SIZE):
                chunk = all_sources[chunk_start:chunk_start + BATCH_SIZE]
                execute_values(
                    cur,
                    """
                    INSERT INTO startup_sources
                        (startup_id, url, extraction_method, raw_excerpt, fetched_at)
                    VALUES %s
                    ON CONFLICT (startup_id, url) DO NOTHING
                    """,
                    chunk,
                )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()

    return ids


def _startup_values(p: StartupProfile) -> tuple:
    return (
        p.name, p.website, p.sector, p.description,
        p.founders if p.founders else None,
        p.funding_stage, p.funding_amount_usd,
        p.employee_count_estimate,
        p.ai_signals if p.ai_signals else None,
        p.tech_stack_mentions if p.tech_stack_mentions else None,
        p.state, p.business_area, p.program,
        p.cohort_year, p.cohort_cycle,
        p.inovativa_status,
    )


def _update_startup_in_txn(cur, startup_id: int, p: StartupProfile) -> None:
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
    cur.execute(
        f"UPDATE startups SET {', '.join(fields)} WHERE id = %s",
        values,
    )
