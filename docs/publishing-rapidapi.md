# Publishing Quesen on RapidAPI Hub

> This document walks the operator through publishing Quesen's REST API on [RapidAPI Hub](https://rapidapi.com/hub). RapidAPI is a REST-API marketplace; it is complementary to the MCP registry surfaces (Smithery, MCP.so, Glama, awesome-mcp-servers) — this listing catches developers browsing for HTTP/JSON APIs rather than MCP clients.

## Why RapidAPI

- RapidAPI Hub aggregates ~40k public REST APIs and is the largest developer marketplace for HTTP APIs.
- Publishing here gives Quesen a second discovery surface parallel to MCP directories, targeting non-MCP developers who want a deterministic risk-verdict API by HTTP alone.
- Every RapidAPI listing gets its own quota / billing plumbing routed through RapidAPI's gateway — the caller sends `X-RapidAPI-Key` to `quesen.p.rapidapi.com`, RapidAPI meters, and forwards to `https://web-production-30ab5.up.railway.app`.

## Publisher path (operator action required)

RapidAPI's publishing dashboard requires an authenticated web session — the platform does **not** currently expose a public REST API for API-provider onboarding (only the [API Analytics API](https://docs.rapidapi.com/reference/get-started) reads existing metrics). The consumer key `4f103d1399msh39abc5b38f1e371p10720cjsn0eb65fadcff5` is a **subscriber** key (`X-RapidAPI-Key`) — it lets *callers* consume APIs on the hub, but does not authorise *publishing* new APIs.

To publish Quesen:

1. Sign in at [https://provider.rapidapi.com/](https://provider.rapidapi.com/) with the Senueren Bureau operator account.
2. Click **Add New API** → paste the OpenAPI spec URL: `https://web-production-30ab5.up.railway.app/openapi.json`.
3. Fill the fields below (all values are pre-verified against `v1.10.0-rc1`).

## Provider metadata (paste into the RapidAPI form)

| Field | Value |
| :--- | :--- |
| **API Name** | Quesen |
| **Base URL** | `https://web-production-30ab5.up.railway.app` |
| **Category** | AI / Machine Learning · Cybersecurity (dual-category if allowed) |
| **Tagline** | Deterministic risk-verdict engine for autonomous agents. Same input → same output. |
| **Description** | Quesen returns a deterministic `PROCEED` / `REVIEW` / `SKIP` verdict for autonomous-agent actions. No LLM in the loop; every response embeds `engine_version`, `weights`, `thresholds`, `input_snapshot_hash` (SHA-256 of the canonical request), and `commit_sha` (git SHA of the engine ruleset at decision time) so every verdict is replayable. Built on the Agent Settlement Protocol (ASP/1.0) for HTTP-402 metered access with USDC-on-Base settlement. |
| **Website / Homepage** | https://senueren.co.za/quesen |
| **Terms of Service** | https://github.com/Shxnque/quesen/blob/main/docs/faq.md |
| **Contact email** | shinque03@gmail.com |
| **OpenAPI URL** | https://web-production-30ab5.up.railway.app/openapi.json |
| **Auth mode** | Header · `X-API-Key` (map from RapidAPI's `X-RapidAPI-Key` at the gateway) |
| **Version tag** | 1.10.0 |

## Endpoints to expose (all documented in the OpenAPI spec)

| Method | Path | Purpose | Auth |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Liveness + engine_version | Public |
| `GET` | `/version` | Full config snapshot | Public |
| `POST` | `/validate` | Deterministic verdict | X-API-Key |
| `POST` | `/simulate` | Free counterfactual scoring | X-API-Key |
| `POST` | `/report` | Post-decision outcome feedback | X-API-Key |
| `GET` | `/billing/plans` | Public pricing catalog | Public |

## Recommended RapidAPI pricing plans

Mirror the existing Quesen plans from `docs/pricing.md` so RapidAPI's billing meters map 1:1 to the sovereign's:

| Plan | Monthly | Requests/mo | Rate limit | Overage |
| :--- | :--- | :--- | :--- | :--- |
| **Developer (Free)** | $0 | 1,000 | 60/min | 429 (hard cap) |
| **Starter** | $19 | 25,000 | 300/min | $0.001/call |
| **Professional** | $99 | 250,000 | 1,000/min | $0.0004/call |
| **Enterprise** | Contact | Custom | Custom | Custom |

RapidAPI charges a 20% platform fee on paid plans; factor that into any margin analysis.

## Verifying the listing after submission

Once RapidAPI approves the listing (typically 1-3 business days):

```bash
# Health check via RapidAPI gateway
curl -H "X-RapidAPI-Key: <YOUR_CONSUMER_KEY>" \
     -H "X-RapidAPI-Host: quesen.p.rapidapi.com" \
     https://quesen.p.rapidapi.com/health

# Expected: {"status":"ok","engine_version":"1.10.0"}
```

The response body must be byte-identical to a direct call to `https://web-production-30ab5.up.railway.app/health`. If it drifts, RapidAPI is rewriting the payload — open a support ticket.

## Post-listing housekeeping

After the listing goes live:

1. Update `Shxnque/quesen/docs/registries.md` with a new row for RapidAPI.
2. Update `Shxnque/quesen/README.md` "Live production" table with the RapidAPI proxy URL as an alternate access surface.
3. File the SITREP entry documenting the listing (governance requirement per DOCTRINE §14).

---

*Prepared 2026-07-31 · Session 26 · Quesen ecosystem alignment. RapidAPI listing is a fresh distribution surface; the sovereign engine remains unchanged and the OpenAPI spec at `/openapi.json` is the single source of truth for the wire contract.*
