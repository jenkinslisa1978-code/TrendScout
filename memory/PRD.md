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

### Programmatic SEO System (March 14, 2026)
- **Part 1: Core SEO Pages:** `/trending-products-today`, `/trending-products-this-week`, `/trending-products-this-month` — public pages listing top products by time period with breadcrumbs, time-period nav, category links, product grid
- **Part 2: Category Trend Pages:** `/category/{slug}` — dynamic pages showing trending products within a specific category, interlinked with other categories
- **Part 3: Product Page Enhancement:** Added "Market Opportunity" section with supplier costs, retail price, margin analysis, growth rate, TikTok views
- **Part 4: Internal Linking:** Cross-links between all SEO pages via time-period nav, category pills, footer link grids, and breadcrumb navigation
- **Part 5: Sitemap Upgrade:** Updated `/api/sitemap.xml` to include all new core SEO pages and 19+ category pages (285 total URLs)
- **Part 6: Structured Data:** Added Product, BreadcrumbList, and FAQ JSON-LD schema to product pages; added BreadcrumbList and ItemList schema to SEO listing pages
- **Part 7: Performance:** All API endpoints cached with 5-minute TTL, lazy-loading images

### Part 1: Shopify OAuth Connection (March 14, 2026)
- OAuth 2.0 flow: `POST /api/shopify/oauth/init` generates auth URL with state token
- Callback: `GET /api/shopify/oauth/callback` exchanges code, verifies HMAC, encrypts token
- Status check: `GET /api/shopify/oauth/status`
- Disconnect: `DELETE /api/shopify/oauth/disconnect`
- Frontend: Domain input + "Connect Shopify Store" button on Connections page

### Part 2: Image Validation Service (March 14, 2026)
- Validates product images against supplier source domains
- Rejects stock/placeholder images
- Integrated into Shopify export pipeline

### Part 3: Enhanced Shopify Export (March 14, 2026)
- Structured HTML descriptions: benefit headline, features list, shipping info
- Pricing logic: supplier_cost × 2.5, snapped to £x.99 price points
- Exports as DRAFT, validates images

### Part 4: Beginner Mode (March 14, 2026)
- BeginnerPanel on dashboard with 4 steps
- Simplified nav labels
- PageExplanation banners (dismissible)

### Part 5: Winning Product Indicator (March 14, 2026)
- SVG score ring (0-100), color-coded verdict
- Strengths/risks bullet points, suggested test budget

### Part 6: Product Launch Playbook (March 14, 2026)
- 5-step launch plan with ad angles and target audiences
- Testing budget: £20-80 range

### Part 7: Security (March 14, 2026)
- Fernet encryption, HMAC-SHA256, Redis rate limiting, JWT auth

### Previous Features (All Completed)
- Redis Cache, SSE Notifications, Multi-step Ad Pipeline
- 5 E-Commerce Platforms (Shopify, WooCommerce, Etsy, BigCommerce, Squarespace)
- 3 Ad Platforms (Meta, TikTok, Google Ads)
- Onboarding Walkthrough, Quick Launch Flow, Data Trust Banner
- Scoring Methodology, Profitability Calculator, Connection Health Check

## Architecture
- Backend: FastAPI + MongoDB + Redis (33+ route files)
- Frontend: React + Shadcn/UI
- Security: Fernet encryption, HMAC verification, JWT auth, Redis rate limiting

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P2: Redis pub/sub for multi-instance SSE
- P3: WebSocket upgrade for bidirectional comms
