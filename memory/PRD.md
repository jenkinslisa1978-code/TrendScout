# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers.

## Architecture
- Backend: FastAPI + MongoDB + Redis + APScheduler
- Frontend: React CRA + Shadcn/UI + Tailwind + react-snap
- Auth: JWT + refresh cookie | Email: Resend | Payments: Stripe

## Test Credentials
- reviewer@trendscout.click / ShopifyReview2026!

## Completed Features

### Trust & Accuracy Framework (March 21, 2026)
- **Methodology page** (`/methodology`): 7-signal framework explained with weights, calculation methods, data sources, FAQ, confidence levels
- **Accuracy page** (`/accuracy`): 4 predicted-vs-actual case studies, 3 summary stats (85% margin accuracy, 78% trend direction, 4h refresh), honest limitations
- **Confidence indicators**: High/Medium/Low badges next to scores (based on data availability), linked to methodology
- **Accuracy disclaimers**: Contextual disclaimers on calculators, scores, trends, margins — linked to methodology/accuracy pages
- **Data source transparency**: Source labels (Google Trends UK, Amazon UK BSR, TikTok Shop, CJ Dropshipping) on signal breakdowns
- **Last updated timestamps**: Visible on product data points
- Verified: iteration_106 (100%, 24/24 tests)

### Backlog Clearance (March 21, 2026)
- Changelog page, TikTok Ad Budget Calculator, Product Validation Checklist
- FAQ schema on comparisons, Trial expiry emails, A/B testing framework, Scoring consolidation
- Verified: iteration_105 (100%, 19/19 tests)

### CRO Features (March 21, 2026)
- Exit-intent popup, Social proof toasts, Product quiz, Weekly digest, Tool recommender, Shareable results
- Verified: iteration_102 (100%)

### Performance & Automation (March 21, 2026)
- Code splitting (80+ lazy pages), Image lazy loading, react-snap, Blog automation, GA4 ready
- Verified: iterations 100-104 (all 100%)

### Phase 3a, 2, 1 (March 19, 2026)
- Website rebuild, analytics, schema, viability score, lead capture, content expansion
- Verified: iterations 98-99 (all 100%)

## Pages & Routes
| Type | Pages |
|------|-------|
| Marketing | /, /pricing, /how-it-works, /about, /contact |
| Trust | /methodology, /accuracy, /sample-product-analysis |
| Free Tools | /tools (6 calculators), /product-quiz |
| Content | /blog, /changelog, 8+ UK landing pages, 5 competitor comparisons |
| Legal | /terms, /privacy, /cookie-policy, /refund-policy |

## Remaining
- Set `REACT_APP_GA4_ID` in production .env
- Wire `useABTest` hook to hero CTA for live A/B testing
- SSR/Next.js migration (long-term)
