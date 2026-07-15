# Architecture Overview

Quesen is a **stateless, deterministic FastAPI service**. It exposes a small
set of endpoints that autonomous agents (or any HTTP client) call to obtain
risk verdicts. No LLM sits inside `/validate`. No randomness. No time-dependent
behavior other than latency measurement.

## Endpoint surface

| Endpoint | Method | Purpose | Auth |
| --- | --- | --- | --- |
| `/health` | GET | Liveness probe. | none |
| `/version` | GET | Weights, thresholds, feature flags. | none |
| `/validate` | POST | The main verdict endpoint. | API key |
| `/simulate` | POST | Counterfactual: what would the verdict be with different weights / thresholds. | API key |
| `/report` | POST | Post-trade outcome feedback. Feeds Conflict Matrix future admissions. | API key |
| `/stats` | GET | Per-key earnings ledger snapshot. | admin key |
| `/billing/plans` | GET | Public pricing catalog. | none |
| `/billing/stripe/checkout` | POST | Create a Stripe Checkout Session for a plan or pack. | none |
| `/billing/stripe/status/{id}` | GET | Poll a Stripe checkout session. | none |
| `/billing/stripe/webhook` | POST | Stripe webhook — signed HMAC verification. | Stripe signature |
| `/billing/crypto/checkout` | POST | Create a Coinbase Commerce charge (USDC / ETH / stablecoins). | none |
| `/billing/crypto/status/{id}` | GET | Poll a Coinbase Commerce charge. | none |
| `/billing/crypto/webhook` | POST | Coinbase Commerce webhook — HMAC-SHA256 verification. | X-CC signature |

## Decision pipeline

1. **Normalize inputs** — `domain_age_days` → domain risk, `engagement_ratio`
   → engagement risk, `scam_keyword_count` → keyword risk.
2. **Weighted sum** — `WEIGHTS["domain_age"] * domain_risk + …` → `base_risk`.
3. **Conflict Matrix v2** — seven pattern rules that add penalties on top of
   base risk. Rules R1..R7 currently active. Each rule fires deterministically
   on strict pattern match.
4. **On-chain enrichment** (optional, feature-flagged) — if `chain` +
   `contract_address` are supplied and the operator has RPC + Blockscout
   configured, the engine reads contract age, ownership, verification status,
   and top-holder concentration. This becomes an additional signal input.
5. **Classify** — `risk >= 0.65` → `SKIP`, `risk >= 0.35` → `REVIEW`, else
   `PROCEED`.

## Determinism

- Every response contains `engine_version`, `weights`, `thresholds`,
  `request_id`, and the exact `conflict_triggers` that fired.
- Same inputs + same engine_version = bit-identical output. This is CI-enforced
  in the sovereign engine repo.
- Weights and thresholds are versioned by `engine_version`. A weight change =
  a new engine version.

## What Quesen is NOT

- **Not KYC.** Quesen scores risk, not identity.
- **Not a chatbot / LLM wrapper.** No prompts anywhere in `/validate`.
- **Not chain-locked.** On-chain enrichment supports 7 EVM chains via a
  provider-agnostic RPC layer.
- **Not framework-locked.** Every SDK is a thin HTTP wrapper; the core has zero
  framework dependencies.

## Operational profile

- Deployed on Railway. Single worker. Cold-start ~ 5–30 s after idle.
- Rate-limited per API key (fixed 60-second window; configurable per key).
- API keys carry per-key pricing metadata; earnings tracked in-memory (durable
  log = Telegram HQ).
- No customer database. Payment state lives in Stripe / Coinbase Commerce.

See [`api-reference.md`](api-reference.md) for exact request/response schemas.
