#!/usr/bin/env python3
"""
TSC v2 Reference POC  ·  Quesen Typed Security Context Contract (P1, design-only)
================================================================================

This is a REFERENCE harness that proves the P1 contract is implementable and
DETERMINISTIC. It is NOT the production engine and imports NO engine source.
It lives in the PUBLIC repo so any integrator (in any language) can reproduce
the canonicalization, normalization, validation, and decision semantics.

It proves four things and exits non-zero if any fails:

  1. DETERMINISM            same context  -> identical canonical JSON, hash, verdict
  2. NORMALIZATION-EQUIV    semantically-equal contexts (casing/whitespace/order/
                            duplicates) -> identical canonical JSON, hash, verdict
  3. TYPED VALIDATION       malformed contexts -> stable typed errors, never a crash
  4. SECURITY INVARIANTS    - unattested client-asserted grants cannot force PASS
                              on a sensitive action
                            - credential/secret egress to an unverified destination
                              is BLOCKed
                            - untrusted text (action.intent / injection patterns)
                              is never interpreted as policy
                            - unknown top-level fields are rejected, not ignored

Python 3.8+, standard library only.
"""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from typing import Any, Dict, List, Tuple

# --------------------------------------------------------------------------- #
# Error taxonomy (mirrors docs/security-context/04-validation-errors.md)
# --------------------------------------------------------------------------- #

