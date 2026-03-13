# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. Scans TikTok, Amazon, and ecommerce stores with AI to identify products ready to scale. One-stop shop that fulfills: "tell you what to sell, set up the shop and produce adverts all in a couple of clicks".

## Pricing Model (LIVE)
| Plan | Price |
|------|-------|
| Free | £0/mo |
| Starter | £19/mo |
| Pro | £39/mo |
| Elite | £79/mo |

## Key Features

### Onboarding Walkthrough (March 13, 2026) - COMPLETED
- 4-step modal for first-time users explaining platform value
- Steps: Welcome, Connect Store, Connect Ads, Quick Launch
- Persists completion state in localStorage
- Accessible (DialogTitle for screen readers)
- Uses static Tailwind COLOR_MAP (indigo/emerald/purple gradients)

### Platform Connections (March 13, 2026) - COMPLETED
**E-Commerce Stores (Real API calls):**
- Shopify — Real Shopify Admin REST API (create product, set price, add images, publish)
- WooCommerce — Real WooCommerce REST API (create product, publish)
- Etsy — Credential storage, manual import guidance
- BigCommerce — Credential storage, manual import guidance
- Squarespace — Credential storage, manual import guidance

**Advertising Platforms (Real API calls):**
- Meta (Facebook + Instagram) — Real Marketing API (create campaign, ad set, creative, PAUSED)
- TikTok Ads — Real Marketing API (create campaign, PAUSED)
- Google Ads — Draft preparation with ad copy (complex OAuth, user completes in Google Ads)

**User Choice:**
- "Make Ads" button generates AI ads and auto-posts to connected platforms
- "Skip, I'll do my own" option lets users skip ad generation entirely

### Quick Launch Flow - COMPLETED
- "Launch a Product in 3 Clicks" widget at top of dashboard
- Step 1: AI recommends top product with profit breakdown
- Step 2: One-click shop creation (auto-publishes if store connected)
- Step 3: Make ads OR skip — user's choice
- Auto-integration: publishes to Shopify/WooCommerce and posts to Meta/TikTok when connected

### Premium Ad Creative Generation - COMPLETED
- Uses OpenAI GPT-4.1-mini via Emergent LLM Key
- Generates: product angles, headlines, TikTok scripts, Facebook ads, Instagram captions, video storyboard, shot list, voiceover script, email sequence, budget recommendations
- Competition-focused, AIDA/PAS frameworks

### Beginner-Friendly UX - COMPLETED
- Score tooltips, plain English descriptions
- Trend alerts with friendly labels
- Currency in £ throughout
- No generic "Search on AliExpress" links on supplier cards
- Data freshness indicator on dashboard

### Supplier Section - COMPLETED
- Internal supplier listings with Select Supplier buttons
- No external generic search links (per user feedback)
- Support for AliExpress and CJ Dropshipping suppliers

### Full 30-Part Spec (ALL COMPLETED)

## Architecture
- Backend: FastAPI + MongoDB (32 route files)
- Frontend: React + Shadcn/UI
- Integrations: OpenAI GPT-4.1-mini, Stripe, Resend, CJ Dropshipping, Shopify API, WooCommerce API, Meta Marketing API, TikTok Marketing API

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P1: Full E2E test of Platform Integrations with real user credentials
- P1: Real Etsy/BigCommerce/Squarespace API integrations
- P1: API rate limiting per subscription tier
- P2: Redis cache migration
- P3: Real-time WebSocket notifications
- P3: Ad generation multi-step refactoring for better quality control
