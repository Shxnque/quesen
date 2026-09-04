# Where to get the API keys (partners + platforms)

Exact developer-access paths for the agentic-commerce integrations and the Shinren
bounty platforms. All are self-serve except where noted.

## Quesen (already have it)
- **Sandbox key:** https://senueren.co.za/quesen → `sk_sandbox_…` (1000 credits, $0/call). Used as `QUESEN_API_KEY`.

## Agentic-commerce integration partners (Thesis A)
- **Crossmint** — sign up at the **Staging Console** (staging.crossmint.com) or Production
  Console → *Project Settings → API Keys* → generate a **client-side** and a **server-side**
  key. Agent wallet: Crossmint **Wallets SDK**; to let the agent sign autonomously, generate a
  32-byte (64-hex) secret and register it as a **server-side signer**
  (`wallet.addSigner({ prepareOnly: true })` + email approval). Docs: docs.crossmint.com
  (`/agents/stablecoin-wallet-quickstart`, `/agents/payment-flows/x402`).
- **Skyfire** — sign up at **https://app.skyfire.xyz** (magic link). A **Buyer Agent** account
  is auto-created. Get the key in **Dashboard → Playground → Generate API Key**. Tokens: `kya`,
  `pay`, `kya-pay`. Docs: docs.skyfire.xyz.
- **Payman AI** — developer API via their platform portal (paymanai.com). Access/keys through
  the developer dashboard; contact them for latest 2026 integration docs (not fully self-serve).

## x402 tooling
- **`@x402/core`** (npm) — `wrapFetchWithPayment(fetch, walletClient)`; no key of its own, it
  uses your funded (USDC) Crossmint wallet. Fund via Crossmint onramp or direct transfer.

## Shinren bounty platforms (Thesis B)
- **HackenProof** — you already have a working researcher token (this session). Programs:
  hackenproof.com/programs (incl. **Sui Ecosystem**, StarkGate).
- **Immunefi** — create a **researcher account** at immunefi.com; submit via the researcher
  dashboard after verification. Sui/Move programs: Scallop ($500k), Suilend ($250k), Sui core
  ($500k). Each requires a runnable testnet/mainnet PoC.

> Security: create each key fresh, store as env vars, never commit. Rotate anything ever pasted
> into chat/transcripts.
