# TrendScout PRD

## Product Vision
UK-focused product validation and trend analysis tool for ecommerce sellers.

## Core Positioning
**"UK Product Validation Tool"** — a single positioning angle applied site-wide.

## Tech Stack
- Frontend: React (CRA/Craco) + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB (Motor async driver)
- AI: OpenAI GPT-5.2 (via Emergent LLM Key)
- Payments: Stripe (GBP), Email: Resend
- Analytics: GTM (GTM-5V7G36GN) -> GA4 (G-S9J8EPWKF9), consent-gated
- Serving: Custom static server (serve.js) + prerendering (39 pages) + Dynamic SSR (3 routes)
- Scheduling: APScheduler (26 tasks including auto-sync every 6h)
- Build: `cd /app/frontend && CI=false yarn build && sudo supervisorctl restart frontend`

## Completed Work

### Auto-Sync Scheduling (March 28, 2026)
- APScheduler task `auto_sync_connected_stores` runs every 6 hours (0 */6 * * *)
- Syncs products from all active Shopify/Etsy/WooCommerce connections
- Logs sync history per-platform with success/error status and trigger type
- Test report: /app/test_reports/iteration_126.json (100% pass)

### Sync History Dashboard (March 28, 2026)
- Backend: GET /api/sync/history (recent 50 sync events)
- Backend: GET /api/sync/history/summary (per-platform aggregates)
- Frontend: SyncHistory component on /synced-products page
- Shows last sync time, product counts, error rates per platform
- Expandable log with manual/scheduled trigger badges

### Shopify Embedded Dashboard Polish (March 28, 2026)
- Tabbed interface: Trending / Radar / Exports
- Product sync from within Shopify admin
- Quick action cards (Browse Products, Full Dashboard)
- Sticky header with store name badge
- Empty states per tab with contextual messaging
- Route: /embedded?shop=xxx&host=xxx

### Extended Dynamic SSR (March 28, 2026)
- /trending-products: Live product data with JSON-LD schema
- /discover: Daily picks injected for crawlers
- /reports/weekly-winning-products: Top trending products
- 5-minute in-memory cache, crawler detection via user-agent
- Regular browsers get SPA (no SSR content visible)

### Connection Wizard (March 28, 2026)
- Step-by-step guided modal for connecting platforms
- 4-step progress bar: Choose Platform -> Setup Guide -> Enter Credentials -> Connect
- Platforms grouped by E-Commerce / Advertising / Marketplaces

### Multi-Platform Synced Products Dashboard (March 28, 2026)
- /synced-products page with platform filter cards
- Unified search and sort across all platforms
- Backend: /api/sync/products, /api/sync/etsy/products, /api/sync/woocommerce/products

### Admin OAuth Credential Management (March 28, 2026)
- Admin panel on /settings/connections for platform OAuth credentials
- Encrypted storage in MongoDB, cached in memory

### CRO/SEO/Positioning Overhaul (March 2026)
- Homepage rewrite, unique SEO titles per page

### Shopify Integration Suite (March 2026)
- One-click OAuth, Webhooks, Token refresh

## Key Files
- /app/frontend/src/components/ConnectionWizard.jsx
- /app/frontend/src/components/SyncHistory.jsx
- /app/frontend/src/pages/SyncedProductsPage.jsx
- /app/frontend/src/pages/ShopifyEmbeddedDashboard.jsx
- /app/frontend/src/pages/PlatformConnectionsPage.jsx
- /app/backend/routes/platform_sync.py
- /app/backend/routes/admin_oauth.py
- /app/backend/services/jobs/tasks.py (auto_sync_connected_stores)
- /app/backend/services/oauth_service.py
- /app/frontend/serve.js (Static + Dynamic SSR)

## Remaining Tasks (User Actions)
- Create OAuth apps on Meta/Etsy/TikTok/Google developer portals, enter credentials via admin panel
- Configure GA4 tag in GTM console
- Configure Resend webhook URL

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
