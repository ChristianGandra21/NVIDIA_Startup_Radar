"""
Repositório — operações CRUD para as tabelas do AIRadar.
Versão otimizada com batch operations para evitar N round-trips.
"""
from __future__ import annotations

from services.scraping.schema import StartupProfile
from db.connection import get_connection, get_cursor


def save_profile(p: StartupProfile) -> int:
    """Persiste um único perfil."""
    return save_profiles([p])[0]


def save_profiles(profiles: list[StartupProfile]) -> list[int]:
    """Persiste múltiplos perfis em uma única transação (batch)."""
    if not profiles:
        return []

    conn = get_connection()
    cur = conn.cursor()
    ids: list[int] = []

    try:
        names_lower = [p.name.lower().strip() for p in profiles]

        cur.execute(
            "SELECT id, LOWER(name) as name FROM startups WHERE LOWER(name) = ANY(%s)",
            (names_lower,),
        )
        existing_map: dict[str, int] = {}
        for row in cur.fetchall():
            existing_map[row["name"]] = row["id"]

        insert_vals: list[tuple] = []
        insert_profiles: list[StartupProfile] = []

        for i, p in enumerate(profiles):
            key = names_lower[i]
            if key in existing_map:
                sid = existing_map[key]
                _update_startup_in_txn(cur, sid, p)
                ids.append(sid)
            else:
                insert_vals.append(_startup_values(p))
                insert_profiles.append(p)

        if insert_vals:
            for vals, p in zip(insert_vals, insert_profiles):
                cur.execute(
                    """
                    INSERT INTO startups
                        (name, website, sector, description, founders,
                         funding_stage, funding_amount_usd, employee_count_estimate,
                         ai_signals, tech_stack_mentions,
                         state, business_area, program, cohort_year, cohort_cycle,
                         inovativa_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    vals,
                )
                sid = cur.fetchone()["id"]
                ids.append(sid)
                _insert_sources_in_txn(cur, sid, p)

        for i, p in enumerate(profiles):
            key = names_lower[i]
            if key in existing_map:
                sid = existing_map[key]
                _insert_sources_in_txn(cur, sid, p)

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


def _insert_sources_in_txn(cur, startup_id: int, p: StartupProfile) -> None:
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
