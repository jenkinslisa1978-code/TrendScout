# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers.

## Architecture
- Backend: FastAPI + MongoDB + Redis + APScheduler
- Frontend: React CRA + Shadcn/UI + Tailwind + react-snap
- Auth: JWT + refresh cookie | Email: Resend | Payments: Stripe

## Test Credentials
- reviewer@trendscout.click / ShopifyReview2026!

## ALL Completed Features

### Backlog Clearance (March 21, 2026)
- **Changelog page** (`/changelog`): 5 version entries (v3.0-v3.4) with categorised entries
- **TikTok Ad Budget Calculator**: Daily budget, CPC, conv rate, AOV → clicks, sales, revenue, ROAS, CPA
- **Product Validation Checklist**: 10 weighted items, 6 categories, 0-100 score with verdict
- **FAQ schema on comparison pages**: Structured JSON-LD + visible FAQ sections on all 5 comparisons
- **Trial expiry notifications**: `send_trial_expiry_notifications` task (every 2h) emails expired trial users
- **A/B testing framework**: `useABTest` hook with localStorage persistence and analytics tracking
- **Scoring consolidation**: `get_canonical_score`, `normalise_product_scores`, `score_label` utilities
- Verified: iteration_105.json (100%)

### CRO Features (March 21, 2026)
1. Exit-intent popup (desktop, lead magnet)
2. Social proof toasts (MOCKED UK names/cities)
3. Product quiz at /product-quiz (4 questions, recommendation)
4. Weekly digest for lead subscribers (Monday 9 AM UTC cron)
5. Tool recommender on comparison pages (3 questions)
6. Shareable calculator results (copy + X/Twitter)
- Verified: iteration_102.json (100%)

### Performance & Automation (March 21, 2026)
- Route-level code splitting (80+ lazy-loaded pages)
- Image lazy loading (all img tags + LazyImage component)
- react-snap pre-rendering (30 marketing pages)
- Blog: 3 seed + 2 AI articles, auto-generation cron
- GA4 ready (needs REACT_APP_GA4_ID in production .env)
- Verified: iteration_103, 104 (100%)

### Phase 3a: Lead Capture, Content Expansion
### Phase 2: Analytics, Schema, Viability Score
### Phase 1: Website Rebuild
(See previous PRD versions for details)

## Scheduled Tasks
| Task | Schedule | Description |
|------|----------|-------------|
| ingest_trending_products | Every 4h | Fetch products from sources |
| weekly_blog_generation | Mon 8 AM | Auto-generate blog posts |
| send_lead_subscriber_digest | Mon 9 AM | Trending products email to leads |
| send_weekly_email_digest | Mon 10 AM | Digest to registered users |
| send_trial_expiry_notifications | Every 2h | Email expired trial users |

## Free Tools (6 total)
1. UK Profit Margin Calculator
2. Break-even ROAS Calculator
3. UK VAT Calculator
4. Product Pricing Calculator
5. TikTok Ad Budget Calculator
6. Product Validation Checklist

## Remaining Work
- Set `REACT_APP_GA4_ID` in production .env
- Wire `useABTest` to hero CTA for live A/B testing
- SSR migration (Next.js) for better SEO crawlability
