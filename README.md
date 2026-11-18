# mcp-il-innovation

<!-- mcp-name: io.github.olegsher-ds-2025/mcp-il-innovation -->

**Israel Innovation Authority (רשות החדשנות)** programs for AI assistants. It finds the right funding track
(R&D Fund, Startup Fund, Tnufa, bilateral and EU programs, MNC pilots, incubators, human capital…), matches
programs to a company's stage and needs, and points to where open calls are published.

Built on the Authority's official [`llm.txt`](https://innovationisrael.org.il/llm.txt), the directory it publishes
for AI tools. The website itself blocks automated reading, so the server uses that directory and links to the
official pages for live calls and terms.

## Tools

| Tool | What it does |
|---|---|
| `match_programs` | Suggests programs for a stage / need / sector / partners profile, with next steps |
| `search_programs` | Keyword search with synonyms ("hiring" → Human Capital & Visas, "Europe" → bilateral & Horizon programs) |
| `list_programs` | Browse sections: Funding Programs, Collaborate With Us, Invest With Us, National Programs… |
| `open_calls_and_events` | Where current calls for proposals, events and press releases are published |
| `key_facts` | The Authority's funding model (30%–85% conditional grants) and ecosystem facts, contacts |
| `health` | Connectivity check |

**Prompt:** `israeli_funding_plan(company_profile)` builds a 6-month funding plan from IIA programs and, together
with [mcp-eu-funding](https://github.com/olegsher-ds-2025/mcp-eu-funding), matching Horizon Europe calls.

## Try asking

- "I'm a pre-seed AI startup working with a German partner — which Innovation Authority programs fit?"
- "How can an Israeli company run a pilot with a multinational abroad?"
- "Which IIA programs help hire foreign experts?"

## Install

```bash
uvx mcp-il-innovation
```

```json
{ "mcpServers": { "il-innovation": { "command": "uvx", "args": ["mcp-il-innovation"] } } }
```

HTTP mode: `MCP_TRANSPORT=http PORT=8000 mcp-il-innovation`. Docker: `docker build -t mcp-il-innovation .`.

## Verify the package

```bash
pip download mcp-il-innovation --no-deps -d dl && gh attestation verify dl/*.whl -R olegsher-ds-2025/mcp-il-innovation
```

## Roadmap

- [ ] Hebrew directory (if the Authority publishes a Hebrew llm.txt)
- [ ] Open calls list, if an official feed or open dataset becomes available

## Related

mcp-eu-funding · mcp-il-companies · mcp-il-vehicles · mcp-il-health · mcp-il-professionals, by [Oleg Sher](https://linkedin.com/in/sheroleg).

Independent project, not affiliated with the Israel Innovation Authority. Content © Israel Innovation Authority. MIT licence.
