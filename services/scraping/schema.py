"""
Schema central de dados do pipeline de scraping/extração.
Apenas modelos -- nenhuma lógica de fetch, parsing ou extração ainda.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class SourceEvidence(BaseModel):
    """Rastreabilidade de uma informação extraída -- usado depois pelo
    Evidence Validator Agent para checar se há fontes suficientes."""

    url: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_method: str  # ex: "playwright+trafilatura", "bs4_directory"
    raw_excerpt: str  # trecho cru que sustenta a informação


class RawPage(BaseModel):
    """Página bruta coletada -- persistida em cache (tabela raw_pages)
    antes de qualquer extração, para permitir reprocessamento sem
    rescraping."""

    url: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    fetch_method: str  # "playwright" | "requests"
    raw_html: str | None = None


class StartupProfile(BaseModel):
    """Perfil estruturado de uma startup."""

    name: str
    website: str | None = None
    sector: str | None = None
    description: str | None = None
    founders: list[str] = []
    funding_stage: str | None = None
    funding_amount_usd: float | None = None
    employee_count_estimate: str | None = None  # faixa, ex: "11-50"
    ai_signals: list[str] = []
    tech_stack_mentions: list[str] = []
    state: str | None = None
    business_area: str | None = None
    program: str | None = None
    cohort_year: int | None = None
    cohort_cycle: str | None = None
    inovativa_status: str | None = None
    sources: list[SourceEvidence] = []