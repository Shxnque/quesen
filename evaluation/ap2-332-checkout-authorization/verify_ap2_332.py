#!/usr/bin/env python3
"""AP2 #332 — checkout-authorization conformance vectors (runnable, SDK-exercising).

Context: https://github.com/google-agentic-commerce/AP2/discussions/332

What this does
--------------
It exercises the *real* AP2 Python SDK checkout-constraint path
(`ap2.sdk.constraints.check_checkout_constraints` / `create_checkout_evaluator`)
and reports, per vector, TWO separate records:

  1. sdk_result            — the mechanical output of the SDK: the list of
                             violation strings (or a fail-closed exception).
                             This is "what the SDK actually evaluates".
  2. authorization_meaning — the normative reading of that same input
                             (what an *omission* MEANS). The SDK does NOT
                             compute this; the vector records it so the two
                             layers stay distinct (per the thread's two-record
                             framing: SDK mechanical check vs. authorization
                             meaning of omission).

Source of truth (verified against AP2 `main`):
  - code/sdk/python/ap2/sdk/constraints.py
      * create_checkout_evaluator() registers EXACTLY two checkout-side
        evaluators: AllowedMerchantsEvaluator, LineItemsEvaluator, and
        raises ValueError on any other constraint type (fail-closed).
      * AllowedMerchantsEvaluator.evaluate(): missing merchant -> violation;
        merchant in allowed set -> []; else -> violation. It only runs when
        an AllowedMerchants constraint is PRESENT.
  - docs/ap2/agent_authorization.md, "Verification and Processing Rules":
        "Any unknown Constraints MUST be treated as failing evaluation."
      and error `unresolved_constraint` for unknown/unverifiable constraints.

How to run
----------
  # 1) make the AP2 SDK importable (from a checkout of google-agentic-commerce/AP2)
  export PYTHONPATH="/path/to/AP2/code/sdk/python:$PYTHONPATH"
  # 2) run
  python3 verify_ap2_332.py
Exit code 0 == every vector matched its expected sdk_result; non-zero otherwise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from ap2.sdk.constraints import check_checkout_constraints, create_checkout_evaluator
    from ap2.sdk.generated.open_checkout_mandate import (
        AllowedMerchants,
        LineItems,
        OpenCheckoutMandate,
    )
    from ap2.sdk.generated.types.checkout import Checkout, Status
    from ap2.sdk.generated.types.merchant import Merchant
except Exception as e:  # pragma: no cover
    print("AP2 SDK not importable. Set PYTHONPATH to AP2/code/sdk/python. Detail:", e)
    sys.exit(2)

CNF = {"jwk": {"kty": "EC", "crv": "P-256", "x": "x", "y": "y"}}
M1 = Merchant(id="merchant_1", name="Demo Merchant", website="https://demo-merchant.example")
M2 = Merchant(id="merchant_2", name="Other Merchant", website="https://other.example")


def checkout(merchant: Merchant | None) -> Checkout:
    """A minimal, valid Checkout. Only `merchant` varies across merchant-dimension vectors."""
    return Checkout(
        id="checkout_1",
        merchant=merchant,
        line_items=[],
        status=Status.ready_for_complete,
        currency="USD",
        totals=[],
        links=[],
    )


def mandate(constraints: list) -> OpenCheckoutMandate:
    return OpenCheckoutMandate(constraints=constraints, cnf=CNF)


# Registered checkout constraint types (introspected from the SDK factory), used by C4b.
REGISTERED_CHECKOUT_TYPES = sorted(
    {AllowedMerchants.model_fields["type"].default, LineItems.model_fields["type"].default}
)


def run_sdk(constraints: list, merchant: Merchant | None):
    """Return ('violations', [...]) or ('raised', 'ExcType: msg') for fail-closed."""
    try:
        return ("violations", check_checkout_constraints(mandate(constraints), checkout(merchant)))
    except Exception as e:
        return ("raised", f"{type(e).__name__}: {e}")


class _UnknownConstraint:
    """A checkout constraint whose type is NOT in the registered set (C0)."""

    type = "checkout.delivery_window"  # not registered


VECTORS = []


def record(vid, desc, kind, expect, got, meaning, citation):
    # `got` is a (kind, value) tuple; compare the value against the expected value.
    ok = (got[0] == "violations") and (got[1] == expect)
    VECTORS.append(
        {
            "id": vid,
            "description": desc,
            "sdk_result": {"kind": got[0], "value": got[1]},
            "expected": expect,
            "match": bool(ok),
            "authorization_meaning": meaning,
            "spec_citation": citation,
        }
    )
    return ok


all_ok = True

# C4a-omitted: NO AllowedMerchants constraint -> merchant dimension is open.
got = run_sdk([], M2)
all_ok &= record(
    "C4a-omitted",
    "AllowedMerchants omitted; arbitrary merchant M2 in the checkout.",
    "violations",
    [],
    got,
    "OPEN on the merchant dimension. Omission == 'unconstrained here', NOT deny. "
    "The SDK runs no merchant evaluator and fabricates no default allowed-set. "
    "A buyer who wants a merchant restriction MUST add an explicit AllowedMerchants constraint.",
    "constraints.py check_checkout_constraints iterates open_mandate.constraints only; "
    "with no AllowedMerchants present, no merchant evaluator is created.",
)

# C4a-explicit-pass: AllowedMerchants=[M1], checkout merchant == M1.
got = run_sdk([AllowedMerchants(allowed=[M1])], M1)
all_ok &= record(
    "C4a-explicit-pass",
    "AllowedMerchants=[M1]; checkout merchant == M1.",
    "violations",
    [],
    got,
    "ALLOWED by an explicit, present constraint (not by omission).",
    "AllowedMerchantsEvaluator.evaluate(): merchant_matches(M1,M1) -> [].",
)

# C4a-explicit-deny: AllowedMerchants=[M1], checkout merchant == M2.
got = run_sdk([AllowedMerchants(allowed=[M1])], M2)
all_ok &= record(
    "C4a-explicit-deny",
    "AllowedMerchants=[M1]; checkout merchant == M2 (not allowed).",
    "violations",
    ["Merchant Other Merchant not in allowed list"],
    got,
    "DENIED by an explicit constraint. This is the only way to get a merchant deny; "
    "it is a present restriction, never an inferred default.",
    "AllowedMerchantsEvaluator.evaluate(): no merchant_matches -> ['Merchant ... not in allowed list'].",
)

# C4a-missing-merchant: AllowedMerchants present, checkout has no merchant.
got = run_sdk([AllowedMerchants(allowed=[M1])], None)
all_ok &= record(
    "C4a-missing-merchant",
    "AllowedMerchants=[M1]; checkout.merchant is None.",
    "violations",
    ["Missing merchant in checkout"],
    got,
    "FAIL-CLOSED: when a merchant restriction is present but the checkout omits the "
    "merchant, the evaluator does not treat 'absent' as 'benign' — it reports a violation.",
    "AllowedMerchantsEvaluator.evaluate(): 'if not merchant_data: return [Missing merchant...]'.",
)

# C0-unknown: an unknown checkout constraint type must fail closed.
try:
    create_checkout_evaluator(_UnknownConstraint())  # type: ignore[arg-type]
    got = ("violations", [])  # did NOT raise -> wrong
    ok = False
except Exception as e:
    got = ("raised", f"{type(e).__name__}: {e}")
    ok = type(e).__name__ == "ValueError"
VECTORS.append(
    {
        "id": "C0-unknown-constraint",
        "description": "A checkout constraint whose type is not in the registered set.",
        "sdk_result": {"kind": got[0], "value": got[1]},
        "expected": "ValueError (fail-closed; never silently skipped)",
        "match": bool(ok),
        "authorization_meaning": "REJECT / fail-closed. An unrecognised constraint MUST NOT be "
        "silently skipped — skipping it is indistinguishable from 'no constraint', which is the "
        "omission case C4a governs. Failing closed keeps the two apart.",
        "spec_citation": "agent_authorization.md Verification rule: 'Any unknown Constraints MUST "
        "be treated as failing evaluation.' + error `unresolved_constraint`.",
    }
)
all_ok &= ok

# C4b-delivery-timing: currently unexpressible on the checkout side.
delivery_expressible = "checkout.delivery_window" in REGISTERED_CHECKOUT_TYPES
VECTORS.append(
    {
        "id": "C4b-delivery-timing",
        "description": "Author wishes to bind a delivery window at checkout.",
        "sdk_result": {
            "kind": "unconstructable",
            "value": f"registered checkout constraint types = {REGISTERED_CHECKOUT_TYPES}; "
            f"a delivery-timing checkout constraint type is {'present' if delivery_expressible else 'ABSENT'}",
        },
        "expected": "no delivery-timing checkout constraint type exists",
        "match": (not delivery_expressible),
        "authorization_meaning": "NORMATIVE_QUESTION / unconstrained-by-construction. There is no "
        "checkout-side constraint type for delivery timing, so a mandate cannot bind it today. "
        "This is a vocabulary gap, NOT an omission-semantics question. If the spec later wants it "
        "enforceable, that is a vocabulary addition; until then delivery-timing enforcement lives "
        "outside AP2 checkout-mandate evaluation.",
        "spec_citation": "constraints.py create_checkout_evaluator registers only "
        "AllowedMerchants + LineItems checkout evaluators.",
    }
)
all_ok &= (not delivery_expressible)

print(json.dumps({"vectors": VECTORS, "all_match": bool(all_ok)}, indent=2))

# Also persist the machine-readable result next to this script.
out = Path(__file__).with_name("vectors.result.json")
out.write_text(json.dumps({"vectors": VECTORS, "all_match": bool(all_ok)}, indent=2))

sys.exit(0 if all_ok else 1)
