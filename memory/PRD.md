# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. Scans TikTok, Amazon, and ecommerce stores with AI to identify products ready to scale.

## Pricing Model (LIVE)
| Plan | Price |
|------|-------|
| Free | £0/mo |
| Starter | £19/mo |
| Pro | £39/mo |
| Elite | £79/mo |

## Key Features

### Platform Connections (March 13, 2026)
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

### Quick Launch Flow
- "Launch a Product in 3 Clicks" widget at top of dashboard
- Step 1: AI recommends top product with profit breakdown
- Step 2: One-click shop creation (auto-publishes if store connected)
- Step 3: Make ads OR skip — user's choice
- Auto-integration: publishes to Shopify/WooCommerce and posts to Meta/TikTok when connected

### Beginner-Friendly UX
- Score tooltips, plain English descriptions
- Trend alerts with friendly labels
- Currency in £ throughout

### Full 30-Part Spec (ALL COMPLETED)

## Architecture
- Backend: FastAPI + MongoDB (32 route files)
- Frontend: React + Shadcn/UI
- Integrations: OpenAI GPT-5.2, Stripe, Resend, CJ Dropshipping, Shopify API, WooCommerce API, Meta Marketing API, TikTok Marketing API

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P1: Real Etsy/BigCommerce/Squarespace API integrations
- P1: API rate limiting per subscription tier
- P2: Redis cache migration
- P3: Real-time WebSocket notifications
