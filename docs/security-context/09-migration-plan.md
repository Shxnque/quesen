# 09 · Migration Plan (engine + six-client release train)

**Principle:** additive, staged, reversible. Nothing here ships until the open
decisions (`11-open-decisions.md`) are resolved. **No version is bumped merely
to look like progress** — a repo's version moves only when it actually ships v2
support.

## Sequencing

### Stage 0 — Approve contract (this P1 package)
Resolve open decisions (transport, ASP version, `unauthorized_claim` policy).
**Gate:** operator sign-off on `11-open-decisions.md`.

### Stage 1 — Engine: additive models behind a flag (`Quesen-sib`)
- Add v2 request/response Pydantic models (`schemas.py`) *alongside* v1 — nothing removed.
- Add `normalize()` + typed validation + reference `decide()` for the typed context, gated by presence of `tsc_version` and/or `QUESEN_TSC_V2_ENABLED`.
- **Engine core (`engine.py`) stays pure**; v1 `evaluate()` untouched. v2 decision path is a new pure function.
- Golden tests: all v1 tests pass unchanged + new v2 invariant tests (I-1…I-13).
- **No change** to weights, thresholds, transport, auth, or `ASP_VERSION` unless Stage 0 approved a bump.

### Stage 2 — Detectors (deferred; P2+)
Implement prompt-injection / tool-authz / data-egress detectors as **signal
producers** that populate the typed context. Contract does not change.

### Stage 3 — Client release train (six repos)
Each client ships an **additive minor** only when it actually supports v2:

| # | Repo | v2 work | Compat |
| --- | --- | --- | --- |
| 1 | `quesen-sdk-py` | Optional `TypedSecurityContext` model + `validate_context()`; keep `validate()` v1. | v1 API unchanged |
| 2 | `quesen-sdk-js` | TS types for TSC v2 + runtime guard; keep v1 client. | v1 API unchanged |
| 3 | `quesen-langchain` | Adapter mapping tool/action/target from LangChain tool-call events. | v1 tool unchanged |
| 4 | `quesen-crewai` | Adapter mapping crew task → action/target/tool. | v1 tool unchanged |
| 5 | `quesen-autogen` | Adapter for **Microsoft AutoGen v0.4+** message/tool events (see `12`? — AG2 is separate). | v1 tool unchanged |
| 6 | `quesen` (this repo) | Docs + evaluation v2 + OpenAPI/`mcp.json` updates. | additive |

**Release ordering:** engine (Stage 1) → `sdk-py` + `sdk-js` → framework
wrappers → docs/registry. A wrapper never ships before the SDK it depends on.

## Evaluation v2 migration (do NOT migrate yet)

The current `evaluation/domain_matrix.py` is the **v1 baseline** (determinism,
thresholds, monotonicity, input-validation, auth, simulate, report, on-chain).
Plan:

- **Keep** all current invariants as the v1 baseline suite.
- **Promote** determinism, input-validation, auth, simulate to v2 (they are
  contract-level and apply to both).
- **Add** typed suites: `authz_matrix`, `egress_matrix`, `injection_matrix`,
  each with positive/negative + adversarial fixtures.
- **New capability:** once detectors exist, measure false-positive / false-negative
  rates per dimension — impossible under v1's flat surface.
- Which domains become *expressible* after P1 vs still need detectors is tabled
  in `01-overview.md`.

## AG2 (separate integration track)

`quesen-autogen` targets **Microsoft AutoGen v0.4+**. **AG2** (`ag2ai/ag2`, the
community fork of legacy AutoGen) is a **different framework** with a different
API surface. P1 makes no AG2 compatibility claim. The AG2 adapter is a
separate, independently-verified track: it maps AG2 agent/tool events into the
same TSC v2 contract, but requires its own repo (or a clearly-namespaced module)
and its own conformance fixtures. **Do not represent `quesen-autogen` as AG2
support.**

## Rollback

Every stage is flag-gated and additive; rollback = disable `QUESEN_TSC_V2_ENABLED`
and the engine serves v1 only. No data migration, no persisted state (Doctrine
§17.5 statelessness).
