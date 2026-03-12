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
- API: GET /api/products/find-winning

### Phase 13: Predictive Engine & Daily Opportunities (DONE - P1)
- 7-signal scoring formula (trend, competition, margin, supplier, search_growth, order_velocity, trend_stage)
- Daily Opportunities Panel on Dashboard with Emerging/Strong Launch/Trend Spikes tabs
- Trend stage classification (Exploding, Emerging, Rising, Stable, Declining)
- API: GET /api/dashboard/daily-opportunities

### Phase 14: Homepage Redesign, SEO & Free Tools (DONE - P2)
- Premium SaaS landing page with live demo product card (fetches from /api/public/featured-product)
- Programmatic SEO pages (/trending/:slug) with 4 pre-configured slugs
- Free Tools page (/tools) with Profit Calculator and Saturation Checker
- APIs: GET /api/public/featured-product, GET /api/public/seo/{slug}

### Phase 15: Product Outcome Learning System (DONE - P3, March 2026)
- Track launched products and their real-world outcomes
- Update metrics: revenue, orders, ad_spend, days_active (auto-computes ROI)
- Auto-label outcomes: success (orders>=50 OR revenue>=500), moderate (orders>=10 OR revenue>=100), failed (days>=30)
- Aggregate stats with learning insights (success rate, avg score correlation, best categories)
- Score comparison cards (Avg Score Successful vs Failed) to reveal what works
- Integrated into Launch Wizard (auto-tracks on launch completion)
- Navigation: Outcomes tab in sidebar
- APIs: POST /api/outcomes/track, GET /api/outcomes/my, PUT /api/outcomes/{id}, POST /api/outcomes/auto-label, GET /api/outcomes/stats
- Route: /outcomes

## Key API Endpoints
- Find Winning: GET /api/products/find-winning (auth required)
- Featured Product: GET /api/public/featured-product (public)
- Daily Opportunities: GET /api/dashboard/daily-opportunities (auth required)
- SEO Pages: GET /api/public/seo/{slug} (public)
- Outcomes: POST /api/outcomes/track, GET /api/outcomes/my, PUT /api/outcomes/{id}, POST /api/outcomes/auto-label, GET /api/outcomes/stats
- Stripe: /api/stripe/plans, /create-checkout-session, /feature-access, /webhook
- Products: /api/products, /api/products/{id}
- Stores: /api/stores/launch
- Ad Creatives: /api/ad-creatives/generate/{id}
- Reports: /api/reports/, /api/reports/*/pdf
- Referrals: /api/viral/referral/stats
- Ad Discovery: /api/ad-discovery/discover/{id}

## Upcoming Tasks
- Integrate real data for order_velocity_score (AliExpress API) and search_growth_score
- Build out Free Tools funnel (Dropshipping Profit Calculator enhancements)
- Programmatic SEO engine for auto-generating new pages
- Viral/shareable product pages
- CJ Dropshipping & Zendrop direct supplier API

## Backlog
- server.py refactoring into modular route files (7500+ lines)
- TikTok Creative Center / Meta Ad Library API integration
- Image/video quality improvements
- Comprehensive automated testing suite
- Enhanced store generation (auto logos, trust badges, review sections)
