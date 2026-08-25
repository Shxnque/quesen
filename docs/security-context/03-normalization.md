# 03 · Normalization

Normalization is a **pure, deterministic, side-effect-free** transform applied
*before* decision evaluation and *before* hashing. Its job: collapse
semantically-equivalent inputs to one canonical form so the same meaning always
produces the same verdict and the same `input_snapshot_hash`.

**Hard rule:** normalization NEVER executes, interprets, or follows the content
of any string. It only trims, folds, lowercases, bounds, and orders. (Reference
implementation: `evaluation/tsc_v2_poc.py::normalize`.)

## Rules

| Class | Rule |
| --- | --- |
| Unicode | NFC-normalize every string. |
| Whitespace | Trim leading/trailing whitespace on every string. |
| Enums | NFC → strip → lowercase, then validate against the enum set. |
| Domains | lowercase + strip a single trailing `.` (`Example.COM.` → `example.com`). |
| Identifiers / scopes | lowercase; scopes/permission lists are **deduplicated and sorted** (order-insensitive canonical form). |
| Enum lists (`data.classes`) | each element normalized as an enum; deduped + sorted. |
| Missing values | absent optional fields stay absent — they are **not** injected with defaults into the hash material (except documented enum defaults like `trust_tier=unknown`). |
| Null values | JSON `null` for an optional field ⇒ treated as absent. Explicit `null` for a required field ⇒ `missing_required`. |
| Unknown fields | **rejected** with `unknown_field` (never dropped silently). |
| Nested objects | validated recursively with the same rules. |
| Oversized inputs | any string/list exceeding its bound ⇒ `oversized` (DoS guard). |
| Untrusted strings | `action.intent`, `prompt_injection.*` are bounded + folded but **content is opaque** to the engine. |

## Canonical serialization (for hashing)

RFC-8785 (JCS) compatible subset, matching the ASP HMAC-body discipline already
used in `quesen.asp.signing.canonical_json`:

- UTF-8, **sorted keys**, no insignificant whitespace (`separators=(",", ":")`).
- `ensure_ascii=false`, `allow_nan=false`.
- `client_request_id` removed from the hashed material (ADR-041 parity).

```
input_snapshot_hash = sha256_hex( canonical_json(normalized_context \ client_request_id) )
```

## Proven properties (see POC output)

- **Determinism:** the same context hashed twice ⇒ identical 64-hex digest.
- **Normalization-equivalence:** two contexts differing only in casing,
  whitespace, list order, duplicate scopes, a trailing domain dot, and
  `client_request_id` ⇒ **identical** canonical JSON, hash, and verdict.
  (POC `equiv_a` vs `equiv_b`.)
