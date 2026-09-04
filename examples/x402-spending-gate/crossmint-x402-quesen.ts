// crossmint-x402-quesen.ts
// Quesen as the DETERMINISTIC pre-payment gate in a Crossmint x402 agent flow.
//
//   npm i quesen-sdk @x402/core
//   + Crossmint Wallets SDK for `walletClient` (agent smart wallet + server-side signer)
//   Keys: see ACQUIRE.md
//
// Flow: agent wants to pay -> Quesen evaluates the spend deterministically BEFORE
// anything is signed -> only PASS proceeds to the x402 settlement. Every attempt
// yields a recomputable receipt (input_snapshot_hash). Policy (budget caps, merchant
// allowlists, human-in-loop thresholds) lives OUTSIDE the model, keyed on the typed
// action + target — exactly the "harness-layer" governance AP2/x402 leave to you.

import { QuesenClient, QuesenFirewall, reasonCodes, TscBlockedError } from "quesen-sdk";
import { wrapFetchWithPayment } from "@x402/core";

const quesen = new QuesenClient({ apiKey: process.env.QUESEN_API_KEY! }); // sk_sandbox_… from senueren.co.za/quesen
const fw = new QuesenFirewall(quesen);

// x402 auto-pays on HTTP 402 using the Crossmint-backed wallet client.
// `walletClient` comes from the Crossmint Wallets SDK; the agent is authorized via a
// server-side signer (`wallet.addSigner({ prepareOnly: true })` + email approval).
const payFetch = wrapFetchWithPayment(fetch, walletClient);

export async function guardedPay(url: string, merchant: string) {
  try {
    // Deterministic gate BEFORE any 402 signature.
    await fw.requirePass({
      action: "x402_payment",
      target: merchant,        // payee — checked against the allowlist/budget policy engine-side
      trustTier: "unverified", // KYA/identity tier (e.g. from Skyfire) asserted upstream
      dataClass: "payment",
    });
  } catch (e) {
    if (e instanceof TscBlockedError) {
      // e.decision is a full receipt (recomputable). REVIEW -> human sign-off
      // (Payman-style approval chain); BLOCK -> deny.
      console.error("quesen gate:", e.decision.decision, reasonCodes(e.decision));
    }
    throw e; // never reaches payFetch unless the verdict was PASS
  }
  return payFetch(url); // PASS -> x402 settles the micropayment
}
