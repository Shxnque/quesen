# FAQ

### What is Quesen?

Quesen is a deterministic AI decision engine for A2A (Agent-to-Agent) risk
evaluation. Given typed inputs about a target action, it returns exactly one
of `PROCEED`, `REVIEW`, or `SKIP` — with a `risk_score`, `confidence`, and the
exact conflict rules that fired.

### Is Quesen an LLM?

No. There is no LLM in `/validate`. No prompts. No randomness. Same input in,
same decision out.

### Why deterministic?

Autonomous agents cannot audit LLM outputs. Deterministic verdicts are
replayable, testable, and legally defensible. Every response embeds
`engine_version`, `weights`, and `thresholds` — an audit trail for regulators.

### Is Quesen KYC?

No. Quesen scores **risk**, not identity. It is chain-neutral,
framework-neutral, LLM-neutral by design (Doctrine §11).

### What chains does Quesen support for on-chain enrichment?

Seven EVM chains as of v1.6.0: Ethereum, Base, Arbitrum, Optimism, Polygon,
BNB, Avalanche. Non-EVM adapters (Solana, Sui, Cosmos) are deferred pending an
integrator conversation.

### What does the API cost?

See [`pricing.md`](pricing.md). TL;DR: free tier with 1,000 calls / month, paid
tiers from $49 / month.

### Can I self-host?

Quesen's engine implementation is not public. The client SDKs are open-source
under MIT.

### Does Quesen store my data?

No. Quesen is stateless. There is no customer database. Payment state lives in
Stripe or Coinbase Commerce. API-key earnings are held in memory per worker
and durably logged to a Telegram audit channel.

### What is the latency profile?

Warm: 5–10 ms end-to-end (deterministic engine, no I/O). Cold-start after
Railway idle: 5–30 seconds. On-chain enrichment adds an RPC + Blockscout round
trip only when opted-in.

### How do I get an API key?

Subscribe or top up via `/billing/stripe/checkout` or `/billing/crypto/checkout`.
On successful payment, the operator receives a provisioning notification and
issues your key within one business day. Enterprise customers receive keys
immediately after contract signature.

### How stable are the weights / thresholds?

Any change to weights or thresholds bumps `engine_version`. You can pin
against a specific engine_version in your integration and only upgrade
intentionally.

### Does Quesen support the Model Context Protocol (MCP)?

Yes. Native MCP server — see [`mcp.md`](mcp.md).
