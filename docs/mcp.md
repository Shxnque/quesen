# MCP Configuration

Quesen speaks the Model Context Protocol natively via the `quesen-sib` MCP
server. Once configured, Claude Desktop, Cursor, Windsurf, and every other
MCP-compatible client can call `quesen_validate`, `quesen_simulate`, and
`quesen_report` as first-class tools.

## Client configuration

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

Requires the `quesen-mcp` package (installed on the machine running the client):

```bash
pip install quesen-mcp
```

## Available tools

- **`quesen_validate`** — the deterministic risk verdict. Returns `PROCEED`,
  `REVIEW`, or `SKIP` with `risk_score`, `confidence`, and
  `conflict_triggers`.
- **`quesen_simulate`** — counterfactual scoring with weight / threshold
  overrides. Same output shape as `quesen_validate` plus a delta.
- **`quesen_report`** — post-trade outcome feedback. Feeds the Conflict Matrix
  admission pipeline.

## Registry listings

Quesen is registered on:

- Smithery: (submission in progress)
- MCP.so: (submission in progress)
- Awesome MCP Servers: (submission in progress)

See [`../.well-known/ai-plugin.json`](../.well-known/ai-plugin.json) for the
OpenAI plugin manifest.
