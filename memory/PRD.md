# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers. Discover trending products, analyse competition, estimate profit potential, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk.

## Architecture
- Backend: FastAPI + MongoDB + Redis + APScheduler
- Frontend: React CRA + Shadcn/UI + Tailwind CSS
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d)
- Email: Resend (transactional emails + weekly digest)
- Payments: Stripe
- Monitoring: Sentry, web-vitals

## Test Credentials
- Reviewer: reviewer@trendscout.click / ShopifyReview2026!

## Completed Features

### Automated Weekly Digest (March 21, 2026)
- `send_lead_subscriber_digest` task registered in APScheduler
- Cron: Every Monday 9 AM UTC (`0 9 * * 1`)
- Sends top 5 trending products to all opted-in email leads via Resend
- Logs each send in `digest_log` collection
- Manual trigger also available via `POST /api/leads/send-digest`

### Blog Content Strategy (March 21, 2026)
- 3 seed articles created: product validation guide, UK VAT guide, TikTok Shop analysis
- Idempotent seed endpoint: `POST /api/blog/seed` (checks by slug)
- Blog renders at /blog with full article pages at /blog/{slug}
- Total: 5 articles (3 seed + 2 AI-generated)
- AI generation system already built (admin endpoint)

### Image Lazy Loading (March 21, 2026)
- Added `loading="lazy"` to all `<img>` tags across 20+ components
- Created `LazyImage.jsx` component with IntersectionObserver + blur placeholder
- Key files updated: DiscoverPage, DashboardPage, TrendingProductsPage, etc.

### CRO Enhancement — 6 Features (March 21, 2026)
1. Exit-intent popup with lead magnet (desktop only, 7-day localStorage dismissal)
2. Social proof toast notifications (MOCKED UK names/cities, 8s delay)
3. Interactive product quiz at /product-quiz (4 questions, personalised recommendation)
4. Weekly email digest for lead subscribers (automated cron)
5. Tool recommender on comparison pages (3-question honest recommendation)
6. Shareable calculator results (copy + X/Twitter share)

### Phase 3a: CRO Base, Lead Capture, Performance (March 19, 2026)
- Sample Product Analysis Page, Email Lead Capture, 4 landing pages
- Route-level code splitting (80+ lazy-loaded pages)
- Scroll depth analytics, mid-page CTAs, social proof in SeoLandingTemplate

### Phase 2: Analytics, Schema, Viability Score, SEO
### Phase 1: Website Rebuild

## Backlog

### P0 — High Priority
- Configure GA4 measurement ID (REACT_APP_GA4_ID) in production .env
- SSR/static generation for marketing pages

### P1 — Medium Priority
- More blog articles (automate weekly generation)
- Changelog / product updates page
- Further bundle tree-shaking

### P2 — Lower Priority
- More free tools (TikTok Ad Budget calculator, Product Validation Checklist)
- FAQ schema on comparison pages
- Backend scoring consolidation
- Trial expiry notification emails
