#!/usr/bin/env python3
"""
Quesen Domain Evaluation Matrix — independent, reproducible black-box validation.

This harness exercises ONLY Quesen's public HTTP surface with a self-served
sandbox key. It contains NO engine source and makes NO assumptions about
internals beyond what /version and /openapi.json publicly declare. Every
assertion is checked against the LIVE response.

Design goals (per the External Validation Program):
  * Evidence-driven: record expected vs actual for every case.
  * No threshold tuning to flatter results — we test the engine AS PUBLISHED.
  * Distinguish architecture limitations (input surface cannot express a domain)
    from implementation bugs (surface exists but behaves wrong).

Usage:
    QUESEN_BASE_URL=https://web-production-aa5ba.up.railway.app \
    python3 evaluation/domain_matrix.py            # self-serves a sandbox key
    # or provide your own:  QUESEN_API_KEY=sk_...  python3 evaluation/domain_matrix.py

Outputs:
    evaluation/results/latest.json   (full machine-readable evidence)
    stdout summary + non-zero exit code if any invariant fails.

Python 3.8+, standard library only.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

BASE = os.environ.get("QUESEN_BASE_URL", "https://web-production-aa5ba.up.railway.app").rstrip("/")
API_KEY = os.environ.get("QUESEN_API_KEY", "").strip()
TIMEOUT = float(os.environ.get("QUESEN_TIMEOUT", "30"))

# Sandbox tier is rate-limited to 30 calls/min. Pace keyed calls to ~1/2.1s and
# retry on 429 so the *engine* is measured, not the throttle.
RATE_MIN_INTERVAL = float(os.environ.get("QUESEN_RATE_INTERVAL", "2.15"))
_last_call = [0.0]


def _pace():
    dt = time.time() - _last_call[0]
    if dt < RATE_MIN_INTERVAL:
        time.sleep(RATE_MIN_INTERVAL - dt)
    _last_call[0] = time.time()

# ----------------------------------------------------------------------------- HTTP


def _req(method, path, body=None, headers=None, timeout=TIMEOUT):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            code = r.getcode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        code = e.code
    except Exception as e:  # network / timeout
        return {"status": 0, "error": str(e), "ms": round((time.time() - t0) * 1000)}
    dt = round((time.time() - t0) * 1000)
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = raw
    return {"status": code, "json": parsed, "ms": dt}


def _keyed_post(path, payload, key):
    """Paced POST with 429 backoff so rate-limiting never masquerades as a finding."""
    for attempt in range(4):
        _pace()
        r = _req("POST", path, payload, {"X-API-Key": key if key is not None else API_KEY})
        if r.get("status") != 429:
            return r
        time.sleep(4 + attempt * 3)
    return r


def validate(payload, key=None):
    return _keyed_post("/validate", payload, key)


def simulate(payload, key=None):
    return _keyed_post("/simulate", payload, key)


def report(payload, key=None):
    return _keyed_post("/report", payload, key)


# ----------------------------------------------------------------------------- results

RESULTS = {
    "meta": {
        "base_url": BASE,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "harness": "domain_matrix.py",
    },
    "engine": {},
    "suites": {},
}
FAILURES = []


def record(suite, name, passed, expected, actual, note=""):
    RESULTS["suites"].setdefault(suite, {"cases": [], "passed": 0, "failed": 0})
    entry = {"case": name, "passed": bool(passed), "expected": expected, "actual": actual, "note": note}
    RESULTS["suites"][suite]["cases"].append(entry)
    RESULTS["suites"][suite]["passed" if passed else "failed"] += 1
    if not passed:
        FAILURES.append(f"[{suite}] {name}: expected={expected} actual={actual} {note}")
    flag = "PASS" if passed else "FAIL"
    print(f"  {flag}  {suite}/{name}  (exp {expected} | got {actual}) {note}")


# ----------------------------------------------------------------------------- setup


def bootstrap_key():
    global API_KEY
    if API_KEY:
        print(f"Using provided API key ...{API_KEY[-6:]}")
        return
    r = _req("POST", "/sandbox/keys", {})
    if r.get("status") == 200 and isinstance(r.get("json"), dict):
        API_KEY = r["json"]["api_key"]
        print(f"Self-served sandbox key ...{API_KEY[-6:]} (credits={r['json'].get('starter_credits')})")
    else:
        raise SystemExit(f"Could not obtain sandbox key: {r}")


def load_engine():
    v = _req("GET", "/version")
    RESULTS["engine"] = v.get("json", {})
    th = RESULTS["engine"].get("thresholds", {})
    print(f"Engine {RESULTS['engine'].get('engine_version')} thresholds={th} weights={RESULTS['engine'].get('weights')}")
    return th


# ----------------------------------------------------------------------------- SUITES

def suite_determinism():
    print("\n== SUITE: determinism (same input -> same decision + snapshot hash) ==")
    inputs = [
        {"domain_age_days": 1, "engagement_ratio": 0.95, "scam_keyword_count": 4},
        {"domain_age_days": 400, "engagement_ratio": 0.05, "scam_keyword_count": 0},
        {"domain_age_days": 30, "engagement_ratio": 0.5, "scam_keyword_count": 1},
        {"domain_age_days": 7, "engagement_ratio": 0.8, "scam_keyword_count": 2},
    ]
    for i, payload in enumerate(inputs):
        seen = []
        for _ in range(3):
            r = validate(payload)
            j = r.get("json", {})
            seen.append((j.get("decision"), j.get("risk_score"), j.get("input_snapshot_hash")))
            time.sleep(0.05)
        uniq = set(seen)
        record("determinism", f"input_{i}", len(uniq) == 1, "1 unique result over 5 calls",
               f"{len(uniq)} unique", note=f"{payload} -> {seen[0]}")


def suite_thresholds(thresholds):
    print("\n== SUITE: threshold_mapping (decision must match published thresholds) ==")
    skip_t = thresholds.get("skip", 0.65)
    review_t = thresholds.get("review", 0.35)
    # sweep a spread of inputs to obtain a range of risk scores
    grid = []
    for d in (1, 15, 120, 400):
        for e in (0.05, 0.5, 0.95):
            for s in (0, 2, 6):
                grid.append({"domain_age_days": d, "engagement_ratio": e, "scam_keyword_count": s})
    checked = 0
    consistent = 0
    samples = []
    for payload in grid[:24]:  # cap calls (rate budget)
        r = validate(payload)
        j = r.get("json", {})
        rs = j.get("risk_score")
        dec = j.get("decision")
        if rs is None or dec is None:
            continue
        expected = "SKIP" if rs >= skip_t else ("REVIEW" if rs >= review_t else "PROCEED")
        checked += 1
        if dec == expected:
            consistent += 1
        else:
            samples.append({"payload": payload, "risk_score": rs, "decision": dec, "expected": expected})
    record("threshold_mapping", "decision_matches_thresholds", consistent == checked,
           f"{checked}/{checked} consistent", f"{consistent}/{checked} consistent",
           note=("mismatches: " + json.dumps(samples[:3])) if samples else "all consistent")


def _score(payload):
    r = validate(payload)
    return r.get("json", {}).get("risk_score")


def suite_monotonicity():
    print("\n== SUITE: monotonicity (risk must move in a consistent direction) ==")
    # more scam keywords -> risk should not decrease
    base = {"domain_age_days": 30, "engagement_ratio": 0.5}
    seq = [_score({**base, "scam_keyword_count": s}) for s in (0, 1, 2, 4, 8)]
    seq = [x for x in seq if x is not None]
    nondec = len(seq) >= 4 and all(seq[i] <= seq[i + 1] + 1e-9 for i in range(len(seq) - 1))
    record("monotonicity", "scam_keywords_nondecreasing", nondec, "risk non-decreasing (>=4 samples)", seq)
    # younger domain -> risk should not decrease (age descending)
    base2 = {"engagement_ratio": 0.5, "scam_keyword_count": 1}
    seq2 = [_score({**base2, "domain_age_days": d}) for d in (400, 120, 45, 15, 5, 1)]
    seq2 = [x for x in seq2 if x is not None]
    nondec2 = len(seq2) >= 4 and all(seq2[i] <= seq2[i + 1] + 1e-9 for i in range(len(seq2) - 1))
    record("monotonicity", "younger_domain_nondecreasing", nondec2, "risk non-decreasing as domain gets younger (>=4 samples)", seq2)
    # higher engagement on a young domain -> risk should not decrease
    base3 = {"domain_age_days": 3, "scam_keyword_count": 1}
    seq3 = [_score({**base3, "engagement_ratio": e}) for e in (0.02, 0.2, 0.5, 0.8, 0.99)]
    seq3 = [x for x in seq3 if x is not None]
    nondec3 = len(seq3) >= 4 and all(seq3[i] <= seq3[i + 1] + 1e-9 for i in range(len(seq3) - 1))
    record("monotonicity", "higher_engagement_nondecreasing", nondec3, "risk non-decreasing with engagement (>=4 samples)", seq3)


def suite_input_validation():
    print("\n== SUITE: input_validation / adversarial input (must reject or handle gracefully; never 500) ==")
    cases = [
        ("engagement_gt_1", {"engagement_ratio": 1.5}, [422]),
        ("negative_domain_age", {"domain_age_days": -1}, [422]),
        ("negative_scam", {"scam_keyword_count": -5}, [422]),
        ("wrong_type_string", {"domain_age_days": "abc"}, [422]),
        ("huge_number", {"domain_age_days": 10 ** 12, "engagement_ratio": 0.5, "scam_keyword_count": 1}, [200, 422]),
        ("empty_body", {}, [200, 422]),
        ("injection_in_trace_id", {"domain_age_days": 1, "engagement_ratio": 0.9, "scam_keyword_count": 3,
                                    "client_request_id": "'><script>alert(1)</script> OR 1=1; DROP TABLE keys;--"}, [200, 422]),
        ("unknown_extra_field", {"domain_age_days": 1, "engagement_ratio": 0.5, "scam_keyword_count": 0, "evil": {"$ne": None}}, [200, 422]),
    ]
    for name, payload, ok_codes in cases:
        r = validate(payload)
        code = r.get("status")
        passed = code in ok_codes and code != 500 and code != 0
        record("input_validation", name, passed, f"status in {ok_codes}", code,
               note=("SAFE echo" if name == "injection_in_trace_id" and code == 200 else ""))


def suite_auth_boundary():
    print("\n== SUITE: auth_boundary (security posture) ==")
    r1 = _req("POST", "/validate", {"domain_age_days": 1, "engagement_ratio": 0.5, "scam_keyword_count": 0}, {})
    record("auth_boundary", "no_key_rejected", r1.get("status") in (401, 403), "401/403", r1.get("status"))
    r2 = validate({"domain_age_days": 1, "engagement_ratio": 0.5, "scam_keyword_count": 0}, key="sk_not_a_real_key")
    record("auth_boundary", "bad_key_rejected", r2.get("status") in (401, 403), "401/403", r2.get("status"))
    r3 = _req("GET", "/stats", None, {"X-API-Key": API_KEY})
    record("auth_boundary", "sandbox_key_denied_admin_stats", r3.get("status") in (401, 403), "401/403 on admin", r3.get("status"))


def suite_simulate():
    print("\n== SUITE: simulate (counterfactual; must not mutate engine state) ==")
    before = _req("GET", "/version").get("json", {}).get("weights")
    payload = {"domain_age_days": 5, "engagement_ratio": 0.9, "scam_keyword_count": 2,
               "thresholds_override": {"skip": 0.1, "review": 0.05}}
    r = simulate(payload)
    j = r.get("json", {})
    ok = r.get("status") == 200
    record("simulate", "override_returns_200", ok, "200", r.get("status"), note=json.dumps(j)[:200] if ok else str(j)[:200])
    after = _req("GET", "/version").get("json", {}).get("weights")
    record("simulate", "no_state_mutation", before == after, "engine weights unchanged", f"before={before} after={after}")


def suite_report():
    print("\n== SUITE: report (post-decision feedback) ==")
    v = validate({"domain_age_days": 2, "engagement_ratio": 0.9, "scam_keyword_count": 3})
    rid = v.get("json", {}).get("request_id")
    if rid:
        good = report({"request_id": rid, "outcome": "OK"})
        record("report", "valid_outcome_accepted", good.get("status") in (200, 201, 202), "2xx", good.get("status"))
    else:
        record("report", "valid_outcome_accepted", False, "had a request_id", "no request_id from /validate")
    bad = report({"request_id": rid or "x", "outcome": "TOTALLY_INVALID"})
    record("report", "invalid_outcome_rejected", bad.get("status") == 422, "422", bad.get("status"))


def suite_onchain():
    print("\n== SUITE: onchain_enrichment (optional external probes; graceful) ==")
    # USDC on Ethereum — a long-lived, verified, widely-held contract.
    usdc = {"domain_age_days": 200, "engagement_ratio": 0.1, "scam_keyword_count": 0,
            "chain": "ethereum", "contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"}
    r = validate(usdc)
    j = r.get("json", {}) if r.get("status") == 200 else {}
    enr = j.get("onchain_enrichment")
    record("onchain_enrichment", "verified_contract_enriches", r.get("status") == 200,
           "200 with onchain_enrichment present", f"status={r.get('status')} enrichment={'yes' if enr else 'no/none'}",
           note=(json.dumps(enr)[:220] if enr else ""))
    # Garbage contract address — must not 500.
    junk = {"domain_age_days": 1, "engagement_ratio": 0.9, "scam_keyword_count": 4,
            "chain": "ethereum", "contract_address": "0x000000000000000000000000000000000000dEaD"}
    r2 = validate(junk)
    record("onchain_enrichment", "junk_contract_graceful", r2.get("status") in (200, 422), "200/422 not 500", r2.get("status"))


# ----------------------------------------------------------------------------- main


def main():
    print(f"Quesen Domain Evaluation Matrix -> {BASE}")
    bootstrap_key()
    thresholds = load_engine()
    suite_determinism()
    suite_thresholds(thresholds)
    suite_monotonicity()
    suite_input_validation()
    suite_auth_boundary()
    suite_simulate()
    suite_report()
    try:
        suite_onchain()
    except Exception as e:
        record("onchain_enrichment", "suite_ran", False, "no exception", f"exception: {e}")

    total_pass = sum(s["passed"] for s in RESULTS["suites"].values())
    total_fail = sum(s["failed"] for s in RESULTS["suites"].values())
    RESULTS["meta"]["finished_at"] = datetime.now(timezone.utc).isoformat()
    RESULTS["meta"]["totals"] = {"passed": total_pass, "failed": total_fail}
    RESULTS["meta"]["failures"] = FAILURES

    out = os.path.join(os.path.dirname(__file__), "results", "latest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(RESULTS, f, indent=2)

    print("\n" + "=" * 64)
    print(f"TOTAL: {total_pass} passed, {total_fail} failed")
    if FAILURES:
        print("FAILURES / FINDINGS:")
        for x in FAILURES:
            print("  -", x)
    print(f"Evidence written to {out}")
    print("=" * 64)
    raise SystemExit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
