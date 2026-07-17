# MCP Configuration

Quesen speaks the Model Context Protocol natively at
`https://web-production-30ab5.up.railway.app/mcp` (Streamable HTTP) and also as
a local stdio server (`python -m quesen.mcp_server`). Once configured, Claude
Desktop, Cursor, Windsurf, and every other MCP-compatible client can call
`quesen.validate`, `quesen.simulate`, `quesen.report`, `quesen.health`, and
`quesen.version` as first-class tools.

---

## Option A — Hosted MCP (recommended for Smithery / MCP.so / any hosted client)

Hosted MCP requires no local install. Point your client at the production URL
and supply your API key as a header. Any MCP client that supports Streamable
HTTP works.

```json
{
  "mcpServers": {
    "quesen": {
      "type": "http",
      "url": "https://web-production-30ab5.up.railway.app/mcp",
      "headers": {
        "X-API-Key": "YOUR_KEY"
      }
    }
  }
}
```

Client hints:

- **Smithery.ai** — install via the Smithery listing (one-click). Smithery
  discovers this endpoint from [`smithery.yaml`](../smithery.yaml).
- **MCP.so** — discovers via [`mcp.json`](../mcp.json).
- **Claude Desktop ≥ 0.7** — supports HTTP MCP servers natively; use the JSON
  snippet above in `claude_desktop_config.json`.

---

## Option B — Local stdio (Claude Desktop / Cursor / Windsurf classic path)

Add this to your MCP client's `mcp.json` (Claude Desktop uses
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "quesen": {
      "command": "python",
      "args": ["-m", "quesen.mcp_server"],
      "env": {
        "QUESEN_BASE_URL": "https://web-production-30ab5.up.railway.app",
        "QUESEN_API_KEY": "YOUR_KEY"
      }
    }
  }
}
```

Requires the `quesen-sdk` package (installed on the machine running the client):

```bash
pip install quesen-sdk
```

---

## Available tools (5)

- **`quesen.validate`** — the deterministic risk verdict. Returns `PROCEED`,
  `REVIEW`, or `SKIP` with `risk_score`, `confidence`, and
  `conflict_triggers`.
- **`quesen.simulate`** — counterfactual scoring with weight / threshold
  overrides. Same output shape as `quesen.validate` plus a delta.
- **`quesen.report`** — post-trade outcome feedback. Feeds the Conflict Matrix
  admission pipeline.
- **`quesen.health`** — liveness probe. Returns `engine_version` and transport
  metadata. No auth required.
- **`quesen.version`** — full engine configuration: weights, thresholds,
  protocol version, feature flags. No auth required.

---

## Registry listings

Quesen's manifests target the following autonomous-discovery registries. See
[`registries.md`](registries.md) for live state per registry.

- **Smithery** · [`smithery.yaml`](../smithery.yaml) is the source of truth.
- **MCP.so** · [`mcp.json`](../mcp.json) is the source of truth.
- **Awesome MCP Servers** · PR to https://github.com/punkpeye/awesome-mcp-servers.

See also [`.well-known/ai-plugin.json`](../.well-known/ai-plugin.json) for the
OpenAI plugin manifest.
