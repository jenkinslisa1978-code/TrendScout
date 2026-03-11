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

### Phase 6: Opportunity Feed (DONE)
- Real-time dashboard feed with 30-second auto-refresh
- Event types: new_strong_launch, trend_spike, competition_drop, supplier_price_drop, new_ad_activity
- Color-coded badges

### Phase 7: Referral & Viral Growth System (DONE - March 2026)
- Unique referral codes per user (auto-generated on first access)
- Referral tracking: pending → verified status flow
- Reward: bonus store slots (up to 5) for verified referrals
- Social sharing: Twitter, Facebook, WhatsApp one-click share
- Signup integration: /signup?ref=CODE shows badge, tracks referral on registration
- Frontend: Full ReferralPage with stats, link, history

### Phase 8: Automated Reports (DONE - March 2026)
- Weekly Winning Products reports (top 20 products, trend analysis, competition, margins, saturation warnings)
- Monthly Market Trends reports (emerging categories, demand vs competition, growth metrics, predictions)
- PDF export for both report types via /api/reports/*/pdf
- Email delivery via Resend (weekly digest, product of the week alerts)
- Report archive with history browsing
- Access-gated sections (Free, Pro, Elite tiers)
- Scheduled generation: weekly on Mondays, monthly on 1st

### Phase 9: Ad Discovery (DONE - March 2026)
- Multi-platform ad scanning: TikTok Creative Center, Meta Ad Library, Google Shopping
- Real scraping with curl_cffi, falls back to direct links when blocked
- Cached results in MongoDB (12-hour TTL)
- Activity level scoring (none → low → moderate → high → very_high)
- Platform breakdown with ad counts
- External links to live ad library search results
- Frontend: AdDiscoverySection on ProductDetailPage with Discover/Refresh buttons

### Phase 10: Shopify Direct Publish (DONE - March 2026)
- Shopify OAuth connection flow endpoints
- Direct publish to connected Shopify store
- Export-only fallback when credentials not configured
- Backend: /api/shopify/status, /connect/init, /connect/callback, /publish, /disconnect

## Key API Endpoints
- Products: GET /api/products, GET /api/products/{id}
- Suppliers: GET /api/suppliers/{id}, POST select, POST find
- Stores: POST /api/stores/launch, GET /api/stores/{id}/export
- Ad Creatives: POST /api/ad-creatives/generate/{id}, GET /api/ad-creatives/{id}
- Ad Discovery: POST /api/ad-discovery/discover/{id}, GET /api/ad-discovery/{id}
- Reports: GET /api/reports/, GET /api/reports/weekly-winning-products, GET /api/reports/monthly-market-trends, GET /api/reports/*/pdf
- Referrals: GET /api/viral/referral/stats, POST /api/viral/referral/track, GET /api/viral/referral/history
- Shopify: GET /api/shopify/status, POST /api/shopify/connect/init, POST /api/shopify/publish/{store_id}
- Dashboard: GET /api/dashboard/opportunity-feed
- Ingestion: POST /api/ingestion/scrape/amazon_movers, google-trends, scores/recompute

## Remaining/Backlog
- Stripe subscription tiers with feature gating (P0)
- CJ Dropshipping & Zendrop direct API supplier integration
- TikTok Creative Center API integration (when available)
- Meta Ad Library API integration (requires App credentials)
- Image/video quality improvements (deduplication, scoring)
- Additional data sources as anti-bot solutions become available
- server.py refactoring into modular route files
