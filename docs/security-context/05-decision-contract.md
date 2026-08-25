# 05 · Decision Contract (v2 response)

## Decision vocabulary

v2 uses a **four-value** decision, a deliberate superset of v1's three:

| v2 | Meaning | v1 analogue |
| --- | --- | --- |
| `PASS` | Allow. No policy-relevant adverse pattern. | `PROCEED` |
| `REVIEW` | Allow only with a human/second-factor in the loop. | `REVIEW` |
| `BLOCK` | Deny. Hard-stop invariant fired or risk ≥ block threshold. | `SKIP` (risk-driven) |
| `SKIP` | Engine **declines to rule** — insufficient typed context or action outside policy scope. | *(new)* |

`SKIP` is the honesty valve (Doctrine §14): the engine refuses to fabricate a
verdict it cannot support, and says so explicitly, rather than defaulting to
`PASS`.

## Response envelope

```json
{
  "tsc_version": "2.0",
  "decision": "PASS|REVIEW|BLOCK|SKIP",
  "risk_score": 0.0,
  "confidence": 0.0,
  "reasons": [
    { "code": "EGRESS_SECRET_UNTRUSTED", "severity": "critical",
      "message": "credential/secret egress to an unverified destination",
      "evidence_ref": "optional-opaque-ref" }
  ],
  "tags": ["exfiltration"],
  "policy": { "id": "...", "version": "..." },
  "provenance_summary": { "source": "adapter_derived", "attested": false },
  "engine_version": "1.x.y",
  "input_snapshot_hash": "<64 hex>",
  "commit_sha": "<40 hex | 'unknown'>",
  "request_id": "...",
  "latency_ms": 3
}
```

- `risk_score` ∈ [0,1]; `confidence` ∈ [0,1].
- `reasons[]` is the human-auditable justification — **every** verdict carries at
  least one reason code (mirrors v1 `conflict_triggers`, but structured).
- `input_snapshot_hash` + `commit_sha` are preserved from ADR-041 verbatim.
- `severity` ∈ `info|low|medium|high|critical`.

## Decision semantics (reference, deterministic)

Applied in fixed priority order (reference: `tsc_v2_poc.py::decide`). Production
weighting/thresholds remain in the sovereign engine; this is the contract-level
behaviour every implementation must honour:

1. **Hard-deny — secret/credential egress to untrusted dest ⇒ `BLOCK`.**
2. **Privilege mismatch — `policy_required` scopes not (verifiably) held ⇒ `BLOCK` (sensitive) / `REVIEW`.**
3. **Unverified grant on a sensitive action ⇒ `REVIEW`** (client-asserted authority cannot PASS a payment/exec/egress).
4. **Prompt-injection suspected ⇒ `REVIEW`** (`high` severity if action is sensitive).
5. **PII/financial/regulated egress to non-trusted dest ⇒ `REVIEW`.**
6. **Insufficient typed context ⇒ `SKIP`.**
7. **Otherwise ⇒ `PASS`.**

"Sensitive" = `action.kind ∈ {payment, code_exec, data_egress, data_write,
file_access}` **or** `tool.capability_class ∈ {financial, admin, exec, write,
filesystem}`.

"Attested" = `provenance.attestation.verified == true` **or**
`provenance.source ∈ {engine_derived, trusted_metadata}`.

## Determinism guarantee

Identical canonical input + identical engine state ⇒ identical `decision`,
`risk_score`, `reasons`, and `input_snapshot_hash`. No time-dependence except
`latency_ms`. No randomness. No LLM.
