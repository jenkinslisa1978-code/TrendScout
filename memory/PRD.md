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
- Landing page overhaul, Radar Alert System, Upgrade prompts, Onboarding wizard, LaunchPad

### Phase 29: Smart Budget Optimizer V2 (DONE - March 2026)
- Rule Presets, Auto-Recommend Mode, Optimization Timeline, Budget Alerts, Weekly Radar Digest

### Phase 30: Growth & SEO Features (DONE - March 2026)
- Public Trending Products Page: /trending-products (SEO-optimized, no auth needed)
- Programmatic SEO Pages: /trending/:slug with meta tags, JSON-LD, related products
- Zendrop Supplier Integration: Wired into enrichment pipeline with estimation fallback
- **Verified:** iteration_44 — 100% pass (20/20 backend, all frontend)

### Phase 31: SEO Infrastructure & Internal Linking (DONE - March 2026)
- **Dynamic sitemap.xml**: 103 URLs (6 static + ~97 product pages) at /api/sitemap.xml
- **robots.txt**: Proper crawl directives at /robots.txt and /api/robots.txt
- **Public Categories API**: /api/public/categories with aggregation pipeline
- **Category Filter UI**: Filterable strip on /trending-products with counts, URL param support
- **Internal Linking**: Category badges on product pages link to filtered views, related products cross-link
- **Meta Ad Library Token**: Configured (awaiting Facebook App permission approval for Ad Library API)
- **Verified:** iteration_45 — 100% pass (17/17 backend, all frontend)

## Key API Endpoints

### Public (No Auth)
- `GET /api/public/trending-products` — SEO product grid
- `GET /api/public/product/{slug}` — Individual product SEO page
- `GET /api/public/categories` — Category list with counts
- `GET /api/public/featured-product` — Landing page demo card
- `GET /api/sitemap.xml` — Dynamic XML sitemap
- `GET /api/robots.txt` — Crawl directives

### Optimizer V2
- `GET /api/optimization/presets` — Available strategy presets
- `POST /api/optimization/set-preset` — Set user's preferred preset
- `POST /api/optimization/toggle-auto-recommend` — Toggle auto mode
- `GET /api/optimization/settings` — Get current settings

### Data Integration
- `POST /api/data-integration/enrich/{product_id}` — Enrich with 5 sources
- `GET /api/data-integration/integration-health` — Health of all API integrations

## Supplier Sources (all estimation mode, auto-activate with API keys)
- AliExpress, CJ Dropshipping, Zendrop, Meta Ad Library, TikTok (live scraper)

## Upcoming Tasks
- **P2: Server.py refactoring** — Migrate routes to dedicated files (when needed)

## Future/Backlog
- Programmatic SEO V2 (richer content, more structured data)
- Additional supplier integrations
- Enhanced Budget Optimizer (anomaly detection, budget pacing, creative fatigue)
- Enhanced store generation (auto logos, trust badges)
- Viral shareable public product pages
