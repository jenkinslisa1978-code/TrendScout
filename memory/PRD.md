# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a fully automated, AI-powered e-commerce intelligence platform that helps users discover winning products, launch stores, and optimize marketing. Core value proposition: "Find winning products early and launch them fast."

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI, html2canvas
- Backend: FastAPI, MongoDB, APScheduler, aiohttp
- Auth: Custom JWT | Payments: Stripe (GBP) | Email: Resend
- Scraping: curl_cffi | Google Trends: pytrends
- LLM: Emergent LLM Key (OpenAI GPT-4.1-mini) via emergentintegrations

## Pricing Structure (GBP)
| Plan | Price | Key Features |
|------|-------|-------------|
| Free | £0 | Limited insights, 1 store, preview reports |
| Starter | £19/mo | 5 analyses/day, 3 simulations/day, 2 stores, basic ads |
| Pro | £39/mo | Unlimited analysis, full supplier intel, ad A/B testing, 5 stores |
| Elite | £79/mo | Everything + Budget Optimizer, LaunchPad, Radar Alerts, unlimited stores |

## Completed Phases

### Phase 1-22: Foundation through Ad Intelligence (DONE)
### Phase 23: Smart Budget Optimizer V1 (DONE)
### Phase 24: System Health Dashboard (DONE)
### Phase 25: Data Credibility & Supplier Intelligence (DONE)
### Phase 26: Official API Integration Layer (DONE)
### Phase 27: Dashboard & Pricing Rework (DONE)

### Phase 28: Launch Readiness — March 2026 (DONE)

**Phase A — Landing Page Overhaul (DONE, TESTED)**
- Hero: "Find winning products early. Launch them faster."
- CTA: "Start with Starter — £19/mo"
- Sections: How It Works, Live Demo Card, Opportunity Detection, Pricing, Testimonials, Final CTA
- Value prop badge: "AI Ecommerce Launch Assistant"

**Phase B — Radar Alert System (DONE, TESTED)**
- Backend: POST /api/notifications/radar-scan (admin-only background task)
- Backend: GET /api/notifications/radar-detections (list radar-detected products)
- Backend: POST /api/notifications/radar-digest (email digest with detected products)
- RADAR_DETECTED notification type added to notification service
- Products marked with radar_detected flag when crossing score thresholds

**Phase C — Upgrade Prompts & Conversion (DONE, TESTED)**
- LimitHitBanner: shown when Starter users exhaust daily limits
- InsightLockedNudge: inline upgrade nudge for locked features
- Correctly hidden for Elite/Pro users, shown for Starter/Free

**Phase D — Onboarding Enhancement (DONE, TESTED)**
- 4-step interactive wizard: Experience Level → Niche Preferences → First Opportunity → First Analysis
- Saves experience_level and preferred_niches to user profile
- Fetches real product data for Step 3
- Accessible (DialogTitle added)

**Phase E — LaunchPad Architecture (DONE, TESTED)**
- Renamed to "TrendScout LaunchPad" with branded header
- Step 1: Product Intelligence + Pricing Strategy (supplier cost, recommended price, margin)
- Step 2: Supplier Confirmation
- Step 3: Store Assets + Shopify Import File section
- Step 4: Ad Creative Pack + A/B Test Plan (3 phases: Testing, Validation, Scale)
- Step 5: Launch Checklist (7 items: 4 auto-checked, 3 manual)

**Phase F — Final Launch Readiness (DONE, TESTED)**
- All 12 spec areas verified via testing_agent_v3_fork
- Backend: 16/16 API tests passed
- Frontend: All features verified via Playwright

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
- **P1: Smart Budget Optimizer V2:** Timeline UI, auto-recommend, rule presets
- **P1: Budget Optimizer Alerts:** Email/push for kill/scale recommendations

## Backlog
- server.py refactoring into modular route files
- Zendrop supplier API integration
- Enhanced store generation (auto logos, trust badges)
- Enhanced Budget Optimizer: anomaly detection, budget pacing, creative fatigue
- Viral shareable public product pages
- Programmatic SEO engine
