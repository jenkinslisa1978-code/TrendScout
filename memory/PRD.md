# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. Scans TikTok, Amazon, and ecommerce stores with AI to identify products ready to scale. One-stop shop: "tell you what to sell, set up the shop and produce adverts all in a couple of clicks".

## Pricing Model (LIVE)
| Plan | Price |
|------|-------|
| Free | £0/mo |
| Starter | £19/mo |
| Pro | £39/mo |
| Elite | £79/mo |

## Key Features

### Data Trust & Transparency (March 13, 2026) - COMPLETED
- **Scoring Methodology endpoint** (`GET /api/scoring/methodology`) — public, no auth, returns 7 signals, 6 data sources, formula, confidence levels, and honest limitations
- **"How Our Scores Work"** collapsible section on Product Detail page — explains each of the 7 scoring signals with high/low meanings, data sources, and limitations
- **Data Trust Banner** on Dashboard — expandable banner showing data sources (Amazon, Google Trends, TikTok, AliExpress, Meta Ad Library, CJ Dropshipping)
- **Platform Automation Badges** — Shows "Full Automation" (Shopify/WooCommerce/Meta/TikTok), "Manual Import" (Etsy/BigCommerce/Squarespace), "Draft Only" (Google Ads)
- **Honest Limitations** — Transparent about estimation vs real data, no guarantees on profitability

### Onboarding Walkthrough (March 13, 2026) - COMPLETED
- 4-step modal for first-time users explaining platform value
- Steps: Welcome, Connect Store, Connect Ads, Quick Launch
- Persists completion state in localStorage
- Accessible (DialogTitle for screen readers)
- Uses static Tailwind COLOR_MAP (indigo/emerald/purple gradients)

### Platform Connections (March 13, 2026) - COMPLETED
**E-Commerce Stores (Real API calls):**
- Shopify — Real Shopify Admin REST API — **Full Automation**
- WooCommerce — Real WooCommerce REST API — **Full Automation**
- Etsy — Credential storage — **Manual Import**
- BigCommerce — Credential storage — **Manual Import**
- Squarespace — Credential storage — **Manual Import**

**Advertising Platforms (Real API calls):**
- Meta (Facebook + Instagram) — Real Marketing API — **Auto-Post Ads** (PAUSED)
- TikTok Ads — Real Marketing API — **Auto-Post Ads** (PAUSED)
- Google Ads — **Draft Only** (user completes in Google Ads Manager)

### Quick Launch Flow - COMPLETED
- "Launch a Product in 3 Clicks" widget at top of dashboard
- Step 1: AI recommends top product with profit breakdown
- Step 2: One-click shop creation (auto-publishes if store connected)
- Step 3: Make ads OR skip — user's choice

### Premium Ad Creative Generation - COMPLETED
- Uses OpenAI GPT-4.1-mini via Emergent LLM Key
- Generates: product angles, headlines, TikTok scripts, Facebook ads, Instagram captions, video storyboard, shot list, voiceover script, email sequence, budget recommendations

### Beginner-Friendly UX - COMPLETED
- Score tooltips, plain English descriptions
- Currency in £ throughout
- Data freshness indicator on dashboard
- No generic supplier links

## Architecture
- Backend: FastAPI + MongoDB (32 route files)
- Frontend: React + Shadcn/UI
- Integrations: OpenAI GPT-4.1-mini, Stripe, Resend, CJ Dropshipping, Shopify API, WooCommerce API, Meta Marketing API, TikTok Marketing API

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P1: Real Etsy/BigCommerce/Squarespace API integrations
- P1: API rate limiting per subscription tier
- P2: Redis cache migration
- P3: Real-time WebSocket notifications
- P3: Ad generation multi-step refactoring
