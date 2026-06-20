"""
Schema central de dados do pipeline de scraping/extração.
Todo conteúdo coletado deve eventualmente virar um StartupProfile.
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class SourceEvidence(BaseModel):
    """Rastreabilidade de cada informação extraída -- usado depois pelo
    Evidence Validator Agent para checar se há fontes suficientes."""

    url: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_method: str  # ex: "playwright+trafilatura", "bs4_directory"
    raw_excerpt: str  # trecho cru que sustenta a informação


class StartupProfile(BaseModel):
    """Perfil estruturado de uma startup, possivelmente consolidado
    a partir de múltiplas fontes (merge_profiles)."""

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
    sources: list[SourceEvidence] = []

    def add_source(self, source: SourceEvidence) -> None:
        self.sources.append(source)


class RawPage(BaseModel):
    """Página bruta coletada -- persistida em cache (tabela raw_pages)
    antes de qualquer extração, para permitir reprocessamento sem
    rescraping."""

    url: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    fetch_method: str  # "playwright" | "requests"
    raw_html: str | None = None
    raw_text: str | None = None  # já limpo, se aplicável