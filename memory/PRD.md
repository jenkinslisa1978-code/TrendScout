# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a fully automated, AI-powered e-commerce intelligence platform that helps users discover winning products, launch stores, and optimize marketing. Core value proposition: "Find winning products early and launch them fast."

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI, html2canvas, react-helmet-async
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

### Phase 28: Launch Readiness (DONE - March 2026)
- Landing page overhaul with hero, testimonials, opportunity detection
- Radar Alert System (backend endpoints + in-app notifications)
- Upgrade prompts (LimitHitBanner, InsightLockedNudge)
- Interactive 4-step onboarding wizard
- TrendScout LaunchPad with pricing strategy, Shopify export, A/B test plan, launch checklist

### Phase 29: Smart Budget Optimizer V2 (DONE - March 2026)
- Rule Presets: Beginner (conservative), Balanced (standard), Aggressive (fast scaling)
- Auto-Recommend Mode: Toggle for continuous recommendation generation
- Optimization Timeline: /optimization/:testId showing chronological events
- Budget Optimizer Alerts: In-app alerts for pause/scale/kill actions
- Weekly Radar Digest: Scheduled task (Monday 8AM UTC)

### Phase 30: Growth & SEO Features (DONE - March 2026)
- Public Trending Products Page: /trending-products (SEO-optimized, no auth needed)
- Programmatic SEO Pages: /trending/:slug with meta tags, JSON-LD, related products
- Zendrop Supplier Integration: Wired into enrichment pipeline with estimation fallback

**Verification (iteration_44):** All features verified — 100% pass rate (20/20 backend, all frontend)

## Key API Endpoints

### Public (No Auth)
- `GET /api/public/trending-products` — SEO product grid
- `GET /api/public/product/{slug}` — Individual product SEO page
- `GET /api/public/featured-product` — Landing page demo card

### Optimizer V2
- `GET /api/optimization/presets` — Available strategy presets
- `POST /api/optimization/set-preset` — Set user's preferred preset
- `POST /api/optimization/toggle-auto-recommend` — Toggle auto mode
- `GET /api/optimization/settings` — Get current settings
- `GET /api/optimization/alerts` — Optimizer alerts with unread count
- `POST /api/optimization/alerts/mark-read` — Mark alerts read
- `GET /api/optimization/timeline/{test_id}` — Timeline events

### Data Integration
- `POST /api/data-integration/enrich/{product_id}` — Enrich with all 5 sources (AliExpress, CJ, Zendrop, TikTok, Meta)
- `GET /api/data-integration/integration-health` — Health of all API integrations

## Supplier Sources
All run in estimation mode (no API keys). Will auto-activate when keys are provided:
- AliExpress (Official API client)
- CJ Dropshipping (Official API client)
- Zendrop (Official API client, integrated March 2026)
- Meta Ad Library (Official API client)
- TikTok (Public scraper, no key needed)

## Upcoming Tasks
- **P1: Sitemap.xml generation** — Dynamic sitemap for public trending product pages
- **P1: Internal linking** — Cross-links between SEO product pages
- **P2: Server.py refactoring** — Migrate routes to dedicated files

## Future/Backlog
- Programmatic SEO V2 (richer content, more structured data)
- Additional supplier integrations
- Enhanced Budget Optimizer (anomaly detection, budget pacing, creative fatigue)
- Enhanced store generation (auto logos, trust badges)
- Viral shareable public product pages
