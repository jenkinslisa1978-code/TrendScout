# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a predictive e-commerce intelligence platform that identifies winning products earlier than competitors. The system should feel like an AI e-commerce co-pilot — enabling users to launch products with 3 clicks: Find Product -> Launch Store -> Generate Ads -> Start Selling.

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI
- Backend: FastAPI, MongoDB, APScheduler, aiohttp
- Auth: Custom JWT | Payments: Stripe (live test keys) | Email: Resend
- Scraping: curl_cffi | Google Trends: pytrends
- LLM: Emergent LLM Key (OpenAI GPT-4.1-mini) via emergentintegrations

## Completed Phases

### Phase 1-22: Foundation through Ad Intelligence (DONE)
- Full pipeline: data, scoring, stores, ads, subscriptions, AI co-pilot, competitor intelligence

### Phase 23: Smart Budget Optimizer V1 (DONE)
- Rule-based budget recommendations, dashboard widget

### Phase 24: Automated System Health Dashboard (DONE)
- Admin-only /admin/health monitoring 18 services

### Phase 25: Data Credibility & Supplier Intelligence (DONE)
- Circuit breakers, fallback chains, source trust badges, CJ supplier intelligence

### Phase 26: Official API Integration Layer (DONE - March 2026)
**Official API clients with auto-upgrade capability:**

**Meta Ad Library API (Graph API v25.0)**
- Client: `/app/backend/services/api_clients/meta_ads_client.py`
- Endpoint: `GET https://graph.facebook.com/v25.0/ads_archive`
- Signals: active ad counts, advertiser/page names, creation dates, platforms
- Rate limiting: 2s interval, 1h cache, circuit breaker
- .env: `META_AD_LIBRARY_TOKEN`

**CJ Dropshipping API v2.0**
- Client: `/app/backend/services/api_clients/cj_client.py`
- Endpoints: product search, product detail query
- Signals: pricing, shipping, variants, stock, warehouse, fulfillment type
- Rate limiting: 1s interval, 30min cache, circuit breaker
- .env: `CJ_API_KEY`

**AliExpress Open Platform (Affiliate API)**
- Client: `/app/backend/services/api_clients/aliexpress_client.py`
- Endpoints: product query, product detail
- Signals: pricing, orders, ratings, reviews, shipping, commission rates
- MD5 signature auth, dual gateway (api-sg + legacy)
- .env: `ALIEXPRESS_API_KEY`, `ALIEXPRESS_API_SECRET`

**Architecture:**
- 4-step fallback chain: Official API → Scraper → Estimation → Hardcoded
- Auto-upgrade: adding key to .env instantly switches source from Estimated → Live
- Per-source circuit breaker (3 failures → 5min cooldown)
- Per-source rate limiting with exponential backoff
- Response caching (30min-1hr TTL)
- Full pull logging (source_pull_log collection)

**Integration Status Dashboard:**
- Admin page: `/admin/integrations`
- Per-source: credential status, current mode, health check, last sync
- Summary bar: Total Products | Live Data | Estimated | Not Enriched
- Source Pull History table with success rates
- Setup guide with exact .env vars and credential URLs
- Run Ingestion button (async background)

**API Endpoints:**
- GET /api/data-integration/integration-health (admin)
- GET /api/data-integration/source-health (auth)
- GET /api/data-integration/ingestion-status (auth)
- POST /api/data-integration/enrich/{product_id} (auth)
- POST /api/data-integration/run-ingestion?limit=N (admin, async)

## Current Data Source Status
| Source | Method | Mode | Status |
|--------|--------|------|--------|
| TikTok | Public scraper | Live | Healthy |
| Amazon | curl_cffi scraper | Live | Healthy |
| Google Trends | pytrends API | Live | Healthy |
| AliExpress | Estimation (API ready) | Estimated | Awaiting key |
| CJ Dropshipping | Estimation (API ready) | Estimated | Awaiting key |
| Meta Ad Library | Estimation (API ready) | Estimated | Awaiting token |

## Upcoming Tasks
- **P1: Smart Budget Optimizer V2:** Timeline UI, auto-recommend, rule presets
- **P1: Budget Optimizer Alerts:** Email/push for kill/scale recommendations
- **P0: TrendScout LaunchPad** (major feature): AI-assisted product launch workflow

## Backlog
- server.py refactoring into modular route files
- Zendrop supplier API integration
- Enhanced store generation (auto logos, trust badges)
- Enhanced Budget Optimizer: anomaly detection, budget pacing, creative fatigue
- Viral shareable public product pages
- Programmatic SEO engine
