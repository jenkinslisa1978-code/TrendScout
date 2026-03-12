# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a fully automated, AI-powered e-commerce intelligence platform that helps users discover winning products, launch stores, and optimize marketing.

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI, html2canvas, react-helmet-async
- Backend: FastAPI, MongoDB, APScheduler, aiohttp
- Auth: Custom JWT | Payments: Stripe (GBP) | Email: Resend
- LLM: Emergent LLM Key (OpenAI GPT-4.1-mini) via emergentintegrations

## Completed Phases

### Phase 1-29: Foundation through Optimizer V2 (DONE)

### Phase 30: Growth & SEO Features (DONE - March 2026)
- Public Trending Products Page, Programmatic SEO Pages, Zendrop Integration

### Phase 31: SEO Infrastructure & Internal Linking (DONE - March 2026)
- Dynamic sitemap.xml (103 URLs), robots.txt, Public Categories API
- Category filter UI on /trending-products
- Internal linking between product pages
- Verified: iteration_45 — 100% pass

### Phase 32: Live API Integrations (DONE - March 2026)
- **CJ Dropshipping**: LIVE — Token auth flow with persistent file cache, price range parsing, v2 API response format fix. Health: healthy, mode: live
- **Meta Ad Library**: Token configured, awaiting Facebook App Ad Library API permission
- **Zendrop**: Wired into enrichment pipeline, estimation mode (awaiting API key)
- **AliExpress**: Not configured (awaiting API key)

## Integration Status
| Source | Status | Mode | Notes |
|--------|--------|------|-------|
| CJ Dropshipping | LIVE | api | Token cached, auto-refresh every 14 days |
| TikTok | LIVE | scraper | No API key needed |
| Meta Ad Library | Configured | estimation | Awaiting Ad Library API permission |
| Zendrop | Configured | estimation | Awaiting ZENDROP_API_KEY |
| AliExpress | Not configured | estimation | Awaiting ALIEXPRESS_API_KEY |

## Key API Endpoints

### Public (No Auth)
- `GET /api/public/trending-products` — SEO product grid
- `GET /api/public/product/{slug}` — Individual product SEO page
- `GET /api/public/categories` — Category list with counts
- `GET /api/sitemap.xml` — Dynamic XML sitemap
- `GET /api/robots.txt` — Crawl directives

### Data Integration
- `POST /api/data-integration/enrich/{product_id}` — Enrich with 5 sources
- `GET /api/data-integration/integration-health` — Health of all API integrations

## Upcoming Tasks
- **P2**: Server.py refactoring into dedicated route files
- Programmatic SEO V2 (richer structured data)

## Future/Backlog
- Enhanced Budget Optimizer (anomaly detection, budget pacing)
- Additional supplier integrations
- Enhanced store generation (auto logos, trust badges)
- Viral shareable public product pages
