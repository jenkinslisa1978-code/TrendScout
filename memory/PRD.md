# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. Scans TikTok, Amazon, and ecommerce stores with AI to identify products ready to scale. One-stop shop: "tell you what to sell, set up the shop and produce adverts all in a couple of clicks".

## Pricing Model (LIVE)
| Plan | Price | API Rate Limit |
|------|-------|----------------|
| Free | £0/mo | 30 req/min |
| Starter | £19/mo | 120 req/min |
| Pro | £39/mo | 300 req/min |
| Elite | £79/mo | 600 req/min |

## Key Features — ALL COMPLETED

### Data Trust & Transparency (March 13, 2026)
- Scoring Methodology endpoint (`GET /api/scoring/methodology`) — 7 signals, 6 data sources, honest limitations
- "How Our Scores Work" section on Product Detail pages
- Data Trust Banner on Dashboard — expandable with real data source info
- Platform Automation Badges on Connections page

### Onboarding Walkthrough (March 13, 2026)
- 4-step modal for first-time users
- Steps: Welcome, Connect Store, Connect Ads, Quick Launch
- Persists in localStorage

### Platform Connections — ALL 5 STORES + 3 AD PLATFORMS
**E-Commerce Stores (ALL Full Automation):**
- Shopify — Real Shopify Admin REST API
- WooCommerce — Real WooCommerce REST API
- Etsy — Real Etsy Open API v3 (listings created as DRAFT)
- BigCommerce — Real BigCommerce REST API v3
- Squarespace — Real Squarespace Commerce API v1

**Advertising Platforms:**
- Meta (Facebook + Instagram) — Auto-Post Ads (PAUSED)
- TikTok Ads — Auto-Post Ads (PAUSED)
- Google Ads — Draft Only (user completes in Google Ads Manager)

### API Rate Limiting (March 13, 2026)
- Per-user, per-plan middleware enforcement
- X-RateLimit headers on all authenticated responses
- Exempt paths: health, auth, scoring methodology
- In-memory storage (production: migrate to Redis)

### Quick Launch Flow
- "Launch a Product in 3 Clicks" widget at top of dashboard

### Premium Ad Creative Generation
- Uses OpenAI GPT-4.1-mini via Emergent LLM Key

### Beginner-Friendly UX
- Score tooltips, plain English, £ currency, no generic supplier links

## Architecture
- Backend: FastAPI + MongoDB (32 route files) + rate limiting middleware
- Frontend: React + Shadcn/UI
- Integrations: OpenAI, Stripe, Resend, CJ Dropshipping, Shopify, WooCommerce, Etsy, BigCommerce, Squarespace, Meta, TikTok, Google Ads APIs

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P2: Redis cache migration (rate limit + API cache)
- P3: Real-time WebSocket notifications
- P3: Ad generation multi-step refactoring
