# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. One-stop shop: find winning products, set up shop, create ads — all in a couple of clicks.

## Architecture
- Backend: FastAPI + MongoDB + Redis
- Frontend: React CRA + Shadcn/UI
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d)
- Security: HSTS, CSP-Report-Only, CSRF double-submit cookie, Fernet encryption
- Monitoring: web-vitals, structured JSON request logging, X-Request-ID correlation

## Production Hardening (March 14, 2026)

### Security & Auth
- Short-lived access tokens (15min) + `__Host-refresh` cookie (7d, HttpOnly, Secure, SameSite=Lax)
- Token refresh endpoint `/api/auth/refresh` with rotation
- CSRF double-submit cookie (`__Host-csrf`) on cookie-authenticated POST/PUT/DELETE
- Security headers: HSTS (2yr), X-Frame-Options: DENY, Referrer-Policy, CSP-Report-Only, Permissions-Policy
- Auth rate limiting: login 10/min, register 5/min, refresh 10/min (IP-based)
- Stripe webhook signature always verified

### Crawlability & SEO
- `/`, `/robots.txt`, `/sitemap.xml` return 200 with meaningful content
- No-JS HTML shell: branding, nav links, auth links (replaces "enable JS" message)
- Server-rendered login/signup forms at `/api/auth/login-page` and `/api/auth/signup-page`
- Programmatic SEO: 285+ indexed pages (trending today/week/month, 24+ categories, products)
- BreadcrumbList, FAQ, Product, ItemList JSON-LD structured data

### Observability
- `GET /api/health` → `{"status": "ok"}` (lightweight, no DB dependency)
- `X-App-Version` header on all responses (sourced from APP_VERSION env)
- `X-Request-ID` header on all responses (for log correlation)
- Structured JSON request logging: request_id, timestamp, method, path, status, latency_ms, user_id
- Standardized API errors: `{success: false, error: {code, message}}`
- web-vitals reporting (CLS, FCP, LCP, TTFB)
- ErrorBoundary with monitoring hook

### QA
- Playwright smoke tests (14 tests): crawlability, auth, security headers, error format, product discovery
- Feature flags: FEATURE_PRERENDER_PUBLIC, FEATURE_NOJS_AUTH, FEATURE_CSP_ENFORCE

## Previous Features (All Completed)
- Shopify OAuth 2.0, WooCommerce, Etsy, BigCommerce, Squarespace integrations
- AI ad generation (Meta, TikTok, Google Ads)
- Beginner Mode, Product Score, Launch Playbook
- Redis Cache, SSE Notifications, Rate Limiting
- Onboarding Walkthrough, Profitability Calculator

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P1: Add Sentry DSN for production error tracking (frontend + backend, errors only)
- P1: CSP enforcement after 48hr burn-in of Report-Only
- P2: Redis pub/sub for multi-instance SSE
- P3: WebSocket upgrade for bidirectional comms
