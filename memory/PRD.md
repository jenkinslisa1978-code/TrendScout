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

### Scroll-Triggered Fade-In Animations (March 21, 2026)
- **useScrollReveal hook**: IntersectionObserver-based scroll reveal with directional animations
- **RevealSection component**: Fade-in with configurable direction (up/down/left/right) and delay
- **RevealStagger component**: Staggered child reveals with configurable timing
- Applied to both homepage and features page sections
- Verified: visual smoke test passed

### Homepage Split into Separate Pages (March 21, 2026)
- **Slim homepage**: Hero + trust bar + 4 feature cards + 3 live trending products + final CTA (~3036px)
- **New /features page**: Core capabilities, UK intelligence, 7-signal methodology, 6 use cases, free tools, CTA
- **Navigation updated**: "Features" added as first top-level nav link
- Verified: iteration_109 (100%, 22/22 tests)

### Homepage Visual Redesign (March 21, 2026)
- 4 AI-generated images: dashboard mockup, product analysis, UK data map, trending products interface
- Verified: iteration_108 (100%, 21/21 tests)

### Prediction Accuracy Tracking System (March 21, 2026)
- GET /api/accuracy/stats, prediction snapshots, 30/90 day reviews, accuracy page
- Honesty overhaul: removed fabricated stats
- Verified: iteration_107 (100%)

### All Previous Features
- Trust & Accuracy Framework, Methodology page, Confidence indicators
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

## Key Files
- `/app/frontend/src/pages/LandingPage.jsx` - Focused homepage
- `/app/frontend/src/pages/FeaturesPage.jsx` - Detailed features page
- `/app/frontend/src/hooks/useScrollReveal.js` - Scroll animation hook

## Remaining
- Wire `useABTest` hook to hero CTA (P1)
- Set `REACT_APP_GA4_ID` in production .env (P2)
