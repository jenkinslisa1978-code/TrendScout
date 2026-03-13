# TrendScout - Product Requirements Document

## Positioning
**TrendScout — The Early Trend Intelligence Platform for Ecommerce**
"Discover winning products before they go viral."

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI, react-helmet-async
- Backend: FastAPI, MongoDB, APScheduler, aiohttp, Pillow
- Auth: Custom JWT | Payments: Stripe (GBP, live) | Email: Resend
- LLM: Emergent LLM Key via emergentintegrations

## Completed Phases

### Phase 1-33: Foundation through Production Readiness (DONE)

### Phase 34: Landing Page & Product Discovery (DONE)
- Landing page rewrite, enhanced trending products with category filters, sort, margin filter, confidence scores

### Phase 35: Image Intelligence System (DONE)
- Multi-source image fetching, quality filtering, optimization, local CDN

### Phase 36: Phase C — Viral & Upgrade Features (DONE)
- Daily Picks, Daily Usage Tracking, Freemium Upgrade Triggers, UpgradeModal, DailyUsageBanner

### Phase 37: Trend Alerts & Conversion Doubling (DONE)
- Threshold Alert Subscriptions, Scheduled Threshold Scanner, Enhanced OG Tags for social sharing

### Phase 38: Shopify Analyzer, Competitor Tracker & Onboarding (DONE - March 2026)
- **Shopify Store Analyzer**: Public tool at /tools/shopify-analyzer. POST /api/tools/analyze-store fetches any Shopify store's /products.json and returns product_count, store_size, categories, price_range, newest_products, top_vendors, assessment. Linked from /tools page.
- **Competitor Store Tracker**: Authenticated dashboard feature at /competitor-tracker. CRUD endpoints: GET/POST/DELETE /api/competitor-stores, POST /api/competitor-stores/{id}/refresh. Plan limits (free=2, starter=5, pro=15, elite=unlimited). Initial scan on add, product change tracking on refresh, scan history.
- **Enhanced Onboarding**: Added goals step (find products, build store, track competitors, research trends) as step 3 in 5-step onboarding flow.
- Verified: iteration_50 — 100% pass (15/15 backend, all frontend)

## Key API Endpoints

### Shopify Analyzer & Competitor Tracker
- `POST /api/tools/analyze-store` — Analyze any Shopify store (public)
- `GET /api/competitor-stores` — List tracked stores (auth)
- `POST /api/competitor-stores` — Add store with initial scan (auth)
- `POST /api/competitor-stores/{id}/refresh` — Re-scan a store (auth)
- `DELETE /api/competitor-stores/{id}` — Remove a store (auth)

### Threshold Alerts
- `GET /api/notifications/threshold-subscription` — Get subscription settings
- `PUT /api/notifications/threshold-subscription` — Update subscription
- `POST /api/notifications/scan-thresholds` — Admin: trigger threshold scan

### Daily & Usage
- `GET /api/public/daily-picks` — 5 curated daily products (public)
- `GET /api/user/daily-usage` — Daily insight usage
- `POST /api/user/track-insight` — Track insight view

### Image System
- `POST /api/images/enrich/{product_id}` — Enrich single product
- `POST /api/images/batch-enrich` — Batch enrichment (admin)

## Upcoming Tasks
- **TikTok Ad Intelligence (Part 9)**: Analyze TikTok ad patterns and trending content
- **Chrome Extension (Part 12)**: "TrendScout – Product & Store Analyzer"
- **AI Product Launch Simulator (Part 13)**: AI-powered trend prediction tool

## Future / Backlog
- Weekly Trend Digest email for re-engagement
- CDN migration (Cloudflare R2/S3) for image storage
- Server.py refactoring into route modules
- Redis cache migration

## DB Collections
- **products**: Core product data with launch_score, images, gallery_images
- **daily_usage**: Per-user daily insight consumption
- **threshold_subscriptions**: User alert subscriptions
- **competitor_stores**: Tracked competitor Shopify stores with scan history
- **notifications**: Alert notifications
- **profiles**: User profiles with plan, is_admin, onboarding data
- **subscriptions**: Stripe subscription data

## Integration Status
| Source | Status | Mode |
|--------|--------|------|
| CJ Dropshipping | LIVE | api |
| TikTok | LIVE | scraper |
| Shopify Analyzer | LIVE | products.json scraping |
| Meta Ad Library | Configured | estimation |
| Zendrop | Wired | estimation |
| Image Enrichment | LIVE | Amazon + web scraping |
