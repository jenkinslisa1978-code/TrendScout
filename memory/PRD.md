# TrendScout PRD

## Product Vision
UK-focused product validation and trend analysis tool for ecommerce sellers.

## Core Positioning
**"UK Product Validation Tool"** — a single positioning angle applied site-wide.

## Tech Stack
- Frontend: React (CRA/Craco) + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-5.2 (via Emergent LLM Key)
- Payments: Stripe (GBP), Email: Resend
- Analytics: GTM (GTM-5V7G36GN) -> GA4 (G-S9J8EPWKF9), consent-gated
- Serving: Custom static server (serve.js) + prerendered content (39 pages)
- Build: `cd /app/frontend && yarn build && sudo supervisorctl restart frontend`

## Completed Work

### Admin OAuth Credential Management (March 2026)
- Admin panel on /settings/connections to configure OAuth app credentials for all platforms
- Credentials stored encrypted in MongoDB (oauth_credentials collection), cached in memory
- DB-stored credentials take priority over env vars
- Admin CRUD endpoints: GET/POST/DELETE /api/admin/oauth/credentials
- Non-admin users get 403 on admin endpoints and don't see the admin panel
- Shopify shows "ENV" badge (from env vars), other platforms show "Not set" / "Configured"
- Test report: /app/test_reports/iteration_124.json (100% pass)

### CRO/SEO/Positioning Overhaul (March 2026)
**Homepage Rewrite:**
- New H1: "Validate product ideas for the UK market before you spend a penny"
- Conversion flow: Hero -> Trust Bar -> How It Works -> UK Viability Score -> Products -> Proof -> Who It's For/Not For -> Pricing Preview -> Data Sources -> FAQ -> Final CTA
- Outcome-based CTAs: "Validate Your First Product", "See a Live Example", "Validate a Product"

**SEO Titles (all unique per page):**
- Homepage: "UK Product Validation Tool for Ecommerce Sellers | TrendScout"
- Pricing: "Plans and Pricing - Start from 19/mo | TrendScout"
- How It Works: "How TrendScout Validates Products for the UK Market"
- Sample Analysis: "Live Product Analysis Example - See What You Get | TrendScout"
- Features: "Product Research Features for UK Ecommerce Sellers | TrendScout"
- About: "About TrendScout - Why We Built a UK-First Product Validation Tool"

### Shopify Integration Suite (March 2026)
- One-click OAuth, Synced Products dashboard, Webhooks, Token refresh
- Test: iteration_122.json (100% pass)

### QA Audit & Bug Fixes (March 2026)
- Mobile overflow fix, login error handling verified
- Test: iteration_120.json (100% pass)

### Previous Work
- GTM integration, crawlability infrastructure, core platform features

## Key Files
- backend/routes/admin_oauth.py - Admin OAuth credential management endpoints
- backend/services/oauth_service.py - OAuth service with DB credential support
- backend/routes/oauth.py - Generic OAuth flow routes
- frontend/src/pages/PlatformConnectionsPage.jsx - Connections page with admin panel
- frontend/src/pages/LandingPage.jsx - Homepage (full rewrite)
- frontend/src/components/PageMeta.jsx - SEO metadata component
- frontend/prerender-data.js - Prerendered content for crawlers

## Remaining Tasks
- P1: User must create OAuth apps and provide credentials for Meta/Etsy/TikTok/Google Ads (admin panel is ready)
- P1: Configure GA4 tag inside GTM console (user task)
- P1: Configure Resend webhook URL (user task)
- P2: Data sync from other stores (Etsy, WooCommerce)
- P2: Synced products dashboard view enhancements
- P2: Build an embedded Shopify app experience
- P3: SSR for dynamic pages

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
