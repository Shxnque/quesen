# Changelog

All notable changes to the Quesen public developer portal will be documented
here. The private engineering repository has its own detailed changelog under
its `enshrine/007-changelog.md`; this file tracks only the public-facing
developer portal.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- Aligned with `Shxnque/Quesen-sib` ADR-041 (Repository Sovereignty).

## [0.1.0] — 2026-07-16 · Initial developer portal

- Initial public repository per ADR-024 (Public Developer Repo Blueprint).
- README, quickstart, docs (architecture, integrations, api-reference, mcp,
  pricing, faq, registries), initial `smithery.yaml`, `.well-known/ai-plugin.json`,
  `llms.txt`.

[Unreleased]: https://github.com/Shxnque/quesen/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Shxnque/quesen/releases/tag/v0.2.0
[0.1.0]: https://github.com/Shxnque/quesen/releases/tag/v0.1.0