class TscError(Exception):
    def __init__(self, code: str, message: str, pointer: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.pointer = pointer

    def as_dict(self) -> Dict[str, str]:
        return {"code": self.code, "message": self.message, "pointer": self.pointer}


ENUMS = {
    "subject.kind": {"agent", "human", "service", "unknown"},
    "subject.framework": {"langchain", "crewai", "autogen", "ag2", "mcp",
                          "openai_assistants", "raw", "other", "unknown"},
    "trust_tier": {"trusted", "verified", "unverified", "unknown"},
    "action.kind": {"tool_call", "http_request", "data_read", "data_write",
                    "data_egress", "message_post", "payment", "code_exec",
                    "file_access", "other"},
    "target.kind": {"endpoint", "domain", "contract", "account", "file",
                    "dataset", "recipient", "tool", "service", "other", "unknown"},
    "tool.capability_class": {"read", "write", "network", "exec", "financial",
                              "admin", "comms", "filesystem", "other"},
    "data.class": {"public", "internal", "confidential", "pii", "financial",
                   "credential", "secret", "regulated", "unknown"},
    "provenance.source": {"client_asserted", "adapter_derived", "engine_derived",
                          "trusted_metadata"},
    "attestation.method": {"none", "signed", "oauth_introspection", "mtls"},
}

TOP_LEVEL_KEYS = {"tsc_version", "policy", "subject", "action", "target", "tool",
                  "permissions", "data", "signals", "provenance", "client_request_id"}

SENSITIVE_ACTIONS = {"payment", "code_exec", "data_egress", "data_write", "file_access"}
SENSITIVE_CAPABILITIES = {"financial", "admin", "exec", "write", "filesystem"}
HIGH_SENSITIVITY_DATA = {"credential", "secret", "pii", "financial", "regulated"}

MAX_INTENT_LEN = 2000


# --------------------------------------------------------------------------- #
# 1. Normalization  (deterministic, side-effect-free, never executes text)
# --------------------------------------------------------------------------- #

def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def _norm_enum(value: Any, name: str, pointer: str) -> str:
    if not isinstance(value, str):
        raise TscError("invalid_type", f"{name} must be a string", pointer)
    v = _nfc(value).strip().lower()
    if v not in ENUMS[name]:
        raise TscError("invalid_enum", f"{name}={value!r} not in {sorted(ENUMS[name])}", pointer)
    return v

def _norm_str(value: Any, pointer: str, max_len: int) -> str:
    if not isinstance(value, str):
        raise TscError("invalid_type", f"expected string at {pointer}", pointer)
    v = _nfc(value).strip()
    if len(v) > max_len:
        raise TscError("oversized", f"string at {pointer} exceeds {max_len} chars", pointer)
    return v

def _norm_domain(value: Any, pointer: str) -> str:
    v = _norm_str(value, pointer, 253).lower().rstrip(".")
    return v

def _norm_str_list(value: Any, pointer: str, name: str = None) -> List[str]:
    if not isinstance(value, list):
        raise TscError("invalid_type", f"expected list at {pointer}", pointer)
    out = set()
    for i, item in enumerate(value):
        if name:  # enum list (e.g. data.classes)
            out.add(_norm_enum(item, name, f"{pointer}[{i}]"))
        else:
            out.add(_norm_str(item, f"{pointer}[{i}]", 128).lower())
    # dedupe + sort => order-insensitive canonical form
    return sorted(out)

def _norm_int(value: Any, pointer: str, minimum: int = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TscError("invalid_type", f"expected integer at {pointer}", pointer)
    if minimum is not None and value < minimum:
        raise TscError("out_of_range", f"{pointer} must be >= {minimum}", pointer)
    return value

def _norm_float(value: Any, pointer: str, lo: float, hi: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TscError("invalid_type", f"expected number at {pointer}", pointer)
    f = float(value)
    if not (lo <= f <= hi):
        raise TscError("out_of_range", f"{pointer} must be in [{lo},{hi}]", pointer)
    return f

def _obj(value: Any, pointer: str, allowed: set) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TscError("invalid_type", f"expected object at {pointer}", pointer)
    unknown = set(value) - allowed
    if unknown:
        raise TscError("unknown_field", f"unknown field(s) {sorted(unknown)} at {pointer}", pointer)
    return value


def normalize(ctx: Any) -> Dict[str, Any]:
    """Return a normalized, validated context. Raises TscError on any problem.
    Normalization NEVER interprets free text as instructions - it only trims,
    NFC-folds, lowercases enums/domains, and canonicalizes list ordering."""
    if not isinstance(ctx, dict):
        raise TscError("malformed", "context must be a JSON object", "/")

    _obj(ctx, "/", TOP_LEVEL_KEYS)

    # ---- version (required, selects v2) ----
    tv = ctx.get("tsc_version")
    if tv is None:
        raise TscError("unsupported_version", "tsc_version required for v2 pipeline", "/tsc_version")
    tv = _norm_str(tv, "/tsc_version", 16)
    if not tv.startswith("2."):
        raise TscError("unsupported_version", f"unsupported tsc_version {tv!r}", "/tsc_version")

    out: Dict[str, Any] = {"tsc_version": tv}

    # ---- subject (required) ----
    if "subject" not in ctx:
        raise TscError("missing_required", "subject is required", "/subject")
    s = _obj(ctx["subject"], "/subject", {"id", "kind", "framework", "trust_tier"})
    subj = {"kind": _norm_enum(s.get("kind", "unknown"), "subject.kind", "/subject/kind")}
    if "id" in s: subj["id"] = _norm_str(s["id"], "/subject/id", 256)
    if "framework" in s: subj["framework"] = _norm_enum(s["framework"], "subject.framework", "/subject/framework")
    subj["trust_tier"] = _norm_enum(s.get("trust_tier", "unknown"), "trust_tier", "/subject/trust_tier")
    out["subject"] = subj

    # ---- action (required) ----
    if "action" not in ctx:
        raise TscError("missing_required", "action is required", "/action")
    a = _obj(ctx["action"], "/action", {"kind", "operation", "intent"})
    act = {"kind": _norm_enum(a.get("kind", "other"), "action.kind", "/action/kind")}
    if "operation" in a: act["operation"] = _norm_str(a["operation"], "/action/operation", 128)
    if "intent" in a:
        # intent is DATA. We bound + fold it but NEVER act on its content.
        act["intent"] = _norm_str(a["intent"], "/action/intent", MAX_INTENT_LEN)
    out["action"] = act

    # ---- provenance (required) ----
    if "provenance" not in ctx:
        raise TscError("missing_required", "provenance is required", "/provenance")
    p = _obj(ctx["provenance"], "/provenance", {"source", "as_of", "attestation", "evidence_refs"})
    prov = {"source": _norm_enum(p.get("source", "client_asserted"), "provenance.source", "/provenance/source")}
    if "as_of" in p: prov["as_of"] = _norm_str(p["as_of"], "/provenance/as_of", 40)
    if "attestation" in p:
        at = _obj(p["attestation"], "/provenance/attestation", {"method", "verified"})
        att = {"method": _norm_enum(at.get("method", "none"), "attestation.method", "/provenance/attestation/method")}
        ver = at.get("verified", False)
        if not isinstance(ver, bool):
            raise TscError("invalid_type", "attestation.verified must be boolean", "/provenance/attestation/verified")
        att["verified"] = ver
        prov["attestation"] = att
    if "evidence_refs" in p:
        prov["evidence_refs"] = _norm_str_list(p["evidence_refs"], "/provenance/evidence_refs")
    out["provenance"] = prov

    # ---- optional blocks ----
    if "policy" in ctx:
        pol = _obj(ctx["policy"], "/policy", {"id", "version"})
        o = {}
        if "id" in pol: o["id"] = _norm_str(pol["id"], "/policy/id", 128)
        if "version" in pol: o["version"] = _norm_str(pol["version"], "/policy/version", 32)
        out["policy"] = o

    if "target" in ctx:
        t = _obj(ctx["target"], "/target", {"kind", "identifier", "domain", "trust_tier"})
        o = {}
        if "kind" in t: o["kind"] = _norm_enum(t["kind"], "target.kind", "/target/kind")
        if "identifier" in t: o["identifier"] = _norm_str(t["identifier"], "/target/identifier", 512)
        if "domain" in t: o["domain"] = _norm_domain(t["domain"], "/target/domain")
        o["trust_tier"] = _norm_enum(t.get("trust_tier", "unknown"), "trust_tier", "/target/trust_tier")
        out["target"] = o

    if "tool" in ctx:
        tl = _obj(ctx["tool"], "/tool", {"id", "capability_class", "requested_scopes", "granted_scopes"})
        o = {}
        if "id" in tl: o["id"] = _norm_str(tl["id"], "/tool/id", 256)
        if "capability_class" in tl:
            o["capability_class"] = _norm_enum(tl["capability_class"], "tool.capability_class", "/tool/capability_class")
        if "requested_scopes" in tl:
            o["requested_scopes"] = _norm_str_list(tl["requested_scopes"], "/tool/requested_scopes")
        if "granted_scopes" in tl:
            o["granted_scopes"] = _norm_str_list(tl["granted_scopes"], "/tool/granted_scopes")
        out["tool"] = o

    if "permissions" in ctx:
        pm = _obj(ctx["permissions"], "/permissions", {"requested", "granted", "policy_required"})
        o = {}
        for fld in ("requested", "granted", "policy_required"):
            if fld in pm:
                o[fld] = _norm_str_list(pm[fld], f"/permissions/{fld}")
        out["permissions"] = o

    if "data" in ctx:
        d = _obj(ctx["data"], "/data", {"classes", "egress"})
        o = {}
        if "classes" in d:
            o["classes"] = _norm_str_list(d["classes"], "/data/classes", name="data.class")
        if "egress" in d:
            eg = _obj(d["egress"], "/data/egress", {"to", "destination_trust"})
            e = {}
            if "to" in eg: e["to"] = _norm_str(eg["to"], "/data/egress/to", 512)
            e["destination_trust"] = _norm_enum(eg.get("destination_trust", "unknown"), "trust_tier", "/data/egress/destination_trust")
            o["egress"] = e
        out["data"] = o

    if "signals" in ctx:
        sg = _obj(ctx["signals"], "/signals",
                  {"prompt_injection", "domain_age_days", "engagement_ratio", "scam_keyword_count", "onchain"})
        o = {}
        if "prompt_injection" in sg:
            pi = _obj(sg["prompt_injection"], "/signals/prompt_injection", {"suspected", "patterns", "sample_ref"})
            po = {}
            if "suspected" in pi:
                if not isinstance(pi["suspected"], bool):
                    raise TscError("invalid_type", "prompt_injection.suspected must be boolean", "/signals/prompt_injection/suspected")
                po["suspected"] = pi["suspected"]
            if "patterns" in pi:
                # patterns are detector LABELS (data), never executed
                po["patterns"] = _norm_str_list(pi["patterns"], "/signals/prompt_injection/patterns")
            if "sample_ref" in pi:
                po["sample_ref"] = _norm_str(pi["sample_ref"], "/signals/prompt_injection/sample_ref", 128)
            o["prompt_injection"] = po
        if "domain_age_days" in sg: o["domain_age_days"] = _norm_int(sg["domain_age_days"], "/signals/domain_age_days", 0)
        if "engagement_ratio" in sg: o["engagement_ratio"] = _norm_float(sg["engagement_ratio"], "/signals/engagement_ratio", 0.0, 1.0)
        if "scam_keyword_count" in sg: o["scam_keyword_count"] = _norm_int(sg["scam_keyword_count"], "/signals/scam_keyword_count", 0)
        if "onchain" in sg:
            if not isinstance(sg["onchain"], dict):
                raise TscError("invalid_type", "signals.onchain must be an object", "/signals/onchain")
            o["onchain"] = sg["onchain"]
        out["signals"] = o

    if "client_request_id" in ctx:
        out["client_request_id"] = _norm_str(ctx["client_request_id"], "/client_request_id", 128)

    return out


# --------------------------------------------------------------------------- #
# 2. Canonicalization + hashing  (RFC-8785-compatible JCS subset)
# --------------------------------------------------------------------------- #

def canonical_json(obj: Dict[str, Any], *, for_hash: bool = False) -> str:
    material = obj
    if for_hash:
        # client_request_id excluded from hash material (parity with ADR-041)
        material = {k: v for k, v in obj.items() if k != "client_request_id"}
    return json.dumps(material, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)

def input_snapshot_hash(normalized: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(normalized, for_hash=True).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# 3. Reference decision function  (deterministic, illustrative, NOT production)
# --------------------------------------------------------------------------- #

def decide(n: Dict[str, Any]) -> Dict[str, Any]:
    """Reference decision. Pure function of the normalized context.
    Demonstrates the PASS / REVIEW / BLOCK / SKIP semantics + invariants.
    Production weighting stays in the sovereign engine; this is a contract demo."""
    reasons: List[Dict[str, str]] = []
    tags: List[str] = []

    action_kind = n["action"]["kind"]
    prov = n["provenance"]
    attested = bool(prov.get("attestation", {}).get("verified")) or prov["source"] in ("engine_derived", "trusted_metadata")

    data = n.get("data", {})
    classes = set(data.get("classes", []))
    egress = data.get("egress", {})
    dest_trust = egress.get("destination_trust", "unknown")

    cap = n.get("tool", {}).get("capability_class")
    sensitive = (action_kind in SENSITIVE_ACTIONS) or (cap in SENSITIVE_CAPABILITIES)

    granted = set(n.get("permissions", {}).get("granted", [])) | set(n.get("tool", {}).get("granted_scopes", []))
    required = set(n.get("permissions", {}).get("policy_required", []))

    # ---- Hard-deny invariant: high-sensitivity data leaving to an untrusted dest ----
    leaking = (classes & {"credential", "secret"}) and action_kind in ("data_egress", "message_post", "http_request")
    if leaking and dest_trust in ("unverified", "unknown"):
        reasons.append({"code": "EGRESS_SECRET_UNTRUSTED", "severity": "critical",
                        "message": "credential/secret egress to an unverified destination"})
        return _verdict("BLOCK", 1.0, _confidence(n), reasons, tags + ["exfiltration"], n)

    # ---- Privilege mismatch: policy requires scopes the caller does not (verifiably) hold ----
    if required:
        missing = required - (granted if attested else set())
        if missing:
            reasons.append({"code": "PRIVILEGE_MISMATCH", "severity": "high",
                            "message": f"missing/unverified required scope(s): {sorted(missing)}"})
            return _verdict("BLOCK" if sensitive else "REVIEW",
                            0.85 if sensitive else 0.5, _confidence(n), reasons, tags + ["authz"], n)

    # ---- Provenance invariant: unattested client grants cannot upgrade a sensitive action to PASS ----
    if sensitive and granted and not attested:
        reasons.append({"code": "UNVERIFIED_GRANT", "severity": "medium",
                        "message": "authorization claimed by unattested client; cannot be trusted to PASS a sensitive action"})
        return _verdict("REVIEW", 0.5, _confidence(n), reasons, tags + ["authz", "provenance"], n)

    # ---- Prompt-injection FINDINGS (data about text, never executed) ----
    pi = n.get("signals", {}).get("prompt_injection", {})
    if pi.get("suspected"):
        sev = "high" if sensitive else "medium"
        reasons.append({"code": "PROMPT_INJECTION_SUSPECTED", "severity": sev,
                        "message": f"injection findings: {pi.get('patterns', [])}"})
        return _verdict("REVIEW", 0.6, _confidence(n), reasons, tags + ["prompt_injection"], n)

    # ---- PII egress to unverified destination -> REVIEW ----
    if (classes & {"pii", "financial", "regulated"}) and action_kind in ("data_egress", "http_request", "message_post") \
            and dest_trust in ("unverified", "unknown"):
        reasons.append({"code": "PII_EGRESS_REVIEW", "severity": "medium",
                        "message": "sensitive data class egress to a non-trusted destination"})
        return _verdict("REVIEW", 0.55, _confidence(n), reasons, tags + ["data_egress"], n)

    # ---- SKIP: not enough typed context to render a supported verdict (honesty > guessing) ----
    if action_kind == "other" and not n.get("target") and not n.get("tool") and not n.get("data") and not n.get("signals"):
        reasons.append({"code": "INSUFFICIENT_CONTEXT", "severity": "info",
                        "message": "no target/tool/data/signals to reason over; engine declines to rule"})
        return _verdict("SKIP", 0.0, _confidence(n), reasons, tags, n)

    reasons.append({"code": "NO_ADVERSE_SIGNAL", "severity": "info", "message": "no policy-relevant risk pattern matched"})
    return _verdict("PASS", 0.1, _confidence(n), reasons, tags, n)


def _confidence(n: Dict[str, Any]) -> float:
    present = sum(1 for k in ("subject", "action", "target", "tool", "permissions", "data", "signals") if n.get(k))
    return round(present / 7.0, 4)

def _verdict(decision, risk, confidence, reasons, tags, n) -> Dict[str, Any]:
    return {
        "tsc_version": n["tsc_version"],
        "decision": decision,
        "risk_score": round(float(risk), 4),
        "confidence": confidence,
        "reasons": reasons,
        "tags": sorted(set(tags)),
        "policy": n.get("policy", {}),
        "provenance_summary": {
            "source": n["provenance"]["source"],
            "attested": bool(n["provenance"].get("attestation", {}).get("verified"))
                        or n["provenance"]["source"] in ("engine_derived", "trusted_metadata"),
        },
        "input_snapshot_hash": input_snapshot_hash(n),
        "engine_version": "poc-ref-0",
    }


def evaluate(ctx: Any) -> Tuple[bool, Dict[str, Any]]:
    """Returns (ok, result). ok=False => result is a typed error envelope."""
    try:
        n = normalize(ctx)
    except TscError as e:
        return False, {"error": e.as_dict()}
    return True, decide(n)


# --------------------------------------------------------------------------- #
# Self-test harness
# --------------------------------------------------------------------------- #

def _load_fixtures() -> Dict[str, Any]:
    import os
    path = os.path.join(os.path.dirname(__file__), "fixtures", "tsc_v2_fixtures.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    fx = _load_fixtures()
    failures: List[str] = []

    def check(name, cond, detail=""):
        flag = "PASS" if cond else "FAIL"
        print(f"  {flag}  {name}  {detail}")
        if not cond:
            failures.append(name)

    print("== 1. DETERMINISM ==")
    base = fx["valid_tool_call"]
    ok, r1 = evaluate(base); _, r2 = evaluate(json.loads(json.dumps(base)))
    check("same_input_same_hash", ok and r1["input_snapshot_hash"] == r2["input_snapshot_hash"],
          f"hash={r1.get('input_snapshot_hash','')[:12]}...")
    check("same_input_same_decision", r1["decision"] == r2["decision"], f"decision={r1['decision']}")

    print("\n== 2. NORMALIZATION-EQUIVALENCE ==")
    a_ok, ra = evaluate(fx["equiv_a"]); b_ok, rb = evaluate(fx["equiv_b"])
    check("equiv_inputs_same_hash", a_ok and b_ok and ra["input_snapshot_hash"] == rb["input_snapshot_hash"],
          f"a={ra.get('input_snapshot_hash','')[:12]} b={rb.get('input_snapshot_hash','')[:12]}")
    check("equiv_inputs_same_decision", ra["decision"] == rb["decision"], f"{ra['decision']}=={rb['decision']}")

    print("\n== 3. TYPED VALIDATION (never crash) ==")
    for name, expect_code in fx["invalid_expected_codes"].items():
        ok, res = evaluate(fx["invalid"][name])
        got = res.get("error", {}).get("code")
        check(f"invalid::{name}", (not ok) and got == expect_code, f"expected={expect_code} got={got}")

    print("\n== 4. SECURITY INVARIANTS ==")
    _, r = evaluate(fx["inv_unverified_grant_payment"])
    check("unverified_grant_not_PASS", r["decision"] in ("REVIEW", "BLOCK"), f"decision={r['decision']}")
    _, r = evaluate(fx["inv_secret_egress_untrusted"])
    check("secret_egress_BLOCK", r["decision"] == "BLOCK", f"decision={r['decision']}")
    _, r = evaluate(fx["inv_attested_grant_pass"])
    check("attested_grant_can_PASS", r["decision"] == "PASS", f"decision={r['decision']}")
    _, r = evaluate(fx["inv_prompt_injection"])
    check("injection_findings_REVIEW", r["decision"] == "REVIEW" and "prompt_injection" in r["tags"],
          f"decision={r['decision']} tags={r['tags']}")
    # untrusted text must not change a benign verdict just by being long/hostile
    _, r_clean = evaluate(fx["inv_benign_readonly"])
    _, r_hostiletext = evaluate(fx["inv_benign_readonly_with_hostile_intent_text"])
    check("untrusted_text_not_policy", r_clean["decision"] == r_hostiletext["decision"] == "PASS",
          f"clean={r_clean['decision']} hostile_text={r_hostiletext['decision']}")

    print("\n" + "=" * 60)
    if failures:
        print(f"RESULT: {len(failures)} FAILED -> {failures}")
        return 1
    print("RESULT: ALL CHECKS PASSED - TSC v2 contract is deterministic + safe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
