# 04 · Validation & Error Taxonomy

Validation is deterministic and total: **every** input maps either to a valid
normalized context or to exactly one typed error. **No input may produce a
500.** (POC suite 3 exercises each code, including hostile payloads.)

## Error codes

| Code | Meaning | HTTP (proposed) |
| --- | --- | --- |
| `malformed` | Body is not a JSON object. | 400 |
| `unsupported_version` | `tsc_version` missing on the v2 path, or not a supported `2.x`. | 400 |
| `missing_required` | A required field (`subject`, `action`, `provenance`, or a required sub-field) is absent/null. | 422 |
| `invalid_type` | A field has the wrong JSON type. | 422 |
| `invalid_enum` | An enum field has a value outside its set. | 422 |
| `out_of_range` | A numeric field violates its min/max. | 422 |
| `oversized` | A string/list exceeds its documented bound. | 413 / 422 |
| `unknown_field` | An object contains a field not in the schema. | 422 |
| `conflicting_fields` | Two fields are mutually exclusive / contradictory (reserved; see §Conflicts). | 422 |
| `unauthorized_claim` | A context asserts a trust/authority level its `provenance` cannot support (reserved; see note). | 422 |

## Error envelope

```json
{ "error": { "code": "invalid_enum",
              "message": "action.kind='delete_everything' not in [...]",
              "pointer": "/action/kind" } }
```

- `pointer` is a JSON-Pointer to the offending location.
- `message` is human-readable and MUST NOT echo secret-bearing values verbatim.

## Determinism of validation

Validation order is fixed and documented so the *same* malformed input always
yields the *same* code: top-level unknown-field check → version → `subject` →
`action` → `provenance` → optional blocks (in schema order). The first violation
encountered wins. (Reference order: `tsc_v2_poc.py::normalize`.)

## Notes on the two reserved codes

- `conflicting_fields`: e.g. `data.egress.destination_trust=trusted` while
  `target.trust_tier=unverified` for the same destination. P1 defines the code;
  the exact conflict set is an **open decision** (`11-open-decisions.md`).
- `unauthorized_claim`: whether an over-claim (e.g. `subject.trust_tier=trusted`
  with `provenance.source=client_asserted, attestation.verified=false`) should be
  a **hard validation error** or a **downgrade + REVIEW** is an open decision.
  P1 default is *downgrade + REVIEW* (see `05-decision-contract.md`), reserving
  the hard-error code for a future strict policy mode.
