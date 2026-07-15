# API Reference

Full HTTP contract for every public endpoint. Base URL:
`https://web-production-30ab5.up.railway.app`

## Authentication

Most endpoints require an API key in the `X-API-Key` header. Admin-scoped
endpoints (`/stats`) require the admin key configured via `QUESEN_ADMIN_KEY`.
Billing endpoints and `/health`, `/version`, `/billing/plans` are open.

## Rate limiting

Per-key fixed 60-second window. Default 60 req/min; configurable per key.
Exceeded requests return `429 Too Many Requests` with a `Retry-After: 60`
header.

---

## GET /health

```json
{ "status": "ok", "engine_version": "1.6.0" }
```

## GET /version

```json
{
  "engine_version": "1.6.0",
  "report_schema_version": "1.1.0",
  "weights": { "domain_age": 0.40, "engagement": 0.35, "scam_keywords": 0.25 },
  "thresholds": { "skip": 0.65, "review": 0.35 },
  "telegram_enabled": true,
  "api_keys_enabled": true,
  "onchain_enabled": false,
  "onchain_supported_chains": ["arbitrum","avalanche","base","bnb","ethereum","optimism","polygon"],
  "onchain_thresholds": { "young_contract_days": 14, "very_young_contract_days": 3, "high_concentration_top1": 0.60 },
  "billing_providers": { "stripe": true, "coinbase_commerce": true },
  "plan_ids": ["developer","starter","professional","enterprise"],
  "pack_ids": ["pack_10k","pack_100k","pack_1m"]
}
```

## POST /validate

**Request**

```json
{
  "domain_age_days": 1,
  "engagement_ratio": 0.95,
  "scam_keyword_count": 4,
  "chain": "base",
  "contract_address": "0x420…",
  "client_request_id": "my-txn-123"
}
```

**Response**

```json
{
  "decision": "SKIP",
  "risk_score": 0.9825,
  "confidence": 1.0,
  "conflict_triggers": ["R1_domain_lt_2d_and_engagement_gt_0.9", "R3_scam_gt_3_and_domain_lt_7d"],
  "engine_version": "1.6.0",
  "latency_ms": 3,
  "request_id": "a1b2c3…",
  "weights": { "domain_age": 0.40, "engagement": 0.35, "scam_keywords": 0.25 },
  "thresholds": { "skip": 0.65, "review": 0.35 }
}
```

## POST /simulate

Counterfactual: what would the decision be with different weights or
thresholds. Same request shape as `/validate` plus optional
`weights_override` and `thresholds_override`. Response contains `baseline`,
`simulated`, and `delta`.

## POST /report

```json
{
  "request_id": "a1b2c3…",
  "outcome": "RUG",
  "realized_pnl": -0.85,
  "elapsed_seconds": 84,
  "venue": "base",
  "notes": "Bought before Conflict Matrix flagged the concentration."
}
```

## GET /billing/plans

Public pricing catalog. Deterministic. See [`pricing.md`](pricing.md).

## POST /billing/stripe/checkout

```json
{
  "target": "plan",
  "target_id": "starter",
  "origin_url": "https://senueren.co.za",
  "email": "customer@example.com"
}
```

Response contains `checkout_url` — redirect the customer there.

## POST /billing/crypto/checkout

Same request shape as Stripe. Response `checkout_url` is a Coinbase Commerce
hosted checkout supporting USDC / ETH / stablecoins across Ethereum, Base,
Polygon, and every other chain Coinbase Commerce natively supports.
