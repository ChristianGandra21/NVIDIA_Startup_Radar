"""
Parser do portfólio da ACE Ventures.
https://aceventures.com.br/venture-capital/portfolio/

Nota: o tapi.md lista "https://acestartups.com.br" (desatualizado —
      o domínio foi sequestrado). ACE Ventures é a empresa atual.
      ACE Startups Ltda. é a razão social (Crunchbase).

Estrutura HTML: Elementor flip-box com h3 (nome) e a (link).
O mesmo startup aparece em múltiplas layers do flip — deduplicamos por nome.
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from services.scraping.schema import RawPage, StartupProfile, SourceEvidence

ACE_URL = "https://aceventures.com.br/venture-capital/portfolio/"
EXTRACTION_METHOD = "bs4_ace_ventures"


def ingest_article(page: RawPage) -> list[StartupProfile]:
    """Extrai lista de startups investidas do HTML do portfólio."""
    if not page.raw_html:
        return []

    soup = BeautifulSoup(page.raw_html, "html.parser")
    seen: set[str] = set()
    profiles: list[StartupProfile] = []

    flip_boxes = soup.find_all("div", class_="elementor-flip-box")
    for box in flip_boxes:
        name_el = box.find(["h2", "h3", "h4", "h5", "h6"])
        if not name_el:
            continue
        name = name_el.get_text(strip=True)
        if not name or name in seen:
            continue

        link_el = box.find("a", href=True)
        website = link_el["href"] if link_el else None

        seen.add(name)
        source = SourceEvidence(
            url=ACE_URL,
            extraction_method=EXTRACTION_METHOD,
            raw_excerpt=f"Nome: {name}, Site: {website or 'N/A'}",
        )
        profiles.append(
            StartupProfile(
                name=name,
                website=website,
                sector="Venture Capital Portfolio",
                sources=[source],
            )
        )

    return profiles


# Aliases para compatibilidade com código legado
parse_portfolio = ingest_article
