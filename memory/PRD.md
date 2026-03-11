# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a comprehensive e-commerce intelligence SaaS platform that enables:
Product Discovery → Validation → Store Creation → Ad Creation → Launch — all in one seamless workflow.

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI
- Backend: FastAPI, MongoDB, APScheduler
- Auth: Custom JWT | Payments: Stripe (live test keys) | Email: Resend
- Scraping: curl_cffi | Google Trends: pytrends
- LLM: Emergent LLM Key (OpenAI GPT-4.1-mini) via emergentintegrations

## Completed Phases

### Phase 1: Real Data Infrastructure (DONE)
- Amazon UK Movers & Shakers scraper (curl_cffi, 12+ categories)
- Google Trends integration (pytrends, keyword velocity)
- Scheduler: scraping every 4h, Google Trends every 6h, score recompute every 4h

### Phase 2: Market Intelligence Engine (DONE)
- launch_score formula with transparent reasoning per component
- Score Breakdown card + data transparency badges

### Phase 3: Supplier Integration (DONE)
- AliExpress + CJ Dropshipping auto-discovery
- One-click supplier selection, external verification links

### Phase 4: One-Click Store Launch (DONE)
- POST /api/stores/launch creates complete store
- Export: Shopify JSON/CSV, WooCommerce JSON

### Phase 5: AI Ad Creative Generation (DONE)
- TikTok scripts, Facebook copy, Instagram captions, video storyboards
- Provider: Emergent LLM Key → OpenAI GPT-4.1-mini

### Phase 6: Opportunity Feed (DONE)
- Real-time dashboard feed with 30-second auto-refresh
- Event types: new_strong_launch, trend_spike, competition_drop, etc.

### Phase 7: Referral & Viral Growth System (DONE - March 2026)
- Unique referral codes, tracking, reward bonus store slots
- Social sharing: Twitter, Facebook, WhatsApp
- Signup integration: /signup?ref=CODE

### Phase 8: Automated Reports (DONE - March 2026)
- Weekly Winning Products + Monthly Market Trends
- PDF export, email delivery, report archive

### Phase 9: Ad Discovery (DONE - March 2026)
- Multi-platform scanning: TikTok, Meta, Google Shopping
- Cached results (12h TTL), activity scoring
- Frontend: AdDiscoverySection on ProductDetailPage

### Phase 10: Shopify Direct Publish (DONE - March 2026)
- OAuth flow, direct publish endpoint, export-only fallback

### Phase 11: Stripe Subscription Tiers & Feature Gating (DONE - March 2026)
**Plans:**
- Free (£0/mo): Limited insights, report previews, 1 store, limited watchlist/alerts, no PDF export
- Pro (£39/mo): Full insights, full reports + PDF export, 5 stores, full watchlist/alerts
- Elite (£99/mo): Everything in Pro + early trends, advanced opportunities, automated reports, priority alerts, unlimited stores, direct Shopify publish

**Stripe Billing:**
- Real Stripe checkout sessions (Pro & Elite)
- Customer portal for billing management
- Webhook handling: checkout.session.completed, subscription.updated/deleted, invoice events
- Cancellation/downgrade at period end

**Server-Side Gating:**
- PDF export: requires Pro plan (403 for free)
- Early trend opportunities: requires Elite (403 for free/pro)
- Store creation: enforces limits (1/5/unlimited)
- Direct Shopify publish: requires Elite

**Frontend Gating:**
- Pricing page: 3-tier cards with GBP pricing, feature comparison table
- Reports page: Lock icons on PDF buttons, upgrade prompts for free users
- Product detail: LockedContent blur on Score Breakdown + Market Intelligence for free users
- Dashboard: EarlyTrendUpgradePrompt replaces section for non-Elite users
- Premium badges, blurred locked sections, "Upgrade to unlock" prompts

## Key API Endpoints
- Stripe: /api/stripe/plans, /create-checkout-session, /create-portal-session, /webhook, /cancel-subscription, /feature-access, /subscription
- Products: /api/products, /api/products/{id}
- Stores: /api/stores/launch, /api/stores/{id}/export
- Reports: /api/reports/, /api/reports/weekly-winning-products, /api/reports/*/pdf
- Ad Discovery: /api/ad-discovery/discover/{id}, /api/ad-discovery/{id}
- Referrals: /api/viral/referral/stats, /api/viral/referral/track
- Shopify: /api/shopify/status, /api/shopify/connect/init, /api/shopify/publish/{store_id}

## Remaining/Backlog
- P1: server.py refactoring into modular route files (7000+ lines)
- P2: CJ Dropshipping & Zendrop direct API supplier integration
- P2: TikTok Creative Center / Meta Ad Library API integration
- P3: Image/video quality improvements (deduplication, scoring)
- P3: Additional data sources as anti-bot solutions become available
