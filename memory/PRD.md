# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. One-stop shop: find winning products, set up shop, create ads — all in a couple of clicks.

## Pricing Model (LIVE)
| Plan | Price | API Rate Limit |
|------|-------|----------------|
| Free | £0/mo | 30 req/min |
| Starter | £19/mo | 120 req/min |
| Pro | £39/mo | 300 req/min |
| Elite | £79/mo | 600 req/min |

## ALL Features — COMPLETED

### Part 1: Shopify OAuth Connection (March 14, 2026)
- OAuth 2.0 flow: `POST /api/shopify/oauth/init` generates auth URL with state token
- Callback: `GET /api/shopify/oauth/callback` exchanges code, verifies HMAC, encrypts token
- Status check: `GET /api/shopify/oauth/status`
- Disconnect: `DELETE /api/shopify/oauth/disconnect`
- Frontend: Domain input + "Connect Shopify Store" button on Connections page
- Requires: SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET env vars from Shopify Partner app

### Part 2: Image Validation Service (March 14, 2026)
- Validates product images against supplier source domains
- Rejects stock/placeholder images (unsplash, via.placeholder.com, etc.)
- Detects category mismatches (e.g., drill image on ring product)
- Flags products as `image_missing` when no valid images found
- Integrated into Shopify export pipeline

### Part 3: Enhanced Shopify Export (March 14, 2026)
- Structured HTML descriptions: benefit headline, features list, shipping info
- Pricing logic: supplier_cost × 2.5, snapped to £x.99 price points
- Exports as DRAFT (user reviews before publishing)
- Validates and exports minimum 3 images when available
- Uses image_validation_service for quality control

### Part 4: Beginner Mode (March 14, 2026)
- BeginnerPanel on dashboard: "New to TrendScout? Start here." with 4 steps
- Simplified nav labels: Find Products, Ad Ideas, Profit Estimate
- PageExplanation banners on key pages (dismissible per-page)

### Part 5: Winning Product Indicator (March 14, 2026)
- SVG score ring on product detail page (0-100)
- Color-coded verdict: Strong/Good/Worth investigating/High risk
- Lists strengths and risks with bullet points
- Suggested test budget based on margins

### Part 6: Product Launch Playbook (March 14, 2026)
- `GET /api/launch-playbook/{product_id}` returns full playbook
- 5 steps: Create page → Review → Create ads → Launch campaign → Evaluate
- 3 ad angles: Problem→Solution, Demonstration, Before/After
- Target audiences based on product category
- Testing budget: £20-80 range, 3 creatives, 48-hour test

### Part 7: Security (March 14, 2026)
- Fernet token encryption for stored access tokens
- HMAC-SHA256 verification on Shopify OAuth callbacks
- Secure state tokens stored in DB with CSRF validation
- API rate limiting via Redis middleware
- All existing: CORS, JWT auth, input validation

### Previous Features (All Completed)
- Redis Cache, SSE Notifications, Multi-step Ad Pipeline
- 5 E-Commerce Platforms (Shopify, WooCommerce, Etsy, BigCommerce, Squarespace)
- 3 Ad Platforms (Meta, TikTok, Google Ads)
- Onboarding Walkthrough, Quick Launch Flow, Data Trust Banner
- Scoring Methodology Transparency, Profitability Calculator
- Connection Health Check

## Architecture
- Backend: FastAPI + MongoDB + Redis (33 route files)
- Frontend: React + Shadcn/UI
- Security: Fernet encryption, HMAC verification, JWT auth, Redis rate limiting

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P2: Redis pub/sub for multi-instance SSE
- P3: WebSocket upgrade for bidirectional comms
