# TrendScout PRD

## Product Vision
UK-focused product validation and trend analysis tool for ecommerce sellers.

## Core Positioning
**"UK Product Validation Tool"** — a single positioning angle applied site-wide.

## Tech Stack
- Frontend: React (CRA/Craco) + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-5.2 (via Emergent LLM Key)
- Payments: Stripe (GBP), Email: Resend
- Analytics: GTM (GTM-5V7G36GN) → GA4 (G-S9J8EPWKF9), consent-gated
- Serving: Custom static server (serve.js) + prerendered content (39 pages)
- Build: `cd /app/frontend && yarn build && sudo supervisorctl restart frontend`

## Completed Work

### CRO/SEO/Positioning Overhaul (March 2026)
**Homepage Rewrite:**
- New H1: "Validate product ideas for the UK market before you spend a penny"
- Conversion flow: Hero → Trust Bar → How It Works (3 steps) → UK Viability Score Explainer → Products → Proof → Who It's For/Not For → Pricing Preview → Data Sources → FAQ (7 questions) → Final CTA
- Outcome-based CTAs: "Validate Your First Product", "See a Live Example", "Validate a Product"
- New sections: UK Viability Score (with US vs UK comparison), Data Sources transparency, Who It's For/Not For, FAQ with accordion

**SEO Titles (all unique per page):**
- Homepage: "UK Product Validation Tool for Ecommerce Sellers | TrendScout"
- Pricing: "Plans and Pricing — Start from £19/mo | TrendScout"
- How It Works: "How TrendScout Validates Products for the UK Market"
- Sample Analysis: "Live Product Analysis Example — See What You Get | TrendScout"
- Features: "Product Research Features for UK Ecommerce Sellers | TrendScout"
- About: "About TrendScout — Why We Built a UK-First Product Validation Tool"

**Trust Improvements:**
- UK Viability Score explanation (7 signals enumerated)
- US vs UK market comparison card showing different economics
- Data sources transparency section (Amazon UK, TikTok, Shopify, Search data)
- Who it's for / not for honest positioning
- FAQ addressing key objections

**CTA Changes:**
- All "Start Free" → "Validate Your First Product" or "Validate a Product"
- All pricing CTAs → "Start validating products"
- Nav header → "Validate a Product"

**Fixed duplicate title suffix** — PageMeta now intelligently avoids double "| TrendScout"
- Test report: /app/test_reports/iteration_123.json (100% pass)

### Shopify Integration Suite (March 2026)
- One-click OAuth, Synced Products dashboard, Webhooks, Token refresh
- Test: iteration_122.json (100% pass)

### QA Audit & Bug Fixes (March 2026)
- Mobile overflow fix, login error handling verified
- Test: iteration_120.json (100% pass)

### Previous Work
- GTM integration, crawlability infrastructure, core platform features

## Key Files
- frontend/src/pages/LandingPage.jsx — Homepage (full rewrite)
- frontend/src/components/PageMeta.jsx — SEO metadata component
- frontend/prerender-data.js — Prerendered content for crawlers
- frontend/src/components/layouts/LandingLayout.jsx — Site header/footer/nav

## Remaining Tasks
- P1: Add Meta/Etsy/TikTok/Google Ads app credentials for one-click OAuth
- P1: Configure GA4 tag inside GTM console (user task)
- P1: Configure Resend webhook URL (user task)
- P2: Data sync from other stores (Etsy, WooCommerce)
- P2: Synced products dashboard view enhancements
- P3: SSR for dynamic pages

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
