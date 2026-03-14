# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. One-stop shop: find winning products, set up shop, create ads — all in a couple of clicks.

## Architecture
- Backend: FastAPI + MongoDB + Redis
- Frontend: React CRA + Shadcn/UI
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d)
- Security: HSTS, CSP-Report-Only, CSRF double-submit cookie, Fernet encryption
- Monitoring: web-vitals, structured JSON request logging, X-Request-ID correlation

## ALL Features — COMPLETED

### Homepage Improvement (March 14, 2026)
- **Hero:** "Find products worth testing before you waste money on ads" + "See Trending Products" primary CTA + "How It Works" scroll button
- **How TrendScout Works:** 3 clear steps — Find products, Check potential, Launch faster
- **Start Here Panel:** "New here? Start with these 3 steps" with numbered steps + "Start Now" button
- **Product Cards:** Show product image, name, score/100, and AI-generated short reason
- **Why Use TrendScout:** 4 value props — Real trend data, Know before you spend, Ad ideas included, Updated daily
- **Layout:** Hero > How It Works > Trending Products > Why > Final CTA > Footer

### Production Hardening (March 14, 2026)
- Security headers (HSTS, X-Frame, Referrer, CSP-Report-Only, Permissions-Policy)
- Short-lived access tokens (15min) + __Host-refresh cookie (7d) + token rotation
- CSRF double-submit cookie on cookie-authenticated routes
- Auth rate limiting (login 10/min, register 5/min, refresh 10/min per IP)
- Standardized API errors `{success: false, error: {code, message}}`
- Health endpoint, X-App-Version, X-Request-ID, structured JSON logging
- Server-rendered login/signup forms (no-JS support)
- Stripe webhook signature always verified
- Feature flags, web-vitals, Playwright smoke tests (14 tests)

### Programmatic SEO System (March 14, 2026)
- Core SEO pages: /trending-products-today, /this-week, /this-month
- Category pages: /category/{slug} with 24+ categories
- Product page: Market Opportunity section, BreadcrumbList + FAQ + Product JSON-LD
- 285+ sitemap URLs, internal linking throughout

### Previous Features (All Completed)
- Shopify OAuth 2.0, WooCommerce, Etsy, BigCommerce, Squarespace integrations
- AI ad generation (Meta, TikTok, Google Ads)
- Beginner Mode, Product Score, Launch Playbook
- Redis Cache, SSE Notifications, Rate Limiting
- Onboarding Walkthrough, Profitability Calculator

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P1: Add Sentry DSN for production error tracking
- P1: CSP enforcement after 48hr burn-in of Report-Only
- P2: Redis pub/sub for multi-instance SSE
- P3: WebSocket upgrade for bidirectional comms
