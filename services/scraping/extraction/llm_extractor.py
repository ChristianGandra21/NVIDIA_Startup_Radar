"""
LLM Extractor Agent — extrai menções de startups de texto corrido
(artigos, blog posts, notícias) via API compatível com OpenAI.

Providers testados:
  - Ollama  (http://localhost:11434/v1, sem API key)
  - Groq    (https://api.groq.com/openai/v1, LLM_API_KEY)
  - OpenAI  (https://api.openai.com/v1, LLM_API_KEY)

Config via env vars:
  LLM_ENDPOINT  (default: http://localhost:11434/v1/chat/completions)
  LLM_API_KEY   (opcional — usado só se setado)
  LLM_MODEL     (default: llama3)
  LLM_JSON_MODE (default: false — desliga response_format pra compatibilidade)
"""
from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

from services.scraping.schema import StartupProfile, SourceEvidence

SYSTEM_PROMPT = """Você é um extrator de dados de startups brasileiras.
Analise o texto fornecido e extraia todas as startups mencionadas.

Para cada startup identificada, retorne um JSON com os campos:
  - "name": nome da startup (obrigatório)
  - "sector": setor (ex: "Fintech", "Healthtech", "HR Tech")
  - "description": descrição curta
  - "funding_stage": estágio de investimento (ex: "Seed", "Série A")
  - "funding_amount": valor captado (em USD, número)
  - "ai_signals": lista de sinais de uso de IA
  - "website": site se mencionado

Retorne SEMPRE APENAS uma lista JSON válida, ex:
[{"name": "Foo", "sector": "Fintech"}, {"name": "Bar", "sector": "Healthtech"}]
NÃO invente informações que não estão no texto."""


_last_call_time: float = 0.0


_rate_limit_backoff: float = 0.0


def _call_llm(text: str) -> list[dict[str, Any]]:
    global _last_call_time, _rate_limit_backoff

    import random
    import time

    endpoint = os.getenv(
        "LLM_ENDPOINT",
        "http://localhost:11434/v1/chat/completions",
    )
    api_key = os.getenv("LLM_API_KEY") or ""
    model = os.getenv("LLM_MODEL", "llama3")
    json_mode = os.getenv("LLM_JSON_MODE", "").lower() in ("1", "true", "yes")
    rate_delay = float(os.getenv("LLM_RATE_DELAY", "10"))

    elapsed = time.time() - _last_call_time
    min_gap = rate_delay + _rate_limit_backoff
    if elapsed < min_gap:
        time.sleep(min_gap - elapsed + random.uniform(0, 1))

    import httpx

    max_chars = 12000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Texto:\n\n{text}"},
        ],
        "temperature": 0.1,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    max_attempts = 6

    for attempt in range(max_attempts):
        try:
            resp = httpx.post(endpoint, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            _last_call_time = time.time()
            _rate_limit_backoff = max(0.0, _rate_limit_backoff - 1.0)
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            return _parse_json_response(raw_content)
        except Exception as e:
            import sys
            is_429 = False
            msg = f"[LLM] attempt {attempt+1}/{max_attempts} failed: {type(e).__name__}"
            if hasattr(e, "response") and e.response is not None:
                status = e.response.status_code
                msg += f" status={status} {e.response.text[:200]}"
                is_429 = status == 429
            print(msg, file=sys.stderr)
            if is_429:
                _rate_limit_backoff += 30.0
            if attempt < max_attempts - 1:
                if is_429:
                    wait = 2 ** (attempt + 4) + random.uniform(0, 5)
                else:
                    wait = 2 ** attempt
                time.sleep(wait)

    return []


def _parse_json_response(raw: str) -> list[dict[str, Any]]:
    raw = raw.strip()

    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, dict):
        startups = parsed.get("startups", parsed.get("companies", None))
        if isinstance(startups, list):
            return startups
        return [parsed]
    if isinstance(parsed, list):
        return parsed
    return []


def extract_startups(
    text: str,
    source_url: str,
    extraction_method: str = "llm_extractor",
) -> list[StartupProfile]:
    """Extrai perfis de startups de um texto corrido via LLM."""
    raw = _call_llm(text)
    profiles: list[StartupProfile] = []

    for item in raw:
        name = (item.get("name") or "").strip()
        if not name:
            continue

        ai_signals = item.get("ai_signals") or []
        if isinstance(ai_signals, str):
            ai_signals = [ai_signals]

        source = SourceEvidence(
            url=source_url,
            extraction_method=extraction_method,
            raw_excerpt=text[:300],
        )

        funding_amount = item.get("funding_amount")
        if funding_amount is not None:
            try:
                funding_amount = float(funding_amount)
            except (ValueError, TypeError):
                funding_amount = None

        profiles.append(
            StartupProfile(
                name=name,
                sector=item.get("sector"),
                description=item.get("description"),
                funding_stage=item.get("funding_stage"),
                funding_amount_usd=funding_amount,
                website=item.get("website"),
                ai_signals=ai_signals,
                sources=[source],
            )
        )

    return profiles
