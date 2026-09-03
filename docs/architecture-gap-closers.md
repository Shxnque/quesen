# Architecture — closing the gaps (2026-09)

A competitive review (arcjet, kontext, tenuo, openfirma, AgentKey, …) surfaced
four gaps between Quesen and adjacent agent-governance layers. This is the
official design for closing them **without diluting the moat** (deterministic,
zero-LLM, replayable). It is reflected across the ecosystem: engine (`Quesen-sib`,
sovereign), SDKs (`quesen-sdk-py` / `quesen-sdk-js`), and this portal.

## Positioning (one line)

> The deterministic decision-and-receipt core for agent actions — the only layer
> that lets you re-run any verdict byte-for-byte and prove it — designed to sit
> *behind* injection detection and *on top of* agent identity, and to bill per
> decision.

## Four layers of the agent-safety stack, and where Quesen sits

```
  [ A. Detection ]      prompt-injection / malicious-input detection   (arcjet, kontext)
        │  sanitised, typed security context
        ▼
  [ B. Identity  ]      signed agent identity + capability tokens      (tenuo, opena2a)
        │  provenance / trust tier
        ▼
  [ C. DECISION  ]  ◀── QUESEN: deterministic verdict + reason codes + receipt
        │  PASS / REVIEW / BLOCK / SKIP  (+ ASP/402 metered billing)
        ▼
  [ D. Enforcement + Evidence ]  gate the action; emit a verifiable receipt
```

Quesen owns **C** and the **evidence half of D**, and integrates with — rather
than competes against — A and B.

## Gap closers

### 1. Enforcement (not just advice) — SHIPPED (SDK ≥ 0.5.0)
`QuesenFirewall.guard()` decorates a callable so it **does not execute** unless the
engine returns PASS (fail-closed on BLOCK/REVIEW/SKIP and on transport error). The
verdict is attached as `.last_decision` for audit. This removes the "advisory
unless wired" objection at the SDK layer; an optional sidecar/proxy enforcement
mode is the next step for non-SDK integrations.

```python
@fw.guard(action="payment", trust_tier="unverified")
def send_funds(to, amount): ...
send_funds("0xabc", 5)   # raises TscBlocked unless PASS
```

### 2. Independently-verifiable receipts — SHIPPED (client), engine signing = next
`quesen_sdk.verify_receipt()` checks (a) structural integrity — a pinnable
`input_snapshot_hash` — and (b) an Ed25519 signature over `canonical_receipt_bytes()`
when the engine signs, against a published engine public key. This upgrades the
receipt from *recomputable* to *issuer-attributable* — the `signature_capability`
the AGV crosswalk currently marks intentionally omitted. Engine-side signing lands
in `Quesen-sib`; the SDK is forward-compatible today (unsigned receipts verify at
the structural level).

**Why this beats a tamper-evident vendor log:** their audit is *their word, kept by
them*; a Quesen receipt is checkable on the caller's side with no trust in Quesen.

### 3. Detection front-end seam — INTERFACE
Quesen evaluates a **typed** context; it does not itself sanitise adversarial
free-text (rossum's point: *a hash proves what the agent was told, not what it
saw*). The design is explicit: a detection layer (arcjet/kontext) produces the
typed context and MAY attach `threat_signals`; Quesen renders a deterministic
verdict over it. We document this as an integration contract rather than
re-implementing ML detection — honest about the trust boundary instead of
pretending the hash closes it.

### 4. Identity integration — INTERFACE
Quesen carries a **provenance tier** referencing an identity asserted upstream; it
is not an identity authority. It composes with cryptographic identity layers
(tenuo/opena2a): they issue the signed identity, Quesen binds its provenance tier
to it and enforces the no-silent-authority-upgrade invariant (authority cannot
strengthen merely by crossing a boundary — see UCP #788, AGV, Google AP2).

## What stays unchanged (the moat)
Determinism, zero-LLM scoring path, `input_snapshot_hash` + `commit_sha`, the
public executable POC (`evaluation/tsc_v2_poc.py`), and the PASS/REVIEW/BLOCK/SKIP
reason-code vocabulary. Every gap closer is additive and preserves byte-exact
replay.
