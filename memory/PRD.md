# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a predictive e-commerce intelligence platform that identifies winning products earlier than competitors. The system should feel like an AI e-commerce co-pilot — enabling users to launch products with 3 clicks: Find Product -> Launch Store -> Generate Ads -> Start Selling.

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI
- Backend: FastAPI, MongoDB, APScheduler, aiohttp
- Auth: Custom JWT | Payments: Stripe (live test keys) | Email: Resend
- Scraping: curl_cffi | Google Trends: pytrends
- LLM: Emergent LLM Key (OpenAI GPT-4.1-mini) via emergentintegrations

## Completed Phases

### Phase 1-22: Foundation through Ad Intelligence (DONE)
- Full pipeline: data, scoring, stores, ads, subscriptions, AI co-pilot, competitor intelligence

### Phase 23: Smart Budget Optimizer V1 (DONE)
- Rule-based budget recommendations, dashboard widget

### Phase 24: Automated System Health Dashboard (DONE)
- Admin-only /admin/health monitoring 18 services

### Phase 25: Data Credibility & Supplier Intelligence (DONE)
- Circuit breakers, fallback chains, source trust badges, CJ supplier intelligence

### Phase 26: Official API Integration Layer (DONE - March 2026)
- Meta Ad Library, CJ Dropshipping, AliExpress API clients with auto-upgrade
- 4-step fallback chain: Official API → Scraper → Estimation → Hardcoded
- Integration Status Dashboard at /admin/integrations

### Phase 27: Dashboard & Pricing Rework (DONE - March 2026)
**Verified and tested. All features working.**
- 3-tier pricing: Starter (£19), Pro (£39), Elite (£79) in GBP
- Redesigned dashboard: WhileYouWereAway, TrendScout Radar, AI Co-pilot, MissedOpportunities
- Feature gating across plans (Free/Starter/Pro/Elite)
- Shareable Product Cards (html2canvas export)
- Feature comparison table with all 4 tiers
- Simple/Advanced view mode toggle

## Current Data Source Status
| Source | Method | Mode | Status |
|--------|--------|------|--------|
| TikTok | Public scraper | Live | Healthy |
| Amazon | curl_cffi scraper | Live | Healthy |
| Google Trends | pytrends API | Live | Healthy |
| AliExpress | Estimation (API ready) | Estimated | Awaiting key |
| CJ Dropshipping | Estimation (API ready) | Estimated | Awaiting key |
| Meta Ad Library | Estimation (API ready) | Estimated | Awaiting token |

## Upcoming Tasks
- **P0: Smart Budget Optimizer V2:** Timeline UI, auto-recommend, rule presets
- **P1: Budget Optimizer Alerts:** Email/push for kill/scale recommendations
- **P2: TrendScout LaunchPad** (major feature): AI-assisted product launch workflow

## Backlog
- server.py refactoring into modular route files
- Zendrop supplier API integration
- Enhanced store generation (auto logos, trust badges)
- Enhanced Budget Optimizer: anomaly detection, budget pacing, creative fatigue
- Viral shareable public product pages
- Programmatic SEO engine
