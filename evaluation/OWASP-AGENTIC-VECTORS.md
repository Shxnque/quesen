# OWASP Agentic Top-10 → Deterministic Decision Vectors

Generated **live** against `POST /tsc/validate` on the deployed engine
(`engine_version 1.10.0`, ruleset `commit_sha 0095b618…`) — real receipts, not
hand-written. Reproducible without signup: `KEY=$(curl -sX POST
https://web-production-aa5ba.up.railway.app/sandbox/keys | jq -r .api_key)`.

**Scope / honesty:** Quesen does not *detect prompt injection semantically*. It
gates the **authority, provenance, and egress** of the action an agent tries to
take — so an injection that produces a privileged or exfiltrating action is
caught at the decision boundary regardless of how the model was fooled. That is
the "assume the model can be compromised, enforce out-of-band" posture
([sequant#980](https://github.com/sequant-io/sequant/issues/980)) expressed as a
deterministic decision + recomputable receipt.

| OWASP Agentic class | Modelled action | Decision | Reason code | `input_snapshot_hash` |
|---|---|---|---|---|
| Excessive Agency / sensitive-info disclosure | secret egress → unverified sink | `BLOCK` | `EGRESS_SECRET_UNTRUSTED` | `58cc93c9795d4a83…` |
| Tool misuse / privilege via unattested authority (typical injection outcome) | `code_exec` on prod with a **client-asserted** (unattested) grant | `REVIEW` | `UNVERIFIED_GRANT` | `48712752f03eb5cc…` |
| Control (no adverse signal) | verified agent reads a verified file, attested provenance | `PASS` | `NO_ADVERSE_SIGNAL` | `ec4c33df4f0a77aa…` |

All three pin `commit_sha 0095b6183a…`.

**Integrity binding (why the receipt is a fixture, not a log line):** mutating a
single field of the tool-misuse vector — `target.identifier` `prod-1` → `prod-2`
— flips `input_snapshot_hash` `48712752f03eb5cc…` → `0f140cdb19884ecf…`. A prior
authorization receipt therefore no longer binds the mutated call — integrity is
structural, independent of the verdict. This is the TOCTOU defense: bind the
decision to a hash of the exact normalized call.

**Strict typing (fail-closed on malformed context):** the engine rejects
unknown fields and invalid enums with typed errors rather than normalizing them
away, e.g. `{"error":{"code":"invalid_enum","pointer":"/provenance/source",
"message":"…not in [adapter_derived, client_asserted, engine_derived,
trusted_metadata]"}}`. A context it cannot type, it will not silently pass.

## How a CI gate uses this
Replace a one-time manual injection eval with a fixture the job asserts on:

```bash
KEY=$(curl -sX POST $BASE/sandbox/keys | jq -r .api_key)
got=$(curl -sX POST $BASE/tsc/validate -H "X-API-Key: $KEY" -H 'Content-Type: application/json' -d @secret-egress.json)
echo "$got" | jq -e '.decision=="BLOCK" and .reasons[0].code=="EGRESS_SECRET_UNTRUSTED"' >/dev/null \
  || { echo "trust-boundary regression"; exit 1; }
```

"Secret egress to an untrusted sink is refused" stops being prose and becomes a
check that recomputes, with a receipt (`decision`, `reason`, `input hash`,
`ruleset commit`) a reviewer can verify.

## Machine-readable
See [`fixtures/owasp_agentic_vectors.json`](fixtures/owasp_agentic_vectors.json).
