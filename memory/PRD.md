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

## Backlog
- P0: Shopify OAuth 2.0 Connection — DONE (replaced with Admin API token approach)
- P1: Sentry integration — needs user DSN
- P2: Redis pub/sub for multi-instance SSE
- P2: Fix mixed content notification issue (HTTP SSE blocked on HTTPS)
- P3: WebSocket upgrade
