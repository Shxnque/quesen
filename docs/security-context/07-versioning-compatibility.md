# 07 · Versioning & Backward Compatibility

## Version selection (proposed)

- A request **without** `tsc_version` → the existing **v1 flat pipeline**, byte-for-byte unchanged. This is the load-bearing compatibility guarantee.
- A request **with** `tsc_version` matching `^2\.[0-9]+$` → the **v2 pipeline**.
- The engine advertises support via a new `/version` field: `"supported_tsc_versions": ["1", "2.0"]` (additive; v1 clients ignore it).

## Transport (OPEN DECISION — see `11-open-decisions.md`)

Three candidates, in preference order:

1. **Body discriminator (recommended).** Same `/validate` endpoint; `tsc_version` in the body chooses the pipeline. Mirrors how ADR-041 added fields inside `ASP/1.0` without a wire-version bump. Lowest client friction.
2. `/v2/validate` path alias. Explicit, but forks the surface and the OpenAPI doc.
3. `Accept-Version` header. Clean but invisible in logs/curl and easy to forget.

## ASP wire version (OPEN DECISION)

ADR-040 pins `ASP_VERSION == "ASP/1.0"`. ADR-041 added response fields **inside**
ASP/1.0 using its forward-compatible field-addition rule. TSC v2 is a larger
change (new request shape + new decision vocabulary). Two options:

- **Stay `ASP/1.0`** and treat v2 as an additive, version-negotiated capability (consistent with ADR-041 precedent). *Recommended default.*
- **Bump to `ASP/1.1`** to signal the decision-vocabulary superset (`BLOCK`, `SKIP`).

This must be decided **before** engine implementation because it changes the
LC1 gate invariant (ADR-040) and every SDK's version assertion.

## Backward-compatibility guarantees (binding)

1. No v1 field renamed, removed, or semantically changed.
2. v1 decision vocabulary (`PROCEED/REVIEW/SKIP`) is unchanged **for v1 requests**.
3. v1 golden tests in `Quesen-sib` must pass untouched after v2 lands.
4. `input_snapshot_hash` + `commit_sha` (ADR-041) present on **both** v1 and v2 responses, same algorithm.
5. SDKs that ignore unknown response fields keep working against v2 responses.

## Decision-vocabulary mapping (for mixed fleets)

If a v1-only client somehow receives a v2 verdict (should not happen under
negotiation, but defensive): `PASS→PROCEED`, `REVIEW→REVIEW`, `BLOCK→SKIP`,
`SKIP→REVIEW` (fail safe: decline maps to human review, never to proceed).
