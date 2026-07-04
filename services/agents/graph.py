from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from services.agents.state import RecommendationState
from services.agents.classifier import classify_startup
from services.agents.validator import validate_evidence
from services.agents.rag_agent import query_nvidia_kb
from services.agents.recommender import generate_recommendations
from services.agents.briefer import generate_briefing
from db.connection import get_cursor


# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------

def load_startup(state: RecommendationState) -> RecommendationState:
    startup_id = state["startup_id"]
    try:
        with get_cursor() as cur:
            cur.execute("""
                SELECT id, name, sector, description, ai_signals,
                       tech_stack_mentions
                FROM startups WHERE id = %s
            """, (startup_id,))
            row = cur.fetchone()

        if not row:
            return {**state, "error": f"Startup {startup_id} não encontrada"}

        return {
            **state,
            "startup_name": row["name"],
            "ai_label": None,
            "ai_confidence": None,
            "ai_justification": None,
            "nvidia_context": [],
            "recommendations": [],
            "evidence_issues": [],
            "briefing": None,
            "error": None,
        }
    except Exception as e:
        return {**state, "error": f"Erro ao carregar startup: {e}"}


def classify(state: RecommendationState) -> RecommendationState:
    if state.get("error"):
        return state
    try:
        result = classify_startup(state["startup_id"])
        return {
            **state,
            "ai_label": result.get("label"),
            "ai_confidence": result.get("confidence"),
            "ai_justification": result.get("justification"),
            "startup_name": result.get("startup_name", state["startup_name"]),
        }
    except Exception as e:
        return {**state, "error": f"Erro na classificação: {e}"}


def validate(state: RecommendationState) -> RecommendationState:
    if state.get("error"):
        return state
    try:
        result = validate_evidence(state["startup_id"])
        return {
            **state,
            "evidence_issues": result.get("issues", []),
        }
    except Exception as e:
        return {**state, "error": f"Erro na validação: {e}"}


def query_nvidia(state: RecommendationState) -> RecommendationState:
    if state.get("error"):
        return state
    try:
        with get_cursor() as cur:
            cur.execute("""
                SELECT sector, description, ai_signals, tech_stack_mentions
                FROM startups WHERE id = %s
            """, (state["startup_id"],))
            row = cur.fetchone()

        if not row:
            return {**state, "error": "Startup não encontrada no banco"}

        context = query_nvidia_kb(
            startup_name=state["startup_name"],
            sector=row["sector"],
            description=row["description"],
            ai_signals=row["ai_signals"] or [],
            tech_stack=row["tech_stack_mentions"] or [],
            ai_label=state.get("ai_label", "non_ai"),
        )
        return {**state, "nvidia_context": context}
    except Exception as e:
        return {**state, "error": f"Erro na consulta RAG: {e}"}


def recommend(state: RecommendationState) -> RecommendationState:
    if state.get("error"):
        return state
    try:
        recs = generate_recommendations(
            startup_id=state["startup_id"],
            startup_name=state["startup_name"],
            ai_label=state.get("ai_label", "non_ai"),
            ai_justification=state.get("ai_justification", ""),
            nvidia_context=state.get("nvidia_context", []),
            evidence_issues=state.get("evidence_issues", []),
        )
        return {**state, "recommendations": recs}
    except Exception as e:
        return {**state, "error": f"Erro nas recomendações: {e}"}


def brief(state: RecommendationState) -> RecommendationState:
    if state.get("error"):
        return state
    try:
        briefing = generate_briefing(
            startup_id=state["startup_id"],
            startup_name=state["startup_name"],
            classification={
                "label": state.get("ai_label"),
                "confidence": state.get("ai_confidence"),
                "justification": state.get("ai_justification"),
            },
            evidence_valid=len(state.get("evidence_issues", [])) == 0,
            evidence_issues=state.get("evidence_issues", []),
            recommendations=state.get("recommendations", []),
            nvidia_context=state.get("nvidia_context", []),
        )
        return {**state, "briefing": briefing}
    except Exception as e:
        return {**state, "error": f"Erro ao gerar briefing: {e}"}


def route_after_classify(
    state: RecommendationState,
) -> Literal["validate", END]:
    if state.get("error"):
        return END
    return "validate"


def route_after_error(
    state: RecommendationState,
) -> Literal["end", "continue"]:
    if state.get("error"):
        return "end"
    return "continue"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_analysis_graph() -> StateGraph:
    graph = StateGraph(RecommendationState)

    graph.add_node("load_startup", load_startup)
    graph.add_node("classify", classify)
    graph.add_node("validate", validate)
    graph.add_node("query_nvidia", query_nvidia)
    graph.add_node("recommend", recommend)
    graph.add_node("brief", brief)

    graph.add_edge(START, "load_startup")
    graph.add_edge("load_startup", "classify")
    graph.add_conditional_edges("classify", route_after_classify, {"validate": "validate", END: END})
    graph.add_edge("validate", "query_nvidia")
    graph.add_edge("query_nvidia", "recommend")
    graph.add_edge("recommend", "brief")
    graph.add_edge("brief", END)

    return graph.compile(checkpointer=MemorySaver())


analysis_graph = build_analysis_graph()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def analyze_startup(startup_id: int) -> dict[str, Any]:
    initial = RecommendationState(
        startup_id=startup_id,
        startup_name="",
        ai_label=None,
        ai_confidence=None,
        ai_justification=None,
        nvidia_context=[],
        recommendations=[],
        evidence_issues=[],
        briefing=None,
        error=None,
    )
    config = {"configurable": {"thread_id": f"startup_{startup_id}"}}
    result = await analysis_graph.ainvoke(initial, config)
    return result


async def analyze_startups_batch(startup_ids: list[int]) -> list[dict[str, Any]]:
    results = []
    for sid in startup_ids:
        try:
            result = await analyze_startup(sid)
            results.append(result)
        except Exception as e:
            results.append({
                "startup_id": sid,
                "startup_name": "",
                "error": str(e),
            })
    return results
