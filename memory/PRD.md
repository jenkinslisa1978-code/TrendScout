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
- UI: Image carousel with thumbnails, hover zoom (scale-110), click-to-zoom fullscreen modal, nav arrows, dot indicators
- Confidence score badges: High Confidence (>=75), Emerging Opportunity (>=50), Experimental (<50)
- Background batch enrichment: POST /api/images/batch-enrich (admin only)
- Auto-regeneration on startup
- Verified: iteration_47 — 100% pass (12/12 backend, all frontend)

## Key API Endpoints

### Image System
- `POST /api/images/enrich/{product_id}` — Enrich single product (auth required)
- `POST /api/images/batch-enrich` — Batch enrichment (admin only)
- `GET /api/images/{filename}` — Serve stored images

### Public (No Auth)
- `GET /api/public/trending-products` — Now includes gallery_images, growth_rate, supplier_cost, retail_price
- `GET /api/public/product/{slug}` — Now includes gallery_images, growth_rate, tiktok_views
- `GET /api/public/categories` — Category list with counts
- `GET /sitemap.xml` — Static sitemap (regenerated on startup)

## Upcoming Tasks (Phase C — Viral & Upgrade Features)
- Daily Winning Product Feed on dashboard
- Viral product leaderboard on public page
- Free user unlock limits (3/day) with upgrade prompts
- Enhanced shareable product pages

## Future Phases
- **Phase D**: Shopify Store Analyzer
- **Phase E**: Competitor Store Tracker, TikTok Ad Intelligence
- **Phase F**: Chrome Extension architecture
- CDN migration (Cloudflare R2/S3) for image storage
- Server.py refactoring

## Integration Status
| Source | Status | Mode |
|--------|--------|------|
| CJ Dropshipping | LIVE | api |
| TikTok | LIVE | scraper |
| Meta Ad Library | Configured | estimation |
| Zendrop | Wired | estimation |
| AliExpress | Not configured | estimation |
| Image Enrichment | LIVE | Amazon + web scraping |
