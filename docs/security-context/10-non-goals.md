# 10 · Non-Goals (explicit scope limits)

TSC v2 (P1) is a **contract**, not a product pivot. To prevent scope creep, the
following are explicitly **out of scope for P1**:

1. **Detectors.** P1 does not implement prompt-injection, tool-authorization, or
   data-exfiltration *detection*. It makes those dimensions **representable and
   deterministically evaluable at the contract level**. Detectors are P2+.
2. **LLM anywhere in the decision path.** The engine stays a pure deterministic
   oracle (Doctrine §13). `action.intent` is never sent to a model.
3. **A policy engine.** The context *references* a policy (`policy.id/version`);
   it does not embed or execute policy logic. Quesen is protocol, not framework
   (Doctrine §13 — ceding the rule surface undoes the moat).
4. **Persistence / stateful receipts.** No verdict is stored inside the protocol
   plane (Doctrine §17.5). Callers persist responses downstream if they wish.
5. **Cryptographic signing of responses.** Deferred unless a named integrator
   files a §5 request (same discipline that deferred signing in ADR-041 §4.3).
6. **KYC / identity.** Quesen scores security context, not identity.
7. **Breaking v1.** v1 remains the default and is untouched.
8. **AG2 support via `quesen-autogen`.** AG2 is a separate track (see `09`).
9. **Mass changes across the six client repos in one motion.** The contract is
   designed first; propagation is staged and gated.

## "Done" definition for P1

P1 is complete when another engineer can implement the engine changes **without
inventing** any of: field meanings, validation behaviour, normalization
behaviour, versioning semantics, decision semantics, error behaviour,
compatibility behaviour, security invariants, or client-migration requirements.
All of those are specified in this package + the JSON Schema + the runnable POC.
