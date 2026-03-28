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
- Analytics: GTM -> GA4, consent-gated
- Serving: Custom static server + prerendering + Dynamic SSR
- Scheduling: APScheduler (26 tasks including auto-sync every 6h)
- Build: `cd /app/frontend && CI=false yarn build && sudo supervisorctl restart frontend`

## Completed Work

### Deployment Fix - 520 Errors (March 28, 2026) - COMPREHENSIVE
Root causes identified and fixed:
1. frontend/.gitignore excluded /build → container had no frontend → 520
2. start.js ran craco build on startup → 30-60s timeout → K8s killed container → 520
3. CRA's build script runs fs.emptyDirSync(build) - deletes committed build during Docker yarn build
4. yarn.lock not committed → Docker builds got unpredictable package versions
5. Backend startup was blocking (indexes, sitemap, scheduler) → health endpoint delayed
6. WebSocket URLs crashed when REACT_APP_BACKEND_URL was empty

All 6 fixes applied:
- FIX 1: Removed /build from frontend/.gitignore, committed 358 build files
- FIX 2: Rewrote start.js - no craco build, fallback HTTP server if build missing, 30s prerender timeout
- FIX 3: Rebuilt frontend with REACT_APP_BACKEND_URL="" (relative URLs work in all environments)
- FIX 4: Committed yarn.lock for reproducible Docker builds
- FIX 5: Moved ALL backend startup to asyncio.create_task (indexes, seed, sitemap, scheduler)
- FIX 6: Fixed WebSocket URLs in useNotifications.js and NotificationCenter.jsx
- Deployment agent: PASS x3, zero blockers

### Product Comparison Tool (March 28, 2026)
- Compare 2-4 products side-by-side on demand scores, margins, competition, pricing, trends
- Compare checkboxes on product cards (hover-reveal, persist when selected)
- Floating compare bar when 2+ products selected
- Save & share comparisons via public URL (/compare/:shareId)
- Sections: Performance Scores, Financial Metrics, Trend & Growth, Score Comparison
- Visual score bars with best-value highlighting
- Backend: POST /api/compare, GET /api/compare/shared/:id, POST /api/compare/quick
- Test: iteration_127.json (100% pass)

### Auto-Sync Scheduling + Sync History (March 28, 2026)
- 6-hour auto-sync for all connected Shopify/Etsy/WooCommerce stores
- Sync history dashboard with per-platform stats
- Test: iteration_126.json (100% pass)

### Connection Wizard + Synced Products (March 28, 2026)
- Step-by-step guided platform connection wizard
- Multi-platform synced products dashboard
- Test: iteration_125.json (100% pass)

### Admin OAuth Credentials (March 28, 2026)
- Admin panel for platform OAuth app credentials
- Test: iteration_124.json (100% pass)

### Shopify Embedded Dashboard, Dynamic SSR, CRO/SEO (March 2026)
- Tabbed embedded dashboard, SSR for 3 routes, full CRO rewrite

## Key Files
- /app/frontend/src/pages/ComparePage.jsx - Product comparison tool
- /app/frontend/src/pages/TrendingProductsPage.jsx - Compare selection UI
- /app/frontend/src/components/ConnectionWizard.jsx - Connection wizard
- /app/frontend/src/components/SyncHistory.jsx - Sync history component
- /app/frontend/src/pages/SyncedProductsPage.jsx - Multi-platform products
- /app/frontend/src/pages/ShopifyEmbeddedDashboard.jsx - Embedded dashboard
- /app/backend/routes/compare.py - Comparison API
- /app/backend/routes/platform_sync.py - Sync endpoints
- /app/backend/routes/admin_oauth.py - Admin OAuth CRUD
- /app/backend/services/jobs/tasks.py - Scheduled tasks
- /app/frontend/serve.js - Static + Dynamic SSR
- /app/OAUTH_SETUP_GUIDE.md - Step-by-step OAuth setup guide

## Remaining Tasks (User Actions)
- Create OAuth apps using /app/OAUTH_SETUP_GUIDE.md
- Configure GA4 tag in GTM console
- Configure Resend webhook URL

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
