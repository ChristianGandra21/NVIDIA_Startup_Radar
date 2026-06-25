"""
Aplica migrations SQL no banco.
Uso:  python -m db.migrate
      python -m db.migrate --dry-run   # só mostra o SQL, não executa
"""
from __future__ import annotations

import sys
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def load_sql(name: str = "001_schema.sql") -> str:
    path = MIGRATIONS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Migration não encontrada: {path}")
    return path.read_text()


def run_migration(dry_run: bool = False) -> None:
    sql = load_sql()
    if dry_run:
        print(sql)
        return

    from db.connection import get_connection

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print("Migration 001_schema.sql aplicada com sucesso.")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao aplicar migration: {e}")
        raise
    finally:
        cur.close()


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    run_migration(dry_run=dry_run)


if __name__ == "__main__":
    main()
