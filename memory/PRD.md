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

### Phase 3: CRO, Lead Capture, Performance (March 19, 2026)

**Sample Product Analysis Page:**
- Public-facing page at /sample-product-analysis with mock Portable Neck Fan data
- Viability score, 7-signal breakdown, AI summary, channel fit, strengths/risks
- Scroll depth tracking via useScrollDepth hook

**Email Lead Capture:**
- Reusable EmailCapture component
- Integrated into: FreeToolsPage, SeoLandingTemplate, ComparisonPage
- Backend: POST /api/leads/capture endpoint (upsert, validates email)
- Analytics: EMAIL_CAPTURE_VIEW, EMAIL_CAPTURE_SUBMIT events

**Content Expansion:**
- 4 new high-intent landing pages: /best-products-to-sell-online-uk, /tiktok-shop-product-research-uk, /shopify-product-research-uk, /product-validation-uk
- 2 new competitor comparisons: Helium 10, Ecomhunt (merged into ComparisonPage)

**Performance Optimisation:**
- Route-level code splitting: 80+ pages lazy-loaded via React.lazy()
- Only LandingPage and NotFoundPage are eager-loaded
- Suspense fallback with branded spinner
- Font loading optimisation (media=print with onload)

**Conversion Path Improvements:**
- Mid-page CTA in SeoLandingTemplate after features ("See a sample product report")
- Social proof in bottom CTAs ("Join 2,000+ UK sellers already using TrendScout")
- EmailCapture as low-commitment alternative on all landing + comparison pages
- "Compare Plans" replaced "See Trending Products" in bottom CTA for stronger conversion intent
- Cross-linking: mid-page links to /tools, /sample-product-analysis

**Scroll Depth Analytics:**
- useScrollDepth hook fires SCROLL_DEPTH events at 25%, 50%, 75%, 100%
- Active on: SeoLandingTemplate, ComparisonPage, SampleAnalysisPage

**Cleanup:**
- Deleted redundant MoreComparisonsPage.jsx and removed its route from App.js

**Verified:** 100% — iteration_100.json (base), iteration_101.json (improvements)

### Phase 2: Analytics, Schema, Viability Score, SEO (March 19, 2026)

**GA4 Analytics Bridge:**
- Analytics service with GA4 gtag() bridge
- 20+ named event constants
- Events wired to hero CTAs, pricing toggle, plan selection, comparison CTAs, free tool tabs

**JSON-LD Schema Markup:** All public pages have appropriate schema

**UK Product Viability Score (Flagship Feature):**
- Dedicated page, ViabilityBadge, ViabilityIndicator components
- Live on homepage product cards

**New UK Landing Pages:** 4 pages with SeoLandingTemplate

**Trust/Policy Pages:** Cookie policy, refund policy

**Verified:** 100% — iteration_99.json

### Phase 1: Website Rebuild (March 19, 2026)
- Homepage, Pricing, How It Works, About, Contact pages rebuilt
- 4 UK landing pages, 3 competitor comparison pages
- Free Tools page (4 calculators), Navigation with dropdowns
- SEO meta tags + OG tags
- Verified: 100% — iteration_98.json

### Previously Completed
(See prior PRD for full list: Shopify OAuth, launch scores, AI generators, content gating, free trials, etc.)

## Backlog

### P0 — High Priority
- Configure GA4 measurement ID (REACT_APP_GA4_ID) in production .env
- SSR/static generation for marketing pages (requires Next.js migration or pre-rendering solution)

### P1 — Medium Priority
- Blog content strategy and article templates
- Changelog / product updates page
- Image lazy loading for product images (consider react-lazy-load-image-component)
- Bundle size analysis and further tree shaking

### P2 — Lower Priority
- More free tools (TikTok Ad Budget calculator, Product Validation Checklist)
- FAQ schema on comparison pages
- SoftwareApplication schema on UK landing pages
- Backend scoring consolidation (unify launch_score + overall_score)
- Trial expiry notification emails
