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

### Phase 2: Analytics, Schema, Viability Score, SEO (March 19, 2026)

**GA4 Analytics Bridge:**
- Analytics service upgraded with GA4 gtag() bridge — fires to both internal batch API and GA4 when configured
- 20+ named event constants: HOMEPAGE_PRIMARY_CTA, PRICING_TOGGLE, PRICING_PLAN_SELECTED, FREE_TOOL_USED, COMPARE_PAGE_CTA, UK_LANDING_CTA, VIABILITY_BADGE_CLICK, etc.
- Events wired to: hero CTAs, pricing toggle, plan selection, comparison CTAs, free tool tabs, landing page CTAs
- GA4 measurement ID configurable via REACT_APP_GA4_ID env var

**JSON-LD Schema Markup (all pages):**
- Homepage: Organization + WebSite + SoftwareApplication
- Pricing: SoftwareApplication + FAQPage + BreadcrumbList
- How It Works: WebPage + FAQPage + BreadcrumbList
- About: AboutPage + BreadcrumbList
- Contact: ContactPage + BreadcrumbList
- UK Viability Score: WebPage + FAQPage + BreadcrumbList
- All UK landing pages: WebPage + FAQPage + BreadcrumbList via SeoLandingTemplate
- All comparison pages: WebPage + BreadcrumbList
- Free Tools: BreadcrumbList + FAQPage
- Policy pages: BreadcrumbList

**Reusable PageMeta component** with schema builders: organizationSchema, websiteSchema, softwareAppSchema, faqSchema(), breadcrumbSchema(), webPageSchema()

**Technical SEO:**
- robots.txt: blocks /dashboard, /admin, /api/, /login, /signup, /settings, /reset-password, /forgot-password, /saved-products, /notification, /ad-tests, etc.
- sitemap.xml: 30+ URLs covering all public pages
- Canonical tags on all public pages via PageMeta component

**UK Product Viability Score (Flagship Feature):**
- Dedicated page at /uk-product-viability-score with: hero, 7 weighted factors, 3-tier score interpretation, 3 product examples, 6 FAQ, CTA
- ViabilityBadge component: expandable badge showing score, band label, progress bar, and explainer
- ViabilityIndicator component: compact inline indicator for product cards
- Live on homepage product cards — every product shows UK Viability Score
- Referenced throughout: homepage, how-it-works, UK landing pages, methodology section

**New UK Landing Pages (4):**
- /dropshipping-product-research-uk
- /winning-products-uk
- /product-validation-uk
- /uk-ecommerce-trend-analysis
Each with unique copy, features, steps, UK points, FAQ, CTA, related links, canonical, meta description

**Trust/Policy Pages:**
- /cookie-policy — cookie types, third-party, management instructions
- /refund-policy — trial, cancellation, refunds, annual plans, billing

**Footer Updates:**
- Added: UK Viability Score, UK Dropshipping, Winning Products UK links
- Added: Cookie Policy, Refund Policy in legal row

**Verified:** 100% frontend pass — iteration_99.json

### Phase 1: Website Rebuild (March 19, 2026)
- Homepage, Pricing, How It Works, About, Contact pages rebuilt
- 4 UK landing pages (uk-product-research, for-shopify, for-amazon-uk, for-tiktok-shop-uk)
- 3 competitor comparison pages (vs Jungle Scout, Sell The Trend, Minea)
- Free Tools page (4 calculators)
- Navigation with dropdowns, mobile responsive menu
- 5-column footer with internal linking
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
- Email capture on free tool result pages
- Sample product analysis page with public mock data
- Changelog / product updates page
- Performance optimisation (image lazy loading, code splitting, font optimisation)

### P2 — Lower Priority
- Additional comparison pages (Helium 10, Ecomhunt)
- More free tools (TikTok Ad Budget calculator, Product Validation Checklist)
- FAQ schema on comparison pages
- SoftwareApplication schema on UK landing pages
- Backend scoring consolidation (unify launch_score + overall_score)
- Trial expiry notification emails
