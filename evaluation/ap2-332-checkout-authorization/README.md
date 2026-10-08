# AP2 #332 — checkout-authorization conformance vectors

**Thread:** https://github.com/google-agentic-commerce/AP2/discussions/332
**Verified against:** `google-agentic-commerce/AP2` `main` @ `e1ea56d` (`code/sdk/python`).
**Status:** runnable; all 6 vectors green (`python3 verify_ap2_332.py` exits 0).
**Posted as:** Shxnque. Implementation-neutral; no systems tested; exercises only the public SDK.

## Why this exists

In the thread, the question is *"when does a checkout change require renewed user
authorization?"* The convergence (arjun2075, send21io, chopmob-cloud) was that two
layers must stay distinct:

1. the **SDK's mechanical constraint-check result** — what `check_checkout_constraints`
   actually returns for a given mandate+checkout; and
2. the **authorization meaning of an omission** — what it *means* that a mandate did
   not express a constraint on some dimension.

These vectors keep those two as separate records so neither is read off the other.
Each vector reports a `sdk_result` (mechanical) **and** an `authorization_meaning`
(normative). The SDK computes only the first; the second is recorded, not inferred.

## What the SDK actually evaluates (verified at source)

From `code/sdk/python/ap2/sdk/constraints.py` on `main`:

- `create_checkout_evaluator()` registers **exactly two** checkout-side evaluators —
  `AllowedMerchantsEvaluator` and `LineItemsEvaluator` — and **raises `ValueError`**
  for any other constraint type (fail-closed).
- `AllowedMerchantsEvaluator.evaluate()`:
  - checkout merchant missing → `['Missing merchant in checkout']` (fail-closed);
  - merchant matches an allowed entry → `[]`;
  - otherwise → `['Merchant <name> not in allowed list']`.
  - It only runs when an `AllowedMerchants` constraint is **present**.
- `check_checkout_constraints()` iterates `open_mandate.constraints` only; a dimension
  with no constraint has **no evaluator** and therefore produces no violation.

From `docs/ap2/agent_authorization.md`, *Verification and Processing Rules*:

> "Any unknown Constraints MUST be treated as failing evaluation."

and the `unresolved_constraint` action-authorization error for unknown/unverifiable
constraints. The SDK's `ValueError` on an unregistered checkout constraint type is the
mechanical realisation of that rule.

## The vectors

| id | input | sdk_result | authorization_meaning |
|---|---|---|---|
| `C4a-omitted` | no `AllowedMerchants`; arbitrary merchant | `[]` (no violation) | **OPEN on the merchant dimension** — omission ≠ deny; no default allowed-set is fabricated |
| `C4a-explicit-pass` | `AllowedMerchants=[M1]`; merchant=M1 | `[]` | allowed by an explicit, present constraint |
| `C4a-explicit-deny` | `AllowedMerchants=[M1]`; merchant=M2 | `['Merchant Other Merchant not in allowed list']` | denied by an explicit constraint (the only way to get a merchant deny) |
| `C4a-missing-merchant` | `AllowedMerchants=[M1]`; merchant=None | `['Missing merchant in checkout']` | **fail-closed**: absent ≠ benign when a restriction is present |
| `C0-unknown-constraint` | unregistered checkout constraint type | `ValueError` (fail-closed) | reject; unknown MUST NOT be silently skipped (else indistinguishable from omission) |
| `C4b-delivery-timing` | author wants to bind a delivery window | *unconstructable* — no such checkout constraint type exists | **NORMATIVE_QUESTION**: vocabulary gap, not an omission-semantics question |

The load-bearing distinction: **C4a** is *expressible, left open* (PASS, no default
invented); **C4b** is *not expressible at all* (records the gap, does not pretend to
enforce); **C0** stops *unknown type* from leaking into either bucket by failing closed.

## Run it

```bash
# make the AP2 SDK importable (from a checkout of google-agentic-commerce/AP2)
export PYTHONPATH="/path/to/AP2/code/sdk/python:$PYTHONPATH"
python3 verify_ap2_332.py          # prints JSON; exits 0 iff every sdk_result matches
```

`vectors.json` is the static declaration (inputs + expected sdk_result +
authorization_meaning + spec citation per vector). `verify_ap2_332.py` regenerates
`vectors.result.json` from the live SDK so the declaration stays checkable.
