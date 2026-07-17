# Registry Submissions Checklist

This document tracks Quesen's presence in autonomous-discovery registries. It
is maintained by the operator; agents parsing this repository can rely on the
state columns.

**All registry submissions target the public developer repository
`Shxnque/quesen`. The private engineering repository is never submitted.**

---

## Live registry state (evidence-verified 2026-07-17 · Session 13A)

| Registry | State | Notes |
| --- | --- | --- |
| **Smithery.ai** | ⚠️ **STUB — not connected.** Listing exists at [`smithery.ai/servers/@shinque03/Quesen`](https://smithery.ai/servers/@shinque03/Quesen), name + description populated, but **no GitHub connection, no `deploymentUrl`, `remote: false`, `tools: null`, `connections: []`**. Clients cannot use it via Smithery. | Operator dashboard action required — see below. |
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

The following actions **cannot be automated**. They require the operator to
sign in to each service's web dashboard.

### 1. Smithery — connect the GitHub App to this repository

The Smithery listing `shinque03/Quesen` currently exists as a stub. To
transition it from stub to functional:

1. Sign in to https://smithery.ai/ as `shinque03`.
2. Open the existing Quesen listing (https://smithery.ai/servers/@shinque03/Quesen).
3. Click "Connect GitHub" (or "Add source" / "Link repository").
4. Select **`Shxnque/quesen`** as the source repository. Do NOT select
   `Shxnque/Quesen-sib` (the private engineering repository — selecting it is
   a constitutional violation per the internal Repository Sovereignty rule).
5. Smithery will read [`smithery.yaml`](../smithery.yaml) from the repository
   root, discover `startCommand.type = http` with
   `url: https://web-production-30ab5.up.railway.app/mcp`, and populate:
   - `remote: true`
   - `deploymentUrl: https://web-production-30ab5.up.railway.app/mcp`
   - `connections: [{ type: "http", ... }]`
   - `tools: [quesen.validate, quesen.simulate, quesen.report, quesen.health, quesen.version]`
6. Re-verify by hitting `GET https://registry.smithery.ai/servers/shinque03/Quesen`
   and confirming `remote=true`, `deploymentUrl` set, `tools` populated.

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
