# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers.

## Architecture
- Backend: FastAPI + MongoDB + Redis + APScheduler
- Frontend: React CRA + Shadcn/UI + Tailwind
- Auth: JWT + refresh cookie | Email: Resend | Payments: Stripe
- AI: GPT-5.2 via Emergent LLM Key (emergentintegrations)
- Real-time: WebSocket (native FastAPI/Starlette)

## Test Credentials
- reviewer@trendscout.click / ShopifyReview2026!

## Completed Features

### Real-time WebSocket Notifications (March 2026)
- **Backend**: WebSocket endpoint at `/api/ws/notifications` with connection manager
- **Backend**: All automation and ingestion routes broadcast `job_started`, `job_progress`, `job_completed`, `job_failed` events
- **Frontend**: `useNotifications` hook with auto-reconnect and ping keepalive
- **Frontend**: `NotificationFeed` component — bell icon with dropdown showing live activity, active jobs with progress bars, and completed/failed job history
- Visible to ALL logged-in users (not admin-only)
- Verified: iteration_115 (100%)

### Real OAuth 2.0 Flows (March 2026)
- **7 platforms**: Shopify, Etsy, Amazon Seller, TikTok Shop, Meta (Facebook/Instagram), Google Ads, TikTok Ads
- **Backend service**: Generic OAuth handler with state management, PKCE support (Etsy), encrypted token storage
- **Backend routes**: `GET /api/oauth/platforms`, `POST /api/oauth/{platform}/init`, `GET /api/oauth/{platform}/callback`, `GET /api/oauth/{platform}/setup`
- **Frontend**: OAuth Connections section on `/settings/connections` with "Connect with OAuth" buttons
- **Frontend**: OAuth modal with setup instructions, redirect URI display, Client ID/Secret inputs
- **Security**: State tokens, encrypted credentials, CSRF protection on init endpoint
- User provides their own Client ID + Client Secret per platform (BYO credentials)
- Verified: iteration_115 (100%)

### CSRF Bug Fix — Admin Automation Buttons (March 2026)
- Fixed "body stream already read", "Failed to run trend scoring", "Failed to generate summaries" errors
- Root cause: raw fetch() without CSRF tokens and unsafe response.json() calls
- Fix: Converted ALL service files to use apiPost/apiGet/apiPut/apiDelete from api.js
- Files fixed: DataIngestionPanel.jsx, productService.js, alertService.js, automationLogService.js
- Verified: iteration_114 (100%)

### Previous Completed Features
- Deployment blockers fixed (react-snap removed, CI=true warnings, .gitignore)
- Admin Command Center (/admin/hub) and Growth Analytics (/admin/analytics)
- Platform Connections: Stores, Ads, Social, Suppliers with health check
- A/B testing on Hero CTA, UTM tracking on emails, Resend webhooks
- Static prerendering (jsdom for Alpine), Connect Accounts prompt
- 3-email drip sequence, Email capture gate, Quick viability search
- Visual redesign suite, Interactive demo, Trust framework
- Prediction accuracy tracking, Methodology page, Changelog
- 6 free tools, Trial expiry, CRO suite, Code splitting

## Key API Endpoints
- POST /api/automation/run — Run automation pipeline (broadcasts WS events)
- POST /api/ingestion/amazon — Import Amazon products (broadcasts WS events)
- POST /api/ingestion/full-sync — Full data sync (broadcasts WS events)
- WS /api/ws/notifications — Real-time WebSocket notifications
- GET /api/oauth/platforms — List OAuth-enabled platforms with setup info
- POST /api/oauth/{platform}/init — Start OAuth flow
- GET /api/oauth/{platform}/callback — Handle OAuth callback
- GET /api/oauth/{platform}/setup — Platform setup instructions

## OAuth Platform Setup Guide
Each platform requires the user to register a developer app:
| Platform | Developer Portal | Connection Type |
|----------|-----------------|-----------------|
| Shopify | partners.shopify.com | Store |
| Etsy | etsy.com/developers | Store |
| Amazon Seller | sellercentral.amazon.co.uk | Social |
| TikTok Shop | partner.tiktokshop.com | Social |
| Meta (FB/IG) | developers.facebook.com | Ads |
| Google Ads | console.cloud.google.com | Ads |
| TikTok Ads | business-api.tiktok.com | Ads |

### Homepage Conversion Redesign (March 2026)
- **Hero rewrite**: "Stop guessing. Find products that actually sell in the UK." — sharper, more commercially persuasive
- **Who it's for section**: Moved up near top — Shopify sellers, Amazon UK sellers, TikTok Shop UK sellers, UK ecommerce founders
- **UK differentiation**: Prominent "Not every viral product works in the UK" section with US vs UK comparison visual
- **How it works**: Clean 3-step flow — Discover → Analyse UK viability → Launch with confidence
- **Feature highlights**: Tightened to outcome-focused copy (Trend detection, Competition analysis, Profit estimation, AI launch insights)
- **Pricing preview**: Compact plan cards on homepage with Growth plan highlighted as "Best for serious sellers"
- **CTA language**: Action-oriented throughout — "Find Winning Products", "See How It Works", "View Sample Analysis"
- **Trust strip**: Enhanced — "Built for UK ecommerce sellers", "7-signal scoring model", "Multi-channel product intelligence"
- **Pricing page**: Updated taglines ("Start validating product ideas", "Best for serious sellers", "For agencies and power users")
- Verified: iteration_116 (100% — 32/32 tests)

### Deployment Fix — jsdom & react-snap Cleanup (March 2026)
- **Removed** `jsdom@29.0.1` from dependencies (was causing Node engine incompatibility error in production: required `^20.19.0`, production had `20.18.1`)
- **Removed** `react-snap` from devDependencies (unused — replaced by custom `prerender.js`)
- **Removed** orphaned `reactSnap` config block from `package.json`
- `prerender.js` never imported jsdom; only uses built-in `fs` and `path`
- Verified: `yarn install` + `yarn build` succeed cleanly

## Remaining Tasks
- P1: Set REACT_APP_GA4_ID in production .env (user needs GA4 ID)
- P1: Configure Resend webhook URL in Resend dashboard
- P2: Implement actual data sync from connected OAuth stores (pull products from Shopify, etc.)
- P3: Add OAuth token refresh logic for expired tokens
