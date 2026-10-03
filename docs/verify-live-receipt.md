# Verify a live Quesen receipt yourself (don't trust — verify)

Quesen's differentiator is not a log you have to trust. A Quesen decision receipt is
**independently verifiable**: you can recompute the verdict *and* (with engine signing
enabled) check an **Ed25519 signature** against a public key the engine publishes itself.

As of **2026-10-03 the production engine signs decision receipts** — `GET /tsc/version`
reports `signing.alg = ed25519` and serves the `public_key_hex` + `key_id`. The steps below
are fully runnable against live production; nothing here requires trusting Senueren.

## 1. Fetch the engine's public key (self-published)

```bash
curl -s https://web-production-3df26.up.railway.app/tsc/version | jq .signing
# { "alg": "ed25519", "public_key_hex": "<hex>", "key_id": "tsc-ed25519-…" }
```

## 2. Get a free sandbox key and a signed decision

```bash
KEY=$(curl -s -X POST https://web-production-3df26.up.railway.app/sandbox/keys | jq -r .api_key)

curl -s -X POST https://web-production-3df26.up.railway.app/tsc/validate \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"tsc_version":"2.0","subject":{"kind":"agent"},"action":{"kind":"data_egress"},
       "provenance":{"source":"adapter_derived"},
       "data":{"classes":["secret"],
               "egress":{"to":"https://paste.evil.example","destination_trust":"unverified"}}}'
# -> decision=BLOCK, reasons=[EGRESS_SECRET_UNTRUSTED],
#    signature=<hex>, signature_alg=ed25519, key_id=tsc-ed25519-…
```

## 3. Verify the signature independently (no Quesen code needed)

The signed preimage is the canonical byte encoding of **exactly**
`{decision, input_snapshot_hash, commit_sha, reasons}` in that fixed order (compact JSON,
UTF-8, no key sorting) — the same bytes `quesen-sdk` (`canonical_receipt_bytes` /
`canonicalReceiptBytes`) verifies.

```python
import json, httpx
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

BASE = "https://web-production-3df26.up.railway.app"
pub  = httpx.get(f"{BASE}/tsc/version").json()["signing"]["public_key_hex"]
rec  = <paste the receipt JSON from step 2>

preimage = json.dumps({k: rec[k] for k in ("decision","input_snapshot_hash","commit_sha","reasons")},
                      separators=(",", ":"), ensure_ascii=False, sort_keys=False).encode()
Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub)).verify(bytes.fromhex(rec["signature"]), preimage)
print("receipt is authentic + untampered")   # raises if the signature does not match
```

Change a single byte of `decision`, `reasons`, or `input_snapshot_hash` and the verify step
fails — that is the property: **a Quesen receipt proves *what* the verdict was (recompute)
and *who* issued it (signature), to a party that never has to trust the running service.**

## Why this matters

- **Authorization ≠ execution.** A receipt is proof of a *decision*, never proof an action
  ran. See [`docs/security-context`](security-context/) and the evidence/execution-binding
  and **admissibility** (constraint-bound authority) primitives in `quesen-sdk`.
- **Deterministic.** No model inference in the scoring path — same input, same verdict,
  same bytes, forever (pin `commit_sha`).
- **Portable.** Verify offline with the public `verify/` bundle or `quesen verify <receipt>`.
