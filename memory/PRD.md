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

### How It Works Visual Walkthrough Redesign (March 21, 2026)
- **4-step visual walkthrough**: Each step has AI-generated illustration + text with alternating left/right layouts
- **Step images**: Discover (multi-channel), Scoring (78/100 gauge), UK Viability (UK map), Launch (rocket dashboard)
- **Interactive FAQ accordion**: Click to expand/collapse, only one open at a time
- **Scroll animations**: RevealSection/RevealStagger applied across all sections
- **Enhanced sections**: 7-signal scoring grid, color-coded score tiers, who it's for/not for cards, UK viability factors
- Verified: iteration_110 (100%, 22/22 tests)

### Scroll-Triggered Fade-In Animations (March 21, 2026)
- useScrollReveal hook with RevealSection (directional) and RevealStagger (staggered children)
- Applied to homepage, features page, and how-it-works page

### Homepage Split into Separate Pages (March 21, 2026)
- **Slim homepage**: Hero + trust bar + 4 feature cards + 3 live products + CTA
- **Dedicated /features page**: Core capabilities, UK intelligence, methodology, use cases, free tools
- **Navigation**: "Features" added as first top-level nav link
- Verified: iteration_109 (100%, 22/22 tests)

### Homepage Visual Redesign (March 21, 2026)
- 4 AI-generated images: dashboard mockup, product analysis, UK data map, trending products
- Verified: iteration_108 (100%, 21/21 tests)

### All Previous Features
- Prediction Accuracy Tracking, Trust & Accuracy Framework, Methodology page
- Changelog, 6 free tools, FAQ schema, Trial expiry, A/B framework
- CRO: Exit-intent, Social proof, Quiz, Digest, Tool recommender
- Performance: Code splitting, Lazy loading, react-snap, Blog automation
- Phase 3a/2/1: Website rebuild, analytics, schema, viability score, lead capture

## Key Files
- `/app/frontend/src/pages/LandingPage.jsx` - Focused homepage
- `/app/frontend/src/pages/FeaturesPage.jsx` - Detailed features page
- `/app/frontend/src/pages/HowItWorksPage.jsx` - Visual walkthrough
- `/app/frontend/src/hooks/useScrollReveal.js` - Scroll animation hook

## Remaining
- Wire `useABTest` hook to hero CTA (P1)
- Set `REACT_APP_GA4_ID` in production .env (P2)
