# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a predictive e-commerce intelligence platform that identifies winning products earlier than competitors. The system should feel like an AI e-commerce co-pilot — enabling users to launch products with 3 clicks: Find Product -> Launch Store -> Generate Ads -> Start Selling.

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI
- Backend: FastAPI, MongoDB, APScheduler
- Auth: Custom JWT | Payments: Stripe (live test keys) | Email: Resend
- Scraping: curl_cffi | Google Trends: pytrends
- LLM: Emergent LLM Key (OpenAI GPT-4.1-mini) via emergentintegrations

## Completed Phases

### Phase 1-6: Foundation (DONE)
- Real data pipeline (Amazon, Google Trends), scoring engine, supplier integration, one-click store launch, AI ad creatives, opportunity feed

### Phase 7-10: Platform Features (DONE)
- Referral system, automated reports + PDF, ad discovery (TikTok/Meta/Google), Shopify direct publish

### Phase 11: Stripe Subscriptions (DONE)
- Free/Pro £39/Elite £99 with server-side + frontend feature gating

### Phase 12: AI Co-Pilot UX (DONE - P0)
- "Find Me a Winning Product" Hero on Dashboard
- 5-Step Product Launch Wizard (/launch/:productId)
- Beginner / Advanced Mode Toggle (persisted in localStorage)

### Phase 13: Predictive Engine & Daily Opportunities (DONE - P1)
- 7-signal scoring formula (trend, competition, margin, supplier, search_growth, order_velocity, trend_stage)
- Daily Opportunities Panel with Emerging/Strong Launch/Trend Spikes tabs
- Trend stage classification (Exploding, Emerging, Rising, Stable, Declining)

### Phase 14: Homepage Redesign, SEO & Free Tools (DONE - P2)
- Premium SaaS landing page with live demo product card
- Programmatic SEO pages (/trending/:slug) with 4 pre-configured slugs
- Free Tools page (/tools) with 4 tools

### Phase 15: Product Outcome Learning System (DONE - P3, March 2026)
- Track launched products and their real-world outcomes
- Update metrics: revenue, orders, ad_spend, days_active (auto-computes ROI)
- Auto-label outcomes: success/moderate/failed based on thresholds
- Aggregate stats with learning insights

### Phase 16: Prediction Accuracy System (DONE - P0, March 2026)
- Dashboard card comparing initial launch_score/success_probability vs actual outcomes
- Accuracy percentage, correct/incorrect predictions, score bucket breakdown
- Learning insights: "Products with score 40-59 succeed 50% of the time"
- API: GET /api/outcomes/prediction-accuracy

### Phase 17: Opportunity Radar — Live Feed (DONE - P1, March 2026)
- Real-time signal feed on dashboard: trend spikes, new ads, supplier demand, competition drops
- Auto-refreshes every 30 seconds with LIVE badge
- Events show product image, name, launch score, signal type badge
- API: GET /api/radar/live-events

### Phase 18: Saturation Radar (DONE - P2, March 2026)
- Per-product saturation risk display (Low/Medium/High)
- Saturation score (0-100) based on stores, ads, search growth, trend stage
- Warning for high saturation products
- API: GET /api/products/{id}/saturation

### Phase 19: Homepage Design Polish (DONE - P4, March 2026)
- Soft gradients, rounded cards, modern typography, subtle shadows
- Smooth hover animations and entrance animations (fadeSlideUp)
- Social proof bar (137+ Products, 8 Live Data Sources, 7-Signal, Real Data Only)
- Glass-morphism effects on demo card and navbar
- Polished LandingLayout (frosted header, Tools nav link, footer with links)

### Phase 20: Enhanced Free Tools (DONE - P3, March 2026)
- TikTok Product Analyzer: URL input, views, engagement, virality, product potential, hashtag growth, ad detection (simulated)
- Product Trend Checker: keyword input, trend score, search growth, stage, demand, best time, risk (simulated)
- Improved layout with 2x2 grid

### Phase 21: Competitor Store Intelligence Engine (DONE - NEW, March 2026)
- Per-product competitor store analysis
- Stores detected, new stores (7d), estimated price range, avg store age, ad activity
- Competition impact assessment
- Side-by-side with Saturation Radar on product detail page
- API: GET /api/products/{id}/competitor-intelligence

## Key API Endpoints
- Find Winning: GET /api/products/find-winning (auth)
- Featured Product: GET /api/public/featured-product (public)
- Daily Opportunities: GET /api/dashboard/daily-opportunities (auth)
- Prediction Accuracy: GET /api/outcomes/prediction-accuracy (auth)
- Opportunity Radar: GET /api/radar/live-events (auth)
- Saturation Radar: GET /api/products/{id}/saturation (public)
- Competitor Intelligence: GET /api/products/{id}/competitor-intelligence (public)
- SEO Pages: GET /api/public/seo/{slug} (public)
- Outcomes: POST /api/outcomes/track, GET /api/outcomes/my, PUT /api/outcomes/{id}, POST /api/outcomes/auto-label, GET /api/outcomes/stats
- Stripe: /api/stripe/plans, /create-checkout-session, /feature-access, /webhook
- Products: /api/products, /api/products/{id}
- Stores: /api/stores/launch
- Ad Creatives: /api/ad-creatives/generate/{id}
- Reports: /api/reports/, /api/reports/*/pdf
- Referrals: /api/viral/referral/stats
- Ad Discovery: /api/ad-discovery/discover/{id}

## Upcoming Tasks (P5)
- **Automated System Health Report**: Dashboard verifying data ingestion, trend scoring, supplier integration, store launch flow, ad generation, Stripe payments, scraper health

## Backlog
- server.py refactoring into modular route files (7800+ lines)
- Integrate real data for order_velocity_score (AliExpress API) and search_growth_score
- CJ Dropshipping & Zendrop direct supplier API
- TikTok Creative Center / Meta Ad Library API integration for real ad detection
- Enhanced store generation (auto logos, trust badges, review sections)
- Comprehensive automated testing suite
- Replace simulated tools (TikTok Analyzer, Trend Checker) with real API data
