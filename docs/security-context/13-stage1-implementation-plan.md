# 13 · Stage 1 Implementation Blueprint (execute only after sign-off)

> **✅ STAGE 1 IMPLEMENTED (Session 27).** Shipped in `Shxnque/Quesen-sib`:
> isolated `quesen/tsc/` module (`normalize.py`, `decide.py`, `errors.py`,
> `router.py`), `QUESEN_TSC_V2_ENABLED` flag (**OFF by default**), a dedicated
> `POST /tsc/validate` route (see D-1 deviation note below), full contract tests
> (`tests/test_tsc_v2.py`), and an 8-family evaluation suite
> (`evaluation/tsc_v2/`, 28 fixtures). **Regression: 0 new test failures vs
> baseline; v1 `/validate` byte-for-byte unchanged.** Production activation is
> NOT authorized — the flag stays unset in prod.
>
> **Enable locally / in staging:** `export QUESEN_TSC_V2_ENABLED=true` then
> `POST /tsc/validate` with a `tsc_version:"2.0"` body.
> **Prove it:** `python3 -m pytest tests/test_tsc_v2.py tests/test_tsc_v2_eval.py`
> and `python3 evaluation/tsc_v2/run.py`.
>
> **D-1 deviation (recorded):** the v1 `/validate` model is `extra=forbid`, so a
> same-endpoint body discriminator would change v1's invalid-input error format
> and break byte-for-byte. Smallest safe adjustment: v2 lives on a dedicated
> `/tsc/validate` route whose body still carries the `tsc_version` discriminator.

**Scope:** the *smallest useful* engine implementation of TSC v2, fully isolated,
flag-gated, with v1 byte-for-byte preserved and instant rollback. **No code is
written until D-1…D-9 (`12-…`) are approved.**

**Sequence (operator-mandated):** ADR review → **Stage 1** → local evaluation →
controlled staging → production evaluation → release. Never "modify production
engine and hope the matrix catches it."

## Hard requirements

1. **v1 byte-for-byte.** A request without `tsc_version` produces the exact same
   response bytes as before Stage 1. Enforced by a golden replay test.
2. **Explicit boundary.** v2 is reachable only when `tsc_version` matches
   `^2\.` **and** `QUESEN_TSC_V2_ENABLED=true`. Default is disabled.
3. **Rollback.** `QUESEN_TSC_V2_ENABLED=false` ⇒ engine serves v1 only,
   immediately, with no data migration (stateless — Doctrine §17.5).
4. **Determinism.** `engine.py` and the new decider are pure; hashing reuses
   `quesen.asp.signing.canonical_json`.

## File plan (all NEW files; existing v1 files untouched except one dispatch branch)

```
quesen/tsc/__init__.py
quesen/tsc/schemas_v2.py     # Pydantic models mirroring tsc-v2.schema.json
quesen/tsc/normalize.py      # port of evaluation/tsc_v2_poc.py::normalize
quesen/tsc/errors.py         # TscError + code->HTTP mapping (04-validation-errors.md)
quesen/tsc/decide.py         # port of reference decide(); tier weights from config
tests/test_tsc_v2_contract.py    # I-1..I-13 invariants (from POC)
tests/test_v1_byte_for_byte.py   # golden replay: v1 fixtures -> identical bytes
```

**Only edit to an existing file** — the request handler gains a *pre-branch*:

```python
# in the /validate handler, BEFORE any v1 logic
body = await request.json()
if isinstance(body, dict) and str(body.get("tsc_version", "")).startswith("2."):
    if not settings.TSC_V2_ENABLED:
        return tsc_error("unsupported_version", "TSC v2 not enabled on this deployment", "/tsc_version")
    return tsc_v2_validate(body)          # new, isolated path
# --- unchanged v1 path below (not touched) ---
```

The v1 code path is not modified; the branch only fires when `tsc_version` is
present, so v1 payloads never enter new code.

## Config additions (`config.py`)

```python
TSC_V2_ENABLED = _env_bool("QUESEN_TSC_V2_ENABLED", default=False)
TSC_PROVENANCE_TIER_WEIGHTS = {          # D-4 deterministic, fixed
    "trusted_metadata": 1.0, "engine_derived": 1.0,
    "adapter_derived": 0.6, "client_asserted": 0.3,
}
TSC_STRICT_MODE = _env_bool("QUESEN_TSC_STRICT", default=False)  # D-3 reserve (b)
```

No change to v1 weights/thresholds/conflict matrix.

## `/version` additions (additive, D-2)

```json
{ "engine_version": "1.x.y", "asp_version": "ASP/1.0",
  "supported_tsc_versions": ["1", "2.0"],
  "tsc_v2_enabled": false }
```

## Test plan (local evaluation gate)

- `test_v1_byte_for_byte.py`: load existing v1 request fixtures, assert response
  bytes identical with flag on **and** off (v1 path must not depend on the flag).
- `test_tsc_v2_contract.py`: port POC checks — determinism (I-1), normalization
  equivalence (I-2), unknown-field reject (I-3), untrusted-text-not-policy (I-4),
  unverified-grant≠PASS (I-5), no-500 on malformed (I-6), explicit version (I-7),
  provenance survives (I-9), oversized reject (I-13).
- All existing v1/engine tests must pass unchanged.

## Rollout (after local gate passes)

1. **Controlled staging:** deploy with `QUESEN_TSC_V2_ENABLED=true` on a staging
   env only; run the evaluation v2 suites; confirm v1 traffic unaffected.
2. **Production evaluation:** enable behind the flag; monitor; v2 is opt-in per
   request so blast radius is bounded.
3. **Release:** SDK release train (py → js → wrappers), then packaging (PyPI/npm),
   then P4 prospect integration. Never market before the integration surface exists.

## Rollback runbook

`QUESEN_TSC_V2_ENABLED=false` → redeploy/restart → engine serves v1 only. No
schema/state changes to reverse. `/version.tsc_v2_enabled` confirms the state.

## Explicitly NOT in Stage 1

Detectors (injection/authz/egress detection engines), response signing, SDK code,
wrapper adapters, packaging. Stage 1 is the contract path + gate + tests only.
