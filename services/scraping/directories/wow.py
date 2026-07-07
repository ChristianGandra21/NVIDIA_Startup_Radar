"""
Parser do portfólio da WOW Aceleradora.
https://www.wow.ac/portfolio

Estrutura: Webflow — cada startup num bloco w-dyn-item.
Dados extraídos do texto plano + links.
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from services.scraping.schema import RawPage, StartupProfile, SourceEvidence

WOW_URL = "https://www.wow.ac/portfolio"
EXTRACTION_METHOD = "bs4_wow"

UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


EXCLUDED_NAMES = {
    "Conheça as Startups", "Portfólio", "Home", "A WOW", "Como funciona",
    "Para Founders", "Parceiros", "Contato", "Portal WOW",
    "Seja uma Acelerada WOW", "Pré-inscreva sua Startup",
}


def ingest_article(page: RawPage) -> list[StartupProfile]:
    if not page.raw_html:
        return []

    soup = BeautifulSoup(page.raw_html, "html.parser")
    profiles: list[StartupProfile] = []

    items = soup.select("div.w-dyn-item") or soup.select("div.w-dyn-list div.w-dyn-item")

    for item in items:
        text = item.get_text(" ", strip=True)

        name = _extract_name(item, text)
        if not name or name in EXCLUDED_NAMES:
            continue

        link_el = item.find("a", href=True)
        website = None
        if link_el:
            href = link_el["href"]
            if href.startswith("http"):
                website = href

        batch = _extract_batch(text)
        estado = _extract_uf(text)
        status = _extract_status(text)

        source = SourceEvidence(
            url=WOW_URL,
            extraction_method=EXTRACTION_METHOD,
            raw_excerpt=f"{name} — batch {batch or '?'}",
        )
        profiles.append(
            StartupProfile(
                name=name,
                website=website,
                state=estado,
                program=f"WOW Batch {batch}" if batch else "WOW Aceleradora",
                inovativa_status=status,
                sources=[source],
            )
        )

    return profiles


def _extract_name(item, text: str) -> str | None:
    strong = item.find("strong")
    if strong:
        t = strong.get_text(strip=True)
        if t and t not in EXCLUDED_NAMES:
            return t
    for tag in ("h3", "h4", "h5", "h6"):
        el = item.find(tag)
        if el:
            t = el.get_text(strip=True)
            if t and t not in EXCLUDED_NAMES:
                return t
    links = item.find_all("a", href=True)
    for link in links:
        t = link.get_text(strip=True)
        href = link.get("href", "")
        if t and t not in ("Acessar o site da Startup", "Acessar", "") and len(t) > 2:
            if href and href.startswith("http") and "facebook.com" not in href and "linkedin.com" not in href:
                return t
    return None


def _extract_batch(text: str) -> str | None:
    m = re.search(r"Batch\s*(\d+)", text)
    return m.group(1) if m else None


def _extract_uf(text: str) -> str | None:
    words = text.split()
    for w in words:
        if w in UFS:
            return w
    return None


def _extract_status(text: str) -> str | None:
    if "Exit" in text:
        return "exit"
    if "Write Off" in text:
        return "write_off"
    return None
