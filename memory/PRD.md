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
- Serving: Custom static server (serve.js) + prerendering (39 pages) + Dynamic SSR
- Build: `cd /app/frontend && CI=false yarn build && sudo supervisorctl restart frontend`

## Completed Work

### Connection Wizard (March 28, 2026)
- Step-by-step guided modal for connecting platforms
- 4-step progress bar: Choose Platform -> Setup Guide -> Enter Credentials -> Connect
- Platforms grouped by E-Commerce / Advertising / Marketplaces
- Auto-fills redirect URIs, shows developer portal links
- OAuth-ready platforms (like Shopify) skip setup guide step
- Non-OAuth platforms show full setup instructions
- Test report: /app/test_reports/iteration_125.json (100% pass)

### Multi-Platform Synced Products Dashboard (March 28, 2026)
- New /synced-products page showing products from all connected stores
- Platform filter cards (All, Shopify, Etsy, WooCommerce, Amazon)
- Unified search and sort across all platforms
- Per-platform sync buttons
- Backend: /api/sync/products (unified), /api/sync/etsy/products, /api/sync/woocommerce/products
- Empty state with "Connect a Store" button
- Test report: /app/test_reports/iteration_125.json (100% pass)

### Dynamic SSR for /trending-products (March 28, 2026)
- Enhanced serve.js detects crawler user agents (Googlebot, Bing, etc.)
- Fetches live product data from backend API for crawlers
- Injects product names, categories, demand scores as HTML articles
- Adds JSON-LD structured data (ItemList schema)
- 5-minute in-memory cache for SSR pages
- Regular browser users get SPA (no SSR content visible)
- Test report: /app/test_reports/iteration_125.json (100% pass)

### Admin OAuth Credential Management (March 28, 2026)
- Admin panel on /settings/connections to configure OAuth app credentials for all platforms
- Credentials stored encrypted in MongoDB (oauth_credentials collection), cached in memory
- DB-stored credentials take priority over env vars
- Admin CRUD endpoints: GET/POST/DELETE /api/admin/oauth/credentials
- Non-admin users get 403 on admin endpoints
- Test report: /app/test_reports/iteration_124.json (100% pass)

### CRO/SEO/Positioning Overhaul (March 2026)
- Homepage rewrite with CRO-focused layout
- Unique SEO titles per page
- Complete metadata audit

### Shopify Integration Suite (March 2026)
- One-click OAuth, Synced Products dashboard, Webhooks, Token refresh

### QA Audit & Bug Fixes (March 2026)
- Mobile overflow fix, login error handling verified

## Key Files
- /app/frontend/src/components/ConnectionWizard.jsx - Guided connection wizard
- /app/frontend/src/pages/SyncedProductsPage.jsx - Multi-platform synced products
- /app/frontend/src/pages/PlatformConnectionsPage.jsx - Connections + admin panel
- /app/backend/routes/admin_oauth.py - Admin OAuth credential CRUD
- /app/backend/routes/platform_sync.py - Multi-platform sync endpoints
- /app/backend/services/oauth_service.py - OAuth service with DB credential support
- /app/frontend/serve.js - Static server + Dynamic SSR

## Remaining Tasks
- P1 (User task): Create OAuth apps on Meta/Etsy/TikTok/Google developer portals, enter credentials via admin panel
- P1 (User task): Configure GA4 tag in GTM console
- P1 (User task): Configure Resend webhook URL
- P2: Embedded Shopify app polish (ShopifyEmbeddedDashboard.jsx exists, needs refinement)
- P3: Extend SSR to more dynamic routes

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
