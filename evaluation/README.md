# Quesen — Domain Evaluation Matrix & External Validation Program

> **Purpose.** Turn Quesen from *"distributed and reachable"* into *"externally
> validated."* This directory holds a reproducible, black-box validation harness
> and the evidence it produces. It contains **no engine source** — it exercises
> only the public HTTP surface with a self-served sandbox key, exactly as an
> outside developer would.

## Why this exists

Registry presence (Smithery, Glama, MCP registry) proves Quesen can be *reached*.
It says nothing about whether Quesen is *correct, deterministic, robust, and
useful across the domains it claims*. This program answers that with evidence,
under two rules:

1. **No threshold tuning to flatter results.** We test the engine *as published*
   in `/version` (weights `domain_age 0.40 / engagement 0.35 / scam 0.25`,
   thresholds `skip 0.65 / review 0.35`).
2. **Separate architecture limits from implementation bugs.** If the input
   surface cannot express a domain, that is a *coverage gap* (architecture), not
   a test failure to paper over.

## Run it

```bash
QUESEN_BASE_URL=https://web-production-aa5ba.up.railway.app \
  python3 evaluation/domain_matrix.py         # self-serves a free sandbox key
```

Python 3.8+, standard library only. Output → `evaluation/results/latest.json`
plus a stdout summary; non-zero exit if any invariant fails. The sandbox tier is
rate-limited to 30 calls/min, so the harness paces keyed calls (~1 / 2.1 s) and
retries `429` — rate-limiting never masquerades as a finding.

## What is checked (suites)

| Suite | Invariant under test |
| --- | --- |
| `determinism` | Same input → identical `decision` + `risk_score` + `input_snapshot_hash` across repeated calls. |
| `threshold_mapping` | Every `decision` matches the published thresholds (`SKIP≥0.65`, `REVIEW≥0.35`, else `PROCEED`). |
| `monotonicity` | Risk moves in a consistent direction as each signal worsens (more scam keywords, younger domain, higher engagement). |
| `input_validation` | Out-of-range / wrong-type / injection / huge / empty / unknown-field inputs are rejected (`422`) or handled gracefully (`200`) — **never `500`**. |
| `auth_boundary` | No key → 401; bad key → 401; sandbox key denied on admin `/stats`. |
| `simulate` | Counterfactual overrides return 200 **and do not mutate** engine state. |
| `report` | Valid outcome enum accepted; invalid rejected (`422`). |
| `onchain_enrichment` | Verified contract enriches; junk address handled gracefully (no `500`). |

## The Domain Evaluation Matrix (honest coverage assessment)

The operating directive names 16 target security domains. Quesen's **actual
input contract** is narrow: `domain_age_days`, `engagement_ratio`,
`scam_keyword_count`, plus optional `chain` + `contract_address` for on-chain
enrichment. That contract expresses a **crypto / token / social-launch risk
oracle with on-chain contract enrichment** — it is *not* (yet) a general agent
policy engine. Mapping the 16 domains onto that reality:

| # | Directive domain | Coverage | Why (evidence-based) |
| --- | --- | --- | --- |
| 1 | Autonomous-agent go/no-go | 🟢 **Covered** | Deterministic `PROCEED/REVIEW/SKIP` an agent can gate capital on — for the token/launch decision. |
| 2 | Transaction-target validation (on-chain) | 🟢 **Covered** | `chain`+`contract_address` → contract age, verification, proxy, ownership, holder concentration. |
| 3 | Adversarial-input robustness | 🟢 **Covered** | Malformed/out-of-range rejected; injection strings echoed harmlessly; unknown fields `422`. |
| 4 | Ambiguous legitimate activity | 🟡 Partial | The `REVIEW` band (0.35–0.65) exists and fires (e.g. aged domain + low engagement → `REVIEW 0.5325`). Needs labelled fixtures to quantify. |
| 5 | Financial operations | 🟡 Partial | Only through the token-risk lens; no amounts, counterparties, or velocity inputs. |
| 6 | Payment / settlement flows | 🟡 Adjacent | ASP/1.0 (HTTP 402 → signed quote → USDC on Base) settles Quesen's **own** metering — not a general payment-risk decision. |
| 7 | Suspicious automation | 🟡 Partial | `engagement_ratio` is a weak bot-likeness proxy only. |
| 8 | False-positive / false-negative rates | 🟡 Partial | Expressible for token-launch cases; requires a labelled ground-truth corpus (not yet built). |
| 9 | API / tool authorization | 🔴 **Gap** | No inputs for tool name, caller identity, scopes, or permissions. |
| 10 | Prompt-injection-derived actions | 🔴 **Gap** | No text/instruction input; `scam_keyword_count` is a pre-computed integer, so the caller — not Quesen — must detect injection. |
| 11 | Identity / KYC | 🔴 **Gap** | Explicitly out of scope ("Not a KYC/identity system"). |
| 12 | Data-access decisions | 🔴 **Gap** | No resource / sensitivity / actor inputs. |
| 13 | Privilege escalation | 🔴 **Gap** | No role/permission model in the contract. |
| 14 | Malicious tool calls | 🔴 **Gap** | Cannot inspect tool-call arguments. |
| 15 | Supply-chain / package risk | 🔴 **Gap** | No package/dependency inputs. |
| 16 | General malicious-instruction detection | 🔴 **Gap** | No natural-language surface. |

**Headline:** Quesen is a *strong, deterministic, single-domain* engine. It
robustly covers ~3 domains, partially touches ~5, and **cannot currently
express ~8** because the input contract has no fields for them.

### What this implies for the "deterministic security boundary for agents" vision

To become the cross-framework policy layer described in the AG2 / LangChain /
CrewAI direction, Quesen needs an **extended, typed context contract** — a
generic `{actor, action, resource, scopes, amount, provenance, signals}`
envelope (or per-domain schemas) — *before* it can honestly claim the tool-authz
/ prompt-injection / data-access domains. Adding keywords to the existing 3-signal
schema will not close those gaps. That is the next serious engineering decision,
and it should be driven by demonstrated external demand, not by this matrix alone.

## Evidence

- `results/latest.json` — full machine-readable evidence (every case, expected vs actual).
- `results/2026-08-25.json` — dated snapshot.
- `REPORT-2026-08-25.md` — human-readable analysis of the first run.
