# LoopX × Quesen — Prepared-Effect Risk-Admission Packet (Scenario 1)

Application packet requested in
[huangruiteng/loopx#3735](https://github.com/huangruiteng/loopx/discussions/3735).
**Not a code proposal.** It answers the eight packet questions against the
**prepared-Effect boundary** (after LoopX binds the exact Effect identity /
operation / scopes / provider revision / target classification / provenance /
canonical request digest, *before* the external provider performs the side
effect). Quesen is proposed as an **optional extension provider** for a
provider-neutral risk-admission contract, never as an authority source.

**Scenario chosen:** *Recurring governed internal report delivery* (the
maintainer's ranked #1 near-term fit).

**Accepted framing (no argument):**
- The **operator gate is human/owner authority**; Quesen must not manufacture or
  auto-approve it. `PASS` means *only* "no additional security objection" —
  execution still requires the existing LoopX decision scope, capability
  permission and provider binding.
- Not targeting the finance `BLOCKING_GATE_STATES` constant.
- The hosted call consumes a **typed, bounded envelope** only — never raw
  secrets, credentials, private documents, or command bodies.
- First step is **shadow mode**: persist the receipt bound to the prepared
  Effect, change nothing about execution, and measure against operator outcomes.

---

## 1. One exact LoopX operation and where its prepared Effect is formed

Operation: **scheduled periodic-report delivery** — LoopX assembles a report
from governed internal sources, applies its public/private projection boundary,
and delivers it to a bound connector (Lark/Slack-style).

Prepared-Effect formation point: the Turn where LoopX has already frozen the
generation + approval receipts and **bound the destination connector**, i.e. the
moment the Effect envelope (Todo/Turn/Effect id, operation, requested + granted
scopes, provider revision, target classification, provenance, canonical request
digest) exists but the provider `deliver()` has **not** been called. The
risk-admission call is inserted on that edge.

## 2. Field-by-field mapping: LoopX Effect envelope → TscContext

| LoopX prepared-Effect field | Quesen `TscContext` field | Notes |
|---|---|---|
| Effect id / Turn id / Todo id | `subject.id` (+ echoed in `client_request_id`, excluded from hash) | trace only; excluded from `input_snapshot_hash` |
| acting service identity | `subject.kind=service`, `subject.trust_tier` | |
| operation (deliver_report) | `action.kind` (`message_post` \| `data_egress`), `action.operation` | egress vs post per connector class |
| target classification | `data.classes[]` (`internal`/`pii`/`credential`/…) | from LoopX projection boundary, **labels not content** |
| destination binding | `target.kind=recipient`, `target.trust_tier`; `data.egress.to`, `data.egress.destination_trust` | trust derived from the exact connector binding |
| requested send scopes | `tool.granted_scopes` / `permissions.requested` | provider profile |
| standing/decision authority | `permissions.granted` | LoopX standing decision |
| provenance (frozen gen+approval receipts) | `provenance.source` (`trusted_metadata`/`adapter_derived`/…) + `provenance.attestation.verified` | |
| provider revision | carried in `provenance` metadata / `tool.id` | version drift → weaker tier |
| canonical request digest | reconciled against Quesen's `input_snapshot_hash` | see §7 |

**Privacy:** every mapped field is a **label, identifier, class, scope or trust
tier** — never report content. LoopX keeps the payload.

## 3. Three fixtures (PASS / REVIEW / BLOCK) with expected reason codes

Generated **live** against `POST /tsc/validate` (`tsc_version 2.0`), ruleset
`commit_sha 0095b6183a796ce678086a77e17de6eef9c6a263`. Full requests + receipts:
[`fixtures/loopx_prepared_effect_fixtures.json`](fixtures/loopx_prepared_effect_fixtures.json).

| Case | Envelope | Decision | Reason code | `input_snapshot_hash` |
|---|---|---|---|---|
| Routine safe path | `internal` summary → bound **trusted** channel, standing authority attested | `PASS` | `NO_ADVERSE_SIGNAL` | `daab6d22…` |
| Meaningful ambiguity | report carries `pii` → **newly selected unverified** channel, send-authority `adapter_derived` (unattested) | `REVIEW` | `UNVERIFIED_GRANT` | `60ba7fc3…` |
| Catastrophic backstop | `credential`+`secret` → **unverified** destination | `BLOCK` | `EGRESS_SECRET_UNTRUSTED` | `90f67cc4…` |

## 4. The human gate PASS removes, and the gates that remain

- **Removed by PASS:** the *repeated technical security-review prompt* on each
  scheduled run whose envelope is unchanged (same trusted channel, same standing
  authority, public-safe/internal class).
- **Explicitly remain (never touched by Quesen):** semantic/content approval of
  the report; production/publication/write authority; the standing LoopX
  decision scope; capability permission; provider binding; payments; merge/
  release; credential grants. `PASS` is a security no-objection, not authority.

## 5. Failure semantics

Fail **closed** to the existing human gate in every abnormal case:

| Condition | Admission result |
|---|---|
| `REVIEW` / `SKIP` | keep/create the human gate; attach receipt as evidence |
| timeout / provider unavailable | treat as `REVIEW` (fail closed) |
| provider/engine version drift (`commit_sha` ≠ pinned) | `REVIEW` + flag `ruleset_drift` |
| unknown ruleset / unverifiable receipt | `REVIEW`, do not admit on it |
| malformed / schema-invalid response | `REVIEW`; log raw for triage |

Only an explicit, schema-valid `PASS` on the **pinned** ruleset deflects the
extra prompt. Everything else routes to a human.

## 6. Privacy / data-retention boundaries for the hosted call

- Request = typed envelope only (labels, ids, classes, scopes, trust tiers). No
  report content, no secrets, no command bodies.
- Recommended retention: store only the **compact receipt**
  (`decision, reasons[], commit_sha, input_snapshot_hash, request_id`) on the
  LoopX side, bound to the Effect id. The hosted service can be run with request
  bodies not persisted (sandbox keys are ephemeral); a self-hosted deployment
  removes the third-party hop entirely for the pilot if preferred.

## 7. How LoopX verifies / locally replays the verdict (honest answer)

The maintainer's concern is exactly right: **today the receipt lets you verify
the *input*, not independently recompute the *verdict*.** Being precise about
what is and isn't possible now:

- **Available today (input integrity):** `input_snapshot_hash` is SHA-256 over
  canonical-JSON of the request with `client_request_id` excluded; LoopX hashes
  the same envelope client-side and proves the engine scored the exact bytes it
  sent ([api-reference.md](https://github.com/Shxnque/quesen/blob/main/docs/api-reference.md#receipt-provenance-v110)).
  `commit_sha` pins which ruleset produced it.
- **Available in shadow mode (determinism):** replay the same envelope N times /
  over days; identical `decision` + `input_snapshot_hash` + `commit_sha` proves
  the scoring path is deterministic and drift-free.
- **Now available (independent verdict replay) — SHIPPED:** the egress/authority
  decision subset is recomputable **offline, with zero network**, via a public
  reference evaluator. LoopX can recompute `PASS/REVIEW/BLOCK` + reason codes +
  `input_snapshot_hash` itself and assert against a self-contained, `commit_sha`-keyed
  fixture — no hosted call, no key, no signup:
  [`evaluation/conformance/verify_conformance.py`](https://github.com/Shxnque/quesen/blob/main/evaluation/conformance/verify_conformance.py)
  ([kit README](https://github.com/Shxnque/quesen/blob/main/evaluation/conformance/README.md)).
  The three prepared-Effect cases above (PASS routine / REVIEW ambiguity / BLOCK
  backstop) are included and recompute byte-for-byte.

**What remains a boundary (honest):** the kit reproduces the *contract-level*
decision/reasons/hash for this subset — it does **not** publish the production risk
weighting/thresholds, make the production `commit_sha` publicly checkoutable, or
issuer-sign receipts. So the hosted engine is now an *optimisation*, not a *trust
dependency*, for the egress/authority gate. Full-ruleset + issuer signature remain the
roadmap in [`verify/README.md`](https://github.com/Shxnque/quesen/blob/main/verify/README.md).

## 8. Measurable benefit target (shadow-mode acceptance gate)

Run in shadow against a **labeled report-delivery corpus**; do not change
execution. Success criteria before any enforcement PR:

- **Security-review deflection rate:** ≥ X% of unchanged-envelope scheduled runs
  score `PASS` (target set with LoopX from the corpus baseline).
- **Zero false-PASS:** no case labeled "should-have-been-stopped" scores `PASS`
  (hard gate — a single false-PASS fails the pilot).
- **Catastrophic recall:** 100% of credential/secret-to-unverified cases `BLOCK`.
- **Latency:** added admission latency within the delivery SLA.

---

### Proposed first step (matches the maintainer's preference)

Shadow mode: LoopX forms the prepared Effect → calls admission → persists the
compact receipt bound to the Effect id → **executes exactly as today** → compare
verdicts to operator outcomes on the labeled corpus. If deflection is strong
with zero false-PASS, promote to a provider-neutral typed admission hook owned by
the LoopX TS control plane, with Quesen as one optional extension provider.

_Reason codes and hashes above are reproducible without signup; see the fixtures
file for exact request bodies._
