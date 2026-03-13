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

### Platform Connections (NEW - March 13, 2026)
- **E-Commerce Stores**: Shopify, WooCommerce, Etsy, BigCommerce, Squarespace
- **Ad Platforms**: Meta (Facebook + Instagram), TikTok Ads, Google Ads
- Users connect their accounts via API keys/tokens
- Quick Launch auto-publishes to connected store and auto-posts ads
- Settings → Connections page with connect/disconnect modals
- **Note**: Auto-publish and auto-post are currently MOCKED (record intent in DB, don't call external APIs yet)

### Quick Launch Flow (March 13, 2026)
- "Launch a Product in 3 Clicks" widget at top of dashboard
- Step 1: AI recommends top product with profit breakdown
- Step 2: One-click shop creation (auto-publishes if Shopify/WooCommerce connected)
- Step 3: One-click ad generation (auto-posts if Meta/TikTok/Google connected)

### Beginner-Friendly UX (March 13, 2026)
- Score tooltips, plain English descriptions
- Trend alerts with friendly labels (Top Pick / Recommended / Worth a Look)
- Currency in £ throughout

### Full 30-Part Spec (ALL COMPLETED)

## Architecture
- Backend: FastAPI + MongoDB (31 route files)
- Frontend: React + Shadcn/UI
- Integrations: OpenAI GPT-5.2, Stripe, Resend, CJ Dropshipping

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P0: Implement real Shopify/WooCommerce API calls for auto-publish
- P0: Implement real Meta/TikTok/Google API calls for auto-post
- P1: API rate limiting per subscription tier
- P2: Redis cache migration
- P3: Real-time WebSocket notifications
