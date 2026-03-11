# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a comprehensive e-commerce intelligence SaaS platform that allows users to:
Discover winning products → Validate market opportunity → Create a store instantly → Generate ads → Launch products — all in one seamless workflow.

## Core Requirements
- Real-time product trend data from multiple e-commerce sources
- Transparent, formula-based scoring with per-component reasoning
- AI-powered ad creative generation
- One-click store creation with Shopify/WooCommerce export
- Supplier linking (AliExpress, CJ Dropshipping)
- Subscription plans with Stripe payments
- Data transparency: never fabricate data, mark unavailable clearly

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI
- Backend: FastAPI, MongoDB
- Auth: Custom JWT
- Payments: Stripe
- Email: Resend
- Scraping: curl_cffi (browser TLS fingerprint impersonation)
- Google Trends: pytrends library
- Scheduling: APScheduler
- LLM: Emergent LLM Key (planned for Phase 5)

## Scoring Formula
```
launch_score = 0.30 * trend_score + 0.25 * margin_score + 0.20 * competition_score + 0.15 * ad_activity_score + 0.10 * supplier_demand_score
```

## What's Been Implemented

### Phase 0: Foundation (DONE)
- Custom JWT authentication
- React frontend with Dashboard, Discover, Product Detail pages
- Store builder with Shopify export
- Stripe payments integration
- APScheduler for background jobs
- Error boundary for crash prevention

### Phase 1: Real Data Infrastructure (DONE — Mar 2026)
- Amazon UK Movers & Shakers scraper using curl_cffi (12+ categories)
- Google Trends integration using pytrends (keyword velocity data)
- 137+ products with real data
- Data transparency: confidence_score, data_sources, last_updated, is_real_data
- "Data unavailable" markers instead of fabricated values

### Phase 2: Market Intelligence Engine (DONE — Mar 2026)
- Transparent scoring with exact formula weights
- Each score includes reasoning text explaining WHY
- launch_score_breakdown stored per product
- Frontend: Score Breakdown card on product detail
- Frontend: Data transparency footer + Live/Confidence badges

### Phase 3: Supplier Integration (DONE — Mar 2026)
- Auto-discovers AliExpress + CJ Dropshipping supplier listings per product
- Each listing shows: cost, shipping cost, delivery days, origin, confidence badge
- One-click supplier selection (deselects others)
- "View on AliExpress" / "View on CJ" external links
- Transparent confidence: "Matched" (from data), "Estimated" (calculated), "Verified" (scraped)
- API: GET /api/suppliers/{product_id}, POST select, POST find/refresh
- Frontend: Full SupplierSection component on product detail page

## Remaining Phases

### Phase 4: One-Click Store Launch (NEXT)
- After supplier selected, single "Launch Store" button
- Auto-generate: product title, description, pricing, variants, shipping rules
- Auto-generate: store branding & homepage, policies
- Connect selected supplier
- Export: Shopify API publish, Shopify CSV, WooCommerce export

### Phase 5: AI Ad Creative Generation
- TikTok ad scripts/hooks, Facebook ad copy, Instagram captions
- Product angles, headline variations
- Video storyboard, content shot list, voiceover script
- Provider: Emergent LLM Key with multi-provider abstraction

### Phase 6: Opportunity Feed & Remaining
- Real-time dashboard feed (new_strong_launch, trend_spike, competition_drop, etc.)
- Auto-refresh every 30 seconds
- Enhanced reports with PDF export & email
- Referral rewards, feature gating per tier
- Ad discovery (TikTok/Meta ad library monitoring)

## Known Limitations
- AliExpress direct scraping blocked by CAPTCHA (supplier costs are estimated from retail price)
- TikTok Creative Center scraping blocked
- CJ Dropshipping scraping blocked
- Only Amazon UK is scraped as live data source
- Ad activity data unavailable (no ad library integration yet)

## API Endpoints
- GET /api/products — List products with scores, transparency
- GET /api/products/{id} — Product detail
- GET /api/products/{id}/launch-score-breakdown — Transparent score breakdown
- GET /api/suppliers/{product_id} — Auto-discover supplier listings
- POST /api/suppliers/{product_id}/find — Refresh supplier listings
- POST /api/suppliers/{product_id}/select/{supplier_id} — Select supplier
- POST /api/ingestion/scrape/amazon_movers — Run Amazon scraper
- POST /api/ingestion/scrape/google-trends — Google Trends enrichment
- POST /api/ingestion/scores/recompute — Batch score recomputation
