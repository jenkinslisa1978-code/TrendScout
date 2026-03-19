# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers. Discover trending products, analyse competition, estimate profit potential, and launch faster across Shopify, TikTok Shop, and Amazon.co.uk.

## Core Positioning
"TrendScout helps UK sellers discover trending products, analyse competition, assess profit potential, and validate whether a product is actually viable in the UK before wasting money on ads, stock, or time."

## Architecture
- Backend: FastAPI + MongoDB + Redis
- Frontend: React CRA + Shadcn/UI + Tailwind CSS
- Auth: JWT (15min access tokens) + __Host-refresh cookie (7d) + forgot/reset password with email
- Email: Resend (transactional emails)
- Security: HSTS, CSP, CSRF, Fernet encryption
- Monitoring: Sentry, PostHog, web-vitals
- Real-time: WebSocket notifications

## Design System
- Fonts: Manrope (headings), Inter (body), JetBrains Mono (data)
- Primary: #4F46E5 (indigo)
- Background: #F8FAFC
- Cards: white with subtle borders
- Philosophy: "Performance Pro" — clean, light, data-focused

## Target Audience
- Shopify UK sellers
- Amazon UK sellers
- TikTok Shop UK sellers
- UK dropshippers
- Ecommerce founders
- Agencies researching products for clients

## Test Credentials
- Reviewer: reviewer@trendscout.click / ShopifyReview2026!
- Admin: jenkinslisa1978@gmail.com / admin123456

## ALL Features — COMPLETED

### Website Rebuild — UK-First Conversion Focus (March 19, 2026)
Complete rebuild of all public-facing pages with UK-first positioning and conversion focus.

**Pages rebuilt/created:**
1. **Homepage** (`/`) — UK-first hero, trust bar, 4 feature cards, 4-step how it works, live trending products, UK viability section (6 factors), 6 use case cards, 7-signal methodology showcase, final CTA
2. **Pricing** (`/pricing`) — Monthly/annual toggle (Save 20%), 3 tiers in GBP (Starter £19/£15, Growth £39/£31, Pro £79/£63), 13-row feature comparison table, 6 FAQ accordions
3. **How It Works** (`/how-it-works`) — 4-step process, 7-signal scoring model with weights, score interpretation guide (4 tiers), who it's for/not for, UK viability section, FAQ
4. **About** (`/about`) — Company story, 4 values, company details (TrendScout Ltd, UK)
5. **Contact** (`/contact`) — Email, help centre, response times, company details
6. **UK Product Research** (`/uk-product-research`) — SEO landing page with unique UK-focused copy
7. **For Shopify** (`/for-shopify`) — Shopify-specific features, push-to-store highlight
8. **For Amazon UK** (`/for-amazon-uk`) — Amazon UK-specific copy, FBA fee integration
9. **For TikTok Shop UK** (`/for-tiktok-shop-uk`) — TikTok-specific features, virality vs viability
10. **vs Jungle Scout** (`/compare/jungle-scout-vs-trendscout`) — Feature comparison table, verdict
11. **vs Sell The Trend** (`/compare/sell-the-trend-vs-trendscout`) — Different content per competitor
12. **vs Minea** (`/compare/minea-vs-trendscout`) — Ad spy angle comparison
13. **Free Tools** (`/free-tools`) — 4 calculators: Profit Margin, ROAS, UK VAT, Product Pricing

**Navigation & Footer:**
- Dropdown nav: Product (Trending, Leaderboard, Free Tools) + Solutions (Shopify, Amazon, TikTok, UK Research)
- 5-column footer: Product, Solutions, Compare, Company + legal links
- Mobile responsive menu

**SEO & Meta:**
- Updated title: "TrendScout | AI Product Research for UK Ecommerce Sellers"
- Updated meta description and OG tags for UK positioning
- og:locale set to en_GB

**Reusable Components:**
- `SeoLandingTemplate` — template for all SEO landing pages
- `ComparisonPage` — handles all /compare/:slug routes with per-competitor data

**Verified:** 100% frontend pass — iteration_98.json

### Previously Completed Features
(See CHANGELOG.md for full history)
- Email-powered password reset, production hardening, programmatic SEO
- Shopify OAuth, 5 ecommerce platforms, 3 ad platforms
- Launch score, profit predictor, launch playbook, ad generator
- Ad Intelligence, Profitability Simulator, 7-Signal Score Breakdown
- Competitor Intelligence, Radar Alerts, Verified Winners
- TikTok Intelligence, CJ Dropshipping Integration
- WebSocket notifications, API access for power users
- Content gating, free trial mechanic, mobile responsive layout
- Shopify App Bridge embedded dashboard, GDPR compliance

## Backlog

### P0 — High Priority
- Server-side rendering / static generation for marketing pages (SSR/SSG)
- Proper canonical tags and schema markup (JSON-LD) on all public pages
- robots.txt and XML sitemap updates for new pages

### P1 — Medium Priority
- Additional UK landing pages: /dropshipping-product-research-uk, /winning-products-uk, /product-validation-uk, /uk-ecommerce-trend-analysis
- "UK Product Viability Score" branded feature with dedicated landing page
- Blog content strategy and article templates
- GA4 + Search Console event tracking for conversion measurement
- User journey optimisation (signup to activation to upgrade flow)

### P2 — Lower Priority
- Breadcrumb schema on all pages
- SoftwareApplication schema on commercial pages
- FAQ schema on pages with FAQ sections
- Changelog / roadmap page
- Cookie policy page
- Refund/cancellation policy page
- Performance optimisation (image lazy loading, code splitting)

### P3 — Backlog
- Backend scoring consolidation (unify launch_score + overall_score)
- Trial expiry notification emails
- Programmatic content templates for category and trend pages at scale
