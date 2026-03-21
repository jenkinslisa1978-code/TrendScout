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

### Interactive Demo & Quick Viability Search (March 21, 2026)
- **Quick Viability Search**: "Try It Now" section on homepage — type any product idea, get instant AI-powered UK viability assessment (score, verdict, signals, strengths, risks, summary). No signup required.
- **Backend endpoint**: POST /api/public/quick-viability — uses GPT-5.2 via Emergent LLM Key, returns structured JSON
- **Interactive Product Tour**: 4-step clickable walkthrough (Browse → Score → Analyse → Launch) with mock browser chrome, mock product data, step progress indicator, and "Next" navigation
- **Suggestion chips**: 4 pre-filled product ideas for quick testing
- Verified: iteration_112 (100%, 8 backend + 25+ frontend tests)

### Pricing Page Visual Enhancement (March 21, 2026)
- Gradient headline, plan icons, trust strip, improved comparison table, FAQ accordion
- Verified: iteration_111 (100%, 21/21 tests)

### How It Works Visual Walkthrough (March 21, 2026)
- 4-step walkthrough with AI-generated illustrations, interactive FAQ
- Verified: iteration_110 (100%, 22/22 tests)

### Scroll-Triggered Animations (March 21, 2026)
- useScrollReveal hook with RevealSection + RevealStagger, applied site-wide

### Homepage Split (March 21, 2026)
- Slim homepage + dedicated /features page + nav updated
- Verified: iteration_109 (100%, 22/22 tests)

### Homepage Visual Redesign (March 21, 2026)
- 4 AI-generated images, verified: iteration_108 (100%, 21/21 tests)

### All Previous Features
- Prediction Accuracy Tracking, Trust Framework, Methodology page
- Changelog, 6 free tools, FAQ schema, Trial expiry, A/B framework
- CRO: Exit-intent, Social proof, Quiz, Digest, Tool recommender
- Performance: Code splitting, Lazy loading, react-snap, Blog automation

## Key Files
- `/app/frontend/src/pages/LandingPage.jsx` - Homepage
- `/app/frontend/src/pages/FeaturesPage.jsx` - Features
- `/app/frontend/src/pages/HowItWorksPage.jsx` - Visual walkthrough
- `/app/frontend/src/pages/PricingPage.jsx` - Pricing
- `/app/frontend/src/components/QuickViabilitySearch.jsx` - AI search
- `/app/frontend/src/components/InteractiveDemo.jsx` - Product tour
- `/app/frontend/src/hooks/useScrollReveal.js` - Scroll animations
- `/app/backend/routes/public.py` - Quick viability API

## Key API Endpoints
- POST /api/public/quick-viability — AI product viability check (public, no auth)
- GET /api/accuracy/stats — Prediction accuracy metrics
- POST /api/leads/capture — Lead capture
- POST /api/blog/seed — Blog content generation

## Remaining
- Wire `useABTest` hook to hero CTA (P1)
- Set `REACT_APP_GA4_ID` in production .env (P2)
