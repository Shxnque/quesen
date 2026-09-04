# Quesen x402 Spending Gate — integration example

**The gap this closes.** Agentic-commerce protocols (x402, AP2, ACP) define *how* an agent
authorizes and settles a payment, but deliberately leave **spending governance** — budget caps,
merchant allowlists, human-in-the-loop thresholds — to the harness. Best practice is to enforce
those **outside the model, before the agent signs**. That is precisely what a deterministic
decision core does.

This example shows Quesen as the **pre-signing gate**: an agent about to pay via x402 asks
Quesen for a verdict; only a `PASS` proceeds to signing, and every attempt yields a
replayable, independently-verifiable receipt.

```python
# pip install quesen-sdk
from quesen_sdk import QuesenClient, QuesenFirewall, verify_receipt

quesen = QuesenClient(api_key="sk_sandbox_...")   # sandbox key: https://senueren.co.za/quesen
fw = QuesenFirewall(quesen)

# The payment action the agent wants to take, described as TYPED context
# (policy lives outside the model — determinism means same inputs -> same verdict).
@fw.guard(
    action="x402_payment",
    trust_tier="unverified",     # agent identity / KYA tier asserted upstream
)
def pay_x402(pay_to: str, amount_usdc: float, invoice: dict):
    # ... only runs if Quesen returns PASS; otherwise TscBlocked is raised
    return x402_client.settle(pay_to, amount_usdc, invoice)

# Attempt a payment. Quesen evaluates budget cap / merchant allowlist / threshold
# deterministically BEFORE any signing happens.
try:
    receipt_tx = pay_x402(
        pay_to="0xMerchant",
        amount_usdc=250.0,
        invoice={"merchant_id": "acme", "category": "compute"},
        _quesen={"target": "0xMerchant", "amount": 250.0, "merchant_id": "acme"},
    )
except Exception as blocked:
    decision = pay_x402.last_decision          # PASS / REVIEW / BLOCK / SKIP + reason codes
    # REVIEW -> route to Payman-style human sign-off; BLOCK -> deny; both produce a receipt
    print("gate:", decision.decision, decision.reason_codes)

# Every decision is an independently-verifiable receipt (recomputable + Ed25519 when signed).
v = verify_receipt(pay_x402.last_decision, public_key_hex=QUESEN_ENGINE_PUBKEY)
assert v.ok            # pinnable input_snapshot_hash (proves exactly what was decided)
```

## Why a deterministic gate (not an LLM check)
- **Reproducible:** same inputs → same verdict; the receipt's `input_snapshot_hash` lets anyone
  re-run and confirm the spend decision — a compliance/audit artifact card rails will ask for.
- **Outside the model:** the policy cannot be prompt-injected; the gate runs before signing.
- **Composable:** wraps any wallet/rail — x402, AP2, or card. Verdict `REVIEW` is the natural
  trigger for human-approval chains; `BLOCK` denies; `SKIP` is out-of-scope.

## Where this fits the ecosystem
Quesen sits **behind** identity/KYA (Skyfire) and **in front of** the wallet/settlement
(Crossmint x402, card rails), as the deterministic decision-and-receipt layer. It does not
replace those layers — it makes the *spend decision* auditable and portable, and bills per
decision (ASP-402). See `../docs/architecture-gap-closers.md`.
