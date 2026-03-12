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

### Phase 1-27: Foundation through Dashboard & Pricing Rework (DONE)

### Phase 28: Launch Readiness (DONE — March 2026)
- Landing page overhaul with hero, testimonials, opportunity detection
- Radar Alert System (backend endpoints + in-app notifications)
- Upgrade prompts (LimitHitBanner, InsightLockedNudge)
- Interactive 4-step onboarding wizard
- TrendScout LaunchPad with pricing strategy, Shopify export, A/B test plan, launch checklist

### Phase 29: Smart Budget Optimizer V2 (DONE — March 2026)
**All features verified via testing_agent (iteration_42, 100% pass)**
- **Rule Presets:** Beginner (conservative), Balanced (standard), Aggressive (fast scaling)
  - Each adjusts CTR/CPC/CPA thresholds, scale factor, and kill thresholds
  - User's preferred preset saved to profile and persists
- **Auto-Recommend Mode:** Toggle that marks the user for continuous recommendation generation
  - Visual green "active" indicator when enabled
- **Optimization Timeline:** Full page at /optimization/:testId showing chronological events
  - Each event shows Day #, action (Scale/Pause/Kill/Monitor), metrics, confidence
  - Timeline line with color-coded action dots
- **Budget Optimizer Alerts:** In-app alerts generated when recommendations trigger pause/scale/kill
  - Alert list with unread count, mark-all-read functionality
  - Also creates notifications via the existing notification service
- **Weekly Radar Digest:** Scheduled task (Monday 8AM UTC)
  - Sends top 5 radar-detected products to all users
  - Includes product name, launch score, trend stage, estimated margin
  - CTA to view full analysis in TrendScout

### Key API Endpoints Added (Phase 29)
- `GET /api/optimization/presets` — Available strategy presets
- `POST /api/optimization/set-preset` — Set user's preferred preset
- `POST /api/optimization/toggle-auto-recommend` — Toggle auto mode
- `GET /api/optimization/settings` — Get current settings
- `GET /api/optimization/alerts` — Optimizer alerts with unread count
- `POST /api/optimization/alerts/mark-read` — Mark alerts read
- `GET /api/optimization/timeline/{test_id}` — Timeline events

### Frontend Pages Added (Phase 29)
- `/optimization` — Smart Budget Optimizer settings + alerts
- `/optimization/:testId` — Optimization timeline for specific test
- Sidebar: "Budget Optimizer" under ELITE FEATURES

## Upcoming Tasks
None in immediate queue — all user-requested features complete.

## Future/Backlog
- **P1: Public Trending Products Page** — Display radar products publicly for SEO
- **P2: Programmatic SEO pages** — Auto-generated pages for trending products
- **P2: Zendrop supplier integration**
- **P2: Enhanced store generation** (auto logos, trust badges)
- **P2: Enhanced Budget Optimizer** — anomaly detection, budget pacing, creative fatigue
- **P3: Viral shareable public product pages**
- server.py refactoring (only when it blocks development)
