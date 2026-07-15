# Pricing

> **All prices are USD.** Crypto (USDC / ETH / stablecoins via Coinbase
> Commerce) is a settlement layer only.
>
> Prices are indicative for the current release; the live catalog is served
> from [`GET /billing/plans`](https://web-production-30ab5.up.railway.app/billing/plans)
> and env-overridable per deployment.

## Subscription tiers

| Tier | Monthly | Included /validate | Overage / call | Rate limit | Audience |
| --- | ---: | ---: | ---: | ---: | --- |
| **Developer Free** | $0 | 1,000 | $0.005 | 30 rpm | Solo builders |
| **Starter** | $49 | 25,000 | $0.003 | 120 rpm | Single production agent |
| **Professional** | $249 | 250,000 | $0.0015 | 600 rpm | Multi-agent fleets, DAOs, protocol treasuries |
| **Enterprise** | $1,499 | 2,000,000 | $0.0008 | 3,000 rpm | Institutional integrators, protocol layers |

## Pay-per-call packs

One-shot top-ups. Perfect for exploratory workloads and evaluation without a
subscription.

| Pack | Calls | Price | Unit cost |
| --- | ---: | ---: | ---: |
| **10K pack** | 10,000 | $39 | $0.0039 |
| **100K pack** | 100,000 | $299 | $0.00299 |
| **1M pack** | 1,000,000 | $1,999 | $0.001999 |

## Payment rails

- **Card / ACH / SEPA** via Stripe Checkout.
- **Crypto** via Coinbase Commerce (USDC, ETH, DAI, USDT, BTC, LTC, and every
  other coin Coinbase Commerce natively supports; multi-chain routing is
  provider-side).

## Enterprise

Dedicated support channel, contractual SLA, compliance / procurement
paperwork, co-designed Conflict Matrix rules, and named integrator status on
[senueren.co.za](https://senueren.co.za). Contact `shinque03@gmail.com`.
