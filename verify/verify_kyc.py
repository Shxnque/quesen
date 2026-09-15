#!/usr/bin/env python3
"""
Quesen KYC/AML decision verifier · independent, offline, stdlib-only
====================================================================

Companion to `verify/verify_receipts.py`, for the governed KYC/AML vectors
(`evaluation/fixtures/kyc_decision_vectors.json`) discussed in
agentguard-ai/tealtiger#434.

WHAT THIS PROVES (from this public repo alone — no hosted service):
  For every KYC scenario, the published `input_snapshot_hash`, `decision`, and
  `reasons` are reproduced byte-for-byte by the PUBLIC reference decision
  function (evaluation/tsc_v2_poc.py). Same inputs -> same verdict, always.

WHAT THIS DOES NOT PROVE (stated honestly):
  * It does NOT perform OFAC/EU/UN sanctions matching. Quesen governs the
    *admission* of the KYC agents' actions (approve / screen / extract) and
    emits a recomputable receipt; the list-match itself is the screening
    agent's job. Quesen turns its result into a deterministic, replayable
    authorization decision.
  * Receipts are contract-level (reference engine `poc-ref-0`), not the
    production ruleset commit_sha, and are NOT cryptographically signed
    (issuer binding is out of the current TSC receipt model). See verify/README.md.

USAGE
  python3 verify/verify_kyc.py            # offline verification
  python3 verify/verify_kyc.py --live     # also cross-check the live engine

Exit 0 = every vector reproduced; non-zero = a mismatch (CI-droppable).
Python 3.8+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_EVAL = os.path.join(_HERE, "..", "evaluation")
sys.path.insert(0, _EVAL)

import tsc_v2_poc as poc  # noqa: E402

BASE = "https://web-production-3df26.up.railway.app"
VECTORS = os.path.join(_EVAL, "fixtures", "kyc_decision_vectors.json")


def _load():
    with open(VECTORS, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_offline():
    data = _load()
    failures = []
    print("== KYC/AML OFFLINE VERIFICATION (public repo only) ==")
    print(f"   reference: evaluation/tsc_v2_poc.py")
    print(f"   vectors:   evaluation/fixtures/kyc_decision_vectors.json\n")
    for v in data["vectors"]:
        label = v["outcome"]
        pub = v["receipt"]
        ok, res = poc.evaluate(v["request"])
        if not ok:
            print(f"  FAIL  {label}: reference rejected the request -> {res.get('error')}")
            failures.append(label)
            continue
        got_hash = res["input_snapshot_hash"]
        got_dec = res["decision"]
        got_reasons = [r["code"] for r in res["reasons"]]
        hash_ok = got_hash == pub["input_snapshot_hash"]
        dec_ok = got_dec == pub["decision"]
        reason_ok = got_reasons == pub["reasons"]
        flag = "PASS" if (hash_ok and dec_ok and reason_ok) else "FAIL"
        print(f"  {flag}  {label}")
        print(f"        hash     {got_hash[:24]}…  match={hash_ok}")
        print(f"        decision {got_dec:<7}  match={dec_ok}")
        print(f"        reasons  {got_reasons}  match={reason_ok}")
        if flag == "FAIL":
            failures.append(label)
    return failures


def verify_live():
    import urllib.request

    def http_json(method, path, body=None, headers=None):
        raw = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(BASE + path, data=raw, method=method, headers=headers or {})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())

    print("\n== LIVE CROSS-CHECK (hosted engine, optional) ==")
    api_key = os.environ.get("QUESEN_API_KEY")
    if not api_key:
        api_key = http_json("POST", "/sandbox/keys")["api_key"]
        print("   using a fresh free sandbox key (POST /sandbox/keys)")
    hdr = {"X-API-Key": api_key, "Content-Type": "application/json"}
    data = _load()
    failures = []
    for v in data["vectors"]:
        label = v["outcome"]
        pub = v["receipt"]
        live = http_json("POST", "/tsc/validate", v["request"], hdr)
        match = (live["input_snapshot_hash"] == pub["input_snapshot_hash"]
                 and live["decision"] == pub["decision"])
        flag = "PASS" if match else "FAIL"
        print(f"  {flag}  {label}  live_hash={live['input_snapshot_hash'][:24]}… "
              f"decision={live['decision']} commit_sha={live.get('commit_sha','?')[:12]}…")
        if not match:
            failures.append(label)
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Independently verify Quesen KYC/AML decision vectors.")
    ap.add_argument("--live", action="store_true", help="also cross-check against the live hosted engine")
    args = ap.parse_args()

    failures = verify_offline()
    if args.live:
        try:
            failures += verify_live()
        except Exception as exc:
            print(f"  (live cross-check skipped: {exc})")

    print("\n" + "=" * 64)
    if failures:
        print(f"RESULT: {len(failures)} MISMATCH -> {failures}")
        return 1
    print("RESULT: every KYC vector reproduced independently (hash + decision + reasons).")
    print("Boundary: Quesen governs decision admission + emits a recomputable receipt;")
    print("          it does NOT perform the OFAC/EU/UN list match, and receipts are not signed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
