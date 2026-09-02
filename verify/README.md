# Independent verification bundle

> Resolves issue [#1 — *Clarify independent replayability of published receipt `commit_sha`*](https://github.com/Shxnque/quesen/issues/1).

This directory lets **any third party** independently reproduce the published
Quesen receipts **from this public repository alone** — no hosted service and no
access to the private engine required — and states honestly where independent
verification currently stops.

```bash
python3 verify/verify_receipts.py          # offline, stdlib-only
python3 verify/verify_receipts.py --live   # also cross-check the live engine
```

## The precise verification boundary

The original question was sharp and fair: *can a third party independently
verify the exact historical ruleset and issuer — not merely reproduce
`input_snapshot_hash` — without relying on the hosted service or the private
engine repository?* Here is the honest, evidence-backed answer, split into what
**is** and **is not** independently verifiable today.

### ✅ Independently verifiable now (public repo only)

| Claim | How | Artifact |
| --- | --- | --- |
| Canonical request bytes | RFC-8785 (JCS) subset: NFC, sorted keys, `separators=(",",":")`, `client_request_id` excluded | [`docs/security-context/03-normalization.md`](../docs/security-context/03-normalization.md) |
| `input_snapshot_hash` | `sha256_hex(canonical_json(normalize(request)))` | [`evaluation/tsc_v2_poc.py`](../evaluation/tsc_v2_poc.py) |
| Contract `decision` + `reason` codes | pure reference decision function (priority-ordered invariants) | `tsc_v2_poc.py::decide` |
| That the above match the **published** UCP #724 vectors | runnable verifier | [`verify/verify_receipts.py`](./verify_receipts.py) |
| That the above match the **live hosted engine** | `--live` flag | [`verify/three_way_match.json`](./three_way_match.json) |

**Result (frozen evidence, [`three_way_match.json`](./three_way_match.json)):**
for all six UCP #724 lifecycle vectors, the **published fixture receipt**, the
**public reference recompute**, and the **live hosted engine** agree byte-for-byte
on `input_snapshot_hash` and agree on `decision` — a full three-way match.

### ⛔ NOT independently verifiable today (stated plainly)

1. **Exact production ruleset `commit_sha` (`0095b618…`) is not publicly resolvable.**
   That commit references Quesen's *sovereign, non-public* engine repository by
   design. What this repo provides instead is a **contract-level** reference
   that reproduces the same `decision` / `reasons` / `input_snapshot_hash` for
   these vectors. It does **not** expose the production risk weighting or
   thresholds. So `commit_sha` today is best read as an **opaque ruleset
   revision label** that binds a receipt to a specific private engine build —
   not as a publicly checkoutable artifact.

2. **Receipts are not cryptographically issuer-signed.** The `/tsc/validate`
   receipt carries a `request_id` and echoes `engine_version` + `commit_sha`,
   but there is no signature binding it to an identified issuer. Issuer binding
   is therefore **currently outside the TSC receipt model**. (Note: the Agent
   Settlement Protocol *settlement* receipts are HMAC-signed — `kid: asp1`,
   `HMAC-SHA256` — but that discipline is not yet applied to the risk-decision
   receipt.)

### What would close the remaining gap (roadmap, not a claim)

To make the *exact historical ruleset* and *issuer* independently verifiable
without trusting the host, a future receipt could add: a published, immutable
ruleset artifact (or hash) resolvable to each `commit_sha`; and a detached
signature over `(input_snapshot_hash, commit_sha, engine_version, request_id)`
under a published issuer key. Until then, the boundary above is the accurate
description — documented here rather than overclaimed.

## Files

- [`verify_receipts.py`](./verify_receipts.py) — runnable, offline, stdlib-only verifier (`--live` optional).
- [`three_way_match.json`](./three_way_match.json) — frozen evidence capture (published ≡ reference ≡ live).
