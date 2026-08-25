# 02 · Schema (field-by-field)

Authoritative machine-readable form: [`tsc-v2.schema.json`](tsc-v2.schema.json)
(JSON Schema draft 2020-12). This page is the human contract. Where they differ,
the JSON Schema wins.

**Top-level policy:** `additionalProperties: false` at every object level.
Unknown fields are **rejected** (typed `unknown_field` error), never silently
ignored — an unknown field must never be able to change a verdict (see
`08-security-invariants.md`).

## Required top-level fields

| Field | Type | Notes |
| --- | --- | --- |
| `tsc_version` | string `^2\.[0-9]+$` | Selects v2. Absent ⇒ v1 pipeline. |
| `subject` | object | The acting entity. `kind` required. |
| `action` | object | The attempted operation. `kind` required. |
| `provenance` | object | Trust anchor. `source` required. |

## `subject`

| Field | Type | Values / bound |
| --- | --- | --- |
| `id` | string | ≤ 256 |
| `kind` *(req)* | enum | `agent` `human` `service` `unknown` |
| `framework` | enum | `langchain` `crewai` `autogen` `ag2` `mcp` `openai_assistants` `raw` `other` `unknown` |
| `trust_tier` | enum | `trusted` `verified` `unverified` `unknown` (default `unknown`) |

## `action`

| Field | Type | Values / bound |
| --- | --- | --- |
| `kind` *(req)* | enum | `tool_call` `http_request` `data_read` `data_write` `data_egress` `message_post` `payment` `code_exec` `file_access` `other` |
| `operation` | string | ≤ 128 (structured op name) |
| `intent` | string | ≤ 2000 — **DATA ONLY**, never interpreted as an instruction |

## `target`

| Field | Type | Values / bound |
| --- | --- | --- |
| `kind` | enum | `endpoint` `domain` `contract` `account` `file` `dataset` `recipient` `tool` `service` `other` `unknown` |
| `identifier` | string | ≤ 512 |
| `domain` | string | ≤ 253 (normalized lowercase, trailing dot stripped) |
| `trust_tier` | enum | `trusted` `verified` `unverified` `unknown` |

## `tool`

| Field | Type | Values / bound |
| --- | --- | --- |
| `id` | string | ≤ 256 |
| `capability_class` | enum | `read` `write` `network` `exec` `financial` `admin` `comms` `filesystem` `other` |
| `requested_scopes` | string[] | ≤ 64, deduped + sorted on normalize |
| `granted_scopes` | string[] | ≤ 64, deduped + sorted; **untrusted unless attested** |

## `permissions`

| Field | Type | Notes |
| --- | --- | --- |
| `requested` | string[] | authority the action asks for |
| `granted` | string[] | authority the caller *claims* to hold — trust gated by `provenance` |
| `policy_required` | string[] | authority the policy demands for this action |

## `data`

| Field | Type | Values |
| --- | --- | --- |
| `classes` | enum[] | `public` `internal` `confidential` `pii` `financial` `credential` `secret` `regulated` `unknown` |
| `egress.to` | string | ≤ 512 destination |
| `egress.destination_trust` | enum | `trusted` `verified` `unverified` `unknown` |

## `signals` (observed evidence bag — untrusted by default)

| Field | Type | Notes |
| --- | --- | --- |
| `prompt_injection.suspected` | bool | detector finding |
| `prompt_injection.patterns` | string[] | detector **labels** (data), never executed |
| `prompt_injection.sample_ref` | string | opaque ref, not the raw text |
| `domain_age_days` | int ≥ 0 | v1 compat |
| `engagement_ratio` | number [0,1] | v1 compat |
| `scam_keyword_count` | int ≥ 0 | v1 compat |
| `onchain` | object | v1.5 on-chain enrichment snapshot |

## `provenance` (the trust anchor — required)

| Field | Type | Notes |
| --- | --- | --- |
| `source` *(req)* | enum | `client_asserted` `adapter_derived` `engine_derived` `trusted_metadata` |
| `as_of` | string | ISO-8601 evidence freshness |
| `attestation.method` | enum | `none` `signed` `oauth_introspection` `mtls` |
| `attestation.verified` | bool | when true (or source ∈ {engine_derived, trusted_metadata}) authorization claims may be trusted |
| `evidence_refs` | string[] | opaque references to supporting evidence |

## `client_request_id`

Optional trace id, ≤ 128. **Excluded from `input_snapshot_hash` material**
(parity with ADR-041) so caller trace ids never perturb the hash.
