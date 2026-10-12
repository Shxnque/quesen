# OpenAmer #69 — A2A `result.receipt` conformance vector

**Thread:** https://github.com/openamer/openamer/issues/69
**Shape source:** `openamer/openamer` `main` @ `1c9aa71` — the envelope + trust model **as described by the maintainer** in the thread (2026-10-08). No OpenAmer code is imported or executed here; this is implementation-neutral.
**Status:** runnable; 6 vectors green (`python3 verify_openamer_69.py` exits 0).
**Posted as:** Shxnque.

## Why this exists

The thread converged on a precise split: OpenAmer's Ed25519 A2A envelope proves message
**authenticity + integrity** (B really sent this, unaltered, within a 300 s freshness window),
but it does **not** prove B's *result* is correct — a correctly-signed envelope can still carry
a wrong or non-reproducible result. The maintainer asked for a concrete vector of the
recomputable-receipt discipline, and gave the exact shape it takes on their side: a new
`kind="result.receipt"` whose `payload` rides *inside* the existing signature, so no new crypto
is needed.

This vector is that artifact. It also closes the **second** gap the maintainer surfaced in the
same comment: `trust.py::Grant` advertises `scope` + `budget` but `has_grant()` enforces
neither (`transport.py:109`) — "a receipt is the natural place to finally make `budget` bite."

## The receipt (rides the existing signed body)

Signed body is canonical sorted-key JSON over `{sender, recipient, kind, payload, nonce, ts}`.
The receipt is:

```
kind:    "result.receipt"
payload: {
  task_id:             "<nonce of the task envelope being answered>",
  input_snapshot_hash: "<sha256 over the exact inputs>",
  code_version:        "<commit sha that ran>",
  policy_version:      "<guardian policy id>",
  outputs_hash:        "<sha256 over declared outputs>",
  outcome:             "<reason code>",
  units_consumed:      "<resource the run consumed>"
}
```

## What verifier A checks (none of which trust B's *competence*)

| # | Check | Vector | Verdict |
|---|---|---|---|
| 1 | **signature** — B sent it, unaltered (their `Envelope.verify`, unchanged) | `R5-signature` (body mutated after signing) | REJECT |
| — | **freshness** — `ts` within the 300 s replay window | `R4-freshness` (replayed after 1 h) | REJECT |
| 2 | **binding** — `task_id` == the nonce A actually requested | `R2-binding` (receipt for another task) | REJECT |
| 3 | **reproducibility** — A re-runs the inputs against `code_version` and compares `outputs_hash` | `R3-reproducibility` (declared result not reproducible) | REJECT |
| 4 | **admissibility** — `units_consumed ≤ bounded grant budget` AND `outcome ∈ grant scope` | `R6-budget-admissibility` (8 units > budget 5) | REJECT |
| — | all pass | `R1-valid` | ACCEPT |

Check 3 is the one that turns "trusting B's competence" into "verifying it." Check 4 is where
the advertised-but-unenforced `budget`/`scope` finally bites — at the receipt, deterministically,
fail-closed.

## Run

```bash
python3 verify_openamer_69.py   # exit 0 iff every vector's verdict matches its expectation
```

`verify_openamer_69.py` uses Ed25519 (their scheme) when `cryptography` is importable, else a
clearly-labelled HMAC-SHA256 stand-in so it stays runnable stdlib-only — the signature primitive
is not the subject; the **payload binding, reproducibility, and budget-admissibility** are.
`vectors.json` is the static declaration; `vectors.result.json` is the last run's output.

## Lineage

The discipline here is the same one Quesen ships as a signed decision receipt —
`{input_snapshot_hash, commit_sha}` on every response (ADR-041), Ed25519 signing (ADR-051), and
constraint-bound **admissibility** / `GrantConstraints` (ADR-052). This vector maps that onto
OpenAmer's envelope without asking OpenAmer to adopt Quesen — the receipt is a plain `kind` on
their own signed body.
