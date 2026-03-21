# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers. Discover trending products, analyse competition, estimate profit potential, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk.

## Core Positioning
"TrendScout helps UK sellers discover trending products, analyse competition, assess profit potential, and validate whether a product is actually viable in the UK before wasting money on ads, stock, or time."

## Architecture
- Backend: FastAPI + MongoDB + Redis
- Frontend: React CRA + Shadcn/UI + Tailwind CSS
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d)
- Email: Resend (transactional emails)
- Payments: Stripe
- Monitoring: Sentry, web-vitals

## Design System
- Fonts: Manrope (headings), Inter (body), JetBrains Mono (data)
- Primary: #4F46E5 (indigo)
- Background: #F8FAFC
- Cards: white with subtle borders

## Test Credentials
- Reviewer: reviewer@trendscout.click / ShopifyReview2026!

## ALL Features — COMPLETED

### Phase 3b: CRO Enhancement — 6 New Features (March 21, 2026)

**1. Exit-Intent Popup (ExitIntentPopup.jsx):**
- Triggers on desktop when mouse leaves viewport top
- Offers "UK Product Research Checklist" lead magnet
- Email capture via /api/leads/capture (source=exit_intent)
- localStorage dismissal for 7 days
- Only shows to non-authenticated visitors

**2. Social Proof Toast Notifications (SocialProofToast.jsx):**
- Periodic toast notifications on marketing pages
- Random UK names/cities with realistic actions (MOCKED data)
- First appears after 8 seconds, repeats every 25-40 seconds
- Only shows to non-authenticated visitors

**3. Interactive Product Quiz (/product-quiz):**
- 4-step quiz: channel, stage, challenge, budget
- Personalized recommendation with match percentage
- Email capture for "detailed report"
- Plan recommendation (Free/Starter/Pro/Elite)
- Added to nav dropdown and footer

**4. Weekly Email Digest (POST /api/leads/send-digest):**
- Admin-only endpoint (auth via STRIPE_WEBHOOK_SECRET)
- Sends top 5 trending products to all opted-in leads
- HTML email template via Resend API
- Logs digest sends in digest_log collection
- Leads automatically opted-in on capture (digest_opt_in: true)

**5. Tool Recommender (ToolRecommender.jsx):**
- 3-question inline widget: market, channels, priority
- Embedded in comparison pages between verdict and CTA
- Honest recommendation (can suggest competitor is better for US/Amazon-only sellers)
- Scoring logic based on UK focus, multi-channel, and priorities

**6. Shareable Calculator Results (ShareResult.jsx):**
- Copy-to-clipboard and X/Twitter share buttons
- Integrated into all 4 calculators on /tools page
- Native share API support on mobile
- Branded share text with TrendScout attribution

**Verified:** 100% — iteration_102.json

### Phase 3a: CRO Base, Lead Capture, Performance (March 19, 2026)
- Sample Product Analysis Page (/sample-product-analysis)
- Email Lead Capture (EmailCapture component + /api/leads/capture)
- 4 new high-intent landing pages
- 2 new competitor comparisons (Helium 10, Ecomhunt)
- Route-level code splitting (80+ lazy-loaded pages)
- Scroll depth analytics (25/50/75/100% thresholds)
- Mid-page CTAs, social proof, email capture on SeoLandingTemplate
- Verified: 100% — iteration_100 + iteration_101

### Phase 2: Analytics, Schema, Viability Score, SEO (March 19, 2026)
- GA4 Analytics Bridge, JSON-LD Schema, UK Product Viability Score
- 4 UK Landing Pages, Trust/Policy Pages
- Verified: 100% — iteration_99.json

### Phase 1: Website Rebuild (March 19, 2026)
- Complete public site rebuild, 4 UK landing pages, 3 comparison pages
- Free Tools, Navigation, Footer, SEO
- Verified: 100% — iteration_98.json

## Backlog

### P0 — High Priority
- Configure GA4 measurement ID (REACT_APP_GA4_ID) in production .env
- SSR/static generation for marketing pages

### P1 — Medium Priority
- Blog content strategy and article templates
- Changelog / product updates page
- Image lazy loading for product images
- Bundle size analysis

### P2 — Lower Priority
- More free tools (TikTok Ad Budget calculator, Product Validation Checklist)
- FAQ schema on comparison pages
- Backend scoring consolidation
- Trial expiry notification emails
