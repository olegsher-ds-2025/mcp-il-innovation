"""mcp-il-innovation — Israel Innovation Authority (רשות החדשנות) programs for AI assistants: funding tracks,
collaboration frameworks, national programs, where to find open calls, and matching programs to a need.
Built on the Authority's official llm.txt directory (the website itself blocks automated reading)."""
from __future__ import annotations

import os
import re

from fastmcp import FastMCP

from . import __version__
from .directory import entries, load, meta

mcp = FastMCP(
    "mcp-il-innovation",
    version=__version__,
    instructions=(
        "Israel Innovation Authority programs. Use match_programs to map a company's need (stage, partners, "
        "region, sector) to the right IIA tracks, search_programs for keywords, list_programs to browse by "
        "section, and open_calls_and_events for where current calls are published. Program terms change — "
        "always send the user to the official program page. For EU calls combine with mcp-eu-funding."
    ),
)

# Plain-language needs -> words that appear in program titles/descriptions
SYNONYMS = {
    "idea": ["ideation", "tnufa", "fledgling", "validate"], "early": ["startup", "pre-seed", "ideation", "incubator"],
    "pre-seed": ["startup", "ideation", "incubator"], "seed": ["startup fund", "incubator", "early-stage"],
    "rnd": ["r&d"], "r&d": ["r&d fund", "research"], "product": ["r&d fund", "new products"],
    "grant": ["fund", "incentive", "grants"], "funding": ["fund", "incentive", "co-funding"],
    "europe": ["european", "eu", "horizon", "bilateral"], "eu": ["european", "horizon", "framework"],
    "horizon": ["eu framework", "horizon"], "international": ["bilateral", "global", "multinational", "bi-national"],
    "abroad": ["bilateral", "foreign", "multinational"], "corporate": ["multinational", "mnc", "innovation labs"],
    "mnc": ["multinational", "mnc"], "pilot": ["pilot"], "academia": ["academia", "research institutions", "consortia"],
    "university": ["academia", "research institutions"], "factory": ["manufacturing", "industrial"],
    "manufacturing": ["manufacturing", "industrial"], "hiring": ["human capital", "visas", "personnel"],
    "talent": ["human capital", "visas"], "visa": ["visas", "foreign high-tech experts"],
    "ai": ["ai", "artificial intelligence"], "health": ["global health", "bio-convergence", "healthcare"],
    "bio": ["bio-convergence", "biology"], "agriculture": ["agriculture", "food"], "climate": ["climate", "energy"],
    "investor": ["co-invest", "invest", "investors"], "vc": ["co-invest", "investors", "venture"],
    "consortium": ["consortia", "consortium"], "lab": ["innovation labs", "infrastructures"],
    "academic": ["academia", "applied research"], "research": ["applied research", "academia"],
    "commercialize": ["applied research", "commercial"], "production": ["manufacturing", "industrial"],
}
HUB_PAGES = {"invest with us", "collaborate with us", "global collaborations", "all programs"}


def _score(entry: dict, terms: list[str]) -> int:
    hay = f"{entry['title']} {entry.get('description') or ''}".lower()
    title = entry["title"].lower()
    s = 0
    for t in terms:
        if t in title:
            s += 3
        elif t in hay:
            s += 1
    return s


def _expand(text: str) -> list[str]:
    words = [w for w in re.split(r"[^\w&+-]+", text.lower()) if len(w) > 1]
    terms = set(words)
    for w in words:
        terms.update(SYNONYMS.get(w, []))
    return sorted(terms)


@mcp.tool
async def list_programs(section: str = "") -> dict:
    """Browse the Authority's directory. Sections include "Funding Programs", "Collaborate With Us",
    "Invest With Us", "National Programs", "News & Resources", "About". Empty section = section list with counts."""
    data = await load()
    if not section:
        return {"sections": {k: len(v) for k, v in data["sections"].items()}, "summary": data["summary"], **meta(data)}
    match = next((k for k in data["sections"] if section.lower() in k.lower()), None)
    if not match:
        raise ValueError(f"Unknown section. Available: {', '.join(data['sections'])}")
    return {"section": match, "programs": data["sections"][match], **meta(data)}


