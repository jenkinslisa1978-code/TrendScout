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

### Homepage Visual Redesign (March 21, 2026)
- **Hero section**: Split layout with headline on left, AI-generated dashboard mockup on right
- **4 AI-generated images**: Dashboard mockup, product analysis visual, UK ecommerce data map, trending products interface
- **Visual storytelling**: Each major section now paired with relevant imagery
- **Feature showcase**: Product viability analysis image + feature cards
- **UK section**: UK data map visual with feature badges
- **Free tools teaser**: New section promoting free calculators
- **Improved hierarchy**: Section labels, gradient accents, modern card design with hover effects
- **Floating badge**: Products tracked counter on hero
- **Responsive**: Fully tested on desktop and mobile
- Verified: iteration_108 (100%, 21/21 tests)

### Prediction Accuracy Tracking System (March 21, 2026)
- **GET /api/accuracy/stats**: Live endpoint returning real tracked accuracy data
- **Prediction snapshots**: Every scored product is snapshotted (score, margin, trend, signals)
- **30/90 day reviews**: Daily cron (`review_prediction_accuracy`, 6 AM UTC) compares snapshots vs current data
- **Accuracy page** (`/accuracy`): Shows live-tracked stats when enough data (5+ reviews), honest "building track record" state otherwise
- **Honesty overhaul**: Removed fabricated "2,000+ sellers", "85% accuracy", fake case studies
- **Real vs estimated transparency**: Clear section explaining what is real data vs calculated estimates
- DB collections: `prediction_snapshots`, `prediction_reviews`
- Verified: iteration_107 (100%)

### Trust & Accuracy Framework (March 21, 2026)
- Methodology page (/methodology), Confidence indicators, Accuracy disclaimers, Data source labels
- Verified: iteration_106 (100%)

### All Previous Features
- Changelog, 6 free tools, FAQ schema, Trial expiry, A/B framework, Scoring consolidation
- CRO: Exit-intent, Social proof, Quiz, Digest, Tool recommender, Shareable results
- Performance: Code splitting, Lazy loading, react-snap, Blog automation
- Phase 3a/2/1: Website rebuild, analytics, schema, viability score, lead capture

## Scheduled Tasks
| Task | Schedule | Description |
|------|----------|-------------|
| review_prediction_accuracy | Daily 6 AM | Snapshot new products + review 30/90 day predictions |
| weekly_blog_generation | Monday 8 AM | Auto-generate blog posts |
| send_lead_subscriber_digest | Monday 9 AM | Trending products email to leads |
| send_weekly_email_digest | Monday 10 AM | Digest to registered users |
| send_trial_expiry_notifications | Every 2h | Email expired trial users |

## Remaining
- Wire `useABTest` hook to hero CTA (P1)
- Set `REACT_APP_GA4_ID` in production .env (P2)
