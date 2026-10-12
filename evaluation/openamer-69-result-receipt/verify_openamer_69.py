#!/usr/bin/env python3
"""OpenAmer #69 — A2A `result.receipt` conformance vector (runnable, self-contained).

Thread: https://github.com/openamer/openamer/issues/69
Maintainer @openamer asked (2026-10-08, checked vs their `main` @ 1c9aa71) for a
concrete vector of the recomputable decision-receipt discipline, in the exact shape
that rides their existing Ed25519 A2A envelope as a new `kind="result.receipt"`.

What this demonstrates (the honest point of the thread)
------------------------------------------------------
OpenAmer's envelope already proves message **authenticity + integrity** (B sent this,
unaltered, recently). It does NOT yet prove B's **result** is correct. This vector shows
the receipt that closes that gap: it binds `{input_snapshot_hash, code_version,
policy_version, outputs_hash, outcome}` into the signed body, so verifier A performs
three checks that never require trusting B's *competence*:

  1. signature       — B sent it (their `Envelope.verify`, unchanged);
  2. binding         — `task_id` == the nonce of the task A actually requested
                       (a receipt for someone else's task is rejected);
  3. reproducibility — A re-runs the inputs against `code_version` and compares
                       `outputs_hash` (this is the step that turns "trust" into "verify").

It also addresses the SECOND gap @openamer surfaced in the same comment: `trust.py::Grant`
advertises `scope`+`budget` but `has_grant()` enforces neither (`transport.py:109`). The
receipt is the natural place to make `budget` bite — check 4 below is an
**admissibility** gate (the Quesen ADR-052 `GrantConstraints` pattern): the receipt
declares the resource it consumed; A rejects it if that exceeds the bounded grant.

Envelope model (reconstructed from the maintainer's description; no OpenAmer code imported)
-----------------------------------------------------------------------------------------
Signed body is canonical sorted-key JSON over {sender, recipient, kind, payload, nonce, ts};
`payload` is inside the signature, so the four receipt fields need no new crypto.
Signature: Ed25519 if `cryptography` is importable (matches their real scheme); otherwise a
clearly-labelled HMAC-SHA256 stand-in so the vector stays runnable stdlib-only. The signature
primitive is NOT the subject here — the payload binding + reproducibility + budget are.

Run
---
  python3 verify_openamer_69.py
Exit 0 iff every vector's verdict matches its expectation.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sys
import time
from pathlib import Path

# ---- signature primitive (Ed25519 if available, else labelled HMAC stand-in) ----
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.exceptions import InvalidSignature

    _SK = Ed25519PrivateKey.generate()
    _PK = _SK.public_key()
    SIG_ALG = "ed25519"

    def sign(body: bytes) -> bytes:
        return _SK.sign(body)

    def sig_ok(body: bytes, sig: bytes) -> bool:
        try:
            _PK.verify(sig, body)
            return True
        except InvalidSignature:
            return False
except Exception:  # stdlib-only fallback
    _HKEY = b"openamer-69-vector-demo-key"
    SIG_ALG = "hmac-sha256-standin"

    def sign(body: bytes) -> bytes:
        return hmac.new(_HKEY, body, hashlib.sha256).digest()

    def sig_ok(body: bytes, sig: bytes) -> bool:
        return hmac.compare_digest(sign(body), sig)


REPLAY_TOLERANCE_SECONDS = 300  # their _REPLAY_TOLERANCE_SECONDS


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


# ---- the worker's deterministic task (pinned by code_version) ----
CODE_V1 = "v1-sum@aaaa111"
CODE_V2 = "v2-sum-doubled@bbbb222"  # a DIFFERENT code version => different outputs


def run_task(inputs: dict, code_version: str) -> dict:
    """Deterministic: same inputs + same code_version => same outputs. A re-runs this."""
    nums = inputs["numbers"]
    if code_version == CODE_V1:
        result = sum(nums)
    elif code_version == CODE_V2:
        result = sum(nums) * 2
    else:
        raise ValueError(f"unknown code_version {code_version!r}")
    return {"result": result, "units_consumed": len(nums)}


def make_envelope(sender, recipient, kind, payload, nonce, ts):
    body = {"sender": sender, "recipient": recipient, "kind": kind,
            "payload": payload, "nonce": nonce, "ts": ts}
    return {"body": body, "signature": sign(canonical(body)).hex()}


def build_receipt(task_nonce, inputs, code_version, policy_version, outcome,
                  sender="B", recipient="A", nonce="r-nonce-1", ts=None,
                  outputs=None):
    """B builds a result.receipt for a task it ran. `outputs` override lets a vector
    inject a non-reproducible claim (R3)."""
    computed = run_task(inputs, code_version)
    declared_outputs = outputs if outputs is not None else computed
    payload = {
        "task_id": task_nonce,
        "input_snapshot_hash": sha(inputs),
        "code_version": code_version,
        "policy_version": policy_version,
        "outputs_hash": sha(declared_outputs),
        "outcome": outcome,
        "units_consumed": declared_outputs["units_consumed"],
    }
    return make_envelope(sender, recipient, "result.receipt", payload,
                         nonce, ts if ts is not None else int(time.time()))


def verify_receipt(request_nonce, inputs_A, env, grant, now=None):
    """A-side verification. Returns (verdict, checks). Fail-closed: any failed check => REJECT."""
    now = int(time.time()) if now is None else now
    body = env["body"]
    p = body["payload"]
    checks = {}

    # 1. signature (authenticity+integrity) — their Envelope.verify, unchanged
    checks["signature"] = sig_ok(canonical(body), bytes.fromhex(env["signature"]))
    # freshness (their 300s replay window)
    checks["freshness"] = abs(now - body["ts"]) <= REPLAY_TOLERANCE_SECONDS
    # 2. binding — receipt answers the exact task A requested
    checks["binding"] = (p.get("task_id") == request_nonce)
    # 3. reproducibility — A re-runs inputs against code_version, compares outputs_hash
    if checks["signature"] and p.get("input_snapshot_hash") == sha(inputs_A):
        try:
            recomputed = run_task(inputs_A, p["code_version"])
            checks["reproducibility"] = (sha(recomputed) == p.get("outputs_hash"))
        except Exception:
            checks["reproducibility"] = False
    else:
        checks["reproducibility"] = False
    # 4. admissibility — make the advertised-but-unenforced `budget` bite (their 2nd gap)
    #    GrantConstraints pattern (Quesen ADR-052): consumed must fit the bounded grant.
    within_scope = p.get("outcome") in grant.get("allowed_outcomes", [])
    within_budget = p.get("units_consumed", 10**9) <= grant.get("budget_remaining", 0)
    checks["admissibility"] = bool(within_scope and within_budget)

    verdict = "ACCEPT" if all(checks.values()) else "REJECT"
    return verdict, checks


# ---- vectors ----
GRANT = {"allowed_outcomes": ["ok"], "budget_remaining": 5}  # bounded: scope={ok}, budget=5 units
INPUTS = {"numbers": [2, 3]}                                 # consumes 2 units; result=5 under v1
REQ_NONCE = "task-nonce-42"

VECTORS = []


def add(vid, desc, verdict, checks, expect):
    VECTORS.append({"id": vid, "description": desc, "verdict": verdict,
                    "checks": checks, "expected": expect, "match": verdict == expect})


# R1 — valid receipt: signed, bound, reproducible, fresh, within scope+budget => ACCEPT
env = build_receipt(REQ_NONCE, INPUTS, CODE_V1, "guardian-1", "ok")
v, c = verify_receipt(REQ_NONCE, INPUTS, env, GRANT)
add("R1-valid", "Signed, task-bound, reproducible, fresh, in-scope, under budget.", v, c, "ACCEPT")

# R2 — binding failure: receipt answers a DIFFERENT task than A requested => REJECT
env = build_receipt("some-other-task", INPUTS, CODE_V1, "guardian-1", "ok")
v, c = verify_receipt(REQ_NONCE, INPUTS, env, GRANT)
add("R2-binding", "Receipt task_id != the nonce A requested (a receipt for someone else's task).", v, c, "REJECT")

# R3 — reproducibility failure: receipt claims an outputs_hash that doesn't recompute
#      (B asserts result=99 but inputs@code_version yield 5) => REJECT
env = build_receipt(REQ_NONCE, INPUTS, CODE_V1, "guardian-1", "ok",
                    outputs={"result": 99, "units_consumed": 2})
v, c = verify_receipt(REQ_NONCE, INPUTS, env, GRANT)
add("R3-reproducibility", "Declared outputs_hash does not match A's re-run of inputs@code_version — the competence-vs-verify case.", v, c, "REJECT")

# R4 — freshness failure: receipt ts older than the 300s replay window => REJECT
env = build_receipt(REQ_NONCE, INPUTS, CODE_V1, "guardian-1", "ok", ts=int(time.time()) - 3600)
v, c = verify_receipt(REQ_NONCE, INPUTS, env, GRANT)
add("R4-freshness", "Signed receipt replayed outside the 300s freshness window.", v, c, "REJECT")

# R5 — signature failure: body tampered after signing => REJECT
env = build_receipt(REQ_NONCE, INPUTS, CODE_V1, "guardian-1", "ok")
env["body"]["payload"]["outcome"] = "ok-tampered"  # mutate after signing
v, c = verify_receipt(REQ_NONCE, INPUTS, env, GRANT)
add("R5-signature", "Payload mutated after signing; signature no longer covers the body.", v, c, "REJECT")

# R6 — admissibility / budget: a correctly-signed, reproducible receipt that CONSUMED MORE
#      than the bounded grant allows => REJECT. This is the gap @openamer named: `budget`
#      finally bites, at the receipt (not silently ignored at transport.py:109).
BIG = {"numbers": [1, 1, 1, 1, 1, 1, 1, 1]}  # 8 units > budget_remaining 5
env = build_receipt(REQ_NONCE, BIG, CODE_V1, "guardian-1", "ok")
v, c = verify_receipt(REQ_NONCE, BIG, env, GRANT)
add("R6-budget-admissibility", "Valid+reproducible receipt whose units_consumed (8) exceeds the bounded grant budget (5) — the advertised-but-unenforced budget made to bite at the receipt.", v, c, "REJECT")

all_ok = all(x["match"] for x in VECTORS)
out = {"signature_alg": SIG_ALG, "replay_tolerance_seconds": REPLAY_TOLERANCE_SECONDS,
       "vectors": VECTORS, "all_match": bool(all_ok)}
print(json.dumps(out, indent=2))
Path(__file__).with_name("vectors.result.json").write_text(json.dumps(out, indent=2))
sys.exit(0 if all_ok else 1)
