# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers. Discover trending products, analyse competition, estimate profit potential, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk.

## Architecture
- Backend: FastAPI + MongoDB + Redis + APScheduler
- Frontend: React CRA + Shadcn/UI + Tailwind CSS + react-snap (pre-rendering)
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d)
- Email: Resend (transactional emails + weekly digest)
- Payments: Stripe
- Monitoring: Sentry, web-vitals

## Test Credentials
- Reviewer: reviewer@trendscout.click / ShopifyReview2026!

## Completed Features

### Production Optimisation (March 21, 2026)
- **react-snap pre-rendering**: 30 marketing pages configured for static HTML generation at build time
- **Hydration support**: index.js updated to use hydrateRoot() for pre-rendered content, createRoot() otherwise
- **GA4 ready**: Script wired in index.html, just needs `REACT_APP_GA4_ID` set in production .env
- **Blog generation fix**: Fixed import bug in weekly_blog_generation task (was importing from `server`, now correctly from `routes.blog`)

### Automated Scheduled Tasks
| Task | Schedule | Description |
|------|----------|-------------|
| `ingest_trending_products` | Every 4 hours | Fetch trending products from sources |
| `weekly_blog_generation` | Monday 8 AM UTC | Auto-generate SEO blog posts for top categories |
| `send_lead_subscriber_digest` | Monday 9 AM UTC | Send trending products email to lead subscribers |
| `send_weekly_email_digest` | Monday 10 AM UTC | Send digest to registered users |

### Blog Content (March 21, 2026)
- 3 seed articles: product validation guide, UK VAT guide, TikTok Shop analysis
- 2 AI-generated articles from previous sessions
- Idempotent seed endpoint: `POST /api/blog/seed`
- AI generation system: `POST /api/blog/generate/{category_slug}` (admin)
- Auto-generation: `weekly_blog_generation` scheduled task

### Image Performance (March 21, 2026)
- `loading="lazy"` on all `<img>` tags across 20+ components
- `LazyImage.jsx` component with IntersectionObserver + blur placeholder
- Route-level code splitting: 80+ pages lazy-loaded via React.lazy()

### CRO Enhancement — 6 Features (March 21, 2026)
1. Exit-intent popup with lead magnet (desktop only)
2. Social proof toast notifications (MOCKED UK names/cities)
3. Interactive product quiz at /product-quiz (4 questions)
4. Weekly email digest for lead subscribers (automated cron)
5. Tool recommender on comparison pages (3-question honest recommendation)
6. Shareable calculator results (copy + X/Twitter)

### Phase 3a: Lead Capture, Content Expansion (March 19, 2026)
- Sample Product Analysis Page, Email Lead Capture, 4 landing pages
- Scroll depth analytics, mid-page CTAs, social proof in SeoLandingTemplate

### Phase 2: Analytics, Schema, Viability Score, SEO
### Phase 1: Website Rebuild

## Backlog

### P1 — Medium Priority
- Changelog / product updates page
- More blog articles (manually trigger generate-all or wait for Monday cron)
- A/B testing framework for CTA copy

### P2 — Lower Priority
- More free tools (TikTok Ad Budget calculator, Product Validation Checklist)
- FAQ schema on comparison pages
- Backend scoring consolidation
- Trial expiry notification emails
- Further bundle tree-shaking
