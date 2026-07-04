"""
CLI do sistema multiagente NVIDIA Startup Radar.

Uso:
    python -m services.agents.cli analyze <startup_id> [startup_id ...]
    python -m services.agents.cli search "<consulta>" [--limit N]
    python -m services.agents.cli batch --unclassified [--limit N]
    python -m services.agents.cli batch --ai-native
    python -m services.agents.cli batch --sector <setor>
    python -m services.agents.cli batch --search "<consulta>"
"""
from __future__ import annotations

import asyncio
import json
import sys

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from services.agents.graph import analyze_startup, analyze_startups_batch
from services.agents.planner import search_startups
from db.connection import get_cursor, close


def _log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


async def cmd_analyze(startup_ids: list[int]) -> None:
    for sid in startup_ids:
        _log(f"\n{'='*60}")
        _log(f"Analisando startup {sid}...")
        _log(f"{'='*60}")

        result = await analyze_startup(sid)

        if result.get("error"):
            _log(f"\n❌ Erro: {result['error']}")
            continue

        _log(f"\n📋 Startup: {result['startup_name']}")
        _log(f"🏷️  Classificação: {result.get('ai_label', 'N/A')} (confiança: {result.get('ai_confidence', 0):.0%})")

        issues = result.get("evidence_issues", [])
        if issues:
            _log(f"\n⚠️  Issues ({len(issues)}):")
            for issue in issues:
                _log(f"  - {issue}")

        techs = result.get("nvidia_context", [])
        if techs:
            _log(f"\n🔧 Tecnologias NVIDIA ({len(techs)}):")
            for t in techs:
                _log(f"  [{t.get('priority', 'N/A').upper()}] {t.get('technology', '?')}: {t.get('relevance', '')[:100]}")

        recs = result.get("recommendations", [])
        if recs:
            _log(f"\n📝 Recomendações ({len(recs)}):")
            for r in recs:
                _log(f"  [{r.get('priority', 'N/A').upper()}] {r.get('technology', '?')}")
                _log(f"    Ação: {r.get('suggested_next_action', 'N/A')}")

        if result.get("briefing"):
            _log(f"\n📄 Briefing Executivo:\n{result['briefing']}")


async def cmd_search(query: str, limit: int = 20) -> None:
    _log(f"\n🔍 Buscando: \"{query}\"")
    plan = search_startups(query)
    _log(f"Estratégia: {plan.get('plan', {}).get('reason', 'N/A')}")
    _log(f"Resultados: {plan['total']} startups encontradas\n")

    for i, r in enumerate(plan.get("results", [])[:limit], 1):
        _log(f"  {i:3d}. [{r['id']:5d}] {r['name']}")
        if r["sector"]:
            _log(f"       Setor: {r['sector']}")
        if r["funding_stage"]:
            _log(f"       Funding: {r['funding_stage']}")
        if r.get("has_ai"):
            _log(f"       🧠 Tem sinais de IA")

    _log(f"\nPara analisar: python -m services.agents.cli analyze <id>")


async def cmd_batch_unclassified(limit: int = 50) -> None:
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.id FROM startups s
            LEFT JOIN startup_classifications sc ON sc.startup_id = s.id
            WHERE sc.id IS NULL
            ORDER BY s.id
            LIMIT %s
        """, (limit,))
        ids = [r["id"] for r in cur.fetchall()]

    _log(f"\n📦 Analisando {len(ids)} startups não classificadas...")
    await cmd_analyze(ids)


async def cmd_batch_ai_native(limit: int = 50) -> None:
    with get_cursor() as cur:
        cur.execute("""
            SELECT s.id FROM startups s
            JOIN (
                SELECT DISTINCT ON (startup_id) startup_id, label
                FROM startup_classifications
                ORDER BY startup_id, classified_at DESC
            ) sc ON sc.startup_id = s.id
            WHERE sc.label = 'ai_native'
            ORDER BY s.id
            LIMIT %s
        """, (limit,))
        ids = [r["id"] for r in cur.fetchall()]

    _log(f"\n📦 Analisando {len(ids)} startups AI-native...")
    await cmd_analyze(ids)


async def cmd_batch_sector(sector: str, limit: int = 50) -> None:
    with get_cursor() as cur:
        cur.execute("""
            SELECT id FROM startups
            WHERE LOWER(sector) LIKE LOWER(%s)
            ORDER BY id
            LIMIT %s
        """, (f"%{sector}%", limit))
        ids = [r["id"] for r in cur.fetchall()]

    _log(f"\n📦 Analisando {len(ids)} startups do setor '{sector}'...")
    await cmd_analyze(ids)


async def cmd_batch_search(query: str, limit: int = 50) -> None:
    plan = search_startups(query)
    ids = [r["id"] for r in plan.get("results", [])[:limit]]
    _log(f"\n📦 Analisando {len(ids)} startups da busca...")
    await cmd_analyze(ids)


async def main() -> None:
    args = sys.argv[1:]
    if not args:
        _log(__doc__)
        return

    command = args[0]

    if command == "analyze":
        ids = [int(a.strip()) for a in args[1:] if a.strip().isdigit()]
        if not ids:
            _log("Forneça IDs de startups para analisar. Ex: python -m services.agents.cli analyze 1 2 3")
            return
        await cmd_analyze(ids)

    elif command == "search":
        query = " ".join(args[1:])
        if not query:
            _log("Forneça uma consulta. Ex: python -m services.agents.cli search 'startups de IA em saude'")
            return
        limit = 20
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])
        await cmd_search(query, limit)

    elif command == "batch":
        sub = args[1] if len(args) > 1 else ""
        limit = 50
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])

        if sub == "--unclassified":
            await cmd_batch_unclassified(limit)
        elif sub == "--ai-native":
            await cmd_batch_ai_native(limit)
        elif sub == "--sector" and len(args) > 2:
            await cmd_batch_sector(args[2], limit)
        elif sub == "--search":
            query = " ".join(args[2:])
            if "--limit" in query:
                query = query.split(" --limit")[0]
            await cmd_batch_search(query, limit)
        else:
            _log("Subcomando batch inválido. Use: --unclassified | --ai-native | --sector <setor> | --search <consulta>")

    else:
        _log(f"Comando desconhecido: {command}")
        _log(__doc__)

    close()


if __name__ == "__main__":
    asyncio.run(main())
