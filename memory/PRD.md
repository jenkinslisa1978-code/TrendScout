# TrendScout - Product Requirements Document

## Product Vision
AI product validation for ecommerce. Find products worth launching before you spend money on ads.

## Architecture
- Backend: FastAPI + MongoDB + Redis
- Frontend: React CRA + Shadcn/UI
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d) + forgot/reset password
- Security: HSTS, CSP-Report-Only, CSRF double-submit cookie, Fernet encryption
- Monitoring: web-vitals, structured JSON request logging, X-Request-ID correlation

## ALL Features — COMPLETED

### Forgot/Reset Password (March 14, 2026)
- `POST /api/auth/forgot-password` — generates reset token (1hr expiry), stores in `password_resets` collection, returns reset link
- `POST /api/auth/reset-password` — validates token + expiry, enforces password rules (8 chars + number), updates password hash, cleans up token
- Frontend `/forgot-password` page with email form and success state
- Frontend `/reset-password?token=xxx` page with password rules, confirm password, error/success states
- Rate limited: 5/min per IP on both endpoints
- Prevents email enumeration (always returns success message)
- Login page has "Forgot your password?" link
- Note: No email service configured — reset link returned in API response and logged

### Homepage Clarity & UX Overhaul (March 14, 2026)
- Hero: "Find products worth testing before you waste money on ads" + "multi-signal AI launch score"
- Winning Product Example: Magnetic Spice Rack, 78/100, demand/competition/profit
- How It Works: Find products → Check launch score → Launch faster
- Start Here Panel, Beginner Mode (4 steps), renamed nav labels
- Help/FAQ page, Demo page (examples without login), improved footer with trust signals
- Signup: confirm password, password rules, forgot password link

### Production Hardening (March 14, 2026)
- Security headers, refresh tokens, CSRF, rate limiting, standardized errors
- Health endpoint, X-App-Version, X-Request-ID, structured logging
- Server-rendered login/signup, Stripe hardening, feature flags

### Programmatic SEO (March 14, 2026)
- 285+ sitemap URLs, trending today/week/month, 24+ categories, JSON-LD schema

### Previously Completed
- Shopify OAuth 2.0, 5 ecommerce platforms, 3 ad platforms
- Launch score, profit predictor, launch playbook, ad generator
- Redis cache, SSE, onboarding, beginner mode

## Test Suite
- 18 Playwright smoke tests covering: crawlability, auth, security, forgot password, help, demo, products

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P1: Add Sentry DSN for production error tracking
- P1: CSP enforcement after 48hr burn-in
- P1: Email service for password reset (SendGrid/Resend)
- P2: Redis pub/sub for multi-instance SSE
- P3: WebSocket upgrade
