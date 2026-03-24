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
- Analytics: GTM (GTM-5V7G36GN) → GA4 (G-S9J8EPWKF9), consent-gated
- Serving: Custom Node.js static server (serve.js) with prerendered content
- Frontend builds to static files: `cd /app/frontend && yarn build && sudo supervisorctl restart frontend`

## Architecture Notes
- OAuth system in `services/oauth_service.py` auto-detects env-var credentials per platform
- Shopify is first platform with full one-click OAuth (SHOPIFY_CLIENT_ID/SECRET in .env)
- Token refresh system: `refresh_platform_token()` and `get_valid_token()` handle expiry
- Webhook system for real-time Shopify product sync (HMAC-verified)
- Health check auto-refreshes tokens on 401 responses

## Completed Work

### Synced Products Dashboard + Webhooks + Token Refresh (March 2026)
- **Shopify Products page** (`/shopify-products`): Full dashboard view with product grid, search, sort, empty state, sync button. Shows products pulled from connected Shopify store with images, prices, inventory, variants.
- **Sidebar navigation**: "Shopify Products" link added between "My Stores" and "Connections"
- **Shopify webhooks**: Auto-registered after OAuth callback. Handles `products/create`, `products/update`, `products/delete`, `app/uninstalled`. HMAC-verified for security.
- **Token refresh**: `refresh_platform_token()` uses refresh tokens to renew expired access tokens. `get_valid_token()` auto-refreshes before expiry. Health check triggers refresh on 401.
- **App uninstall cleanup**: When user uninstalls from Shopify, all connections and synced products are automatically removed.
- Test report: /app/test_reports/iteration_122.json (100% pass rate)

### One-Click OAuth Connections (March 2026)
- Shopify OAuth simplified: User enters store domain → clicks "Connect with Shopify" → redirected to Shopify consent → token stored
- Scalable OAuth pattern: Adding `PLATFORM_CLIENT_ID` + `PLATFORM_CLIENT_SECRET` enables one-click OAuth for any platform
- Product sync endpoints: `POST /api/shopify/sync-products`, `GET /api/shopify/synced-products`
- Test report: /app/test_reports/iteration_121.json (100% pass rate)

### QA Audit & Bug Fixes (March 2026)
- Fixed mobile horizontal overflow (overflow-x: clip, flex-wrap footer)
- Verified login error handling
- Test report: /app/test_reports/iteration_120.json (100% pass rate)

### Previous Work
- GTM integration (consent-gated), crawlability infrastructure (39 prerendered pages)
- Core platform: Product discovery, UK Viability Score, AI analysis, Stripe subscriptions, admin tools

## Key API Endpoints
- POST /api/shopify/oauth/init — Start Shopify OAuth (only shop_domain needed)
- POST /api/shopify/sync-products — Pull products from connected Shopify store
- GET /api/shopify/synced-products — Get synced product list
- POST /api/shopify/webhooks/{topic} — Webhook handlers (products-create/update/delete, app-uninstalled)
- GET /api/oauth/platforms — List all platforms with oauth_ready status
- GET /api/connections/platforms — Platform list enriched with oauth_ready
- POST /api/connections/health-check — Verify connections, auto-refresh expired tokens

## Key Files
- backend/services/oauth_service.py — Platform configs, credential detection, token refresh
- backend/routes/shopify_oauth.py — Shopify OAuth + product sync
- backend/routes/shopify_webhooks.py — Webhook handlers (HMAC-verified)
- backend/routes/oauth.py — Generic OAuth for all platforms
- backend/routes/connections.py — Connection management with health check + auto-refresh
- frontend/src/pages/ShopifyProductsPage.jsx — Synced products dashboard
- frontend/src/pages/PlatformConnectionsPage.jsx — OAuth-aware connection UI

## Remaining Tasks
- P1: Add app credentials for Meta, Etsy, TikTok, Google Ads to enable one-click OAuth
- P1: Configure GA4 tag inside GTM console (G-S9J8EPWKF9) — User task
- P1: Configure Resend webhook URL — User task
- P2: Data sync from other connected stores (Etsy, WooCommerce, BigCommerce)
- P2: Embedded Shopify app experience (already scaffolded)
- P3: SSR for dynamic pages (trending-products)

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
