# Quesen — Developer Portal

[![MCP compatible](https://img.shields.io/badge/MCP-2025--03--26-8B5CF6?labelColor=1F2937)](https://spec.modelcontextprotocol.io/)
[![ASP version](https://img.shields.io/badge/ASP-1.0-06B6D4?labelColor=1F2937)](docs/api-reference.md)
[![Engine version](https://img.shields.io/badge/engine-1.9.0-16A34A?labelColor=1F2937)](https://web-production-30ab5.up.railway.app/version)
[![License](https://img.shields.io/badge/license-MIT-6B7280?labelColor=1F2937)](./LICENSE)

> **Quesen** is the deterministic AI decision engine for **A2A (Agent-to-Agent)**
> risk evaluation. It is the trust filter that sits between autonomous agents
> and capital loss.
>
> This repository is the **public developer portal**. It contains **only**
> documentation, integration guides, examples, registry manifests, and
> reference links. **No engine source code lives here.** Quesen's engine
> implementation is sovereign, non-public infrastructure.

**Live production**

| Surface | URL |
| :--- | :--- |
| REST API | `https://web-production-30ab5.up.railway.app` |
| MCP (Streamable HTTP) | `https://web-production-30ab5.up.railway.app/mcp` |
| OpenAPI 3.1 | `https://web-production-30ab5.up.railway.app/openapi.json` |
| Swagger UI | `https://web-production-30ab5.up.railway.app/docs` |
| Health | `https://web-production-30ab5.up.railway.app/health` |
| Version | `https://web-production-30ab5.up.railway.app/version` |

---

## Quick start (30 seconds)

### Python

```bash
pip install quesen-sdk
```

```python
from quesen_sdk import QuesenClient

q = QuesenClient(base_url="https://web-production-30ab5.up.railway.app",
                 api_key="YOUR_KEY")

verdict = q.validate(domain_age_days=1, engagement_ratio=0.95, scam_keyword_count=4)
if verdict.decision == "SKIP":
    return  # respect the deterministic answer
```

### JavaScript / TypeScript

```bash
npm i quesen-sdk
```

```ts
import { QuesenClient } from "quesen-sdk";

const q = new QuesenClient({
  baseUrl: "https://web-production-30ab5.up.railway.app",
  apiKey: process.env.QUESEN_API_KEY,
});

const verdict = await q.validate({
  domain_age_days: 1,
  engagement_ratio: 0.95,
  scam_keyword_count: 4,
});
```

### Framework wrappers

| Framework | Package | Repository |
| --- | --- | --- |
| LangChain / LangGraph | `quesen-langchain` | [Shxnque/quesen-langchain](https://github.com/Shxnque/quesen-langchain) |
| CrewAI | `quesen-crewai` | [Shxnque/quesen-crewai](https://github.com/Shxnque/quesen-crewai) |
| AutoGen v0.4+ | `quesen-autogen` | [Shxnque/quesen-autogen](https://github.com/Shxnque/quesen-autogen) |
| Python (core) | `quesen-sdk` | [Shxnque/quesen-sdk-py](https://github.com/Shxnque/quesen-sdk-py) |
| JavaScript / TypeScript | `quesen-sdk` (npm) | [Shxnque/quesen-sdk-js](https://github.com/Shxnque/quesen-sdk-js) |

### MCP (Claude Desktop, Cursor, Windsurf, etc.)

Quesen exposes **five** MCP tools over the production endpoint. See
[`docs/mcp.md`](docs/mcp.md) for the client-config snippet.

---

## Why Quesen?

Autonomous agents make more decisions per second than any human oversight can
audit. When those decisions involve capital — launching a token, opening a
position, executing a trade, greenlighting a smart-contract deployment — the
marginal cost of a bad decision is fatal.

**Quesen answers exactly one question:**

> *Should the calling agent proceed with this action?*

Inputs are typed. Outputs are one of `PROCEED`, `REVIEW`, `SKIP`, always with a
`risk_score` in `[0.0, 1.0]`, a `confidence` in `[0.0, 1.0]`, and the exact
conflict rules that fired. **Same inputs → same output. Every time.** Every
response embeds `engine_version`, `weights`, and `thresholds`. Fully
reproducible. Fully auditable.

### What Quesen is not

- **Not an LLM wrapper.** No prompts. No probabilities.
- **Not a chatbot.** It is A2A infrastructure.
- **Not a KYC/identity system.** It scores risk, not identity.
- **Not chain-locked / framework-locked / LLM-locked.** Ecosystem-neutral by design.

---

## Documentation

- [Architecture overview](docs/architecture.md)
- [Integration guide](docs/integrations.md)
- [API reference](docs/api-reference.md)
- [MCP setup](docs/mcp.md)
- [Pricing tiers](docs/pricing.md)
- [FAQ](docs/faq.md)
- [Registry status](docs/registries.md)

### Tutorials

- [Moltbook post-guard](docs/tutorials/moltbook-post-guard.md) — deterministic pre-post safety gate for autonomous social agents.
- [OpenClaw MCP plugin](docs/tutorials/openclaw-plugin.md) — wiring Quesen as an MCP-native guardrail into OpenClaw-style agents.

---

## Live status

- Production: `https://web-production-30ab5.up.railway.app`
- Health check: `GET /health` returns `{"status":"ok","engine_version":"1.9.0"}`
- Version snapshot: `GET /version` returns full engine + billing + on-chain flags (ASP/1.0)
- Uptime and version widget on [senueren.co.za/quesen](https://senueren.co.za/quesen)

---

## Registry presence

Quesen is discoverable via Model Context Protocol registries and the standard
agent-directory ecosystem. See [`docs/registries.md`](docs/registries.md) for
the current state of each submission. Manifests:

- [`smithery.yaml`](./smithery.yaml) — Smithery.ai (canonical)
- [`mcp.json`](./mcp.json) — MCP.so / generic MCP client (canonical)
- [`.well-known/ai-plugin.json`](./.well-known/ai-plugin.json) — OpenAI plugin
  manifest / `.well-known/ai-plugin.json` autodiscovery
- [`llms.txt`](./llms.txt) — machine-readable summary for LLM crawlers

---

## Contributing

This is a documentation-only repository. Engine PRs cannot be accepted here.
If you have integration-specific feedback, please [open an issue](https://github.com/Shxnque/quesen/issues) or read [`CONTRIBUTING.md`](CONTRIBUTING.md).

SDK contributions belong in the corresponding public SDK repository:

- Python: [Shxnque/quesen-sdk-py](https://github.com/Shxnque/quesen-sdk-py)
- JavaScript: [Shxnque/quesen-sdk-js](https://github.com/Shxnque/quesen-sdk-js)
- LangChain: [Shxnque/quesen-langchain](https://github.com/Shxnque/quesen-langchain)
- CrewAI: [Shxnque/quesen-crewai](https://github.com/Shxnque/quesen-crewai)
- AutoGen: [Shxnque/quesen-autogen](https://github.com/Shxnque/quesen-autogen)

Security issues: please read [`SECURITY.md`](SECURITY.md) before filing publicly.

---

## License

MIT. See [`LICENSE`](LICENSE).
