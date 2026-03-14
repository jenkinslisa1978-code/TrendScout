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

## Backlog
- P1: Add Sentry DSN for production error tracking
- P1: CSP enforcement after 48hr burn-in
- P2: Redis pub/sub for multi-instance SSE
- P3: WebSocket upgrade
