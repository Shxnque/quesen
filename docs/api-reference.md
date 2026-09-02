# API Reference

Full HTTP contract for every public endpoint. Base URL:
`https://web-production-aa5ba.up.railway.app`

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
{ "status": "ok", "engine_version": "1.10.0" }
```

## GET /version

```json
{
  "engine_version": "1.10.0",
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
  "conflict_triggers": ["<rule_id>", "<rule_id>"],
  "engine_version": "1.10.0",
  "latency_ms": 3,
  "request_id": "a1b2c3…",
  "weights": { "domain_age": 0.40, "engagement": 0.35, "scam_keywords": 0.25 },
  "thresholds": { "skip": 0.65, "review": 0.35 },
  "input_snapshot_hash": "e8c3…64-char-hex…",
  "commit_sha": "aabbcc…40-char-hex…"
}
```

### Receipt provenance (v1.10)

Every response carries two additional fields that make the verdict
self-contained-replayable:

- **`input_snapshot_hash`** · lowercase 64-char SHA-256 hex over canonical-JSON
  of the received request payload, with `client_request_id` excluded from the
  hash material. Callers can hash the same payload client-side and prove the
  engine evaluated the exact input they sent.
- **`commit_sha`** · a 40-char lowercase identifier the engine returns to pin the
  ruleset revision that produced the verdict, or the sentinel `"unknown"`. It is
  the engine-reported ruleset revision of Quesen's **sovereign (non-public)
  engine**; it does **not** resolve against a commit in the public
  `Shxnque/quesen` developer portal. What *is* public and independently
  reproducible is the `input_snapshot_hash` and the contract-level decision (see
  the [verification bundle](../verify/README.md)).

**Client-side hash reconstruction:**

```python
import hashlib, json
def input_snapshot_hash(payload: dict) -> str:
    to_hash = {k: v for k, v in payload.items()
               if v is not None and k != "client_request_id"}
    canonical = json.dumps(to_hash, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
```

**Replay recipe** (independently reproducible from this public repo — no hosted
service or private engine required):

```
git clone https://github.com/Shxnque/quesen && cd quesen
python3 verify/verify_receipts.py          # recompute input_snapshot_hash + decision
python3 verify/verify_receipts.py --live   # also cross-check the live engine
# The production ruleset commit_sha is a sovereign-engine revision label and is
# not a checkoutable commit in this public repo — see verify/README.md.
```

## POST /tsc/validate

The deterministic **typed-security-context decision surface** (Trust & Safety
Context v2). A typed context — `subject`, `action`, `target`, `tool`, `data`,
`provenance` — is normalized, then evaluated to one of `PASS | REVIEW | BLOCK |
SKIP` with machine reason codes and a self-describing receipt. No model
inference is in the scoring path, so the same normalized input always yields the
same verdict. Shipped and live on `engine_version 1.10.0`; `GET /tsc/version`
reports `tsc_schema_version 2.0`.

**Request** (`tsc_version 2.0`)

```json
{
  "tsc_version": "2.0",
  "subject":    { "kind": "agent", "trust_tier": "unverified" },
  "action":     { "kind": "payment", "operation": "transfer" },
  "target":     { "kind": "account", "identifier": "merchant-acct-77", "trust_tier": "verified" },
  "tool":       { "id": "pay.send", "capability_class": "financial", "granted_scopes": ["payment.send"] },
  "permissions":{ "granted": ["payment.send"] },
  "provenance": { "source": "client_asserted" }
}
```

**Response** — the emitted receipt fields are carried directly on the response:

```json
{
  "tsc_version": "2.0",
  "decision": "REVIEW",
  "risk_score": 0.5,
  "confidence": 0.2143,
  "reasons": [
    { "code": "UNVERIFIED_GRANT", "severity": "medium",
      "message": "authorization claimed by unattested client; cannot PASS a sensitive action" }
  ],
  "tags": ["authz", "provenance"],
  "provenance_summary": { "source": "client_asserted", "attested": false },
  "engine_version": "1.10.0",
  "commit_sha": "0095b6183a796ce678086a77e17de6eef9c6a263",
  "input_snapshot_hash": "40078edcc0e13fe02a7baf68e6acd7dc12ab2c9d0004c56a6fbd4839616e1660",
  "request_id": "…",
  "latency_ms": 0
}
```

### Receipt provenance for /tsc/validate (v1.10) {#tsc-validate-receipt-provenance}

Two receipt fields are **emitted** on every `/tsc/validate` response and make
the verdict self-describing:

- **`input_snapshot_hash`** · lowercase 64-char SHA-256 hex over the canonical
  JSON of the **normalized** typed context (NFC-folded, enum/domain-lowercased,
  list-ordering canonicalized), with `client_request_id` excluded from the hash
  material. This is distinct from [`POST /validate`](#post-validate)'s hash,
  which is taken over the **raw** request payload. The public, executable
  reference for the normalization + hash is
  [`evaluation/tsc_v2_poc.py`](../evaluation/tsc_v2_poc.py)
  (`normalize()` → `canonical_json(for_hash=True)` → `input_snapshot_hash()`),
  which reproduces this field byte-for-byte from the same context.
- **`commit_sha`** · a 40-char identifier the engine returns to pin the ruleset
  version that produced the verdict. It is the engine-reported identifier; the
  binding between it and the executed ruleset is not independently resolvable
  from the public repository.

**Reproducible without signup** (issues a free sandbox key, then calls the live
decision surface):

```bash
BASE=https://web-production-aa5ba.up.railway.app
KEY=$(curl -sX POST $BASE/sandbox/keys | jq -r .api_key)

# secret egress to an unverified sink -> BLOCK / EGRESS_SECRET_UNTRUSTED
curl -sX POST $BASE/tsc/validate -H "X-API-Key: $KEY" -H 'Content-Type: application/json' -d '{
  "tsc_version":"2.0","subject":{"kind":"agent"},
  "action":{"kind":"data_egress","operation":"upload"},
  "target":{"kind":"endpoint","identifier":"https://paste.example","trust_tier":"unverified"},
  "data":{"classes":["secret","internal"],"egress":{"to":"https://paste.example","destination_trust":"unverified"}},
  "provenance":{"source":"adapter_derived"}}'
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
