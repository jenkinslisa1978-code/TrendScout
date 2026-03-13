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
- Landing page rewrite, enhanced trending products with category filters, sort, margin filter, confidence scores

### Phase 35: Image Intelligence System (DONE - March 2026)
- Multi-source image fetching (Amazon, DuckDuckGo), quality filtering, optimization, local CDN

### Phase 36: Phase C — Viral & Upgrade Features (DONE - March 2026)
- Features link fix: Landing page nav links scroll correctly via scrollIntoView
- Daily Picks: GET /api/public/daily-picks returns 5 curated products, "Today's Picks" section on /trending-products
- Daily Usage Tracking: GET /api/user/daily-usage + POST /api/user/track-insight for freemium gating
- Freemium Upgrade Triggers: Supplier & Ad sections locked for free users with UpgradeModal
- Daily Usage Banner on dashboard for free/starter users
- Verified: iteration_48 — 100% pass

### Phase 37: Trend Alerts, Conversion Doubling & Social Sharing (DONE - March 2026)
- **Threshold Alert Subscriptions**: GET/PUT /api/notifications/threshold-subscription — users set score threshold, select categories, choose email/in-app channels
- **Scheduled Threshold Scanner**: scan_threshold_subscriptions task runs every 6 hours, scans products against user thresholds and creates notifications via notification_service
- **ThresholdSubscriptionCard**: UI on /alerts page with toggle, slider (30-95), category filters, email/in-app checkboxes
- **Conversion Doubling**: Product detail page now tracks insights via POST /api/user/track-insight on load
- **Enhanced OG Tags**: PublicProductPage has og:image, twitter:card=summary_large_image, product:price:amount/currency for rich social sharing
- Verified: iteration_49 — 100% pass (17/17 backend, all frontend)

## Key API Endpoints

### Threshold Alerts
- `GET /api/notifications/threshold-subscription` — Get user's threshold subscription settings
- `PUT /api/notifications/threshold-subscription` — Update subscription (enabled, score_threshold, categories, email_alerts, in_app_alerts)
- `POST /api/notifications/scan-thresholds` — Admin: trigger threshold scan manually

### Daily & Usage
- `GET /api/public/daily-picks` — 5 curated daily products (public, cached 30min)
- `GET /api/user/daily-usage` — User's daily insight usage and limits
- `POST /api/user/track-insight` — Track insight view, returns updated usage

### Image System
- `POST /api/images/enrich/{product_id}` — Enrich single product
- `POST /api/images/batch-enrich` — Batch enrichment (admin)
- `GET /api/images/{filename}` — Serve stored images

### Public (No Auth)
- `GET /api/public/trending-products` — Trending products with gallery
- `GET /api/public/product/{slug}` — Product detail with gallery
- `GET /api/public/categories` — Categories with counts

## Upcoming Tasks
- **Onboarding (Part 6)**: 3-step personalized onboarding flow
- **Killer Features (Part 9)**: Competitor Store Tracker, TikTok Ad Intelligence
- **Shopify Store Analyzer (Part 11)**: Analyze Shopify store URLs

## Future Phases
- Chrome Extension architecture
- AI Product Launch Simulator
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
- **daily_usage**: Per-user daily insight consumption (user_id, date, insights_used)
- **threshold_subscriptions**: User alert subscriptions (user_id, enabled, score_threshold, categories, email_alerts, in_app_alerts)
- **notifications**: Alert notifications with dedup, quiet hours, email delivery
- **profiles**: User profiles with plan, is_admin flags
- **subscriptions**: Stripe subscription data
