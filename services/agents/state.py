from typing import TypedDict, Any


class StartupAnalysisState(TypedDict):
    startup_id: int
    startup_name: str
    error: str | None


class ClassificationState(TypedDict):
    startup_id: int
    startup_name: str
    ai_label: str | None
    ai_confidence: float | None
    ai_justification: str | None
    error: str | None


class RecommendationState(TypedDict):
    startup_id: int
    startup_name: str
    ai_label: str | None
    ai_confidence: float | None
    ai_justification: str | None
    nvidia_context: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    evidence_issues: list[str]
    briefing: str | None
    error: str | None
