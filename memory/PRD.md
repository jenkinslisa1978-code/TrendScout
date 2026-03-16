# TrendScout - Product Requirements Document

## Product Vision
AI product validation for ecommerce. Find products worth launching before you spend money on ads.

## Architecture
- Backend: FastAPI + MongoDB + Redis
- Frontend: React CRA + Shadcn/UI
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d) + forgot/reset password with email
- Email: Resend (transactional emails — password resets)
- Security: HSTS, CSP-Report-Only, CSRF double-submit cookie, Fernet encryption
- Monitoring: web-vitals, structured JSON request logging, X-Request-ID correlation

## ALL Features — COMPLETED

### Email-Powered Password Reset (March 14, 2026)
- Resend integration for transactional emails (`onboarding@resend.dev` sender)
- `POST /api/auth/forgot-password` sends styled HTML reset email via Resend, falls back to link-in-response if email fails
- `POST /api/auth/reset-password` validates token (1hr expiry), enforces password rules (8 chars + number)
- Frontend `/forgot-password` and `/reset-password?token=xxx` pages with full UX
- Rate limited 5/min per IP, prevents email enumeration

### Homepage Clarity & UX Overhaul (March 14, 2026)
- Hero, How It Works, Winning Product Example, Start Here Panel
- Help/FAQ page, Demo page, improved signup, renamed nav labels, trust footer

### Production Hardening (March 14, 2026)
- Security headers, refresh tokens, CSRF, rate limiting, standardized errors
- Health endpoint, X-App-Version, X-Request-ID, structured logging
- Server-rendered login/signup, Stripe hardening, feature flags, Playwright tests

### Programmatic SEO (March 14, 2026)
- 285+ sitemap URLs, trending today/week/month, 24+ categories, JSON-LD schema

### Previously Completed
- Shopify OAuth 2.0, 5 ecommerce platforms, 3 ad platforms
- Launch score, profit predictor, launch playbook, ad generator
- Redis cache, SSE, onboarding, beginner mode

## Test Suite
- 18 Playwright smoke tests: crawlability, auth, security, forgot password, help, demo, products

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

### Weekly Email Digest with "What Should I Do Next?" (March 14, 2026)
- Expanded `EmailService` class with `send_email`, `send_weekly_digest`, `send_product_alert_email`, `send_product_of_the_week`
- Weekly digest now includes personalised "What Should You Do Next?" section per user
- Scheduled task `send_weekly_email_digest` generates per-user next-steps recommendations
- Module-level `email_service` instance + backward-compatible `send_password_reset_email` function

### CSP Enforcement (March 14, 2026)
- Switched Content-Security-Policy from report-only to enforcing mode
- Feature flag `FEATURE_CSP_ENFORCE=true` in backend .env

### Product Decision Panel (March 14, 2026)
- Backend `GET /api/dashboard/next-steps` returns personalised action recommendations
- Analyses saved products, stores, watchlist, alerts, usage to generate prioritised steps
- Frontend `ProductDecisionPanel` component renders on dashboard with "What Should I Do Next?" header
- Up to 5 prioritised action items with labels, descriptions, and navigation buttons

## Bug Fixes
### P0: Free Trial Upgrade Fix (March 14, 2026)
- **Root Cause 1:** CSRF middleware blocked POST /api/stripe/create-checkout-session because frontend api.js wasn't sending x-csrf-token header
- **Root Cause 2:** PricingPage.jsx didn't check response.ok, so error responses were silently swallowed
- **Fix:** Added getCsrfToken() to api.js to read __Host-csrf cookie and include x-csrf-token header on all authenticated requests. Added response.ok check in PricingPage.jsx with toast.error() for error messages
- **Verified:** Full flow tested — free user now redirected to Stripe checkout

### Shopify Connection Redesign + Fix (March 15, 2026)
- Replaced OAuth Client ID/Secret flow with Admin API access token approach (matches how real Shopify store owners connect)
- Backend verifies token by calling Shopify's Admin API before saving
- Returns HTTP 200 with success=false for validation errors (workaround for fetch API bodyUsed bug with 4xx responses)
- Clear setup instructions in UI: "Settings > Apps > Develop apps > Create app > Configure Admin API scopes > Install"
- Descriptive error messages: "Store not found", "Invalid access token", "Could not reach store"
- Verified end-to-end with testing agent (100% pass rate)

### Phase 1: Strategic Vision — Decision & Launch Engine (March 15, 2026)
- **Ad Intelligence (Ad Spy) Page:** `/ad-spy` — unified ad search across TikTok, Meta, Pinterest with keyword search, platform filters, sort by engagement/recent/spend. Backend `GET /api/ads/discover` returns product-derived ad intelligence.
- **Profitability Simulator Page:** `/profitability-simulator` — interactive calculator with product cost, selling price, CPM, CVR, ad budget, competition level inputs. Backend `POST /api/tools/profitability-simulator` returns unit economics, monthly projection, saturation analysis, and verdict.
- **7-Signal Score Breakdown Panel:** `ScoreBreakdownPanel` component on product detail pages. Backend `GET /api/products/{id}/launch-score-breakdown` returns 7 weighted signal components (trend, margin, competition, ad_activity, supplier_demand, search_growth, social_buzz) with explanations.
- **Social Share Snippet:** `ShareSnippet` component on product detail pages with Tweet and Copy Link buttons for sharing product scores.
- **Sidebar Navigation:** Added "Ad Intelligence" and "Profit Simulator" links.
- **Verified:** 100% pass rate — 21/21 backend tests, all frontend features verified.

