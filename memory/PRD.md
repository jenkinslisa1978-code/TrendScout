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
- Generate 3 ad variations per product, test plan, performance tracker, auto-determine winner
- Launch Simulator: profit estimates, CPC/CPA, break-even timeline, risk classification

### Phase 23: Smart Budget Optimizer V1 (DONE - March 2026)
**Rule-Based Budget Recommendation Engine:**
- Analyzes ad test variation results and generates actionable budget recommendations
- 5 actions: increase_budget (scale 20-40%), maintain, pause, kill, needs_more_data
- Confidence scoring (0-1) based on spend volume, click volume, purchase volume, signal agreement
- Benchmarks: CTR excellent 2.5%, good 1.8%, poor 1.0%; CPC good £0.50, poor £1.50; ATC good 8%, poor 3%
- Conservative budget scaling tiers (£10→£15→£20→£25→£35→£50→£70→£100→£140)
- Event sourcing: every recommendation logged to optimization_events collection
- Frontend: BudgetOptimizerCard in AdTestPlanner Results tab, OptimizationDashboardWidget on Dashboard
- APIs: POST /api/optimization/recommend/{test_id}, GET /api/optimization/timeline/{test_id}, GET /api/optimization/dashboard-summary

## Key API Endpoints
All previous endpoints plus:
- Budget Optimizer: POST /api/optimization/recommend/{test_id} (auth)
- Optimization Timeline: GET /api/optimization/timeline/{test_id} (auth)
- Dashboard Summary: GET /api/optimization/dashboard-summary (auth)

## Upcoming Tasks (P0-P1)
- **Smart Budget Optimizer V2 (Phases 2-4):** Optimization Timeline UI, auto-recommend mode, rule presets, feedback into Outcome Learning System
- **Automated System Health Report:** Dashboard monitoring data ingestion, scoring, store launch, ad generation, Stripe, scraper health

## Backlog
- server.py refactoring into modular route files (8500+ lines)
- Real data: AliExpress order velocity API, TikTok Creative Center, Meta Ad Library
- Replace simulated free tools (TikTok Analyzer, Trend Checker) with real API data
- CJ Dropshipping & Zendrop supplier APIs
- Enhanced store generation (auto logos, trust badges)
- Enhanced Budget Optimizer: anomaly detection, budget pacing, creative fatigue detection
- Viral shareable public product pages
- Programmatic SEO engine for trending product pages
