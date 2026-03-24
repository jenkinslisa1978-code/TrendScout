# TrendScout PRD

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers.

## Core Positioning
"Find products that can actually sell in the UK."

## Tech Stack
- Frontend: React (CRA with Craco) + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-5.2 (via Emergent LLM Key)
- Payments: Stripe (GBP), Email: Resend
- Analytics: GTM (GTM-5V7G36GN) → GA4 (G-S9J8EPWKF9), consent-gated; PostHog
- Serving: Custom Node.js static server (serve.js) with prerendered content
- Frontend builds to static files, served by serve.js (NOT hot-reload in preview)

## Architecture Notes
- Frontend must be rebuilt after changes: `cd /app/frontend && yarn build && sudo supervisorctl restart frontend`
- Backend has hot-reload via supervisor
- OAuth system in `services/oauth_service.py` auto-detects env-var credentials per platform
- Shopify is first platform with full one-click OAuth (SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET in .env)
- Other platforms fall back to manual credential forms

## Completed Work

### One-Click OAuth Connections (March 2026)
- **Shopify OAuth simplified**: User enters store domain → clicks "Connect with Shopify" → redirected to Shopify consent → token stored. No client_id/secret needed from user.
- **Scalable OAuth architecture**: All platforms have `env_prefix` config. Adding `PLATFORM_CLIENT_ID` + `PLATFORM_CLIENT_SECRET` to .env enables one-click OAuth for any platform.
- **Product sync from Shopify**: POST `/api/shopify/sync-products` pulls active products from connected Shopify store into TrendScout. GET `/api/shopify/synced-products` returns synced product list.
- **Frontend auto-detects OAuth readiness**: Platforms with `oauth_ready=true` show simplified connect button; others show manual credential form.
- **Fixed TOKEN_ENCRYPTION_KEY format**: Changed from hex to valid Fernet base64 key.
- Test report: /app/test_reports/iteration_121.json (100% pass rate)

### QA Audit & Bug Fixes (March 2026)
- Fixed mobile horizontal overflow on homepage (overflow-x: clip on body, flex-wrap on footer links)
- Verified login error handling works correctly
- Full e2e audit completed: /app/test_reports/iteration_120.json (100% pass)

### GTM Integration (March 2026)
- GTM container GTM-5V7G36GN installed, consent-gated
- GA4 G-S9J8EPWKF9 managed through GTM, standalone removed
- analytics.js uses dataLayer

### Crawlability Infrastructure (March 2026)
- Custom serve.js + prerender.js: 39 pages with unique content

### Core Platform
- Product discovery, UK Viability Score, AI analysis
- Stripe subscriptions, admin tools, OAuth, WebSocket notifications

## Key API Endpoints
- POST /api/shopify/oauth/init — Start Shopify OAuth (only shop_domain needed)
- POST /api/shopify/sync-products — Pull products from connected Shopify store
- GET /api/shopify/synced-products — Get synced product list
- GET /api/oauth/platforms — List all platforms with oauth_ready status
- GET /api/connections/platforms — Platform list enriched with oauth_ready flag

## Key Files
- backend/services/oauth_service.py — Platform configs, env-var credential detection
- backend/routes/shopify_oauth.py — Shopify OAuth + product sync
- backend/routes/oauth.py — Generic OAuth for all platforms
- backend/routes/connections.py — Connection management (enriched with oauth_ready)
- frontend/src/pages/PlatformConnectionsPage.jsx — OAuth-aware connection UI

## Remaining Tasks
- P1: Add app credentials for other platforms (Meta, Etsy, TikTok, Google Ads) to enable one-click OAuth
- P1: Configure GA4 tag inside GTM console (G-S9J8EPWKF9) — User task
- P1: Configure Resend webhook URL — User task
- P2: OAuth data sync from other connected stores (Etsy, WooCommerce, etc.)
- P2: Show synced Shopify products in the dashboard (UI for synced products)
- P3: Token refresh logic for expired OAuth tokens
- P3: Webhook subscriptions for real-time product/order updates

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