### Phase 2: Enhanced Ad Spy + Competitor Intelligence (March 16, 2026)
- **Enhanced Ad Intelligence:** Save/bookmark ads, ad detail modal with rich metrics (launch score, est. spend, trend stage, engagement), category filter dropdown (25 categories), platform filters.
  - Backend: `POST /api/ads/save`, `GET /api/ads/saved`, `DELETE /api/ads/saved/{id}`, `GET /api/ads/categories`
- **Competitor Intelligence Dashboard:** `/competitor-intel` — deep-analyze any Shopify store by URL.
  - Revenue estimates (monthly revenue, daily orders), pricing strategy (Premium/Mid-Range/Value), supplier risk scoring (Low/Medium/High), category breakdown with progress bars, top products by price.
  - Store comparison: side-by-side metrics for 2-3 stores.
  - Analysis history: recent analyses saved per user.
  - Backend: `POST /api/competitor-intel/analyze`, `POST /api/competitor-intel/compare`, `GET /api/competitor-intel/history`
- **Verified:** 100% pass rate — 19/19 backend tests, all frontend features verified.

### Sentry Error Monitoring (March 16, 2026)
- **Frontend:** `@sentry/react` v10.43 — captures JS errors, React error boundaries, browser tracing, session replay (10% normal, 100% on error).
- **Backend:** `sentry-sdk[fastapi]` — captures Python exceptions, performance traces (30%), profiles (10%).
- DSNs configured via `REACT_APP_SENTRY_DSN` (frontend) and `SENTRY_DSN` (backend).

### Phase 3: Shopify Push + Radar Alerts + Verified Winners (March 16, 2026)
- **1-Click Product Import to Shopify:** "Push to Shopify" button on product detail pages. Pushes product as draft with title, description, images, pricing, tags via Admin API. Backend: `POST /api/shopify/push-product`, `GET /api/shopify/exports`.
- **Real-time Radar Alerts:** `/radar-alerts` — Live signal feed (trend spikes, ad activity, supplier demand, competition drops). Custom watches with create/toggle/delete. Watch types: product_score, category_trend, competitor_new_products. Backend: `POST/GET/PUT/DELETE /api/radar/watches`, `GET /api/radar/live-events`, `GET /api/radar/alert-feed`.
- **Verified Winners Community:** `/verified-winners` — Anonymous winner submissions with revenue range, timeframe, proof. Admin verification workflow. Upvote/downvote system. Leaderboard with sort and category filters. Backend: `POST /api/winners/submit`, `GET /api/winners/`, `POST /api/winners/{id}/upvote`, `GET /api/winners/my-submissions`, `POST /api/winners/{id}/verify`.
- **Product Search API:** `GET /api/products/search?q=&limit=` for autocomplete/selection.
- **Verified:** 100% pass rate — 21/21 backend tests, all frontend features verified.

### Phase 4: SEO Pages + API Access + Winner Streak Badges (March 16, 2026)
- **Winner Streak Badge System:** Badge tiers — Bronze (3 wins), Silver (5), Gold (10). Badges displayed on winner submissions in leaderboard. Profile updated on verification. Backend: `GET /api/winners/my-badge` returns tier, count, next tier.
- **Public SEO Trending Index:** `/trending` — public, no auth, 19 products with launch scores, category filters, JSON-LD, OG meta tags, "Start Free Trial" CTAs. Backend: `GET /api/public/trending-index`.
- **Public SEO Product Pages:** `/trending/:slug` — full product detail with score, AI summary, related products, structured data (schema.org Product), canonical URLs. Backend: `GET /api/public/trending/:slug`.
- **API Access for Power Users:** API key management (generate, list, revoke, max 3 keys). Rate-limited REST API v1 (100 req/min per key). Endpoints: `GET /api/v1/products/search`, `GET /api/v1/products/{id}/score`, `GET /api/v1/trends/categories`, `GET /api/v1/trends/top`. Frontend: `/api-docs` page with key management + reference docs.
- **Verified:** 100% pass rate — 15/15 backend tests, all frontend features verified.

### Weekly SEO Digest Enhancement (March 16, 2026)
- **Weekly Digest:** `/weekly-digest` — auto-generated top 5 trending products with category diversity, per-product insights, launch scores, share buttons (Tweet + Copy Link), and signup CTAs. Public, SEO-optimized.
- **Digest Archive:** `/weekly-digest/archive` — browse past weekly roundups.
- **Admin Generate:** `POST /api/digest/generate` — manually trigger digest creation. Selects top products with category diversity, generates insights from signals.
- **Cross-linking:** `/trending` page nav links to weekly digest. Digest links to individual product SEO pages.
- **Verified:** 100% pass rate — 8/8 backend, all frontend features verified.

## Backlog
- P2: Automate weekly digest via cron/scheduler (currently admin-triggered)
- P2: Redis pub/sub for multi-instance SSE
- P2: Fix mixed content notification issue (HTTP SSE blocked on HTTPS)
- P3: WebSocket upgrade
