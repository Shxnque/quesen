# 11 · Open Decisions (require operator approval before implementation)

Per the P1 mandate: where a choice is genuinely ambiguous, it is surfaced here as
an explicit decision rather than silently made. Engine implementation (Stage 1)
MUST NOT begin until these are resolved.

| # | Decision | Options | Recommendation |
| --- | --- | --- | --- |
| D-1 | **Transport for v2** | (a) body discriminator on `/validate` · (b) `/v2/validate` path · (c) `Accept-Version` header | **(a)** — lowest client friction; mirrors ADR-041's in-place additive precedent |
| D-2 | **ASP wire version** | (a) stay `ASP/1.0` · (b) bump `ASP/1.1` | **(a)** default; revisit only if a client's LC1 assertion needs the signal. Changes ADR-040 invariant either way — needs explicit call |
| D-3 | **Over-claimed trust handling** | (a) downgrade + `REVIEW` · (b) hard `unauthorized_claim` error | **(a)** as default; reserve (b) for a future strict policy mode |
| D-4 | **Confidence model for v2** | (a) field-presence ratio (v1-style) · (b) evidence-weighted by provenance tier | **(b)** — provenance is the whole point; but (a) is simpler for v1 parity. Needs a call |
| D-5 | **Attestation methods in scope for v1 of v2** | `signed` only · `signed`+`oauth_introspection` · all four incl. `mtls` | Start with `signed` + `oauth_introspection`; `mtls` is deployment-specific |
| D-6 | **`SKIP` billing** | billable like a verdict · free (no-charge decline) | Recommend **free** — charging for "I decline" invites gaming and hurts trust |
| D-7 | **`conflicting_fields` set** | minimal (egress-trust vs target-trust) · broad | Start **minimal**; expand from real adversarial findings, not speculation |
| D-8 | **Policy representation** | reference-only (`id`/`version`) · allow inline policy pack | **reference-only** — inline packs violate Doctrine §13 (protocol, not framework) |
| D-9 | **Decision-vocabulary default for v2 clients** | 4-value native · emit v1 words unless client opts into v2 vocab | 4-value native under negotiation; v1 words only on the v1 path |

## Cross-repo blast radius (why approval matters)

The contract is consumed by **six** public client/wrapper repos
(`quesen-sdk-py`, `quesen-sdk-js`, `quesen-langchain`, `quesen-crewai`,
`quesen-autogen`, and this docs/registry repo). A wrong call on D-1/D-2 forces a
second breaking change across all of them. That is precisely why P1 is
design-first and these decisions are gated.
