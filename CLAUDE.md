# mcp-il-innovation — CLAUDE.md

Israel Innovation Authority programs MCP server.

## Data source (verified 2026-11-18)
- Only https://innovationisrael.org.il/llm.txt is machine-readable (official directory for AI tools, ~44 entries in 7 sections).
- All other pages, /wp-json and /feed return a Cloudflare bot challenge (403). Do NOT try to bypass it; link to pages instead.
- No IIA datasets on data.gov.il.

## Layout
- src/mcp_il_innovation/directory.py — fetch + parse llm.txt (cache 12h; override URL with IIA_LLM_TXT_URL)
- src/mcp_il_innovation/server.py — tools, SYNONYMS map for matching, `israeli_funding_plan` prompt
- tests/ — offline with a sample llm.txt; `pytest -m live` for the real file

## Rules
- Every response includes `source`, `retrieved_at`, `attribution` via `meta()`.
- If llm.txt format changes, update `parse()` and the sample in tests.
- Bump version in pyproject.toml, __init__.py and server.json together BEFORE tagging.
- Update MEMORY.md at the end of every session.

## Model routing
Architect/Advisor: Fable (else Opus) · Orchestrator: Opus · Executor: Sonnet · Explorer/tests: Haiku · tiny text jobs: Jetson llama.cpp · graphics: Gemini/ChatGPT.
