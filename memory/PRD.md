# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a predictive e-commerce intelligence platform that identifies winning products earlier than competitors. The system should feel like an AI e-commerce co-pilot — enabling users to launch products with 3 clicks: Find Product → Launch Store → Generate Ads → Start Selling.

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

### Phase 12: AI Co-Pilot UX (DONE - March 2026)
**"Find Me a Winning Product" Hero:**
- Large CTA button on dashboard → auto-selects highest launch_score product
- Shows product name, launch score, success probability, estimated profit
- Shows auto-matched supplier with cost, shipping origin, delivery estimate
- "Launch This Product" button → enters Launch Wizard
- Alternative product suggestions
- API: GET /api/products/find-winning

**5-Step Product Launch Wizard:**
- Route: /launch/:productId
- Step 1: Select Product (shows name, scores, trend stage with tooltips)
- Step 2: Confirm Supplier (auto-matched, selectable options)
- Step 3: Preview Store (auto-generated with branding, policies, checkout)
- Step 4: Generate Ads (AI creates TikTok scripts, FB copy, IG captions)
- Step 5: Launch (store goes live, view store button)
- Each step has beginner-friendly explanations and tooltips

**Beginner / Advanced Mode Toggle:**
- Persists in localStorage as 'trendscout_view_mode'
- Toggle component on Dashboard and Discover pages
- **Beginner (Simple) Mode:**
  - Dashboard: Shows hero, top products, stores only (hides early trends, market opportunities, intelligence panels)
  - Discover: Simplified cards (launch score + profit + trend badge), "Launch Product" button → wizard
- **Advanced Mode:**
  - Full analytics: early trends, market opportunities, competition, intelligence panels
  - "Build Store" button opens StoreBuilderModal

## Key API Endpoints
- Find Winning: GET /api/products/find-winning (auth required)
- Stripe: /api/stripe/plans, /create-checkout-session, /feature-access, /webhook
- Products: /api/products, /api/products/{id}
- Stores: /api/stores/launch
- Ad Creatives: /api/ad-creatives/generate/{id}
- Reports: /api/reports/, /api/reports/*/pdf
- Referrals: /api/viral/referral/stats
- Ad Discovery: /api/ad-discovery/discover/{id}

## Upcoming Tasks
- **P1: Predictive Engine Enhancement** — Add search_growth_score + order_velocity_score, update formula weights, recompute all scores, improve trend classification UI (Exploding/Emerging/Rising/Stable/Declining)
- **P2: Tooltip Education System** — Contextual tooltips explaining Supplier, Launch Score, Trend Stage, Profit Estimate
- **P2: Enhanced Store Generation** — Auto-generate logo, brand colors, trust badges, review sections

## Backlog
- server.py refactoring into modular route files (7000+ lines)
- CJ Dropshipping & Zendrop direct supplier API
- TikTok Creative Center / Meta Ad Library API integration
- Image/video quality improvements
