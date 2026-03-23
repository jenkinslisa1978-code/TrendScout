# TrendScout PRD

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers. TrendScout helps users discover trending products, analyse competition, estimate viability, and make better launch decisions for Shopify, TikTok Shop, and Amazon UK.

## Core Positioning
"Find products that can actually sell in the UK."

## Target Audience
- Shopify sellers, Amazon UK sellers, TikTok Shop UK sellers
- UK ecommerce founders, dropshippers, agencies / power users

## Tech Stack
- Frontend: React (CRA) + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-5.2 (via Emergent LLM Key)
- Payments: Stripe (GBP), Email: Resend
- Analytics: GA4 (consent-gated), PostHog
- Auth: JWT, Prerendering: Custom content-injecting Node.js script

## Completed Work

### Crawlability & SEO Infrastructure (March 2026)
- **Content-injecting prerender system**: 39 pages get unique title, meta description, canonical, OG tags, JSON-LD schema, H1, body copy, CTAs, and internal links in first-response HTML
- **Legal pages in raw HTML**: Privacy, Terms, Cookie Policy, Refund Policy all have full legal text in prerendered output
- **Sitemap.xml**: 60+ URLs covering all marketing, commercial intent, comparison, tool, and legal pages
- **Robots.txt**: Clean, blocks private routes, allows all public routes, includes sitemap reference
- **Noscript fallback**: Updated to UK-first positioning with correct nav links
- **index.js**: Hides prerender-content after React mount
- Verified: iteration_118 (100% pass)

### Homepage Conversion & Trust (March 2026)
- Hero: "Find products that can actually sell in the UK." with 3 value points
- Trust strip, Who it's for (4 audience cards), UK Differentiation section
- How it works (3-step flow), Feature highlights, Proof section, Pricing preview, Final CTA
- Cookie consent banner (Accept all / Reject non-essential)
- GA4/GTM consent-gated in index.html and analytics.js

### Site-wide Improvements (March 2026)
- Cookie policy with 3 documented categories
- Sample analysis: product image, schema.org Product markup, expanded internal links
- About page: scoring methodology section
- Security headers: CSP, HSTS, X-Frame-Options
- html lang="en-GB", alternate routes for SEO

### Core Platform (v1)
- Product discovery dashboard, UK Viability Score (7-signal model)
- AI product analysis, user auth, Stripe subscriptions
- Admin Command Center, Analytics dashboard
- WebSocket notifications, OAuth 2.0 flows

## Remaining Tasks
- P1: Set REACT_APP_GA4_ID in production .env
- P1: Configure Resend webhook URL
- P2: Implement data sync from connected OAuth stores
- P3: OAuth token refresh logic

## Key Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
