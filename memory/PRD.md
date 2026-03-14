# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. One-stop shop: find winning products, set up shop, create ads — all in a couple of clicks.

## Architecture
- Backend: FastAPI + MongoDB + Redis
- Frontend: React CRA + Shadcn/UI
- Auth: JWT (short-lived access tokens) + __Host-refresh cookie
- Security: HSTS, CSP, CSRF (double-submit cookie), Fernet encryption

## ALL Features — COMPLETED

### Production Hardening (March 14, 2026)
- **P0 Crawlability:** `/`, `/robots.txt`, `/sitemap.xml` all return 200 with meaningful content
- **No-JS HTML Shell:** Replaced "enable JavaScript" noscript with full branding, nav links, auth links
- **Server-Rendered Auth:** `/api/auth/login-page` and `/api/auth/signup-page` serve real HTML forms that work without JS
- **Refresh Token Flow:** Short-lived access tokens (15min), `__Host-refresh` cookie (7d, HttpOnly, Secure, SameSite=Lax), `/api/auth/refresh` endpoint, token rotation, `/api/auth/logout` clears cookies
- **CSRF Protection:** Double-submit cookie (`__Host-csrf`), verified on cookie-authenticated POST/PUT/DELETE; exempts Stripe webhooks and bearer-only APIs
- **Security Headers:** HSTS (2yr), Referrer-Policy (strict-origin-when-cross-origin), X-Frame-Options (DENY), X-Content-Type-Options (nosniff), Permissions-Policy, CSP-Report-Only
- **Standardized API Errors:** All errors return `{success: false, error: {code, message}}` via global exception handler
- **Stripe Webhook Hardening:** Always verifies webhook signature; rejects unsigned requests
- **Feature Flags:** `FEATURE_PRERENDER_PUBLIC`, `FEATURE_NOJS_AUTH`, `FEATURE_CSP_ENFORCE` in backend .env
- **Web Vitals:** CLS, FCP, LCP, TTFB reporting via web-vitals library
- **Playwright Smoke Tests:** 14 tests covering /, robots.txt, sitemap.xml, login, signup, security headers, error format, auth flow, product discovery
- **ErrorBoundary:** Enhanced with monitoring hook (`window.__ERROR_REPORTER`)

### Programmatic SEO System (March 14, 2026)
- Core SEO pages: `/trending-products-today`, `/trending-products-this-week`, `/trending-products-this-month`
- Category pages: `/category/{slug}` with 24+ categories
- Product page enhancement: Market Opportunity section, BreadcrumbList + FAQ JSON-LD schema
- Internal linking: time-period nav, category pills, footer links, breadcrumbs
- Sitemap: 285 URLs including categories and products

### Previous Features (All Completed)
- Shopify OAuth 2.0 with HMAC + encrypted credentials
- 5 E-Commerce Platforms, 3 Ad Platforms
- Beginner Mode, Product Score, Launch Playbook
- Redis Cache, SSE Notifications, Rate Limiting
- Onboarding Walkthrough, Profitability Calculator

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P1: Enable CSP enforcement (set `FEATURE_CSP_ENFORCE=true` after verifying report-only logs)
- P2: Add Sentry DSN for production error tracking
- P2: Redis pub/sub for multi-instance SSE
- P3: WebSocket upgrade for bidirectional comms
