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
- Products scraped with: name, price, BSR change %, rating, reviews, images
- Auto-generated AliExpress supplier search URLs
- Scheduler runs every 4 hours for scraping, every 6 hours for Google Trends
- 137+ products in database with real data
- Data transparency: confidence_score, data_sources, last_updated, is_real_data on every product
- "Data unavailable" markers instead of fabricated values

### Phase 2: Market Intelligence Engine (DONE — Mar 2026)
- Transparent scoring with exact formula weights: trend(30%), margin(25%), competition(20%), ad_activity(15%), supplier(10%)
- Each score includes reasoning text explaining WHY the score is what it is
- launch_score_breakdown stored per product with score/weight/weighted/reasoning per component
- Frontend: Score Breakdown card on product detail with 5 components visible
- Frontend: Data transparency footer (Sources, Confidence %, Updated, Live Data badge)
- Frontend: "Live" and "X% conf." badges on Discover page product cards
- Batch score recomputation endpoint and scheduled task

## Remaining Phases

### Phase 3: Supplier Integration (NEXT)
- AliExpress supplier linking with cost, shipping origin, estimated shipping time, stock
- CJ Dropshipping supplier catalog
- One-click supplier selection attached to store product

### Phase 4: One-Click Store Launch
- Auto-generate product title, description, pricing, variants, shipping rules
- Auto-generate store branding & homepage
- Connect supplier
- Shopify CSV export + WooCommerce export

### Phase 5: AI Ad Creative Generation
- TikTok ad scripts/hooks, Facebook ad copy, Instagram captions
- Product angles, headline variations
- Video storyboard, content shot list, voiceover script
- Provider: Emergent LLM Key with abstraction layer for multi-provider

### Phase 6: Opportunity Feed & Reports
- Real-time dashboard feed (new_strong_launch, trend_spike, competition_drop, etc.)
- Auto-refresh every 30 seconds
- Enhanced reports with PDF export & email delivery
- Referral rewards system
- Feature gating per subscription tier

## Known Limitations
- AliExpress direct scraping blocked by CAPTCHA
- TikTok Creative Center scraping blocked
- CJ Dropshipping scraping blocked (human verification)
- Only Amazon UK Movers & Shakers is scraped as live data source
- Ad activity data unavailable (no Meta/TikTok ad library integration yet)

## API Endpoints
- GET /api/products — List products with scores, transparency
- GET /api/products/{id} — Product detail
- GET /api/products/{id}/launch-score-breakdown — Transparent score breakdown
- POST /api/ingestion/scrape/amazon_movers — Run Amazon scraper
- POST /api/ingestion/scrape/google-trends — Google Trends enrichment
- POST /api/ingestion/scores/recompute — Batch score recomputation
- POST /api/ingestion/scrape/full — Full scrape pipeline
