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
| **Smithery.ai** | ✅ **LIVE.** Listing `shinque03/Quesen` is fully populated: `remote: true`, `deploymentUrl: https://quesen--shinque03.run.tools`, `iconUrl` set, **5 tools indexed with input schemas** (`quesen.validate`, `quesen.simulate`, `quesen.report`, `quesen.health`, `quesen.version`), 1 HTTP connection configured. Installable via `npx -y @smithery/cli mcp add shinque03/Quesen`. Listing page: https://smithery.ai/servers/@shinque03/Quesen. | Published in Session 13B via the Smithery Platform API. Release `7df59cac-...` status `SUCCESS`. |
| **MCP.so** | ❌ Not listed. `GET https://mcp.so/server/quesen` returns 404. | Operator dashboard action required. |
| **Awesome MCP Servers** | ❌ No PR found. GitHub search of `punkpeye/awesome-mcp-servers` for `quesen` returns zero hits. | Operator must open a PR against `punkpeye/awesome-mcp-servers` linking `https://github.com/Shxnque/quesen`. |
| **PyPI — `quesen-sdk`** | ready, not yet published | Operator holds PyPI token. |
| **PyPI — `quesen-langchain`** | ready, not yet published | — |
| **PyPI — `quesen-crewai`** | ready, not yet published | — |
| **PyPI — `quesen-autogen`** | ready, not yet published | — |
| **npm — `quesen-sdk`** | ready, not yet published | Operator holds npm token. |
| **OpenAI plugin manifest** | ✅ Prepared. [`.well-known/ai-plugin.json`](../.well-known/ai-plugin.json) points at `senueren.co.za`. | Auto-discovered by ChatGPT / OpenAI clients when hosted at the plugin URL. |
| **LLM crawler summary** | ✅ Prepared. [`../llms.txt`](../llms.txt) at engine v1.9.0. | Auto-discovered by LLM crawlers. |
| **Live MCP endpoint** | ✅ **Healthy · engine v1.9.0 · 5 tools live** at `https://web-production-30ab5.up.railway.app/mcp` | Verified via `initialize` / `tools/list` / `tools/call`. |

---

## Registry manifest source of truth

- **Smithery** · [`smithery.yaml`](../smithery.yaml) at this repository's root.
- **MCP.so** · [`mcp.json`](../mcp.json) at this repository's root.
- **OpenAI plugin** · [`.well-known/ai-plugin.json`](../.well-known/ai-plugin.json).
- **LLM crawlers** · [`../llms.txt`](../llms.txt).

All four files are aligned with production (engine v1.9.0; five tools
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

## Verification commands (post-Smithery connection)

After the operator connects Smithery to `Shxnque/quesen`, verify with:

```bash
# Smithery listing state
curl -sS https://registry.smithery.ai/servers/shinque03/Quesen | python3 -m json.tool

# Should now show:
#   "remote": true,
#   "deploymentUrl": "https://web-production-30ab5.up.railway.app/mcp",
#   "tools": [ ... five entries ... ],
#   "connections": [ ... at least one HTTP connection ... ]
```

---

## Anti-pattern reminder

Registry submissions are **not** an adoption KPI. The only signal that counts
is a distinct API key making ≥ 1 `/validate` call in a 24 h window.

Additionally: **the private engineering repository must never be submitted to
any public registry.** The public developer repository `Shxnque/quesen` is the
only canonical registry source. See the Repository Sovereignty governance in
the private engineering repository for the constitutional rule.
