# Quesen Quickstart — first decision in under 10 minutes

Quesen is a **deterministic** pre-decision engine for autonomous agents. Before a
high-impact action runs, you ask Quesen and get one explainable answer —
`PROCEED`, `REVIEW`, or `SKIP` — with a numeric `risk_score`, a `confidence`, the
exact conflict rules that fired, and a **replayable receipt**. Same inputs → same
output. No LLM in the scoring loop.

- **Production base URL:** `https://web-production-aa5ba.up.railway.app`
- **Try it in the browser (no setup):** https://senueren.co.za/try
- **OpenAPI / Swagger:** `https://web-production-aa5ba.up.railway.app/docs`

---

## 1. Get a free sandbox key (no signup, no card)

```bash
curl -X POST https://web-production-aa5ba.up.railway.app/sandbox/keys
```

Response:

```json
{
  "api_key": "sk_sandbox_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tier": "sandbox",
  "price_per_call": 0.0,
  "rate_limit_per_min": 30,
  "starter_credits": 1000,
  "engine_version": "1.10.0"
}
```

Sandbox keys are free and rate-limited (30 calls/min). They come with starter
credits so your first `/validate` works immediately. When the credits run out you
will see the Agent Settlement Protocol (ASP/1.0) `HTTP 402` flow — that is part of
the product, not an error.

## 2. Run your first decision

```bash
curl -X POST https://web-production-aa5ba.up.railway.app/validate \
  -H "X-API-Key: sk_sandbox_..." \
  -H "Content-Type: application/json" \
  -d '{"domain_age_days": 1, "engagement_ratio": 0.95, "scam_keyword_count": 4}'
```

Response (abridged):

```json
{
  "decision": "SKIP",
  "risk_score": 1.0,
  "confidence": 1.0,
  "conflict_triggers": [
    "R1: New domain (<=30d) + unusually high engagement (>=0.50)",
    "R3: Scam keywords present + unusually high engagement",
    "R4: New domain + 3 or more scam keywords"
  ],
  "engine_version": "1.10.0",
  "request_id": "…",
  "input_snapshot_hash": "8f5a847af8e6e6d9…",
  "weights": { "...": "..." },
  "thresholds": { "skip": 0.65, "review": 0.35 }
}
```

## 3. Verify determinism (the whole point)

Re-run the exact same request. The `decision` and the `input_snapshot_hash` are
byte-identical every time — you can hash the same payload client-side and get the
same value, which makes every decision auditable and replayable.

## 4. Decide in your agent

```python
resp = requests.post(
    "https://web-production-aa5ba.up.railway.app/validate",
    headers={"X-API-Key": KEY},
    json={"domain_age_days": 1, "engagement_ratio": 0.95, "scam_keyword_count": 4},
).json()

if resp["decision"] == "SKIP":
    abort(reason=resp["conflict_triggers"])       # do not take the action
elif resp["decision"] == "REVIEW":
    escalate_to_human(evidence=resp)              # needs oversight
else:
    proceed()                                     # PROCEED
```

## 5. Inputs

| Field | Type | Meaning |
| --- | --- | --- |
| `domain_age_days` | int ≥ 0 | Age of the counterparty domain. `0` = brand new. |
| `engagement_ratio` | float 0.0–1.0 | Engagement signal; unusually high on a fresh domain is suspicious. |
| `scam_keyword_count` | int ≥ 0 | Number of scam-pattern keywords detected. |
| `chain` + `contract_address` | optional | On-chain enrichment (EVM chains) when supplied. |

## 6. Going to production

Sandbox is for evaluation. For production volume and pricing, see
`GET /billing/plans` and the [pricing docs](./pricing.md). The sandbox key you got
above is a normal Quesen key — your integration code does not change.

## 7. Other surfaces

- **MCP (Claude Desktop, Cursor, Windsurf, …):** streamable-HTTP at
  `https://web-production-aa5ba.up.railway.app/mcp`. See [`mcp.md`](./mcp.md).
- **SDKs:** Python, JS/TS, LangChain, CrewAI, AutoGen — see the [README](../README.md).
