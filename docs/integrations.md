# Integration Guide

Five-minute integration for the four most common surfaces.

---

## 1. Python (any framework)

```bash
pip install quesen-sdk
```

```python
from quesen_sdk import QuesenClient

q = QuesenClient(base_url="https://web-production-30ab5.up.railway.app",
                 api_key="YOUR_KEY")

decision = q.validate(domain_age_days=1, engagement_ratio=0.95, scam_keyword_count=4)
if decision.decision != "PROCEED":
    log.warning("Quesen blocked action %s: %s", decision.request_id, decision.conflict_triggers)
    return
```

Every response is a plain, typed Pydantic model. Access `.risk_score`,
`.confidence`, `.conflict_triggers`, `.engine_version`, `.weights`,
`.thresholds`, and `.request_id`.

---

## 2. JavaScript / TypeScript (any runtime)

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

if (verdict.decision === "SKIP") return;
```

Zero runtime dependencies. Works on Node 18+, Bun, Deno, and modern browsers
that provide `fetch`.

---

## 3. LangChain / LangGraph

```bash
pip install quesen-langchain
```

```python
from quesen_langchain import QuesenValidateTool

tool = QuesenValidateTool(base_url=..., api_key=...)
agent = create_react_agent(model, tools=[tool])
```

---

## 4. CrewAI

```bash
pip install quesen-crewai
```

```python
from quesen_crewai import QuesenValidateTool

crew = Crew(agents=[...], tools=[QuesenValidateTool(base_url=..., api_key=...)])
```

---

## 5. AutoGen v0.4+

```bash
pip install quesen-autogen
```

```python
from quesen_autogen import quesen_validate

assistant = AssistantAgent("risk-checker", tools=[quesen_validate])
```

---

## 6. MCP (Claude Desktop / Cursor / Windsurf)

Quesen speaks the Model Context Protocol natively. See [`mcp.md`](mcp.md) for
the exact client configuration snippet.

## 7. Agent-native platform integrations

Ready-to-use recipes for specific agent-native platforms:

- **Moltbook** post-guard for autonomous social agents \u2014 [`tutorials/moltbook-post-guard.md`](tutorials/moltbook-post-guard.md)
- **OpenClaw** local-agent framework via MCP \u2014 [`tutorials/openclaw-plugin.md`](tutorials/openclaw-plugin.md)

---

## Common patterns

### Fail-open vs fail-closed

On transport error, do you want to `PROCEED` (fail-open) or `SKIP` (fail-closed)?
Make that call at the caller level:

```python
try:
    verdict = q.validate(**inputs)
except Exception:
    # Deterministically fail closed on transport errors.
    return "SKIP"
```

### Threshold overrides for local testing

Use `/simulate` (not `/validate`) to preview what a threshold change would do
**without** mutating the live engine:

```python
sim = q.simulate(
    domain_age_days=1, engagement_ratio=0.95, scam_keyword_count=4,
    thresholds_override={"skip": 0.5, "review": 0.25},
)
print(sim.baseline.decision, "→", sim.simulated.decision)
```

### Post-trade feedback (Conflict Matrix admission signal)

After an action completes, POST the outcome back so future Conflict Matrix
versions can learn from real reports:

```python
q.report(request_id=verdict.request_id, outcome="RUG", realized_pnl=-0.85)
```

`outcome ∈ {"RUG", "LOSS", "OK", "WIN", "UNKNOWN"}`.
