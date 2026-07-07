"""
Conexão com Postgres/Supabase via DATABASE_URL.
Gerencia pool de conexões (uma por processo, lazy).
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _get_dsn() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL não configurada. Defina no .env ou export."
        )
    return url


_connection = None


def get_connection():
    """Retorna conexão global (lazy, singleton por processo)."""
    global _connection
    if _connection is None or _connection.closed:
        _connection = psycopg2.connect(_get_dsn(), cursor_factory=RealDictCursor)
    return _connection


@contextmanager
def get_cursor() -> Generator[RealDictCursor, None, None]:
    """Context manager que garante rollback em caso de erro."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def close():
    """Fecha a conexão (chamar no shutdown do app)."""
    global _connection
    if _connection is not None and not _connection.closed:
        _connection.close()
    _connection = None
