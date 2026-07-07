"""
Aplica todas as migrations SQL no banco em ordem.
Uso:  python -m db.migrate
      python -m db.migrate --dry-run   # só mostra o SQL, não executa
"""
from __future__ import annotations

import sys
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def list_migrations() -> list[str]:
    """Retorna nomes dos arquivos .sql em ordem alfabética."""
    return sorted(f.name for f in sorted(MIGRATIONS_DIR.iterdir()) if f.suffix == ".sql")


def load_sql(name: str) -> str:
    path = MIGRATIONS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Migration não encontrada: {path}")
    return path.read_text()


def run_migrations(dry_run: bool = False) -> None:
    migrations = list_migrations()
    if not migrations:
        print("Nenhuma migration encontrada.")
        return

    from db.connection import get_connection

    conn = get_connection()
    cur = conn.cursor()
    try:
        for name in migrations:
            sql = load_sql(name)
            if dry_run:
                print(f"-- {name}\n{sql}\n")
            else:
                cur.execute(sql)
                conn.commit()
                print(f"✓ {name}")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao aplicar migration: {e}")
        raise
    finally:
        cur.close()


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    run_migrations(dry_run=dry_run)


if __name__ == "__main__":
    main()
