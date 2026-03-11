# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a comprehensive e-commerce intelligence SaaS platform that allows users to:
Discover winning products → Validate market opportunity → Create a store instantly → Generate ads → Launch products — all in one seamless workflow.

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI
- Backend: FastAPI, MongoDB
- Auth: Custom JWT | Payments: Stripe | Email: Resend
- Scraping: curl_cffi | Google Trends: pytrends | Scheduling: APScheduler
- LLM: Emergent LLM Key (planned for Phase 5)

## Scoring Formula
```
launch_score = 0.30*trend + 0.25*margin + 0.20*competition + 0.15*ad_activity + 0.10*supplier_demand
```

## Completed Phases

### Phase 0: Foundation (DONE)
- JWT auth, Dashboard/Discover/Product Detail pages, Stripe, APScheduler, Error Boundary

### Phase 1: Real Data Infrastructure (DONE — Mar 2026)
- Amazon UK Movers & Shakers scraper (curl_cffi, 12+ categories)
- Google Trends integration (pytrends, keyword velocity)
- 137+ real products, confidence_score, data_sources, last_updated

### Phase 2: Market Intelligence Engine (DONE — Mar 2026)
- Transparent scoring with exact formula weights + per-component reasoning
- launch_score_breakdown with score/weight/weighted/reasoning per component
- Frontend Score Breakdown card + data transparency badges

### Phase 3: Supplier Integration (DONE — Mar 2026)
- Auto-discovers AliExpress + CJ Dropshipping listings per product
- One-click supplier selection, View on AliExpress/CJ links
- Transparent confidence: Matched/Estimated/Verified badges

### Phase 4: One-Click Store Launch (DONE — Mar 2026)
- POST /api/stores/launch: single endpoint creates complete store
- Auto-generates: title, description, bullet points, pricing, variants, shipping rules, branding, policies
- Connects selected supplier (or auto-discovers best)
- Export: Shopify JSON, Shopify CSV download, WooCommerce JSON download
- Frontend: "Launch Store" green button on product detail page
- Store detail: Shipping & Supplier tab, 3 export buttons

## Remaining Phases

### Phase 5: AI Ad Creative Generation (NEXT)
- TikTok ad scripts/hooks, Facebook ad copy, Instagram captions
- Product angles, headline variations, video storyboard, voiceover script
- Provider: Emergent LLM Key with multi-provider abstraction layer

### Phase 6: Opportunity Feed & Remaining
- Real-time dashboard feed (trend_spike, competition_drop, etc.), 30s refresh
- Enhanced reports with PDF export & email
- Referral rewards, feature gating per tier
- Ad Discovery (TikTok/Meta ad library monitoring)

## Key API Endpoints
- GET /api/products, GET /api/products/{id}, GET /api/products/{id}/launch-score-breakdown
- GET /api/suppliers/{id}, POST /api/suppliers/{id}/find, POST /api/suppliers/{id}/select/{sid}
- POST /api/stores/launch, GET /api/stores/{id}/export?format=shopify|shopify_csv|woocommerce
- POST /api/ingestion/scrape/amazon_movers, POST /api/ingestion/scrape/google-trends
- POST /api/ingestion/scores/recompute
