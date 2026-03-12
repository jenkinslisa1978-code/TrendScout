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
- Product Outcome Learning, Prediction Accuracy, Opportunity Radar, Saturation Radar
- Homepage Design Polish, Competitor Store Intelligence

### Phase 21: Ad Winning Engine (DONE - March 2026)
- Winning Ad Patterns, Ad Blueprint, Ad Performance Indicator

### Phase 22: Ad A/B Test Planner + Launch Simulator (DONE - March 2026)
- Ad variations, test plan, performance tracker, launch simulator

### Phase 23: Smart Budget Optimizer V1 (DONE - March 2026)
- Rule-based budget recommendation engine (increase/maintain/pause/kill/needs_more_data)
- Confidence scoring, conservative budget scaling, event sourcing
- BudgetOptimizerCard in Ad Test Planner, OptimizationDashboardWidget on Dashboard
- APIs: POST /api/optimization/recommend/{test_id}, GET /api/optimization/timeline/{test_id}, GET /api/optimization/dashboard-summary

### Phase 24: Automated System Health Dashboard (DONE - March 2026)
**Admin-only operational monitoring dashboard covering:**
- Data Ingestion: Opportunity Feed, Amazon Scraper, Google Trends Enrichment, Score Recomputation, Product Data Freshness
- API Integrations: TikTok API, AliExpress, Meta Ad Library, CJ Dropshipping, Zendrop
- Core Systems: Product Scoring Engine, Opportunity Feed Generation, Ad Blueprint Generator, Store Launch Pipeline
- Infrastructure: MongoDB, Stripe Payments, Job Scheduler, Job Queue Worker
- Each service: status (healthy/warning/error), last successful run, error message, uptime indicator
- Overall platform banner with aggregate stats
- API: GET /api/system-health (admin only)
- Frontend: /admin/health with expandable service rows, refresh capability

## Key API Endpoints
All previous endpoints plus:
- System Health: GET /api/system-health (admin auth)

## Upcoming Tasks (P0-P1)
- **P0: Real Data Integrations:** TikTok Creative Center, AliExpress velocity API, Meta Ad Library
- **P1: Smart Budget Optimizer V2 (Phases 2-4):** Optimization Timeline UI, auto-recommend mode, rule presets, feedback into Outcome Learning System
- **P1: Budget Optimizer Alerts:** Email/push notifications for kill/scale recommendations

## Backlog
- server.py refactoring into modular route files (8500+ lines)
- Replace simulated free tools (TikTok Analyzer, Trend Checker) with real API data
- CJ Dropshipping & Zendrop supplier APIs
- Enhanced store generation (auto logos, trust badges)
- Enhanced Budget Optimizer: anomaly detection, budget pacing, creative fatigue detection
- Viral shareable public product pages
- Programmatic SEO engine for trending product pages
