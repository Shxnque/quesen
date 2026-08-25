# 08 · Security Invariants (future golden tests)

These are the invariants a v2 implementation MUST satisfy. Each is written so it
can become a golden test in `Quesen-sib/tests/`. The reference POC
(`evaluation/tsc_v2_poc.py`) already demonstrates the starred (★) ones.

| # | Invariant | Status in POC |
| --- | --- | --- |
| I-1 | ★ Deterministic: identical canonical input ⇒ identical decision + hash. | proven |
| I-2 | ★ Normalization-equivalent inputs ⇒ identical decision + hash. | proven |
| I-3 | ★ Unknown fields are rejected (`unknown_field`), never silently ignored. | proven |
| I-4 | ★ Untrusted text (`action.intent`, injection patterns) never alters a verdict as if it were an instruction. | proven |
| I-5 | ★ Client-asserted authorization cannot PASS a sensitive action without attestation. | proven |
| I-6 | ★ Malformed inputs never 500 — always a typed error. | proven |
| I-7 | `tsc_version` is explicit; the v2 path rejects requests lacking it (`unsupported_version`). | proven |
| I-8 | Policy is referenced by `id`/`version`; policy **logic** is never embedded in the context. | contract-enforced (schema) |
| I-9 | Provenance survives evaluation and is echoed in `provenance_summary`. | proven |
| I-10 | Simulation/counterfactual is side-effect-free (no engine state mutation). | inherited from v1 `/simulate` |
| I-11 | v1 requests (no `tsc_version`) are byte-for-byte unchanged. | design guarantee (v1 tests) |
| I-12 | `input_snapshot_hash` excludes `client_request_id`; varying it does not change the hash. | ADR-041 parity |
| I-13 | Oversized inputs are bounded and rejected (`oversized`) — DoS guard. | proven |

## Adversarial fixtures (seed set)

The P1 fixture file seeds the adversarial corpus. Evaluation v2
(`09-migration-plan.md`) expands it into false-positive / false-negative suites
once detectors exist:

- injection text smuggled into `action.intent`, `operation`, `evidence_refs`
- over-claimed `trust_tier` with weak `provenance`
- scope smuggling via duplicate / case-variant scopes (normalization must collapse)
- egress destination laundering (`destination_trust` vs `target.trust_tier` mismatch → reserved `conflicting_fields`)
- unknown-field injection (`{"$ne": null}`-style) → rejected
