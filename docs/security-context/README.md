# Quesen Typed Security Context (TSC) v2 — P1 Design Package

**Status:** SHIPPED. The TSC v2 decision surface is live on the deployed engine:
`POST /tsc/validate` returns `PASS | REVIEW | BLOCK | SKIP` with reason codes and
the emitted receipt fields, and `GET /tsc/version` reports `tsc_schema_version 2.0,
engine_version 1.10.0`. See the shipped, reproducible-without-signup surface in
[`../api-reference.md` → **POST /tsc/validate**](../api-reference.md#post-tsc-validate).
This document remains the **design rationale** for that surface; where a field
below is not yet emitted by the deployed engine it is called out inline rather
than implied to be shipped.
**Engine baseline at authorship:** `engine_version = 1.10.0` (verified live on Railway `/version`).
**Wire baseline:** `ASP/1.0` (ADR-040 LC1 gate). Receipt provenance: ADR-041 (`input_snapshot_hash` + `commit_sha`).

---

## Why this exists

Quesen v1 evaluates a **narrow, flat signal payload** — `domain_age_days`,
`engagement_ratio`, `scam_keyword_count` (+ optional on-chain enrichment) — and
returns `PROCEED | REVIEW | SKIP`. That is a crypto/scam *risk scorer*.

The P1 **Typed Security Context Contract (TSC v2)** generalizes the input from a
bag of scalars into a **typed description of what an agent is trying to do** —
`subject` (agent), `action`, `target`, `tool`, `permissions`, `data`, `signals`,
`provenance`, `policy` — so the same deterministic, no-LLM engine can reason
about general agent-security questions (prompt injection, tool authorization,
data exfiltration) **without becoming an LLM or a detector-in-a-box.**

P1 delivers the **contract**. Detectors for each dimension are explicitly
deferred (see `10-non-goals.md`). The contract must be able to *represent* those
dimensions today so detectors can slot in later without another contract break.

## Design invariants (non-negotiable)

1. **Determinism.** Identical canonical input + identical engine state ⇒ identical verdict. No randomness, no time-dependence (except latency measurement), no LLM in the decision path.
2. **v1 is untouched.** A request with no `tsc_version` runs the existing v1 pipeline byte-for-byte. v2 is additive and explicitly versioned.
3. **Provenance-tiered trust.** Client-asserted authorization is *never* trusted merely because it was supplied. Trust requires attestation or a trusted source tier.
4. **Untrusted text is data, never policy.** `action.intent` and injection findings are evaluated *about*, never *as*, instructions.
5. **No invalid input yields a 500.** Every malformed context maps to a stable, typed error.
6. **Honesty over guessing.** When typed context is insufficient the engine returns `SKIP` (declines to rule) rather than fabricating a verdict.

## Contents

| File | What |
| --- | --- |
| `01-overview.md` | Motivation, principles, the v1→v2 relationship |
| `02-schema.md` | Field-by-field contract (mirror of `tsc-v2.schema.json`) |
| `03-normalization.md` | Deterministic normalization rules |
| `04-validation-errors.md` | Error taxonomy + status mapping |
| `05-decision-contract.md` | v2 response envelope + `PASS/REVIEW/BLOCK/SKIP` semantics |
| `06-examples.md` | Worked examples: prompt-injection, tool-authz, data-egress |
| `07-versioning-compatibility.md` | Version negotiation + backward compatibility |
| `08-security-invariants.md` | Golden invariants (future CI) |
| `09-migration-plan.md` | Engine + six-client release train + evaluation v2 + AG2 |
| `10-non-goals.md` | Explicit scope limits |
| `11-open-decisions.md` | Decisions requiring operator approval before implementation |
| `12-adr-decision-review.md` | **Recommended resolutions to D-1..D-9 + all-environments impact matrix (review gate)** |
| `13-stage1-implementation-plan.md` | **Stage 1 engine blueprint: v1 byte-for-byte gate + rollback (execute after sign-off)** |
| `tsc-v2.schema.json` | Machine-readable JSON Schema (draft 2020-12) |
| `fixtures/tsc_v2_fixtures.json` | Canonical + adversarial fixtures |
| `../../evaluation/tsc_v2_poc.py` | Runnable reference harness (proves determinism + invariants) |

## Reproduce the proof

```bash
python3 evaluation/tsc_v2_poc.py
# -> DETERMINISM / NORMALIZATION-EQUIVALENCE / TYPED VALIDATION / SECURITY INVARIANTS
# -> RESULT: ALL CHECKS PASSED
```

The POC contains **no engine source** — it is an independent, language-agnostic
reference any integrator can port.
