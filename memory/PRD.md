# TrendScout PRD

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers. Helps users discover trending products, analyse competition, estimate viability, and make better launch decisions for Shopify, TikTok Shop, and Amazon UK.

## Core Positioning
"Find products that can actually sell in the UK."

## Tech Stack
- Frontend: React (CRA) + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-5.2 (via Emergent LLM Key)
- Payments: Stripe (GBP), Email: Resend
- Analytics: GA4 (consent-gated), PostHog
- Serving: Custom static server (serve.js) serving prerendered build files
- Prerendering: Content-injecting Node.js script (39 routes with unique HTML)

## Completed Work

### Crawlability Infrastructure (March 2026)
- **Custom static server (serve.js)**: Resolves prerendered HTML per route, falls back to root index.html for app routes
- **Content-injecting prerender (prerender.js + prerender-data.js)**: 39 pages with unique title, meta description, canonical, OG tags, JSON-LD schema, H1, body copy, CTAs, and internal links
- **Legal pages**: Privacy, Terms, Cookie Policy, Refund Policy all have full legal text in first-response HTML
- **Verified via curl**: Every route returns unique titles, meta descriptions, H1s, and body content
- Build runs on `yarn start` (CI=false craco build && node prerender.js && node serve.js)

### Homepage & Marketing (March 2026)
- Hero: "Find products that can actually sell in the UK." + 3 value points
- Trust strip, Who it's for, UK Differentiation, How it works, Features, Proof section, Pricing preview, Final CTA
- Cookie consent banner (Accept all / Reject non-essential)
- GA4/GTM consent-gated

### SEO Infrastructure (March 2026)
- Sitemap: 60+ URLs
- Robots.txt: clean, correct
- Noscript fallback: UK-first positioning
- html lang="en-GB"
- JSON-LD: Organization, SoftwareApplication, WebSite, BreadcrumbList, FAQPage, AboutPage, ContactPage

### Core Platform
- Product discovery dashboard, UK Viability Score (7-signal)
- AI product analysis, Stripe subscriptions, admin tools
- WebSocket notifications, OAuth 2.0 flows

## Remaining Tasks
- P1: Set REACT_APP_GA4_ID in production .env
- P1: Configure Resend webhook URL
- P2: OAuth data sync from connected stores
- P3: Token refresh logic

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
