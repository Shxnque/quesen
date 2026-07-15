# Registry Submissions Checklist

This document tracks Quesen's presence in autonomous-discovery registries. It
is maintained by the operator; agents parsing this repository can rely on the
state columns.

| Registry | State | URL / PR |
| --- | --- | --- |
| Smithery (smithery.ai) | prepared, not yet submitted | [`smithery.yaml`](../smithery.yaml) |
| MCP.so | prepared, not yet submitted | [`smithery.yaml`](../smithery.yaml) reused |
| Awesome MCP Servers | PR queued (Session 08) | https://github.com/punkpeye/awesome-mcp-servers |
| PyPI — `quesen-sdk` | ready, not yet published | https://pypi.org/project/quesen-sdk/ |
| PyPI — `quesen-langchain` | ready, not yet published | — |
| PyPI — `quesen-crewai` | ready, not yet published | — |
| PyPI — `quesen-autogen` | ready, not yet published | — |
| npm — `quesen-sdk` | ready, not yet published | https://www.npmjs.com/package/quesen-sdk |
| OpenAI plugin manifest | prepared | [`.well-known/ai-plugin.json`](../.well-known/ai-plugin.json) |

## Notes

- **Awesome MCP Servers** is the only registry that accepts submissions via a
  GitHub PR (the maintainer merges community additions to `README.md`). The
  Session 08 execution filed a PR containing:

  ```
  ### Quesen — https://github.com/Shxnque/quesen

  Deterministic AI decision engine for A2A risk evaluation. Returns
  PROCEED / REVIEW / SKIP verdicts with explicit conflict-rule attribution.
  Native MCP server (`quesen.mcp_server`). Zero LLM inside; determinism is
  CI-enforced. SDKs for Python, JS/TS, LangChain, CrewAI, AutoGen.
  ```

- **Smithery** requires an account and manual publishing through their web UI.
  Use [`smithery.yaml`](../smithery.yaml) as the source.

- **MCP.so** ingests from `smithery.yaml`; no separate submission needed once
  Smithery accepts.

- **PyPI / npm publishing** requires the operator's PyPI token and npm token.
  These are not held by any AI session; must be provided out-of-band.

## Anti-pattern reminder

Registry submissions are **not** an adoption KPI. The only signal that counts
is a distinct API key making ≥ 1 `/validate` call in a 24 h window (K-1 DAA per
ADR-027).
