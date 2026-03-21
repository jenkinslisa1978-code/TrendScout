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

### Pricing Page Visual Enhancement (March 21, 2026)
- **Gradient headline**: Matching site-wide style
- **Enhanced pricing cards**: Plan icons (Eye/TrendingUp/Rocket), improved spacing, bigger prices, rounded checkmarks
- **Most Popular badge**: Sparkles icon, centered pill, indigo shadow
- **Trust strip**: "7 days, 0 contracts, GBP, < 2 min" section between cards and comparison table
- **Improved comparison table**: Rounded container, better column headers, indigo highlight on Growth
- **FAQ accordion**: Consistent with How It Works page (animated chevron, smooth expand/collapse)
- **Final CTA**: Dark section with gradient accent
- **Scroll animations**: RevealSection/RevealStagger across all sections
- Stripe checkout functionality fully preserved
- Verified: iteration_111 (100%, 21/21 tests)

### How It Works Visual Walkthrough (March 21, 2026)
- 4-step visual walkthrough with AI-generated illustrations, alternating layouts, interactive FAQ
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
- `/app/frontend/src/pages/LandingPage.jsx` - Focused homepage
- `/app/frontend/src/pages/FeaturesPage.jsx` - Detailed features
- `/app/frontend/src/pages/HowItWorksPage.jsx` - Visual walkthrough
- `/app/frontend/src/pages/PricingPage.jsx` - Enhanced pricing
- `/app/frontend/src/hooks/useScrollReveal.js` - Scroll animations

## Remaining
- Wire `useABTest` hook to hero CTA (P1)
- Set `REACT_APP_GA4_ID` in production .env (P2)
