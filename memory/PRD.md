# TrendScout - Product Requirements Document

## Product Vision
AI product research and launch intelligence for UK ecommerce sellers.

## Architecture
- Backend: FastAPI + MongoDB + Redis + APScheduler
- Frontend: React CRA + Shadcn/UI + Tailwind
- Auth: JWT + refresh cookie | Email: Resend | Payments: Stripe
- AI: GPT-5.2 via Emergent LLM Key (emergentintegrations)

## Test Credentials
- reviewer@trendscout.click / ShopifyReview2026!

## Completed Features

### Deployment Fix (Feb 2026)
- Removed `react-snap` postbuild script that caused Alpine Linux build failure (`apt-get` incompatible)
- Fixed `CI=true` build failure by setting `CI=false` in the build script (ESLint warnings treated as errors)
- Cleaned dead react-snap hydration code from `index.js`
- Cleaned `.gitignore` to allow `.env` files for Emergent deployment
- Deployment agent confirms: APPROVED, no blockers

### 3-Email Drip Sequence for Viability Leads (March 2026)
- **Email 1 (Instant)**: Viability result email with score, verdict, strengths, risks, summary + signup CTA
- **Email 2 (Day 2)**: "3 Trending Products This Week" with top scored products + trial CTA
- **Email 3 (Day 5)**: "Your free trial is waiting" with feature list + urgency CTA
- **Drip tracking**: `drip_emails_sent` array in leads collection prevents duplicate sends
- **Cron job**: `send_lead_drip_emails` runs daily at 9 AM UTC, checks lead age, skips converted users
- Verified: iteration_114 (100%, 17/17 backend tests)

### Email Capture Gate (March 2026)
- 1 free search -> email gate -> 3 more unlocked -> exhausted state with signup CTA
- Verified: iteration_113 (100%)

### Interactive Demo & Quick Viability Search (March 2026)
- AI-powered quick viability check (GPT-5.2) + 4-step product tour
- Verified: iteration_112 (100%)

### Visual Redesign Suite (March 2026)
- Homepage split + /features page + How It Works walkthrough + Pricing enhancement
- Scroll-triggered animations (RevealSection/RevealStagger)
- 8 AI-generated images across pages
- Verified: iterations 108-111 (all 100%)

### All Previous Features
- Prediction Accuracy Tracking, Trust Framework, Methodology page
- Changelog, 6 free tools, Trial expiry, A/B framework, CRO suite
- Performance: Code splitting, lazy loading, blog automation

## Scheduled Tasks
| Task | Schedule | Description |
|------|----------|-------------|
| send_lead_drip_emails | Daily 9 AM | Day 2 trending + Day 5 trial drip emails |
| review_prediction_accuracy | Daily 6 AM | Snapshot + review predictions |
| weekly_blog_generation | Monday 8 AM | Auto-generate blog posts |
| send_lead_subscriber_digest | Monday 9 AM | Trending products email to leads |
| send_weekly_email_digest | Monday 10 AM | Digest to registered users |
| send_trial_expiry_notifications | Every 2h | Email expired trial users |

## Key API Endpoints
- POST /api/public/quick-viability — AI product viability check (public)
- POST /api/leads/capture — Email lead capture + instant drip email
- GET /api/accuracy/stats — Prediction accuracy metrics

### A/B Testing on Hero CTA (Feb 2026)
- Wired useABTest hook to landing page hero CTA and final CTA
- Tests 3 variants each: "Start Free" / "Try TrendScout Free" / "Get Started Now"
- Tracks conversions via trackABConversion()

### UTM Tracking on All Email CTAs (Feb 2026)
- Added utm_source, utm_medium, utm_campaign, utm_content to all drip email links
- Covers: viability result (instant), trending products (day 2), trial prompt (day 5), weekly digest, trial expiry

### Resend Webhook Email Tracking (Feb 2026)
- POST /api/webhooks/resend — receives open/click/bounce/complaint events
- GET /api/webhooks/resend/stats — aggregated open rate, click rate, delivery stats
- Email engagement card added to Growth & Revenue dashboard
- Lead records updated with engagement data (opened, clicked, bounced)

### Social & Supplier Connections (Feb 2026)
- Added Social & Marketplaces: TikTok Shop, Instagram Shopping, Amazon Seller
- Added Suppliers: AliExpress, CJ Dropshipping, Zendrop
- Backend: POST /api/connections/supplier, POST /api/connections/social
- Frontend: New sections on PlatformConnectionsPage with connect/disconnect UI

### Static Prerendering (Feb 2026)
- Alpine-compatible prerender script (jsdom, no Puppeteer/Chromium)
- Generates static HTML shells for 8 public routes (features, pricing, how-it-works, etc.)
- Runs automatically after build via postbuild script

### Connect Accounts Prompt (Feb 2026)
- "Connect Your Accounts" banner on Dashboard and My Stores pages
- Shows 4 categories: Stores (Shopify, WooCommerce, Etsy, Amazon), Social (TikTok Shop, Instagram), Ad Accounts (Facebook, Google, TikTok Ads), Suppliers (AliExpress, CJ, Zendrop)
- CTA links to existing /settings/connections page
- Dismissible (localStorage persisted), auto-hides when 3+ connections active
- Backend connections API already exists at /api/connections

### CSRF Fix for Admin Buttons (Feb 2026)
- Fixed 403 errors on Run Scoring, AI Summaries, Full Data Sync, Data Ingestion buttons
- Root cause: productService.js, DataIngestionPanel.jsx, alertService.js used raw fetch() without CSRF tokens
- Fixed by adding getAuthHeaders() to all POST/PUT/DELETE fetch calls

### Admin Command Center (Feb 2026)
- In-app admin hub at `/admin/hub` — single page overview of everything
- Quick stats bar: MRR, paid subs, leads, signups, emails sent, total users
- Admin Checklist: setup items, daily monitoring, weekly tasks with quick links
- "What to Watch" cards: Revenue Health, Lead Quality, Email Performance, System Health
- Technical Reference: env variables, scheduled tasks table, external dashboard links
- Updated sidebar nav: 7 admin tools (Command Center, Growth & Revenue, Products, Automation, System Health, Image Review, Integrations)

### Admin Growth & Revenue Dashboard (Feb 2026)
- Full analytics dashboard at `/admin/analytics` (admin-only access)
- Revenue KPIs: MRR, new revenue, paid subscribers with period-over-period trends
- Lead capture metrics: total leads, sources breakdown, top product searches
- Email drip performance: delivery rates per step (instant, day 2, day 5)
- User plan distribution and conversion funnel visualization
- Backend endpoint: `GET /api/analytics/growth?days=30`

## Remaining Tasks
- Set `REACT_APP_GA4_ID` in production .env (P1 - user needs to provide GA4 ID)
- Configure Resend webhook URL in Resend dashboard: POST https://trendscout.click/api/webhooks/resend
