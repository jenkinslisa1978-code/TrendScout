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

### Phase 12: AI Co-Pilot UX (DONE)
- "Find Me a Winning Product" Hero, 5-Step Launch Wizard, Beginner/Advanced Mode

### Phase 13: Predictive Engine & Daily Opportunities (DONE)
- 7-signal scoring, Daily Opportunities Panel, Trend stage classification

### Phase 14: Homepage, SEO & Free Tools (DONE)
- Premium landing page, programmatic SEO pages, 4 free tools (Profit Calculator, Saturation Checker, TikTok Analyzer, Trend Checker)

### Phase 15: Product Outcome Learning (DONE)
- Track outcomes, update metrics, auto-label, aggregate stats with insights

### Phase 16: Prediction Accuracy System (DONE)
- Dashboard card: accuracy %, correct/incorrect predictions, score buckets, learning insights

### Phase 17: Opportunity Radar (DONE)
- Real-time live feed: trend spikes, new ads, supplier demand, competition drops (30s refresh)

### Phase 18: Saturation Radar (DONE)
- Per-product risk (Low/Medium/High), saturation score 0-100, signals breakdown

### Phase 19: Homepage Design Polish (DONE)
- Soft gradients, rounded cards, modern typography, glass-morphism, smooth animations

### Phase 20: Competitor Store Intelligence (DONE)
- Stores detected, new stores (7d), price range, avg store age, competition impact

### Phase 21: Ad Winning Engine (DONE - March 2026)
**Full ad intelligence system on every product page:**
- **Winning Ad Patterns**: Hook types (primary/secondary with frequency, strength, confidence), video lengths, UGC vs studio ratio, CTA styles, music/sound patterns, engagement indicators
- **Ad Blueprint**: 5-scene filming plan (Hook → Product Intro → Demo → Transformation → CTA), 3 hook variations, 5 filming tips, optimized for TikTok/Reels/Shorts
- **Ad Performance Indicator**: Engagement level, activity trend, ad saturation, platform breakdown, actionable advice
- **Pattern-Informed Creatives**: Existing AI ad generation now shows "Generated using winning ad patterns" indicator
- APIs: GET /api/ad-engine/patterns/{id}, GET /api/ad-engine/blueprint/{id}, GET /api/ad-engine/performance/{id}

## Key API Endpoints
- Find Winning: GET /api/products/find-winning
- Featured Product: GET /api/public/featured-product
- Daily Opportunities: GET /api/dashboard/daily-opportunities
- Prediction Accuracy: GET /api/outcomes/prediction-accuracy
- Opportunity Radar: GET /api/radar/live-events
- Saturation: GET /api/products/{id}/saturation
- Competitor Intelligence: GET /api/products/{id}/competitor-intelligence
- Ad Patterns: GET /api/ad-engine/patterns/{id}
- Ad Blueprint: GET /api/ad-engine/blueprint/{id}
- Ad Performance: GET /api/ad-engine/performance/{id}
- Outcomes: POST/GET /api/outcomes/*
- SEO: GET /api/public/seo/{slug}
- Stripe: /api/stripe/*
- Products/Stores/Reports/Referrals/Ad Discovery: existing endpoints

## Upcoming Tasks
- **P5: Automated System Health Report**: Dashboard verifying data ingestion, scoring, store launch, ad generation, Stripe, scraper health

## Backlog
- server.py refactoring into modular route files (8000+ lines)
- Real data integrations: AliExpress order velocity, TikTok Creative Center, Meta Ad Library
- CJ Dropshipping & Zendrop supplier APIs
- Replace simulated tools (TikTok Analyzer, Trend Checker) with real API data
- Enhanced store generation (auto logos, trust badges)
