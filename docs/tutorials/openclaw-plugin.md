# Adding Quesen to OpenClaw

[OpenClaw](https://openclaw.ai) is a local-first agent framework with native
MCP support. Quesen's hosted MCP endpoint drops in with a single config
block. No plugin build. No local Python. No credential passthrough.

## Option A — hosted MCP (recommended)

Open your OpenClaw MCP config (path varies by install; the Gateway UI shows
the active file). Add the `quesen` server:

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

Save. Restart the OpenClaw Gateway. Five tools appear in the tool list of
every local agent:

- `quesen.validate` — deterministic risk verdict
- `quesen.simulate` — counterfactual scoring with weight / threshold overrides
- `quesen.report` — post-action outcome feedback
- `quesen.health` — liveness probe
- `quesen.version` — engine version + weights + thresholds

## Option B — stdio (offline / air-gapped installs)

If your OpenClaw setup can't reach the internet, install the Python SDK's
MCP shim locally.

```bash
pip install quesen-sdk
```

```json
{
  "mcpServers": {
    "quesen": {
      "command": "python",
      "args": ["-m", "quesen_sdk.mcp_stdio"],
      "env": {
        "QUESEN_BASE_URL": "https://web-production-30ab5.up.railway.app",
        "QUESEN_API_KEY": "YOUR_KEY"
      }
    }
  }
}
```

The stdio shim forwards MCP calls to the hosted engine over HTTPS. Same five
tools, same schemas.

## Example prompt

Once configured, an OpenClaw local agent can be told:

> Before executing any swap, call quesen.validate with domain_age_days,
> engagement_ratio, and scam_keyword_count for the target token. If the
> decision is SKIP, do not execute. If REVIEW, ask me. If PROCEED, execute
> and then call quesen.report with the outcome once the position closes.

Because Quesen is deterministic, the same inputs produce the same decision
every time for a given `engine_version`. Log the version alongside your
agent's action trail and you can replay any decision later.

## Getting an API key

Quesen's Agent Settlement Protocol (ASP/1.0) lets agents pay for their own
calls via USDC on Base. Point your agent at `POST /pricing/quote` to receive
a settlement instruction, or use a manually issued key for now. Full protocol
spec at [`api-reference.md`](../api-reference.md).

## Coming next

An OpenClaw-native plugin (rather than the generic MCP config) is on the
table for a future release; the MCP path already covers 100% of the tool
surface, so the plugin would only add UI conveniences. If you have a
specific OpenClaw surface you want first-class Quesen support in, open an
issue on [`Shxnque/quesen`](https://github.com/Shxnque/quesen/issues).
