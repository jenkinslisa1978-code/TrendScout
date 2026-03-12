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

### Phase 12-14: AI Co-Pilot, Predictive Engine, SEO (DONE)
- "Find Me a Winning Product" Hero, 5-Step Launch Wizard, Beginner/Advanced Mode
- 7-signal scoring, Daily Opportunities, Trend stage classification
- Premium landing page, programmatic SEO pages, 4 free tools

### Phase 15-20: Intelligence Systems (DONE)
- Product Outcome Learning: track, update metrics, auto-label, stats
- Prediction Accuracy: compare predictions vs outcomes
- Opportunity Radar: live signal feed (30s refresh)
- Saturation Radar: per-product risk (0-100 score)
- Homepage Design Polish: soft gradients, animations, glass-morphism
- Competitor Store Intelligence: stores, pricing, age, competition impact

### Phase 21: Ad Winning Engine (DONE - March 2026)
- Winning Ad Patterns: hook types, video lengths, UGC ratio, CTA styles, engagement, confidence scores
- Ad Blueprint: 5-scene filming plan, 3 hook variations, filming tips
- Ad Performance Indicator: engagement level, activity trend, saturation, platform breakdown

### Phase 22: Ad A/B Test Planner + Launch Simulator (DONE - March 2026)
**Ad A/B Test System:**
- Generate 3 ad variations (different hooks) per product with full scripts
- Step-by-step test plan (6 steps + 4 metrics with good/poor thresholds)
- Performance tracker: record spend, clicks, CTR, add-to-cart, purchases per variation
- Auto-determine winner by CTR comparison
- Complete test & save learnings to ad_learnings collection for future model improvement
- Dedicated /ad-tests page listing all active/completed tests with winner info
- APIs: GET /variations/{id}, POST /create, GET /my, PUT /{id}/results, POST /{id}/complete

**Product Launch Simulator:**
- Estimates: profit per sale, conversion rate, CPC, CPA, daily sales range, daily profit range, break-even timeline
- Uses: launch_score, trend_stage, competition, supplier cost, ad activity, historical outcomes
- Potential classification: High / Moderate / Risky with risk factors
- Beginner-friendly guidance text ("Start small with £15-20 daily budget...")
- Visual profit projection bar + expandable simulation inputs
- API: GET /api/ad-tests/simulate/{id}

## Key API Endpoints
All previous endpoints plus:
- Ad Variations: GET /api/ad-tests/variations/{id} (public)
- Create Test: POST /api/ad-tests/create (auth)
- My Tests: GET /api/ad-tests/my (auth)
- Record Results: PUT /api/ad-tests/{id}/results (auth)
- Complete Test: POST /api/ad-tests/{id}/complete (auth)
- Simulate Launch: GET /api/ad-tests/simulate/{id} (auth)

## Upcoming Tasks
- **P5: Automated System Health Report**: Dashboard verifying data ingestion, scoring, store launch, ad generation, Stripe, scraper health

## Backlog
- server.py refactoring into modular route files (8500+ lines)
- Real data: AliExpress order velocity API, TikTok Creative Center, Meta Ad Library
- Replace simulated free tools (TikTok Analyzer, Trend Checker) with real API data
- CJ Dropshipping & Zendrop supplier APIs
- Enhanced store generation (auto logos, trust badges)
