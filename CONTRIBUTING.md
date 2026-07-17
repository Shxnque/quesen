# Contributing to Quesen (public developer portal)

First, thank you for your interest. This repository is the **public developer
portal** for Quesen — documentation, quickstarts, integration guides, and
registry manifests. **The engine source code lives in a separate, sovereign
repository maintained by the Senueren Bureau.** Engine PRs cannot be accepted
here.

## What belongs here

- Fixes to documentation typos or clarifications.
- Additional integration examples (LangChain, CrewAI, AutoGen, MCP clients,
  Vercel AI SDK, custom agents).
- Improvements to the registry manifests (`smithery.yaml`, `mcp.json`,
  `.well-known/ai-plugin.json`, `llms.txt`) that stay in sync with the
  production endpoint.
- Corrections to the `docs/registries.md` state table.
- Improvements to `CHANGELOG.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  `CONTRIBUTING.md`.

## What does NOT belong here

- Engine source code, weights, thresholds, or conflict-matrix rules.
- ASP/1.0 protocol implementation code.
- SDK source code (each SDK lives in its own repository — see the table in
  `README.md`).
- Internal doctrine, decision logs, or governance artifacts from the private
  engineering repository.

## SDK-specific contributions

- Python: [Shxnque/quesen-sdk-py](https://github.com/Shxnque/quesen-sdk-py)
- JavaScript / TypeScript: [Shxnque/quesen-sdk-js](https://github.com/Shxnque/quesen-sdk-js)
- LangChain: [Shxnque/quesen-langchain](https://github.com/Shxnque/quesen-langchain)
- CrewAI: [Shxnque/quesen-crewai](https://github.com/Shxnque/quesen-crewai)
- AutoGen: [Shxnque/quesen-autogen](https://github.com/Shxnque/quesen-autogen)

## How to submit changes

1. Fork this repository.
2. Create a branch: `git checkout -b your-topic`.
3. Make your changes. Keep commits atomic and use meaningful messages.
4. Verify your changes render correctly by reviewing the diff on GitHub.
5. Open a pull request against `main` describing the intent of your change.

Please keep your changes focused on documentation quality, registry-manifest
accuracy, or example clarity.

## Security disclosures

Do NOT open a public issue for security vulnerabilities. See
[`SECURITY.md`](SECURITY.md) for the responsible-disclosure process.

## Code of Conduct

By participating in this project you agree to abide by the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Questions

Open a GitHub issue with the `question` label, or email
`shinque03@gmail.com`.
