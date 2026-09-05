#!/usr/bin/env python3
"""
Quesen egress/authority conformance verifier  ·  OFFLINE, stdlib-only, ZERO network
=================================================================================

Why this exists (criticism-driven — see BEA criticism-ledger C-003 / C-004):

  * C-003 (sequant / @admarble): "a security gate that requires a network call to a
    third-party hosted service at CI time adds a new external dependency to the exact
    surface this issue is trying to shrink."  -> This verifier makes ZERO network calls.
  * C-004 (loopx / @huangruiteng): "verify or locally replay the verdict rather than only
    trusting input_snapshot_hash plus a claimed engine commit."  -> This verifier RECOMPUTES
    the decision + reason codes + input_snapshot_hash locally from the public reference
    evaluator, and asserts them against the self-contained conformance fixture.

What it proves, from this public repo alone (no hosted engine, no signup, no key):
  1. Every egress/authority conformance case's `input_snapshot_hash` is reproducible
     byte-for-byte from the request via the public normalization + JCS spec.
  2. Every case's `decision` + `reason_codes` are reproducible from the public reference
     decision function (`evaluation/tsc_v2_poc.py::decide`).
  3. The integrity binding holds: mutating one field (prod-1 -> prod-2) changes the hash,
     so a prior authorization receipt no longer binds the mutated call (TOCTOU defense).

What it does NOT prove (stated honestly; identical boundary to verify/README.md):
  * It does not resolve the production ruleset commit_sha to a public checkout, and receipts
    are not cryptographically issuer-signed. The reference reproduces the *contract-level*
    decision/reasons/hash for this subset, not the production risk weighting/thresholds.

USAGE
  python3 evaluation/conformance/verify_conformance.py     # offline; exit!=0 on any mismatch

Python 3.8+, standard library only. CI-droppable with no secrets and no network egress.
"""
from __future__ import annotations

import copy
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_EVAL = os.path.join(_HERE, "..")
sys.path.insert(0, _EVAL)

import tsc_v2_poc as poc  # noqa: E402  public reference: normalize + hash + decide

KIT = os.path.join(_HERE, "egress_authority_conformance.json")


def main() -> int:
    kit = json.load(open(KIT, "r", encoding="utf-8"))
    print("== QUESEN EGRESS/AUTHORITY CONFORMANCE (offline, zero network) ==")
    print(f"   ruleset_commit_sha: {kit['ruleset_commit_sha']}")
    print(f"   engine_version:     {kit['engine_version']}")
    print(f"   reference:          {kit['reference_evaluator']}")
    print(f"   network_required:   {kit['network_required']}\n")

    failures = []
    for c in kit["cases"]:
        ok, res = poc.evaluate(c["request"])
        exp = c["expect"]
        if not ok:
            print(f"  FAIL  [{c['family']}] {c['label']}: reference rejected -> {res.get('error')}")
            failures.append(c["label"]); continue
        got_dec = res["decision"]
        got_reasons = [r["code"] for r in res["reasons"]]
        got_hash = res["input_snapshot_hash"]
        dec_ok = got_dec == exp["decision"]
        reason_ok = got_reasons == exp["reason_codes"]
        hash_ok = got_hash == exp["input_snapshot_hash"]
        flag = "PASS" if (dec_ok and reason_ok and hash_ok) else "FAIL"
        print(f"  {flag}  [{c['family']}] {c['label']}")
        print(f"        decision {got_dec:<6} match={dec_ok}   reasons {got_reasons} match={reason_ok}")
        print(f"        hash     {got_hash[:24]}… match={hash_ok}")
        if flag == "FAIL":
            failures.append(c["label"])

    # Integrity-flip invariant: mutate prod-1 -> prod-2, hash MUST change.
    flip = kit.get("integrity_flip")
    if flip:
        base = next((c for c in kit["cases"]
                     if c["request"].get("target", {}).get("identifier") == "prod-1"), None)
        if base:
            mut = copy.deepcopy(base["request"]); mut["target"]["identifier"] = "prod-2"
            ok, res = poc.evaluate(mut)
            differs = ok and res["input_snapshot_hash"] != base["expect"]["input_snapshot_hash"]
            print(f"  {'PASS' if differs else 'FAIL'}  integrity-flip prod-1->prod-2 hash changes: {differs}")
            if not differs:
                failures.append("integrity_flip")

    print("\n" + "=" * 64)
    if failures:
        print(f"RESULT: {len(failures)} MISMATCH -> {failures}")
        return 1
    print("RESULT: every egress/authority case recomputed offline (decision + reasons + hash).")
    print("Boundary: production ruleset commit_sha is not publicly checkoutable; receipts are")
    print("          not issuer-signed. See verify/README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
