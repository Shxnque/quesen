# 12 · ADR-042 Decision Review — recommended resolutions (review gate)

**Purpose:** resolve the nine open decisions from `11-open-decisions.md` with
technical rationale so the operator can approve/adjust in one pass. **This is a
review-gate artifact.** No `Quesen-sib` runtime code changes until these are
signed off.

**Status:** RECOMMENDED · pending operator sign-off.
**Constraints honoured by every recommendation:** v1 stays byte-for-byte; the
engine stays pure/deterministic (no LLM, no I/O in `engine.py`); v2 is additive
and explicitly version-gated.

---

## Recommended resolutions

| # | Decision | **Recommendation** | Rationale (technical) |
| --- | --- | --- | --- |
| **D-1** | Transport for v2 | **(a) body discriminator on `/validate`** | Additive; single OpenAPI/`mcp.json` surface; mirrors ADR-041's in-place field addition. `/v2/validate` forks the surface; header is invisible in logs/curl. Presence of `tsc_version` selects the pipeline. |
| **D-2** | ASP wire version | **Stay `ASP/1.0`** | ADR-040 LC1 pins `ASP/1.0`; ADR-041 already added fields within it. Bumping to `1.1` forces every SDK's version assertion to change = needless breakage. v2 capability is advertised via `/version.supported_tsc_versions`, not a wire bump. v1 clients never see v2 fields. |
| **D-3** | Over-claimed trust tier | **(a) downgrade + `REVIEW`** default; reserve **(b) hard `unauthorized_claim`** behind a `strict` policy mode | Fail-safe and available: a benign over-claim shouldn't 4xx. High-assurance deployments can opt into hard rejection. |
| **D-4** | Confidence model (v2) | **(b) evidence-weighted by provenance tier** (deterministic, fixed tier weights in config) | Provenance is the whole point of v2. Keep it deterministic (tier→weight is a fixed table, not learned). v1 requests keep the v1 field-presence confidence unchanged. |
| **D-5** | Attestation methods in scope | **`signed` + `oauth_introspection`**; defer `mtls` | Covers the two portable, app-layer attestation paths. `mtls` is transport/deployment-specific and can be added without a contract change. |
| **D-6** | `SKIP` billing | **Free (no-charge decline)** | Charging for "I decline" invites gaming and erodes trust (Doctrine §14 honesty). A decline must never have a profit incentive. |
| **D-7** | `conflicting_fields` set | **Minimal**: (i) `data.egress.destination_trust` vs `target.trust_tier` mismatch for the same destination; (ii) a scope in `permissions.granted` that contradicts `tool.capability_class` | Start from real, unambiguous conflicts; expand only from observed adversarial findings, not speculation. |
| **D-8** | Policy representation | **Reference-only (`id`/`version`)** | Inline policy packs would make Quesen a policy *framework* — violates Doctrine §13 (protocol, not framework). The context references policy; it never embeds or executes it. |
| **D-9** | Decision vocabulary default | **4-value native on the v2 path** (`PASS/REVIEW/BLOCK/SKIP`); v1 path unchanged | A caller sending `tsc_version` has explicitly opted into v2 semantics, so it should receive v2's decision vocabulary. No mixed-fleet ambiguity because v1 requests never reach the v2 decider. |

---

## All-environments impact matrix

How each Quesen environment is affected **if these resolutions are approved and
Stage 1 proceeds**. "None (v1)" = no change for existing v1 traffic.

| Environment | Impact under approved decisions | Action required | When |
| --- | --- | --- | --- |
| **`Quesen-sib` engine** | New isolated `quesen/tsc/` module + `QUESEN_TSC_V2_ENABLED` flag; `engine.py` v1 path **untouched** | Stage 1 (see `13-…`) | after sign-off |
| **ASP wire (ADR-040)** | Stays `ASP/1.0`; `/version` advertises `supported_tsc_versions` | additive `/version` field | Stage 1 |
| **`quesen` (public docs / `mcp.json` / OpenAPI)** | Document v2 body discriminator + response vocab | docs + schema publish | Stage 1 |
| **Evaluation harness** | v1 matrix stays baseline; add typed suites (authz/egress/injection) | Evaluation v2 | after Stage 1 |
| **`quesen-sdk-py`** | Additive `TypedSecurityContext` model + `validate_context()`; v1 API unchanged | SDK release train | after engine v2 |
| **`quesen-sdk-js`** | Additive TS types + runtime guard; v1 API unchanged | SDK release train | after engine v2 |
| **`quesen-langchain`** | Adapter: tool-call event → `action/target/tool` | wrapper release | after SDKs |
| **`quesen-crewai`** | Adapter: crew task → `action/target` | wrapper release | after SDKs |
| **`quesen-autogen`** | Adapter for MS AutoGen v0.4+ events | wrapper release | after SDKs |
| **AG2 (`ag2ai/ag2`)** | **Separate track** — verify API before any claim | research spike | independent |
| **Glama connector (A3.6)** | No change; keep connector, no fake public server | none (link docs) | anytime |
| **Smithery listing** | No change; ensure listing links v2 docs | none (link docs) | anytime |
| **Railway deployment** | New env var `QUESEN_TSC_V2_ENABLED` (default `false`); no infra change | set flag when staging | Stage 1 rollout |
| **PyPI / npm distribution** | Unblocked *after* engine v2 + SDK work — **must follow, not precede** | packaging track | P4 |

## Stage-1 authorization conditions (operator-set)

Stage 1 may begin **only** when:
1. D-1…D-9 above are approved (or amended).
2. The v1 byte-for-byte compatibility gate is implemented as a test (replay of existing v1 fixtures ⇒ identical response bytes).
3. A documented rollback exists (`QUESEN_TSC_V2_ENABLED=false` ⇒ engine serves v1 only; no persisted state to unwind).
4. v2 lives behind the explicit feature/version boundary (never the default path).

Detail: `13-stage1-implementation-plan.md`.
