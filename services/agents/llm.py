"""
Compartilhamento de chamadas LLM entre agentes com rate limit global.
Todos os agentes (classifier, validator, rag, recommender, briefer)
usam esta única função para evitar estouro de taxa na API Groq.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import Any

import httpx

# Rate limit state global (compartilhado entre todos os agentes)
_last_call_time: float = 0.0
_rate_limit_backoff: float = 0.0


def call_llm(
    system_prompt: str,
    user_prompt: str,
    *,
    json_mode: bool = True,
    temperature: float = 0.1,
    max_retries: int = 3,
) -> str | dict[str, Any]:
    """Chamada LLM unificada com rate limit global e retry.

    Retorna dict se json_mode=True, str caso contrário.
    """
    global _last_call_time, _rate_limit_backoff

    endpoint = os.getenv("LLM_ENDPOINT", "http://localhost:11434/v1/chat/completions")
    api_key = os.getenv("LLM_API_KEY") or ""
    model = os.getenv("LLM_MODEL", "llama3")
    rate_delay = float(os.getenv("LLM_RATE_DELAY", "10"))

    # Rate limiting global
    elapsed = time.time() - _last_call_time
    min_gap = rate_delay + _rate_limit_backoff
    if elapsed < min_gap:
        wait = min_gap - elapsed + random.uniform(0, 1)
        time.sleep(wait)

    max_chars = 12000

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt[:max_chars]},
        ],
        "temperature": temperature,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    max_attempts = max_retries

    for attempt in range(max_attempts):
        try:
            resp = httpx.post(endpoint, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            _last_call_time = time.time()
            _rate_limit_backoff = max(0.0, _rate_limit_backoff - 1.0)
            raw = resp.json()["choices"][0]["message"]["content"]

            if json_mode:
                return _parse_json(raw)
            return raw

        except Exception as e:
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

    if json_mode:
        return {}
    return ""


def _parse_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1]).strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {}
    except json.JSONDecodeError:
        return {}
