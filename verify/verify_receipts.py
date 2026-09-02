#!/usr/bin/env python3
"""
Quesen receipt verifier  ·  independent, offline, stdlib-only
============================================================

Resolves GitHub issue #1: "Clarify independent replayability of published
receipt commit_sha."

WHAT THIS PROVES (independently, from this public repo alone — no hosted
service, no private engine required):

  1. The exact canonical request bytes for every published UCP #724 vector.
  2. The published `input_snapshot_hash` is reproducible byte-for-byte from
     those request bytes using the public normalization + JCS canonicalization
     spec (docs/security-context/03-normalization.md), implemented in the
     public reference `evaluation/tsc_v2_poc.py`.
  3. The published contract-level `decision` + `reason` codes are reproducible
     from the public reference decision function.

WHAT THIS DOES **NOT** PROVE (stated honestly — see verify/README.md):

  * It does NOT resolve the production ruleset `commit_sha`
    (0095b61…). That commit lives in Quesen's sovereign (non-public) engine
    repository and is intentionally not publicly resolvable. What is public is
    a *contract-level* reference that reproduces the same decision/reasons/hash
    for these vectors — not the production risk weighting/thresholds.
  * It does NOT verify a cryptographic issuer binding. The /tsc/validate
    receipt carries a `request_id` but is NOT signed; issuer binding is
    currently outside the TSC receipt model (see README § "Issuer binding").

USAGE
  python3 verify/verify_receipts.py            # offline verification (default)
  python3 verify/verify_receipts.py --live     # also cross-check the live engine

Exit code 0 = every published vector reproduced; non-zero = a mismatch (so this
is CI-droppable). Python 3.8+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_EVAL = os.path.join(_HERE, "..", "evaluation")
sys.path.insert(0, _EVAL)

import tsc_v2_poc as poc  # noqa: E402  (public reference: normalize + hash + decide)

BASE = "https://web-production-aa5ba.up.railway.app"
VECTORS = os.path.join(_EVAL, "fixtures", "ucp724_lifecycle_vectors.json")


def _load_vectors():
    with open(VECTORS, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_offline():
    data = _load_vectors()
    failures = []
    print("== OFFLINE VERIFICATION (public repo only) ==")
    print(f"   spec:      docs/security-context/03-normalization.md")
    print(f"   reference: evaluation/tsc_v2_poc.py")
    print(f"   vectors:   evaluation/fixtures/ucp724_lifecycle_vectors.json\n")
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
        api_key = http_json("POST", "/sandbox/keys")["api_key"]  # no signup required
        print("   using a fresh free sandbox key (POST /sandbox/keys)")
    hdr = {"X-API-Key": api_key, "Content-Type": "application/json"}
    data = _load_vectors()
    failures = []
    for v in data["vectors"]:
        label = v["outcome"]
        pub = v["receipt"]
        live = http_json("POST", "/tsc/validate", v["request"], hdr)
        match = (
            live["input_snapshot_hash"] == pub["input_snapshot_hash"]
            and live["decision"] == pub["decision"]
        )
        flag = "PASS" if match else "FAIL"
        print(f"  {flag}  {label}  live_hash={live['input_snapshot_hash'][:24]}… "
              f"decision={live['decision']} commit_sha={live.get('commit_sha','?')[:12]}…")
        if not match:
            failures.append(label)
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Independently verify published Quesen receipts.")
    ap.add_argument("--live", action="store_true", help="also cross-check against the live hosted engine")
    args = ap.parse_args()

    failures = verify_offline()
    if args.live:
        try:
            failures += verify_live()
        except Exception as exc:  # network optional; offline result still stands
            print(f"  (live cross-check skipped: {exc})")

    print("\n" + "=" * 64)
    if failures:
        print(f"RESULT: {len(failures)} MISMATCH -> {failures}")
        return 1
    print("RESULT: every published vector reproduced independently (hash + decision + reasons).")
    print("Boundary: production ruleset commit_sha is NOT publicly resolvable; receipts are")
    print("          NOT cryptographically issuer-signed. See verify/README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
