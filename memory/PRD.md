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
- Real data pipeline (Amazon, Google Trends), scoring engine, supplier integration
- Store launch, AI ads, opportunity feed, referrals, reports, Stripe subscriptions
- AI Co-Pilot, Predictive Engine, SEO, Outcome Learning, Prediction Accuracy
- Opportunity/Saturation Radar, Competitor Intelligence, Ad Winning Engine
- A/B Test Planner, Launch Simulator

### Phase 23: Smart Budget Optimizer V1 (DONE - March 2026)
- Rule-based budget recommendations (increase/maintain/pause/kill/needs_more_data)
- BudgetOptimizerCard in Ad Test Planner, OptimizationDashboardWidget on Dashboard

### Phase 24: Automated System Health Dashboard (DONE - March 2026)
- Admin-only dashboard monitoring 18 services across 4 categories
- Route: /admin/health

### Phase 25: Data Credibility & Supplier Intelligence (DONE - March 2026)
**Data Reliability Layer:**
- Circuit breaker pattern per source (failure threshold, recovery timeout)
- Fallback chains: scraper → estimation → hardcoded for every source
- Source pull logging (source_pull_log collection) with success/failure/latency
- `data_confidence` field per product: live | estimated | fallback
- `source_signals` dict tracking per-signal confidence, source, and update time

**AliExpress Integration:**
- Scraper attempts real data (curl_cffi, JS pages)
- Falls back to estimation with plausible signals from existing data
- Fields: orders_30d, ae_shipping_days, ae_processing_days, ae_availability, ae_rating, ae_reviews

**CJ Dropshipping Supplier Intelligence:**
- Full supplier intelligence: price, shipping_days, processing_days, availability, stock, variants, warehouse, fulfillment_type, product_url, last_sync
- Scraper with estimation fallback
- Fields: cj_price, cj_shipping_days, cj_processing_days, cj_availability, cj_variants_count, cj_warehouse, cj_fulfillment_type

**TikTok Creative Center:**
- Real scraper returning live data (views, engagement, ad counts, trend velocity)
- Fields: tiktok_views, engagement_rate, ad_count, view_growth_rate

**Meta Ad Library:**
- API integration (when META_AD_LIBRARY_TOKEN is set) + estimation fallback
- Fields: meta_active_ads, meta_ad_growth_7d, estimated_monthly_ad_spend, ad_platform_distribution

**Scoring Engine Updates:**
- `scoring_metadata.source_breakdown` per product documenting each signal's confidence, source, and timestamp
- Supplier demand score now uses enriched fields from AliExpress/CJ
- Real data signals weighted higher than estimation

**Frontend Source Trust Labels:**
- `SourceTrustBadge`: Live Data (green) / Estimated (amber) / Fallback (gray)
- `SourceDot`: Small colored indicator next to product names on dashboard
- `FreshnessIndicator`: "Just now" / "3h ago" / "2d ago" with color coding
- `SourceBreakdownPanel`: Per-signal source grid in Data Transparency section

**API Endpoints:**
- POST /api/data-integration/enrich/{product_id} (auth)
- POST /api/data-integration/run-ingestion?limit=N (admin, async background)
- GET /api/data-integration/source-health (auth)
- GET /api/data-integration/ingestion-status (auth)

**Current Data Source Status:**
| Source | Method | Confidence |
|--------|--------|------------|
| Amazon | Scraper (curl_cffi) | Live |
| Google Trends | API (pytrends) | Live |
| TikTok | Scraper | Live |
| AliExpress | Estimation (scraper blocked) | Estimated |
| CJ Dropshipping | Estimation (scraper blocked) | Estimated |
| Meta Ad Library | Estimation (no token) | Estimated |

## Upcoming Tasks (P0-P1)
- **P1: Smart Budget Optimizer V2:** Optimization Timeline UI, auto-recommend, rule presets
- **P1: Budget Optimizer Alerts:** Email/push for kill/scale recommendations

## Backlog
- server.py refactoring into modular route files (8500+ lines)
- Official API keys for AliExpress, CJ Dropshipping, Meta when available
- Replace estimation with real data as API access becomes available
- Enhanced store generation (auto logos, trust badges)
- Enhanced Budget Optimizer: anomaly detection, budget pacing, creative fatigue
- Viral shareable public product pages
- Programmatic SEO engine for trending product pages
