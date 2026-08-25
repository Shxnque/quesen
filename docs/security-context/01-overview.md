# 01 · Overview

## The problem with a flat contract

The v1 `/validate` request (see `Shxnque/Quesen-sib · quesen/schemas.py ·
ValidateRequest`) is three optional scalars plus optional on-chain inputs. It can
express exactly one question: *"how scam-shaped is this opportunity?"* Every new
security question a caller has asked on the intelligence surface — *"is this tool
call authorized?"*, *"is this text a prompt-injection?"*, *"is this egress a
leak?"* — is **inexpressible** because the input surface has no place to put the
facts.

The Domain Evaluation Matrix (`evaluation/domain_matrix.py`) made this concrete:
several real-world security domains are **architecture-limited, not
bug-limited** — the surface cannot express them, so the engine cannot rule on
them. TSC v2 removes that limitation at the contract layer.

## The core idea

Replace "bag of scalars" with a **typed security context**: a structured,
provenance-tagged description of an attempted agent operation.

```
subject  — WHO is acting (agent / human / service, framework, trust tier)
action   — WHAT operation (tool_call / payment / data_egress / code_exec / …)
target   — WHAT resource / destination is affected
tool     — WHICH capability, with requested vs granted scopes
permissions — requested vs granted vs policy_required authority
data     — data classes involved + egress destination + destination trust
signals  — observed evidence bag (incl. v1 flat signals for lossless lift)
provenance — HOW the context was produced (the trust anchor)
policy   — WHICH policy governs (referenced by id/version, never embedded)
```

The engine remains a **pure deterministic oracle**. TSC v2 is a richer *input*,
not a richer *mechanism*. No LLM enters the decision path (Doctrine §13:
infrastructure, not chatbot).

## v1 ↔ v2 relationship

- v1 and v2 are **the same engine, two input shapes.**
- A v1 payload lifts losslessly into v2 under `signals.{domain_age_days,
  engagement_ratio, scam_keyword_count, onchain}` — so the existing Conflict
  Matrix (R1–R7) keeps working as a *signal family* inside the generalized
  contract.
- Version is selected by the **presence of `tsc_version`** (see
  `07-versioning-compatibility.md`). No `tsc_version` ⇒ v1, unchanged.

## What "generalized" buys us

| Dimension | v1 | TSC v2 (representation) | Detector status |
| --- | --- | --- | --- |
| Crypto/scam risk | ✅ native | `signals.*` + on-chain | shipped (R1–R7) |
| Prompt injection | ❌ | `signals.prompt_injection` | **deferred (P2+)** |
| Tool authorization | ❌ | `tool.*` + `permissions.*` | **deferred (P2+)** |
| Data exfiltration / PII | ❌ | `data.classes` + `data.egress` | **deferred (P2+)** |

P1 makes all four **expressible and deterministically evaluable at the contract
level** (the reference POC already renders safe verdicts for representative
cases). Production-grade detectors are a separate, sequenced effort.
