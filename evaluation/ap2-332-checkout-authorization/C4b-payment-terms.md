# AP2 #332 — C4b addendum: UCP payment terms (Pay-Now vs Net-30)

**Thread:** https://github.com/google-agentic-commerce/AP2/discussions/332
**Credit:** scenario contributed by @arjun2075 (2026-10-09), tested locally against AP2 `e1ea56d`
+ UCP `f2206e6` (Payment Terms draft). This file records the classification against the same
two-record framing used by `verify_ap2_332.py`; it does **not** re-assert arjun's local SDK run.
**Posted as:** Shxnque.

## The scenario (arjun2075)

A buyer delegates authority to purchase $1,000 of equipment from an allowed merchant under an
open Checkout Mandate carrying `checkout.allowed_merchants` + `checkout.line_items`. The business
offers the same purchase under three UCP payment schedules:

1. $1,000 due at checkout completion;
2. $1,000 due Net-30;
3. $200 at completion, $800 deferred.

The buyer intended to authorize the *purchase* but **not** any deferred-payment obligation.

## Observed SDK behavior (as reported)

- `check_checkout_constraints` returns `[]` for all three schedules — merchant + line-item
  constraints are satisfied; the UCP payment extension survives as an `extra` but is **not
  evaluated**.
- `payment.execution_date` / `payment.amount_range` do not close it: `check_payment_constraints`
  receives no Checkout or schedule input, and `execution_date` constrains the PaymentMandate's own
  field, not the derived checkout.

## Classification (same frame as the C4b-delivery-timing vector)

| Record | Value |
|---|---|
| `sdk_result` | **unconstructable** — the checkout-side vocabulary registers only `AllowedMerchants` + `LineItems`; there is no checkout constraint type for a UCP payment schedule, so a mandate cannot bind it today. |
| `authorization_meaning` | **NORMATIVE_QUESTION / unconstrained-by-construction.** This is an **open→closed authority-derivation** gap: can an open mandate's silence on payment terms be read as authority to accept *any* schedule? It is distinct from **C0** (a *present* but unknown constraint already fails evaluation) and distinct from the **closed→execution** integrity issue tracked in #358/#359. |

## Why it is C4b, not C0 or #358/#359

- **vs C0:** C0 is a constraint that *is present* on the mandate but of an unregistered type → it
  fails closed (`ValueError` / `unresolved_constraint`). Here there is **no constraint to
  present** — the dimension cannot be expressed with the built-in types at all.
- **vs #358/#359:** those concern integrity of an *already-closed* mandate at execution. This is
  about what authority is *derived* when an open mandate is silent on a dimension — upstream of
  execution.

## Suggested resolution direction (non-binding)

Two honest options, mirroring the delivery-timing conclusion: (a) treat payment-schedule as a
**vocabulary addition** (a registered checkout-side constraint type that a mandate can bind,
e.g. `max_deferred_amount` / `allowed_payment_terms`), or (b) keep it **out of AP2 checkout-mandate
evaluation** and enforce it in the payment layer — but then say so explicitly, because today the
silent `[]` is indistinguishable from "authorized." Either way the fix is a *declared* decision,
not an inferred default — the same principle as C4a's omission semantics.

Happy to add a runnable `C4b-payment-terms` branch to `verify_ap2_332.py` (introspecting the
registered checkout constraint types, exactly as the delivery-timing vector does) and/or open a
PR placing the whole fixture set under an AP2 `tests/`/`fixtures` path, whichever AP2 prefers.
