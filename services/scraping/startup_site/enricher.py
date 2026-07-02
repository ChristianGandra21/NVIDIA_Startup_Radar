"""
Profile Enricher — takes an existing StartupProfile and a batch of
RawPage objects (from site_crawler) and enriches the profile with
founders, tech-stack signals, AI signals, description, and headcount
via an LLM call.

Follows the same LLM-call pattern as
services.scraping.extraction.llm_extractor (env vars, retry logic,
JSON parsing) but uses a specialised *enrichment* system prompt.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

from services.scraping.schema import StartupProfile, RawPage, SourceEvidence
from services.scraping.extraction.clean_text import clean_text

logger = logging.getLogger(__name__)

EXTRACTION_METHOD = "site_crawl+llm_enrichment"

# ── LLM config (same env vars used by llm_extractor.py) ────────────
_endpoint = os.getenv(
    "LLM_ENDPOINT",
    "http://localhost:11434/v1/chat/completions",
)
_api_key = os.getenv("LLM_API_KEY") or ""
_model = os.getenv("LLM_MODEL", "llama3")
_json_mode = os.getenv("LLM_JSON_MODE", "").lower() in ("1", "true", "yes")

# ── Enrichment system prompt ───────────────────────────────────────
ENRICHMENT_PROMPT = """\
Você é um assistente especializado em análise de startups.
Receba o texto extraído do site de uma startup e retorne UM único objeto
JSON com os seguintes campos:

  - "founders": lista de nomes dos fundadores / co-fundadores mencionados.
  - "tech_stack_mentions": lista de tecnologias, frameworks, linguagens
    ou ferramentas mencionadas (ex: "PyTorch", "Kubernetes", "React").
  - "ai_signals": lista de sinais que indicam uso de inteligência
    artificial ou machine learning (ex: "modelo de NLP", "visão
    computacional", "LLM fine-tuning").
  - "description": descrição curta (1-3 frases) da startup e o que ela faz.
  - "employee_count_estimate": estimativa do número de funcionários
    como faixa (ex: "1-10", "11-50", "51-200"). Se não houver
    informação suficiente, retorne null.

Retorne APENAS o JSON, sem markdown e sem texto adicional.
NÃO invente informações que não estejam no texto fornecido.\
"""


# ── Rate-limiting state ────────────────────────────────────────────
_last_call_time: float = 0.0


def _call_enrichment_llm(text: str) -> dict[str, Any]:
    """Send combined page text to the LLM and return parsed JSON dict."""
    global _last_call_time

    # Truncate overly long input to stay within context limits.
    max_chars = 12_000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    # Simple rate-limiting (same cadence as llm_extractor).
    elapsed = time.time() - _last_call_time
    if elapsed < 3.0:
        time.sleep(3.0 - elapsed)

    payload: dict[str, Any] = {
        "model": _model,
        "messages": [
            {"role": "system", "content": ENRICHMENT_PROMPT},
            {"role": "user", "content": f"Texto do site:\n\n{text}"},
        ],
        "temperature": 0.1,
    }

    if _json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if _api_key:
        headers["Authorization"] = f"Bearer {_api_key}"

    for attempt in range(3):
        try:
            resp = httpx.post(
                _endpoint, headers=headers, json=payload, timeout=120
            )
            resp.raise_for_status()
            _last_call_time = time.time()
            raw_content = resp.json()["choices"][0]["message"]["content"]
            return _parse_enrichment_response(raw_content)
        except Exception as exc:
            msg = f"[Enrichment LLM] attempt {attempt + 1} failed: {type(exc).__name__}"
            if hasattr(exc, "response") and exc.response is not None:
                msg += f" status={exc.response.status_code} {exc.response.text[:200]}"
            print(msg, file=sys.stderr)
            if attempt < 2:
                wait = 10 ** attempt  # 1 s, 10 s
                time.sleep(wait)

    return {}


def _parse_enrichment_response(raw: str) -> dict[str, Any]:
    """Parse the raw LLM string into a dict, tolerating markdown fences."""
    raw = raw.strip()

    # Strip markdown code fences if present.
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM enrichment response as JSON")
        return {}

    if isinstance(parsed, dict):
        return parsed
    return {}


# ── Public API ─────────────────────────────────────────────────────

async def enrich_profile(
    profile: StartupProfile,
    pages: list[RawPage],
) -> StartupProfile:
    """Enrich *profile* using text extracted from *pages*.

    The function:
    1. Extracts clean text from each page.
    2. Concatenates the texts (with page-URL headers for context).
    3. Calls the enrichment LLM to extract structured data.
    4. Merges extracted fields into *profile* **without** overwriting
       existing non-None / non-empty fields.
    5. Appends a ``SourceEvidence`` entry for every page consumed.

    Returns the (mutated) profile.
    """
    # --- 1. Extract & concatenate text ---
    text_parts: list[str] = []
    used_pages: list[RawPage] = []

    for page in pages:
        extracted = clean_text(page)
        if extracted:
            text_parts.append(f"--- {page.url} ---\n{extracted}")
            used_pages.append(page)

    if not text_parts:
        logger.info("No extractable text from pages; skipping enrichment.")
        return profile

    combined_text = "\n\n".join(text_parts)

    # --- 2. LLM enrichment ---
    enrichment = _call_enrichment_llm(combined_text)

    if not enrichment:
        logger.warning("LLM enrichment returned empty; profile unchanged.")
        return profile

    # --- 3. Merge fields (don't overwrite existing data) ---
    _merge_string_field(profile, "description", enrichment.get("description"))
    _merge_string_field(
        profile, "employee_count_estimate", enrichment.get("employee_count_estimate")
    )

    _merge_list_field(profile, "founders", enrichment.get("founders"))
    _merge_list_field(profile, "tech_stack_mentions", enrichment.get("tech_stack_mentions"))
    _merge_list_field(profile, "ai_signals", enrichment.get("ai_signals"))

    # --- 4. Source evidence ---
    for page in used_pages:
        profile.sources.append(
            SourceEvidence(
                url=page.url,
                fetched_at=page.fetched_at,
                extraction_method=EXTRACTION_METHOD,
                raw_excerpt=(clean_text(page) or "")[:300],
            )
        )

    return profile


# ── Merge helpers ──────────────────────────────────────────────────

def _merge_string_field(
    profile: StartupProfile, field: str, value: Any
) -> None:
    """Set *field* on *profile* only if the current value is None/empty."""
    if value and not getattr(profile, field, None):
        setattr(profile, field, str(value))


def _merge_list_field(
    profile: StartupProfile, field: str, values: Any
) -> None:
    """Extend list *field* on *profile* with new unique items."""
    if not values or not isinstance(values, list):
        return
    existing: list[str] = getattr(profile, field, [])
    existing_lower = {v.lower() for v in existing}
    for v in values:
        if isinstance(v, str) and v.strip() and v.strip().lower() not in existing_lower:
            existing.append(v.strip())
            existing_lower.add(v.strip().lower())
