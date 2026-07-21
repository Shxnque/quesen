# Changelog

All notable changes to the Quesen public developer portal will be documented
here. The private engineering repository has its own detailed changelog under
its `enshrine/007-changelog.md`; this file tracks only the public-facing
developer portal.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/Shxnque/quesen/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Shxnque/quesen/releases/tag/v0.3.0
[0.2.1]: https://github.com/Shxnque/quesen/releases/tag/v0.2.1
[0.2.0]: https://github.com/Shxnque/quesen/releases/tag/v0.2.0
[0.1.0]: https://github.com/Shxnque/quesen/releases/tag/v0.1.0
