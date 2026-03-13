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

### Phase 34: Landing Page & Product Discovery (DONE - March 2026)
- Landing page rewrite: "Early Trend Intelligence" positioning, hero, How It Works, Winning Products, Built For, Pricing, Testimonials
- Enhanced trending products: category filters, sort (5 options), margin filter, confidence score badges
- Verified: iteration_46 — 100% pass

### Phase 35: Image Intelligence System (DONE - March 2026)
- Multi-source image fetching: Amazon product pages, DuckDuckGo web search
- Image quality filtering: min 400px, file size check, deduplication by hash
- Image optimization: crop to square (800x800), JPEG compression (82%), Pillow processing
- Local storage served via /api/images/ (30+ images enriched)
- Multi-image gallery support: gallery_images field in product documents
- UI: Image carousel with thumbnails, hover zoom, click-to-zoom fullscreen modal
- Verified: iteration_47 — 100% pass

### Phase 36: Phase C — Viral & Upgrade Features (DONE - March 2026)
- **Features link fix**: Landing page nav links (#features, #pricing) now smooth-scroll correctly via scrollIntoView
- **Daily Picks**: Public endpoint GET /api/public/daily-picks returns 5 curated products, deterministic per day (seeded by date). Renders as "Today's Picks" section on /trending-products
- **Daily Usage Tracking**: GET /api/user/daily-usage + POST /api/user/track-insight endpoints for freemium gating. Free users limited to 2 insights/day, Starter to 5
- **Feature-access enhanced**: GET /api/stripe/feature-access now returns max_analyses_daily and insights_used_today
- **Freemium Upgrade Triggers**: Supplier Intelligence and Ad Creative sections locked behind plan checks with blur overlay + UpgradeModal component
- **Daily Usage Banner**: Dashboard shows remaining insights count with progress bar and upgrade CTA for free/starter users
- **UpgradeModal**: Context-aware modal showing plan features, pricing, and CTA for supplier, ads, insights, daily_limit, early_trends, launch_simulator
- Verified: iteration_48 — 100% pass (14/14 backend, all frontend)

## Key API Endpoints

### Image System
- `POST /api/images/enrich/{product_id}` — Enrich single product (auth required)
- `POST /api/images/batch-enrich` — Batch enrichment (admin only)
- `GET /api/images/{filename}` — Serve stored images

### Daily & Usage
- `GET /api/public/daily-picks` — 5 curated daily products (public, cached 30min)
- `GET /api/user/daily-usage` — User's daily insight usage and limits (auth required)
- `POST /api/user/track-insight` — Track insight view, returns updated usage (auth required)

### Public (No Auth)
- `GET /api/public/trending-products` — Includes gallery_images, growth_rate, supplier_cost, retail_price
- `GET /api/public/product/{slug}` — Includes gallery_images, growth_rate, tiktok_views
- `GET /api/public/categories` — Category list with counts
- `GET /sitemap.xml` — Static sitemap (regenerated on startup)

## Upcoming Tasks
- **Trend Alerts Enhancement**: Email/in-app alerts when product virality score crosses threshold
- **Conversion Doubling (Part 15)**: Full daily unlock limit enforcement across all product pages
- **Enhanced shareable product pages**: Social sharing with OG images

## Future Phases
- **Phase D**: Onboarding (3-step personalized flow)
- **Phase E**: Killer Features — Competitor Store Tracker, TikTok Ad Intelligence
- **Phase F**: Shopify Store Analyzer
- **Phase G**: Chrome Extension architecture
- **Phase H**: AI Product Launch Simulator
- CDN migration (Cloudflare R2/S3) for image storage
- Server.py refactoring into route modules
- Redis cache migration

## Integration Status
| Source | Status | Mode |
|--------|--------|------|
| CJ Dropshipping | LIVE | api |
| TikTok | LIVE | scraper |
| Meta Ad Library | Configured | estimation |
| Zendrop | Wired | estimation |
| AliExpress | Not configured | estimation |
| Image Enrichment | LIVE | Amazon + web scraping |

## DB Collections
- **products**: Core product data with launch_score, images, gallery_images
- **daily_usage**: Tracks per-user daily insight consumption (user_id, date, insights_used)
- **profiles**: User profiles with plan, is_admin flags
- **subscriptions**: Stripe subscription data
