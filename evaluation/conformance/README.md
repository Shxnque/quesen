# Quesen egress/authority conformance kit (offline, zero-network)

> Extends [`verify/`](../../verify/) (which independently reproduces the UCP #724 lifecycle
> vectors) to the **egress / authority decision subset** — the part that security-minded
> integrators actually gate on. Self-contained and **recomputable with no hosted service,
> no API key, and no network call.**

## Why this exists (criticism-driven)

Two serious prospects rejected the *hosted, closed-ruleset* verification story for the same
reason (recorded in BEA `intelligence/criticism-ledger.md`):

| # | Source | Criticism | How this kit answers it |
|---|---|---|---|
| **C-003** | sequant / @admarble | "a network call to a third-party hosted service at CI time adds a new external dependency to the exact surface this issue is trying to shrink" | `verify_conformance.py` makes **zero** network calls. It is stdlib-only and CI-droppable with no secrets. |
| **C-004** | loopx / @huangruiteng | "verify or **locally replay the verdict** rather than only trusting `input_snapshot_hash` plus a claimed engine commit" | The kit **recomputes the verdict** (decision + reason codes) *and* the hash locally from the public reference evaluator, and asserts them against a self-contained fixture. |

The earlier joint test (`evaluation/joint_tests/sequant_trust_boundary_test.py`) minted a
sandbox key and called the live engine — exactly the dependency C-003 objected to. This kit
is the network-free replacement for that verification need.

## What it proves (from this public repo alone)

1. Every case's `input_snapshot_hash` is reproducible byte-for-byte via the public
   normalization + JCS spec (`docs/security-context/03-normalization.md`).
2. Every case's `decision` + `reason_codes` are reproducible from the public reference
   decision function (`evaluation/tsc_v2_poc.py::decide`).
3. The integrity binding holds (`prod-1` -> `prod-2` changes the hash), so a prior receipt
   does not bind a mutated call.

The six cases (3 OWASP-agentic + 3 loopx prepared-Effect) recompute **byte-for-byte identical**
to the live-engine receipts previously captured in the fixtures — that equivalence is the
whole point: the hosted engine is now an *optimisation*, not a *trust dependency*, for this
subset.

## Run it

```bash
python3 evaluation/conformance/verify_conformance.py    # exit 0 = all recomputed; !=0 = mismatch
```

No signup, no key, no network. Drop it straight into CI:

```yaml
- run: python3 evaluation/conformance/verify_conformance.py
```

## Honest boundary (unchanged from `verify/README.md`)

This kit reproduces the **contract-level** decision/reasons/hash for the egress/authority
subset. It does **not** publish the production risk weighting/thresholds, does **not** make
the production ruleset `commit_sha` publicly checkoutable, and receipts are **not** yet
cryptographically issuer-signed. Closing those is the roadmap in `verify/README.md`, not a
claim made here.

## Files

- `egress_authority_conformance.json` — self-contained cases with offline-recomputed expected
  `{decision, reason_codes, input_snapshot_hash}`, keyed by `ruleset_commit_sha` + `engine_version`.
- `verify_conformance.py` — offline, stdlib-only, zero-network verifier (CI-droppable).
