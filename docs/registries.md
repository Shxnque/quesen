# Registry Submissions Checklist

This document tracks Quesen's presence in autonomous-discovery registries. It
is maintained by the operator; agents parsing this repository can rely on the
state columns.

**All registry submissions target the public developer repository
`Shxnque/quesen`. The private engineering repository is never submitted.**

---

## Live registry state (evidence-verified 2026-07-17 · Session 13B)

| Registry | State | Notes |
| --- | --- | --- |
| **Smithery.ai** | ✅ **LIVE.** Listing `shinque03/Quesen` is fully populated: `remote: true`, `deploymentUrl: https://quesen--shinque03.run.tools`, `iconUrl` set, **5 tools indexed with input schemas** (`quesen.validate`, `quesen.simulate`, `quesen.report`, `quesen.health`, `quesen.version`), 1 HTTP connection configured. Installable via `npx -y @smithery/cli mcp add shinque03/Quesen`. Listing page: https://smithery.ai/servers/@shinque03/Quesen. Re-verified healthy **2026-08-25 Session 31** via full MCP handshake through the canonical client URL `https://server.smithery.ai/@shinque03/quesen/mcp?api_key=…` (`initialize`→200, `notifications/initialized`→202, `tools/list`→5 tools, `tools/call quesen.health`→`{"status":"ok","engine_version":"1.10.0"}`). Latest release `f5b40647` = `SUCCESS`, `type: external_shttp`, `upstreamUrl: https://web-production-aa5ba.up.railway.app/mcp`. **The `deploymentUrl` `quesen--shinque03.run.tools` is Smithery's internal gateway id, NOT the client connect URL — a direct 404 there is expected, not a defect.** | Published via the Smithery Platform API (external_shttp). No GitHub App / repo connection installed and none required. |
| **MCP.so** | ❌ Not listed. `GET https://mcp.so/server/quesen` returns 404. | Operator dashboard action required. |
| **Glama.ai** | 🟡 **Prepared.** [`../glama.json`](../glama.json) shipped at repository root claims Quesen for `Shxnque` per the Glama schema at `https://glama.ai/mcp/schemas/server.json`. Operator submission still required: sign in at https://glama.ai, click **+ Add MCP Server**, paste `https://github.com/Shxnque/quesen`. For the remote (streamable-HTTP) surface, additionally add a **Connector** at https://glama.ai/mcp/connectors with URL `https://web-production-aa5ba.up.railway.app/mcp`. Glama's automated indexing pipeline runs security scan + license detection + health test within minutes of submission. **Note:** awesome-mcp-servers PR flow now routes to Glama's ingestion queue, so the pending PR (see below) will surface Quesen automatically once merged. | Glama token available in operator's environment. |
| **Awesome MCP Servers** | 🟡 PR [`punkpeye/awesome-mcp-servers#10402`](https://github.com/punkpeye/awesome-mcp-servers/pull/10402) — *"Add Quesen — deterministic MCP risk-decision server (Finance & Fintech)"* — **open** as of 2026-07-31. Session 14 opened it; no operator action pending on Quesen's side. Awaiting upstream merge. | Merge unblocks Glama ingestion (per Glama routing). |
| **RapidAPI Hub** | 🟡 **Prepared.** Publishing guide at [`docs/publishing-rapidapi.md`](./publishing-rapidapi.md) — provider metadata, endpoint list, and pricing-plan mapping pre-filled against `v1.10.0-rc1`. RapidAPI does not expose a public REST API for publisher onboarding; the operator must sign in at https://provider.rapidapi.com and paste `https://web-production-aa5ba.up.railway.app/openapi.json`. The RapidAPI token in the operator's environment is a subscriber key (`X-RapidAPI-Key`), not a publisher key. | Consumer key `4f103d13...` verified live but not usable for publishing. |
| **PyPI — `quesen-sdk`** | ready at v0.2.0, not yet published | Operator holds PyPI token. |
| **PyPI — `quesen-langchain`** | ready at v0.2.0, not yet published | — |
| **PyPI — `quesen-crewai`** | ready at v0.2.0, not yet published | — |
| **PyPI — `quesen-autogen`** | ready at v0.2.0, not yet published | — |
| **npm — `quesen-sdk`** | ready at v0.2.0, not yet published | Operator holds npm token. |
| **OpenAI plugin manifest** | ✅ Prepared. [`.well-known/ai-plugin.json`](../.well-known/ai-plugin.json) points at `senueren.co.za`. | Auto-discovered by ChatGPT / OpenAI clients when hosted at the plugin URL. |
| **LLM crawler summary** | ✅ Prepared. [`../llms.txt`](../llms.txt) at engine v1.10.0. | Auto-discovered by LLM crawlers. |
| **Live MCP endpoint** | ✅ **Healthy · engine v1.10.0 · 5 tools live** at `https://web-production-aa5ba.up.railway.app/mcp` | Verified via `initialize` / `tools/list` / `tools/call`. |

---

## Registry manifest source of truth

- **Smithery** · [`smithery.yaml`](../smithery.yaml) at this repository's root.
- **MCP.so** · [`mcp.json`](../mcp.json) at this repository's root.
- **Glama.ai** · [`glama.json`](../glama.json) at this repository's root (schema `https://glama.ai/mcp/schemas/server.json`).
- **OpenAI plugin** · [`.well-known/ai-plugin.json`](../.well-known/ai-plugin.json).
- **LLM crawlers** · [`../llms.txt`](../llms.txt).
- **RapidAPI Hub** · [`../docs/publishing-rapidapi.md`](./publishing-rapidapi.md) (provider onboarding walk-through; the OpenAPI spec at `https://web-production-aa5ba.up.railway.app/openapi.json` is the wire-contract source of truth).

All six files are aligned with production (engine v1.10.0; five tools
`quesen.validate`, `quesen.simulate`, `quesen.report`, `quesen.health`,
`quesen.version`; hosted-HTTP transport as primary).

---

## Operator actions to complete the registry rollout

The following actions **cannot be automated** (or, in Smithery's case, have now been completed). They require the operator to sign in to each service's web dashboard.

### 1. ✅ Smithery — COMPLETED in Session 13B

The Smithery listing `shinque03/Quesen` was published programmatically via the Smithery CLI. State:

- `remote: true`
- `deploymentUrl: https://quesen--shinque03.run.tools` (Smithery proxy → Railway MCP endpoint)
- `iconUrl: https://api.smithery.ai/servers/shinque03/Quesen/icon` (Smithery CDN)
- All 5 tools indexed with full input schemas
- Listing page: https://smithery.ai/servers/@shinque03/Quesen
- Install command for MCP clients: `npx -y @smithery/cli mcp add shinque03/Quesen`

No further Smithery action is required unless a schema, description, or deployment URL needs to change (in which case re-publish with `smithery mcp publish ... -n shinque03/Quesen`).

### 2. MCP.so — submit the public repository

1. Visit https://mcp.so/.
2. Submit `https://github.com/Shxnque/quesen`.
3. MCP.so will read [`mcp.json`](../mcp.json).

### 3. Awesome MCP Servers — open a PR

1. Fork `https://github.com/punkpeye/awesome-mcp-servers`.
2. Add the following entry under the appropriate category (agents / risk / settlement):

   ```
   ### Quesen — https://github.com/Shxnque/quesen

   Deterministic AI decision engine for A2A risk evaluation. Returns
   PROCEED / REVIEW / SKIP verdicts with explicit conflict-rule attribution.
   Native MCP server over Streamable HTTP. Zero LLM inside; determinism is
   CI-enforced. SDKs for Python, JS/TS, LangChain, CrewAI, AutoGen.
   ```

3. Open the PR.

### 4. PyPI + npm publication

Separate action. Operator holds the tokens. Each of the five public sibling
repositories has its own release workflow.

---

## Verification commands (evidence-driven — 2026-08-25)

The listing is an **external** streamable-HTTP release. Verify against the
**client connect URL**, not the internal gateway id.

```bash
# 1. Registry record (management API) — confirms the external release + upstream
curl -sS -H "Authorization: Bearer $SMITHERY_API_KEY" \
  https://api.smithery.ai/servers/%40shinque03%2Fquesen/releases | python3 -m json.tool
# Latest release should be: status=SUCCESS, type=external_shttp,
#   upstreamUrl=https://web-production-aa5ba.up.railway.app/mcp

# 2. Full MCP handshake through the CLIENT connect URL (this is what works)
URL="https://server.smithery.ai/@shinque03/quesen/mcp?api_key=$SMITHERY_API_KEY"
curl -sS -X POST "$URL" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}'
# -> 200 with serverInfo {name:"quesen", version:"1.10.0"} and an mcp-session-id header
```

> **STOPPING RULE (do not reopen without new evidence).**
> `https://quesen--shinque03.run.tools/mcp` returning HTTP 404 is **NOT** a
> defect. That host is Smithery's internal deployment identifier stored in the
> registry `deploymentUrl` field; it is never the client connect URL and is not
> meant to be hit directly/unauthenticated. MCP clients connect via
> `server.smithery.ai/@shinque03/quesen/mcp` (or `npx -y @smithery/cli mcp add
> shinque03/Quesen`), which is verified healthy. Do **not** re-publish the
> release, install the Smithery GitHub App, or modify the Quesen engine to
> "fix" this 404 — the integration already works.

---

## Anti-pattern reminder

Registry submissions are **not** an adoption KPI. The only signal that counts
is a distinct API key making ≥ 1 `/validate` call in a 24 h window.

Additionally: **the private engineering repository must never be submitted to
any public registry.** The public developer repository `Shxnque/quesen` is the
only canonical registry source. See the Repository Sovereignty governance in
the private engineering repository for the constitutional rule.
