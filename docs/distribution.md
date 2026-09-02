# Distribution & Verification-Badge Playbook

Evidence-verified map of every surface where Quesen can be **discovered,
installed, tested, integrated, or recommended**, plus the exact action to
advance each. Distribution is treated as a discoverability + credibility lever
(authoritative backlinks + independent badges), **not** as an adoption KPI — the
only adoption signal that counts is a distinct API key making ≥ 1 `/validate`
call in 24 h.

> **Verification status legend:** ✅ live/listed · 🟡 action pending · ❌ gap
> **Automation legend:** `[api]` programmatic · `[dash]` requires operator web login

_Last audit: 2026-09-02 (evidence-driven, direct HTTP probes)._

## MCP registries & directories

| Surface | Status | Evidence | Next action |
| --- | --- | --- | --- |
| **MCP official registry** (`registry.modelcontextprotocol.io`) | ✅ listed | `io.github.Shxnque/quesen` v1.10.0, full record + icon | Keep `server.json` in sync; re-publish on version bump via `.github/workflows/publish-mcp-registry.yml`. `[api]` |
| **Smithery.ai** | ✅ live | `@shinque03/quesen`, 5 tools w/ input schemas, live MCP handshake OK, public page 200 | None. Re-publish only if schema/description/URL changes. `[api]` |
| **Glama.ai** | ✅ connector live | `glama.ai/mcp/connectors/io.github.Shxnque/quesen` → 200 | Confirm the connector exposes the current firewall/TSC surface + description is not stale. `[dash]` |
| **MCP.so** | ❌ not listed | `mcp.so/server/quesen` → 404 | Submit `https://github.com/Shxnque/quesen` at mcp.so (reads `mcp.json`). `[dash]` |
| **PulseMCP** | 🟡 verify | `/servers/quesen` → 403 to bots; v0beta API sunsetting | Confirm listing in a browser; PulseMCP auto-indexes GitHub `mcp` topic — ensure topic present (it is). `[dash]` |
| **Awesome MCP Servers** (`punkpeye/awesome-mcp-servers`) | 🟡 PR flow | prior PR opened | Track merge; merge routes into Glama ingestion. `[api]` (PR) |
| **mcpservers.org / mcp.run / mcp-get / cursor.directory** | 🟡 candidates | all reachable (200/429) | Evaluate each submit path; most read a GitHub repo or `mcp.json`. `[dash]` |

## Verification / trust badges (credibility)

| Badge program | Status | Evidence | Next action |
| --- | --- | --- | --- |
| **m8ven Verified** | ❌ not verified | `m8ven.ai/verified` lists Quesen + Senueren as *not verified* | Submit the MCP at **https://m8ven.ai/developers** (form; requires MCP details + contact + description). Supporting evidence: the [`verify/`](../verify/) bundle (runnable verifier + honest boundary) directly answers a security/reputation review. `[dash]` |
| **Independent receipt verification** (self-hosted) | ✅ shipped | [`verify/three_way_match.json`](../verify/three_way_match.json): 6/6 byte-for-byte | Linked from README badge + `llms.txt`. Keep evidence fresh on ruleset bumps. `[api]` |

## Package registries

| Package | Status | Evidence |
| --- | --- | --- |
| PyPI `quesen-sdk` | ✅ v0.4.1 | pypi.org/project/quesen-sdk |
| PyPI `quesen-langchain` / `quesen-crewai` / `quesen-autogen` | ✅ v0.3.0 | pypi.org |
| npm `quesen-sdk` | ✅ v0.4.0 | npmjs.com/package/quesen-sdk |

## Agent platforms / marketplaces

| Surface | Status | Next action |
| --- | --- | --- |
| **ASI:One** (`asi1.ai/developer`, Fetch.ai / ASI Alliance) | 🟡 listing pending | Sign in → list Quesen as an MCP server/tool using the hosted endpoint. Inference key verified working (`asi1-mini`); it is an inference key, not a publishing key, so listing is `[dash]`. **Bonus:** reuse that key to power BEA's AI classifier (removes the HuggingFace credit-limit dependency). |
| **RapidAPI Hub** | 🟡 prepared | Sign in at provider.rapidapi.com → paste `…/openapi.json`. See `docs/publishing-rapidapi.md`. `[dash]` |
| **OpenAI plugin manifest** | ✅ prepared | `.well-known/ai-plugin.json` auto-discovered when hosted. |

## SEO / web-discovery surfaces (this repo)

- `llms.txt`, `robots.txt`, `sitemap.xml`, `.well-known/ai-plugin.json`, `mcp.json`,
  `smithery.yaml`, `server.json`, `glama.json` — all aligned to engine v1.10.0.
- Website (`senueren.co.za`) carries Organization + WebSite + SoftwareApplication +
  FAQ JSON-LD, OG/Twitter cards, canonical, IndexNow key, LLM-crawler allows, and
  per-route prerendered content for no-JS crawlers.

## Operator quick-action queue (highest leverage first)

1. **m8ven** — submit at m8ven.ai/developers (credibility badge). `[dash]`
2. **MCP.so** — submit the repo (fills a 404 gap; authoritative backlink). `[dash]`
3. **ASI:One** — list Quesen + wire the ASI key into BEA's classifier. `[dash]`
4. **Glama** — confirm connector exposes the current TSC/firewall surface. `[dash]`
5. **RapidAPI** — paste the OpenAPI spec. `[dash]`
