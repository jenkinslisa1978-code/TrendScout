# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a comprehensive e-commerce intelligence SaaS platform that allows users to:
Discover winning products → Validate market opportunity → Create a store instantly → Generate ads → Launch products — all in one seamless workflow.

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI
- Backend: FastAPI, MongoDB, APScheduler
- Auth: Custom JWT | Payments: Stripe | Email: Resend
- Scraping: curl_cffi | Google Trends: pytrends
- LLM: Emergent LLM Key (OpenAI GPT-4.1-mini) via emergentintegrations

## Completed Phases

### Phase 1: Real Data Infrastructure (DONE)
- Amazon UK Movers & Shakers scraper (curl_cffi, 12+ categories)
- Google Trends integration (pytrends, keyword velocity)
- 137+ real products, confidence_score, data_sources, last_updated
- Scheduler: scraping every 4h, Google Trends every 6h, score recompute every 4h

### Phase 2: Market Intelligence Engine (DONE)
- launch_score = 0.30*trend + 0.25*margin + 0.20*competition + 0.15*ad_activity + 0.10*supplier_demand
- Per-component transparent reasoning
- Frontend: Score Breakdown card + data transparency badges

### Phase 3: Supplier Integration (DONE)
- Auto-discovers AliExpress + CJ Dropshipping listings per product
- One-click supplier selection, external verification links
- Transparent confidence badges: Matched/Estimated/Verified

### Phase 4: One-Click Store Launch (DONE)
- POST /api/stores/launch creates complete store in one call
- Auto-generates: title, description, pricing, variants, shipping rules, branding, policies
- Connects selected supplier
- Export: Shopify JSON, Shopify CSV download, WooCommerce JSON

### Phase 5: AI Ad Creative Generation (DONE)
- TikTok ad scripts with hooks, Facebook ad copy, Instagram captions with hashtags
- Product angles with target audiences, headline variations
- Video storyboard (6 scenes), shot list (5 shots), voiceover script
- Provider: Emergent LLM Key → OpenAI GPT-4.1-mini
- Abstraction layer supports OpenAI/Anthropic/Gemini switch

### Phase 6: Opportunity Feed (DONE)
- Real-time dashboard feed with 30-second auto-refresh
- Event types: new_strong_launch, trend_spike, competition_drop, supplier_price_drop, new_ad_activity
- 38+ real events from product data analysis
- Color-coded badges: green (opportunity), blue (trend), purple (ad activity), amber (competition), red (saturation)

## Key API Endpoints
- Products: GET /api/products, GET /api/products/{id}, GET /api/products/{id}/launch-score-breakdown
- Suppliers: GET /api/suppliers/{id}, POST select, POST find
- Stores: POST /api/stores/launch, GET /api/stores/{id}/export?format=shopify|shopify_csv|woocommerce
- Ad Creatives: POST /api/ad-creatives/generate/{id}, GET /api/ad-creatives/{id}
- Ingestion: POST /api/ingestion/scrape/amazon_movers, google-trends, scores/recompute
- Dashboard: GET /api/dashboard/opportunity-feed

## Remaining/Backlog
- Ad Discovery (TikTok/Meta ad library monitoring)
- Enhanced reports with PDF export & email delivery
- Referral rewards system enhancement
- Feature gating per subscription tier
- Additional data sources as anti-bot solutions become available
