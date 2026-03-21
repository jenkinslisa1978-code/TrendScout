# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers.

## Architecture
- Backend: FastAPI + MongoDB + Redis + APScheduler
- Frontend: React CRA + Shadcn/UI + Tailwind + react-snap
- Auth: JWT + refresh cookie | Email: Resend | Payments: Stripe
- AI: GPT-5.2 via Emergent LLM Key (emergentintegrations)

## Test Credentials
- reviewer@trendscout.click / ShopifyReview2026!

## Completed Features

### Email Capture Gate on Quick Viability Search (March 21, 2026)
- **1 free search** without email, then email gate appears: "Unlock 3 more free searches"
- **Email capture** via POST /api/leads/capture (source: 'quick_viability_gate', context: searched product)
- **3 more searches** unlocked after email, progress dots + "X searches left" counter
- **Exhausted state** after 4 total: disabled input + "Sign up for unlimited" CTA
- **localStorage persistence**: ts_viability_searches (count), ts_viability_email (email)
- Verified: iteration_113 (100%, 10 backend + 20+ frontend tests)

### Interactive Demo & Quick Viability Search (March 21, 2026)
- Quick viability search with AI-powered UK viability assessment (GPT-5.2)
- Interactive 4-step product tour (Browse/Score/Analyse/Launch)
- Verified: iteration_112 (100%)

### Pricing Page Visual Enhancement (March 21, 2026)
- Gradient headline, plan icons, trust strip, comparison table, FAQ accordion
- Verified: iteration_111 (100%)

### How It Works Visual Walkthrough (March 21, 2026)
- 4-step walkthrough with AI-generated illustrations, interactive FAQ
- Verified: iteration_110 (100%)

### Homepage Split + Visual Redesign (March 21, 2026)
- Slim homepage + /features page + scroll animations + AI images
- Verified: iterations 108-109 (100%)

### All Previous Features
- Prediction Accuracy Tracking, Trust Framework, Methodology page
- Changelog, 6 free tools, Trial expiry, A/B framework, CRO suite
- Performance: Code splitting, lazy loading, react-snap, blog automation

## Key API Endpoints
- POST /api/public/quick-viability — AI product viability check (public)
- POST /api/leads/capture — Email lead capture
- GET /api/accuracy/stats — Prediction accuracy metrics
- POST /api/blog/seed — Blog content generation

## Remaining
- Wire `useABTest` hook to hero CTA (P1)
- Set `REACT_APP_GA4_ID` in production .env (P2)
