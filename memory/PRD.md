# TrendScout PRD

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers.

## Core Positioning
"Find products that can actually sell in the UK."

## Tech Stack
- Frontend: React (CRA) + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-5.2 (via Emergent LLM Key)
- Payments: Stripe (GBP), Email: Resend
- Analytics: GTM (GTM-5V7G36GN) → GA4 (G-S9J8EPWKF9), consent-gated; PostHog
- Serving: Custom static server (serve.js) with prerendered content

## Completed Work

### GTM Integration (March 2026)
- GTM container GTM-5V7G36GN installed in index.html head (consent-gated)
- GTM noscript iframe immediately after body tag
- Standalone GA4 gtag.js snippet completely removed
- GA4 measurement ID G-S9J8EPWKF9 configured through GTM, not as separate site tag
- analytics.js updated to push events to dataLayer instead of gtag()
- Consent flow: dataLayer initialised → consent_default (denied) → user accepts → consent_update (granted) → GTM loads
- Verified: single page_view per page load, no duplicate GA4

### Crawlability Infrastructure (March 2026)
- Custom static server (serve.js) serving prerendered build files per route
- 39 pages with unique title, meta, canonical, OG, schema, H1, body, CTAs, links
- Legal pages with full policy text in first-response HTML

### Homepage & Marketing (March 2026)
- UK-first positioning throughout
- Cookie consent banner, proof sections, pricing preview

### Core Platform
- Product discovery, UK Viability Score, AI analysis
- Stripe subscriptions, admin tools, OAuth, WebSocket notifications

## Remaining Tasks
- P1: Configure GA4 tag inside GTM console (G-S9J8EPWKF9)
- P1: Configure Resend webhook URL
- P2: OAuth data sync from connected stores
- P3: Token refresh logic

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
