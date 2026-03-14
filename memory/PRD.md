# TrendScout - Product Requirements Document

## Product Vision
AI product validation for ecommerce. Find products worth launching before you spend money on ads.

## Architecture
- Backend: FastAPI + MongoDB + Redis
- Frontend: React CRA + Shadcn/UI
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d)
- Security: HSTS, CSP-Report-Only, CSRF double-submit cookie, Fernet encryption
- Monitoring: web-vitals, structured JSON request logging, X-Request-ID correlation

## ALL Features — COMPLETED

### Homepage Clarity & UX Overhaul (March 14, 2026)
- **Part 1-2 Hero:** "Find products worth testing before you waste money on ads" + "analyzes...multi-signal AI launch score" subheading + Browse Trending Products CTA + See How It Works scroll
- **Part 2 How It Works:** 3 steps — Find products, Check the launch score (analyzes demand, competition, ad potential), Launch faster
- **Part 3 Winning Product Example:** Magnetic Spice Rack card with score 78/100, demand/competition/profit metrics, "why it works" bullet points
- **Part 4 Start Here Panel:** "New here? Start with these 3 steps" — browse, analyze, decide + Start Now button
- **Part 5 Navigation:** Renamed — Product Analysis (was My Stores), Market Data (was Competitors), Find Products, Leaderboard, Examples, Help
- **Part 6 Beginner Mode:** 4-step dashboard panel — Find product, Check score, Import to Shopify, Test ads — with clickable step cards
- **Part 15 Signup UX:** Confirm password field, password rules (min 8 chars + number), visual validation, forgot password link
- **Part 16 Trust & Help:** New /help page with FAQ, How it works, Support contact. Footer grid: Products, Resources, Legal columns with company info + contact email
- **Part 17 Demo Pages:** New /demo page with Example Product Analysis, Example Launch Plan, Example Ad Ideas — all visible without login
- **Part 19 Positioning:** "AI product validation for ecommerce" tagline across login, signup, hero

### Production Hardening (March 14, 2026)
- Security headers, refresh tokens, CSRF, rate limiting, standardized errors
- Health endpoint, X-App-Version, X-Request-ID, structured logging
- Server-rendered login/signup, Stripe hardening, feature flags, Playwright tests

### Programmatic SEO System (March 14, 2026)
- 285+ sitemap URLs, trending today/week/month, 24+ categories, JSON-LD schema

### Previously Completed
- Parts 7-14 (Shopify OAuth, public trending feed, product SEO pages, launch score 0-100, profit predictor, product decision panel, launch playbook, ad creative generator)
- 5 ecommerce platforms, 3 ad platforms, Redis cache, SSE, onboarding

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P1: Add Sentry DSN for production error tracking
- P1: CSP enforcement after 48hr burn-in
- P1: Forgot password flow (link added, backend endpoint needed)
- P2: Redis pub/sub for multi-instance SSE
- P3: WebSocket upgrade
