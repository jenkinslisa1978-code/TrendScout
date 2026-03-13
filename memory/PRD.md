# TrendScout - Product Requirements Document

## Positioning
**TrendScout — The Early Trend Intelligence Platform for Ecommerce**
"Discover winning products before they go viral."

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI, react-helmet-async
- Backend: FastAPI, MongoDB, APScheduler, aiohttp, Pillow
- Auth: Custom JWT | Payments: Stripe (GBP, live) | Email: Resend
- LLM: GPT 5.2 via emergentintegrations (Emergent LLM Key)

## Completed Phases

### Phase 1-33: Foundation through Production Readiness (DONE)
### Phase 34: Landing Page & Product Discovery (DONE)
### Phase 35: Image Intelligence System (DONE)
### Phase 36: Phase C — Viral & Upgrade Features (DONE)
### Phase 37: Trend Alerts & Conversion Doubling (DONE)
### Phase 38: Shopify Analyzer, Competitor Tracker & Onboarding (DONE)

### Phase 39: AI Simulator, TikTok Intelligence & Weekly Scans (DONE - March 2026)
- **AI Product Launch Simulator**: GET /api/ad-tests/ai-simulate/{product_id} — GPT 5.2 generates verdict, confidence score, 3-phase launch strategy (Testing/Scaling/Optimization with budgets), target audience, revenue projections (month 1/3/6), risk assessments, creative ad angles. Frontend has "Generate AI Launch Strategy" button that reveals phased strategy, audience, revenue charts, and creative angles.
- **TikTok Ad Intelligence**: GET /api/tools/tiktok-intelligence (public) — aggregates TikTok data showing viral products (1.1B+ views tracked), category performance with bar charts, trending ad patterns (TikTok Made Me Buy It, Oddly Satisfying, etc.). Dashboard page at /tiktok-intelligence with stats, ranked product list, and pattern cards.
- **Weekly Competitor Scans**: Scheduled task `weekly_competitor_scan` runs every Monday 6 AM. Re-scans all tracked Shopify stores via products.json, detects product count changes, and creates notifications for users when significant changes occur (3+ products added/removed).
- Verified: iteration_51 — 100% pass (23/23 backend, all frontend)

## Key API Endpoints

### AI Simulator
- `GET /api/ad-tests/simulate/{product_id}` — Base algorithmic simulation (auth)
- `GET /api/ad-tests/ai-simulate/{product_id}` — AI-powered simulation with GPT 5.2 (auth)

### TikTok Intelligence
- `GET /api/tools/tiktok-intelligence` — Viral products, category performance, patterns (public)

### Shopify Analyzer & Competitor Tracker
- `POST /api/tools/analyze-store` — Analyze any Shopify store (public)
- `GET /api/competitor-stores` — List tracked stores (auth)
- `POST /api/competitor-stores` — Add store with initial scan (auth)
- `POST /api/competitor-stores/{id}/refresh` — Re-scan a store (auth)
- `DELETE /api/competitor-stores/{id}` — Remove a store (auth)

### Threshold Alerts
- `GET /api/notifications/threshold-subscription` — Get subscription settings
- `PUT /api/notifications/threshold-subscription` — Update subscription

### Daily & Usage
- `GET /api/public/daily-picks` — 5 curated daily products (public)
- `GET /api/user/daily-usage` — Daily insight usage
- `POST /api/user/track-insight` — Track insight view

## Scheduled Tasks (18 total)
- `weekly_competitor_scan` — Monday 6 AM, re-scans all tracked stores
- `scan_threshold_subscriptions` — Every 6 hours, sends threshold alerts
- `generate_alerts` — Hourly, generates trend notifications
- Plus 15 other data ingestion, enrichment, and maintenance tasks

## Upcoming Tasks
- Chrome Extension — "TrendScout – Product & Store Analyzer" (deferred)
- Weekly Trend Digest email for re-engagement
- Enhanced shareable product cards with OG images

## Future / Backlog
- CDN migration (Cloudflare R2/S3) for image storage
- Server.py refactoring into route modules
- Redis cache migration
- Community growth features
- Advanced competitor diff tracking (product-level changes)

## Integration Status
| Source | Status | Mode |
|--------|--------|------|
| CJ Dropshipping | LIVE | api |
| TikTok | LIVE | scraper |
| GPT 5.2 | LIVE | emergentintegrations |
| Shopify Analyzer | LIVE | products.json |
| Meta Ad Library | Configured | estimation |
| Zendrop | Wired | estimation |
| Image Enrichment | LIVE | Amazon + web scraping |

## DB Collections
- products, daily_usage, threshold_subscriptions, competitor_stores
- notifications, profiles, subscriptions, stores, product_outcomes
