"""Loads the Israel Innovation Authority's official llm.txt — the machine-readable directory the Authority
publishes for AI tools — and parses it into sections and entries. Cached in memory for 12 hours."""
from __future__ import annotations

import os
import re
import time
from datetime import UTC, datetime

import httpx

LLM_TXT = os.environ.get("IIA_LLM_TXT_URL", "https://innovationisrael.org.il/llm.txt")
USER_AGENT = "mcp-il-innovation/0.1 (+https://github.com/olegsher-ds-2025/mcp-il-innovation)"
TTL = 12 * 3600
_ENTRY = re.compile(r"^- \[(?P<title>[^\]]+)\]\((?P<url>[^)]+)\):?\s*(?P<desc>.*)$")
_cache: dict = {}


class DirectoryError(RuntimeError):
    pass


def parse(text: str) -> dict:
    out: dict = {"title": None, "summary": None, "sections": {}, "facts": [], "contact": []}
    section = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("# ") and not out["title"]:
            out["title"] = line[2:].strip()
        elif line.startswith("> ") and not out["summary"]:
            out["summary"] = line[2:].strip()
        elif line.startswith("## "):
            section = line[3:].strip()
            out["sections"].setdefault(section, [])
        elif line.startswith("- ") and section:
            m = _ENTRY.match(line)
            if m:
                out["sections"][section].append({"title": m["title"].strip(), "url": m["url"].strip(),
                                                 "description": m["desc"].strip() or None, "section": section})
            elif section.lower().startswith("key facts"):
                out["facts"].append(line[2:].strip())
            elif section.lower().startswith("contact"):
                out["contact"].append(line[2:].strip())
    out["sections"] = {k: v for k, v in out["sections"].items() if v}
    return out


async def load(force: bool = False) -> dict:
    now = time.time()
    if not force and _cache.get("data") and now - _cache["at"] < TTL:
        return _cache["data"]
    try:
        async with httpx.AsyncClient(timeout=20, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as c:
            r = await c.get(LLM_TXT)
            r.raise_for_status()
    except httpx.HTTPError as exc:
        if _cache.get("data"):
            return _cache["data"]
        raise DirectoryError(f"Could not load {LLM_TXT}: {exc}") from exc
    data = parse(r.text)
    if not data["sections"]:
        raise DirectoryError("llm.txt format not recognised")
    data["fetched_at"] = datetime.now(UTC).isoformat(timespec="seconds")
    _cache.update(data=data, at=now)
    return data


def entries(data: dict) -> list[dict]:
    return [e for items in data["sections"].values() for e in items]


def meta(data: dict | None = None) -> dict:
    return {
        "source": f"Israel Innovation Authority — official AI directory ({LLM_TXT})",
        "retrieved_at": (data or {}).get("fetched_at") or datetime.now(UTC).isoformat(timespec="seconds"),
        "attribution": "© Israel Innovation Authority. Unofficial tool; confirm terms and open calls on innovationisrael.org.il.",
    }