@mcp.tool
async def search_programs(query: str, limit: int = 10) -> dict:
    """Keyword search over all programs and pages (title + description), with synonym expansion
    (e.g. "hiring" also finds Human Capital and Visas; "Europe" finds bilateral and Horizon programs)."""
    data = await load()
    terms = _expand(query)
    ranked = sorted(((e, _score(e, terms)) for e in entries(data)), key=lambda x: -x[1])
    hits = [dict(e, relevance=s) for e, s in ranked if s > 0][: max(1, min(limit, 50))]
    return {"query": query, "matched_terms": terms, "results": hits, **meta(data)}


@mcp.tool
async def match_programs(stage: str = "", need: str = "", sector: str = "", partners: str = "", limit: int = 6) -> dict:
    """Suggest IIA programs for a company.

    Args:
        stage: e.g. "idea", "pre-seed startup", "growth company", "academic lab", "factory".
        need: e.g. "R&D grant for new product", "hire foreign experts", "pilot with a corporate abroad".
        sector: e.g. "AI", "health", "agriculture", "climate", "manufacturing".
        partners: e.g. "European company", "multinational", "university", "investors".
    Only funding/collaboration programs are ranked; always confirm eligibility on the program page.
    """
    data = await load()
    terms = _expand(" ".join([stage, need, sector, partners]))
    pool = [e for e in entries(data) if e["section"] in ("Funding Programs", "Collaborate With Us", "National Programs",
                                                         "Invest With Us")
            and "calls for proposals" not in e["title"].lower() and e["title"].lower() not in HUB_PAGES]
    ranked = sorted(((e, _score(e, terms)) for e in pool), key=lambda x: -x[1])
    picks = [dict(e, relevance=s) for e, s in ranked if s > 0][: max(1, min(limit, 15))]
    calls = next((e for e in entries(data) if "calls for proposals" in e["title"].lower()), None)
    return {
        "profile": {"stage": stage, "need": need, "sector": sector, "partners": partners},
        "suggestions": picks,
        "next_steps": [
            "Open each program page to check eligibility, grant rate and application windows.",
            f"Check currently open calls: {calls['url'] if calls else 'https://innovationisrael.org.il/en/calls_for_proposal/'}",
            "For EU-funded collaboration (Horizon Europe), also search EU calls with mcp-eu-funding.",
        ],
        **meta(data),
    }


@mcp.tool
async def open_calls_and_events() -> dict:
    """Where the Authority publishes open calls for proposals, events/webinars and press releases.
    (The pages themselves can't be read automatically — the site blocks bots — so this returns the links.)"""
    data = await load()
    want = ("calls for proposals", "events", "press releases", "success stories", "digital reports")
    links = [e for e in entries(data) if any(w in e["title"].lower() for w in want)]
    return {"links": links, "contact": data["contact"],
            "tip": "Open calls change frequently; ask the user to check the Calls for Proposals page or subscribe there.",
            **meta(data)}


@mcp.tool
async def key_facts() -> dict:
    """The Authority's own key facts about Israel's tech ecosystem and its funding model (e.g. 30%–85% co-funding,
    conditional grants repaid only on commercial success), plus contact details."""
    data = await load()
    return {"organisation": data["title"], "summary": data["summary"], "facts": data["facts"],
            "contact": data["contact"], **meta(data)}


@mcp.tool
async def health() -> dict:
    """Check that the Authority's directory can be loaded."""
    try:
        data = await load(force=True)
        return {"status": "ok", "entries": len(entries(data)), "sections": len(data["sections"]), **meta(data)}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


@mcp.prompt
def israeli_funding_plan(company_profile: str) -> str:
    """Build a funding plan for an Israeli company combining Innovation Authority tracks and EU calls."""
    return f"""Company profile: {company_profile}

1. Call `match_programs` with the company's stage, need, sector and partners. Pick the 3 most relevant
   Israel Innovation Authority programs and explain in one line each why they fit.
2. If the company works with European partners or wants EU money, and the `search_funding` tool from
   mcp-eu-funding is available, find 3 matching open Horizon Europe / Digital Europe calls and mention the
   IIA program "Increasing Participation in EU Framework Program" as support for applying.
3. Give a 6-month sequence: which application first, what to prepare, and the official links to check
   (program pages and the Calls for Proposals page).
Make clear that grant rates and eligibility must be confirmed on the official pages."""


def main() -> None:
    if os.environ.get("MCP_TRANSPORT", "stdio") == "stdio":
        mcp.run()
    else:
        mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()
