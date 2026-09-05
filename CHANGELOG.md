# Changelog

All notable changes to the Quesen public developer portal will be documented
here. The private engineering repository has its own detailed changelog under
its `enshrine/007-changelog.md`; this file tracks only the public-facing
developer portal.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Offline egress/authority conformance kit** ([`evaluation/conformance/`](evaluation/conformance/))
  — makes the decision subset security integrators gate on independently
  *verdict*-replayable with **zero network**. `verify_conformance.py` (stdlib-only,
  CI-droppable) recomputes `{decision, reason_codes, input_snapshot_hash}` for 6 cases
  (OWASP-agentic + LoopX prepared-Effect PASS/REVIEW/BLOCK) from the public reference
  evaluator, byte-for-byte, plus a `prod-1→prod-2` integrity-flip check — no signup, key,
  or hosted call. Where `verify/` proves *input integrity* (UCP #724), this proves *verdict
  reproducibility* for the egress/authority gate. Addresses external feedback that a
  hosted, closed-ruleset verdict was not locally recomputable.
- **Independent verification bundle** ([`verify/`](verify/)) — resolves issue #1
  (*independent replayability of published receipt `commit_sha`*). Ships a
  runnable, offline, stdlib-only verifier (`verify/verify_receipts.py`, `--live`
  optional) that recomputes `input_snapshot_hash` + contract `decision` + reason
  codes for every published UCP #724 vector, plus a frozen three-way-match
  evidence capture (`verify/three_way_match.json`: published fixture ≡ public
  reference ≡ live engine, 6/6 byte-for-byte). `verify/README.md` states the
  verification boundary honestly.

### Changed
- **Corrected a factually wrong `commit_sha` claim** in `docs/api-reference.md`
  (`/validate` section) and `CHANGELOG` 0.4.0: `commit_sha` is **not** a git SHA
  of `Shxnque/quesen` HEAD — it is a revision label of the sovereign (non-public)
  engine and does not resolve in this public repo. The replay recipe no longer
  tells readers to `git checkout $COMMIT_SHA` (impossible publicly); it points at
  the verification bundle instead. This mismatch was the root cause of issue #1.
- **SDK publication status** updated across `README.md` and `docs/registries.md`:
  `quesen-sdk` is live on PyPI (v0.4.1) and npm (v0.4.0); `quesen-langchain`,
  `quesen-crewai`, `quesen-autogen` live on PyPI (v0.3.0). Previous "preview — not
  yet on PyPI/npm" notes were stale.
- **Registry tracking** in `docs/registries.md` extended with m8ven Verified
  (not yet verified) and ASI:One developer-listing rows + operator steps.

## [0.4.0] — 2026-07-30 · v1.10 receipt provenance (Session 24)

### Added
- **Receipt Provenance** shipped in engine `v1.10.0-rc1`. Every `/validate` and `/simulate` response now carries two additional fields:
  - **`input_snapshot_hash`** — lowercase 64-char SHA-256 hex over canonical-JSON of the received request payload (with `client_request_id` excluded from hash material). Enables callers to hash the same request payload client-side and prove the engine evaluated the exact input they sent.
  - **`commit_sha`** — 40-char lowercase revision label the engine returns to pin the ruleset that produced the verdict, or the sentinel `"unknown"`. It identifies a revision of Quesen's **sovereign (non-public) engine** and does **not** resolve against a commit in this public developer portal. (This was originally mis-described as `Shxnque/quesen` HEAD; corrected in `[Unreleased]`.) Independently reproducible verification of the receipt is provided by [`verify/`](verify/).
- `docs/api-reference.md` §POST /validate — new **Receipt provenance** subsection with response schema update, client-side hash reconstruction snippet, and replay recipe.

### Ecosystem attribution
Both fields ship in direct response to three independent Moltbook engineers who converged on the same missing receipt-shape primitive across four engagement sessions: `@novaclaw_ken` proposed the receipt shape at Session 18 (comment `2d5a1667`); `@gadgethumans-trader-v2` named `commit_sha` as the load-bearing missing field in the same session (comment `3b8542b4`); `@wiplash` cited both by name in a substantive follow-up on Quesen's own release-gate post at Session 22-window (comment `be28fb1f`). The three-independent-voice bar for validated patterns cleared at Session 23, and Session 24's first formal engineering review promoted the paired shape from Repeated to Validated and shipped it.

### Version invariants preserved
- Engine version bumped 1.9.0 → **1.10.0**.
- ASP wire contract unchanged (`ASP_VERSION == "ASP/1.0"` invariant preserved).
- Additive-only response shape change; existing SDKs that ignore unknown fields continue to work unchanged.

### Changed
- `README.md` — health check example bumped to `engine_version: "1.10.0"`.

## [0.3.0] — 2026-07-21 · Triune-consistency pass (Session 18B)

### Changed
- `mcp.json` — `transports.stdio.requires` corrected from `["quesen-sdk>=1.9.0", "mcp>=1.9.0"]` to `["mcp>=1.9.0"]`. The prior `quesen-sdk>=1.9.0` requirement was incorrect: the public `quesen-sdk` PyPI package is at v0.1.0 (client-only, does not ship `quesen.mcp_server`). An explanatory `_note` field on the stdio transport clarifies that self-hosters must bring their own local engine build; HTTP transport remains the fully-supported path.
- `README.md` — new **Tutorials** subsection under Documentation, linking `docs/tutorials/moltbook-post-guard.md` and `docs/tutorials/openclaw-plugin.md` (both landed in Session 15 but were previously unlinked from the top-level README).

### Fixed
- Governance-side hygiene: cross-repository homepage / documentation URL audit ran across the five SDK repositories in Session 18B. No fixes required in `Shxnque/quesen` itself, but engine-version pins in each SDK's README and `pyproject.toml` were normalised to `1.9.0` and all references to any non-public source of truth were removed. The public developer portal (`Shxnque/quesen`) remains the sole canonical registry-facing source of truth.

## [0.2.1] — 2026-07-18 · Documentation additions (Session 14/15)

### Added
- `docs/tutorials/` — new directory carrying two reference integration tutorials extracted from real production integrations:
  - `docs/tutorials/moltbook-post-guard.md` — canonical worked example for wiring Quesen as a pre-post safety gate on autonomous social agents. Includes signal-schema mapping, deterministic gate wiring, telemetry emission, and receipt-side auditability.
  - `docs/tutorials/openclaw-plugin.md` — MCP-native integration walk-through for OpenClaw-style agents. Covers manifest wiring, tool discovery via `tools/list`, and the recommended pre-action call pattern.
- Global distribution assets landed in Session 14: `.well-known/ai-plugin.json`, `llms.txt`, `robots.txt`, `sitemap.xml`, `server.json`. All indexed by the sitemap and referenced from `docs/registries.md`.

### Changed
- `docs/registries.md` — state column updated to reflect Session-14 submissions (Awesome MCP Servers PR `punkpeye/awesome-mcp-servers#10402` opened 2026-07-18, currently `open`; MCP.so submission remains a manual operator action).

## [0.2.0] — 2026-07-17 · Registry alignment

### Changed
- `smithery.yaml` — full rewrite. Hosted-HTTP transport (`startCommand: type: http`)
  as primary; stdio configuration preserved as secondary for local use.
  Version bumped from 1.6.0 to 1.9.0. Tool list expanded from 3 (underscore
  naming) to 5 (dot-namespaced canonical form): `quesen.validate`,
  `quesen.simulate`, `quesen.report`, `quesen.health`, `quesen.version`.
- `README.md` — engine version references bumped 1.6.0 → 1.9.0. Added a live
  production surface table. Tool count corrected to 5. All references to the
  private engineering repository removed.
- `llms.txt` — bumped to engine 1.9.0. Added MCP endpoint, protocol version,
  and tool name mapping.
- `docs/mcp.md` — hosted-HTTP client-config snippet added alongside the
  existing stdio snippet. Tool names corrected to dot-namespaced canonical
  form. Registry-listings section rewritten.
- `docs/registries.md` — state column updated. Explicit statement that
  registry submissions target the public repository only.

### Added
- `mcp.json` at repository root — canonical MCP registry manifest with
  Streamable HTTP as primary transport, stdio as secondary. Includes ASP/1.0
  protocol block.
- `CHANGELOG.md` (this file).
- `CONTRIBUTING.md`.
- `SECURITY.md`.
- `CODE_OF_CONDUCT.md`.

### Governance
- Aligned with the internal Repository Sovereignty ADR maintained in the sovereign engineering repository (private).

## [0.1.0] — 2026-07-16 · Initial developer portal

- Initial public repository per ADR-024 (Public Developer Repo Blueprint).
- README, quickstart, docs (architecture, integrations, api-reference, mcp,
  pricing, faq, registries), initial `smithery.yaml`, `.well-known/ai-plugin.json`,
  `llms.txt`.

[Unreleased]: https://github.com/Shxnque/quesen/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/Shxnque/quesen/releases/tag/v0.4.0
[0.3.0]: https://github.com/Shxnque/quesen/releases/tag/v0.3.0
[0.2.1]: https://github.com/Shxnque/quesen/releases/tag/v0.2.1
[0.2.0]: https://github.com/Shxnque/quesen/releases/tag/v0.2.0
[0.1.0]: https://github.com/Shxnque/quesen/releases/tag/v0.1.0
