# Security Policy

## Reporting a vulnerability

The Quesen engine handles risk decisions for autonomous agents. A vulnerability
in the engine — including any deterministic-decision leak, credential leak,
or rate-limit bypass — has downstream financial consequences for every
integrator.

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email `shinque03@gmail.com` with the subject prefix `[SECURITY]`.
Include:

- A description of the vulnerability.
- Steps to reproduce (against `https://web-production-30ab5.up.railway.app`
  or a local self-hosted deployment).
- Any proof-of-concept code or curl invocations.
- The impact you believe the vulnerability has.
- Your GitHub handle (optional, for credit).

We will acknowledge receipt within 72 hours and provide an initial assessment
within 7 days. Critical vulnerabilities affecting production will be
triaged immediately.

## Scope

In scope for security reports:

- The production API at `https://web-production-30ab5.up.railway.app`.
- The MCP endpoint at `https://web-production-30ab5.up.railway.app/mcp`.
- The ASP/1.0 protocol implementation (`POST /asp/quotes`, `POST /asp/redeem`,
  `GET /asp/providers`, `HTTP 402` challenge on `/validate`).
- The published SDKs (`quesen-sdk` for Python and JS/TS,
  `quesen-langchain`, `quesen-crewai`, `quesen-autogen`).
- Any documented integration example in this repository.

Out of scope:

- Rate-limit findings that only affect a self-issued key.
- Denial-of-service via traffic volume.
- Findings that require an already-compromised host or already-leaked API key.
- Any issue in a third-party service Quesen integrates with (Stripe, Coinbase
  Commerce, Railway, GitHub, PyPI, npm) — report those directly to the
  vendor.

## Cryptographic and protocol claims

Quesen's Agent Settlement Protocol (ASP/1.0) uses HMAC-SHA256 in a canonical
JSON envelope. If you can:

- Produce a valid signature without the shared secret,
- Replay a redeemed quote,
- Bypass EIP-3009 authorization on the USDC-on-Base adapter,

please report it. These claims are constitutional.

## Determinism claims

Quesen advertises that `/validate` is deterministic — same inputs and same
`engine_version` produce bit-identical outputs. If you can produce a
counter-example, that is a security-grade defect (an integrator's audit trail
depends on it). Please report it.

## Public disclosure

We follow a coordinated-disclosure policy. After a fix is deployed to
production and integrators have had a reasonable time to update, the
vulnerability will be published in the engine repository's changelog (which is
reflected here as a summary entry in `CHANGELOG.md`).
