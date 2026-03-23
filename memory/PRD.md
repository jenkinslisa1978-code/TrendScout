# TrendScout PRD

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers. TrendScout helps users discover trending products, analyse competition, estimate viability, and make better launch decisions for Shopify, TikTok Shop, and Amazon UK.

## Core Positioning
"Find products that can actually sell in the UK."

## Target Audience
- Shopify sellers
- Amazon UK sellers
- TikTok Shop UK sellers
- UK ecommerce founders
- Dropshippers
- Agencies / power users

## Tech Stack
- Frontend: React (CRA) + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-5.2 (via Emergent LLM Key)
- Payments: Stripe (GBP)
- Email: Resend
- Analytics: GA4 (consent-gated), PostHog
- Auth: JWT custom auth
- Prerendering: Custom Node.js script (prerender.js) for SEO

## Completed Work

### v1 Core Platform
- Full product discovery dashboard with trending products
- UK Product Viability Score (7-signal scoring model)
- AI-powered product analysis (ad creatives, launch simulation, profit estimation)
- User authentication and subscription management (Stripe)
- Admin Command Center (/admin/hub)
- Growth & Revenue Analytics dashboard (/admin/analytics)

### Homepage Conversion Redesign (March 2026)
- Hero: "Find products that can actually sell in the UK."
- 3 practical value points: trend detection, saturation analysis, UK viability
- Trust strip: 4 credibility statements
- Who it's for: 4 audience cards (Shopify, Amazon UK, TikTok Shop UK, UK founders)
- UK Differentiation: "Not every viral product works in the UK" with US vs UK comparison
- How it works: 3-step flow (Discover, Analyse, Launch)
- Feature highlights: 4 outcome-focused cards
- Proof section: "See what TrendScout shows you" linking to sample analysis
- Pricing preview: 3 plans in GBP with Growth highlighted
- Final CTA: validated, specific language

### Site-wide Improvements (March 2026)
- Cookie consent banner (Accept all / Reject non-essential) with localStorage persistence
- GA4/GTM consent-gated (scripts only load after explicit consent)
- Analytics service consent-gated (sendToGA4 checks consent)
- Cookie policy page with 3 documented categories (essential, analytics, preference)
- Sample analysis page: product image, schema.org Product markup, improved internal links
- Viability score page: sample analysis CTA, improved internal links
- About page: scoring methodology section with transparency
- Security headers: CSP updated, HSTS, X-Frame-Options, Referrer-Policy
- html lang="en-GB" for UK localisation
- Expanded sitemap.xml (all marketing pages, commercial intent pages, comparison pages)
- Expanded prerender.js (35 routes for static HTML shells)
- Alternate routes: /for-shopify-sellers, /for-amazon-uk-sellers, /dropshipping-uk, /trend-analysis-uk
- Pricing page: updated taglines, "Try before you commit" language

### OAuth & Real-time Features (March 2026)
- WebSocket notifications (useNotifications hook, ws_manager.py)
- OAuth 2.0 flows for Shopify, Etsy, Amazon Seller, TikTok Shop, Meta, Google Ads
- Platform Connections hub (/settings/connections)

### Deployment Fixes (March 2026)
- Removed jsdom (unused, blocked build on Node 20.18.1)
- Removed react-snap (replaced by custom prerender.js)
- Removed Emergent badge and script

## Remaining Tasks
- P1: Set REACT_APP_GA4_ID in production .env
- P1: Configure Resend webhook URL
- P2: Implement actual data sync from connected OAuth stores
- P3: Add OAuth token refresh logic for expired tokens

## Key Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
