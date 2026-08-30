# UCP #724 — Commercial-Intervention Lifecycle Test Vectors

Cross-domain test vectors mapping the **commercial-intervention provenance
lifecycle** discussed in
[Universal-Commerce-Protocol/ucp#724](https://github.com/Universal-Commerce-Protocol/ucp/discussions/724)
onto Quesen's deterministic decision path. They demonstrate the invariant both
that discussion and MCP
[modelcontextprotocol#2498](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2498)
converged on:

> An inherited assertion keeps its originating authority; crossing a resource
> boundary (Catalog → Offer → Cart → Checkout) **without valid re-attestation**
> downgrades how much policy may rely on it; a sensitive effect **must not clear
> on downgraded authority.**

Every row below is produced live by the hosted engine — no fixture-only values.

- Engine: `POST https://web-production-aa5ba.up.railway.app/tsc/validate` (`tsc_version` `2.0`)
- Ruleset pinned by receipt: `commit_sha` `0095b6183a796ce678086a77e17de6eef9c6a263`
- Machine-readable vectors + full requests/receipts: [`fixtures/ucp724_lifecycle_vectors.json`](fixtures/ucp724_lifecycle_vectors.json)

## Results

| Lifecycle outcome | Modelled authority state | Decision | Reason code |
| --- | --- | --- | --- |
| **PRESERVED** | trusted origin, attested; survives transition unchanged | `PASS` | `NO_ADVERSE_SIGNAL` |
| **RECOVERED** | evidence reconstructed **and re-attested** after the boundary | `PASS` | `NO_ADVERSE_SIGNAL` |
| ↳ RECOVERED (contrast, *pre*-re-attestation) | same inherited authority, before re-attestation | `REVIEW` | `UNVERIFIED_GRANT` |
| **DEGRADED** | crossed a derivation boundary as `client_asserted`, no re-attestation | `REVIEW` | `UNVERIFIED_GRANT` |
| **MISSING** | required authority claimed but attestation evidence absent/unverifiable | `REVIEW` | `UNVERIFIED_GRANT` |
| **MUTATED** (hard invariant) | mutated flow exfiltrates a secret to an unverified sink | `BLOCK` | `EGRESS_SECRET_UNTRUSTED` |

### Integrity binding (why MUTATED is detectable)

The receipt's `input_snapshot_hash` binds the verdict to the *exact* normalized
call. Mutating a single field (`merchant-acct-77` → `merchant-acct-78`) changes
the hash, so a prior authorization receipt no longer binds the mutated call:

```
authorized_call_hash : 2ae328fc73bc10ce32d5fe3746febd3056a43f5c9dbaa9516105570ae120abfd
mutated_call_hash    : eaa8f69956f49924e618b74fff3ac1391f82c2f20b92a3e11f816a17d1c03366
hashes_differ        : true
```

### Observed boundary (stated honestly)

This engine fails closed on an **unattested claim** (`UNVERIFIED_GRANT`), not on
the mere *absence* of a claim. A sensitive action with **no** authority claimed
at all returns `PASS` — absence is not treated as a violation. Both DEGRADED and
MISSING therefore collapse to the same `REVIEW/UNVERIFIED_GRANT` path: the engine
treats *downgraded* and *unverifiable* authority identically — neither may clear
a sensitive effect. Consumers wanting "deny on absence" must assert the required
grant so it becomes a checkable claim.

## Reproduce

```bash
BASE=https://web-production-aa5ba.up.railway.app
KEY=$(curl -sX POST $BASE/sandbox/keys | jq -r .api_key)   # no signup

# DEGRADED -> REVIEW (UNVERIFIED_GRANT)
curl -sX POST $BASE/tsc/validate -H "X-API-Key: $KEY" -H 'Content-Type: application/json' -d '{
  "tsc_version":"2.0","subject":{"kind":"agent","trust_tier":"unverified"},
  "action":{"kind":"payment","operation":"transfer"},
  "target":{"kind":"account","identifier":"merchant-acct-77","trust_tier":"verified"},
  "tool":{"id":"pay.send","capability_class":"financial","granted_scopes":["payment.send"]},
  "permissions":{"granted":["payment.send"]},
  "provenance":{"source":"client_asserted"}}'
```

Related: [aeoess/agent-governance-vocabulary#152](https://github.com/aeoess/agent-governance-vocabulary/issues/152)
(`provenance_tier` proposed as a context dimension).
