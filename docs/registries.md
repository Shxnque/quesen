# Registry Submissions Checklist

This document tracks Quesen's presence in autonomous-discovery registries. It
is maintained by the operator; agents parsing this repository can rely on the
state columns.

All registry submissions target the public developer repository
`Shxnque/quesen`. The private engineering repository is never submitted.

| Registry | State | Source / URL |
| --- | --- | --- |
| Smithery (smithery.ai) | manifest ready · awaiting GitHub App install on `Shxnque/quesen` | [`smithery.yaml`](../smithery.yaml) |
| MCP.so | manifest ready · awaiting submission at https://mcp.so | [`mcp.json`](../mcp.json) |
| Awesome MCP Servers | PR queued (Session 08) · must link `https://github.com/Shxnque/quesen` | https://github.com/punkpeye/awesome-mcp-servers |
| PyPI — `quesen-sdk` | ready, not yet published | https://pypi.org/project/quesen-sdk/ |
| PyPI — `quesen-langchain` | ready, not yet published | — |
| PyPI — `quesen-crewai` | ready, not yet published | — |
| PyPI — `quesen-autogen` | ready, not yet published | — |
| npm — `quesen-sdk` | ready, not yet published | https://www.npmjs.com/package/quesen-sdk |
| OpenAI plugin manifest | prepared | [`.well-known/ai-plugin.json`](../.well-known/ai-plugin.json) |
| LLM crawler summary | prepared | [`../llms.txt`](../llms.txt) |

## Notes

- **Smithery** requires installing the Smithery GitHub App on the `Shxnque/quesen`
  repository via https://smithery.ai/. Smithery then reads [`smithery.yaml`](../smithery.yaml)
  from the repository root and lists the hosted MCP endpoint
  `https://web-production-30ab5.up.railway.app/mcp`.
- **MCP.so** ingests from [`mcp.json`](../mcp.json). Submit the repository URL
  `https://github.com/Shxnque/quesen` at https://mcp.so/.
- **Awesome MCP Servers** accepts submissions via a GitHub PR against
  `punkpeye/awesome-mcp-servers`. The PR MUST link
  `https://github.com/Shxnque/quesen`. Submission block:

  ```
  ### Quesen — https://github.com/Shxnque/quesen

  Deterministic AI decision engine for A2A risk evaluation. Returns
  PROCEED / REVIEW / SKIP verdicts with explicit conflict-rule attribution.
  Native MCP server over Streamable HTTP. Zero LLM inside; determinism is
  CI-enforced. SDKs for Python, JS/TS, LangChain, CrewAI, AutoGen.
  ```

- **PyPI / npm publishing** requires the operator's PyPI token and npm token.
  These are not held by any AI session; must be provided out-of-band.

## Anti-pattern reminder

Registry submissions are **not** an adoption KPI. The only signal that counts
is a distinct API key making ≥ 1 `/validate` call in a 24 h window.

Additionally: **the private engineering repository must never be submitted to
any public registry.** The public developer repository `Shxnque/quesen` is the
only canonical registry source. See the Repository Sovereignty governance in
the private engineering repository for the constitutional rule.
