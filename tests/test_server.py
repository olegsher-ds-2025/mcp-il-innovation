import asyncio

import pytest
from fastmcp import Client

from mcp_il_innovation import directory, server

SAMPLE = """# Israel Innovation Authority

> The Authority supports innovation.

## Invest With Us

- [Calls for Proposals](https://example.org/calls/): Current open calls.

## Funding Programs

- [R&D Fund](https://example.org/rd/): Supports companies developing new products.
- [Visas for Foreign High-Tech Experts](https://example.org/visa/): Visa program for foreign experts.
- [Bilateral R&D Incentive Program](https://example.org/bi/): Joint R&D with foreign companies.

## Key Facts

- Conditional grants of 30%-85%.

## Contact

- Website: https://example.org/
"""


@pytest.fixture
def offline(monkeypatch):
    data = directory.parse(SAMPLE)
    data["fetched_at"] = "2026-01-01T00:00:00+00:00"

    async def fake_load(force=False):
        return data

    monkeypatch.setattr(server, "load", fake_load)


def _call(tool, args):
    async def run():
        async with Client(server.mcp) as c:
            r = await c.call_tool(tool, args)
            return r.data if hasattr(r, "data") else r
    return asyncio.run(run())


def test_parse():
    d = directory.parse(SAMPLE)
    assert d["title"] == "Israel Innovation Authority"
    assert [e["title"] for e in d["sections"]["Funding Programs"]][0] == "R&D Fund"
    assert d["facts"] == ["Conditional grants of 30%-85%."] and d["contact"]


def test_search_synonyms(offline):
    data = _call("search_programs", {"query": "hiring"})
    assert data["results"][0]["title"].startswith("Visas")


def test_match_excludes_calls_page(offline):
    data = _call("match_programs", {"need": "R&D grant", "partners": "foreign company"})
    titles = [s["title"] for s in data["suggestions"]]
    assert "R&D Fund" in titles and "Calls for Proposals" not in titles
    assert "source" in data


def test_tools_registered():
    async def run():
        async with Client(server.mcp) as c:
            return {t.name for t in await c.list_tools()}
    assert {"list_programs", "search_programs", "match_programs", "open_calls_and_events", "key_facts", "health"} <= asyncio.run(run())


@pytest.mark.live
def test_live_health():
    assert _call("health", {})["status"] == "ok"
