# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. Scans TikTok, Amazon, and ecommerce stores with AI to identify products ready to scale. One-stop shop: "tell you what to sell, set up the shop and produce adverts all in a couple of clicks".

## Pricing Model (LIVE)
| Plan | Price | API Rate Limit |
|------|-------|----------------|
| Free | £0/mo | 30 req/min |
| Starter | £19/mo | 120 req/min |
| Pro | £39/mo | 300 req/min |
| Elite | £79/mo | 600 req/min |

## ALL Features — COMPLETED

### Redis Cache (March 13, 2026)
- Redis-backed caching with automatic in-memory fallback
- Rate limiting uses Redis atomic INCR for distributed support
- API response caching migrated from in-memory to Redis
- `redis_cache.py`: cache_get, cache_set, cache_delete, cache_incr, cache_get_ttl

### Real-Time SSE Notifications (March 13, 2026)
- Server-Sent Events endpoint: `GET /api/notifications/stream`
- Accepts auth via query param (for EventSource) or Authorization header
- Pushes new notifications, unread counts in real-time
- Frontend NotificationCenter connects via SSE with polling fallback
- In-memory event queue (production: Redis pub/sub)

### Multi-Step Ad Generation Pipeline (March 13, 2026)
- 7-step pipeline for higher quality ad creatives:
  1. Product angles & target audiences
  2. Headlines & hooks
  3. TikTok scripts
  4. Facebook ads (story-driven, AIDA/PAS)
  5. Instagram captions
  6. Video storyboard + shot list + voiceover
  7. Email sequence + budget advice
- Endpoint: `POST /api/ad-creatives/generate-pipeline/{product_id}`
- Partial success support (returns what was generated before failure)

### Connection Health Check (March 13, 2026)
- `POST /api/connections/health-check` pings all connected platforms
- Tests Shopify, WooCommerce, Etsy, BigCommerce, Squarespace, Meta, TikTok
- Updates health_status in DB for each connection
- Frontend: Health Check button on Connections page with results grid

### Profitability Calculator (March 13, 2026)
- `POST /api/profitability-calculator` — ROI estimation
- Inputs: daily_ad_budget, conversion_rate, avg_cpc, days
- Returns: projections (revenue, profit, ROI%), break_even analysis, verdict
- Verdict: green (ROI>100%), amber (0-100%), red (negative)
- Frontend widget on Product Detail page with 4 input fields

### Data Trust & Transparency
- Scoring Methodology endpoint with 7 signals, 6 data sources, honest limitations
- "How Our Scores Work" section on Product Detail pages
- Data Trust Banner on Dashboard

### Platform Connections — ALL 5 STORES + 3 AD PLATFORMS
- Shopify, WooCommerce, Etsy, BigCommerce, Squarespace — Full Automation
- Meta, TikTok — Auto-Post Ads (PAUSED)
- Google Ads — Draft Only
- Platform automation badges on Connections page

### Onboarding Walkthrough
- 4-step modal for first-time users

### Quick Launch Flow
- "Launch a Product in 3 Clicks" dashboard widget

### Premium Ad Creative Generation
- Single-shot: OpenAI GPT-4.1-mini via Emergent LLM Key
- Pipeline: 7-step multi-LLM pipeline

### API Rate Limiting
- Per-user, per-plan via Redis with in-memory fallback
- X-RateLimit headers on all authenticated responses

## Architecture
- Backend: FastAPI + MongoDB + Redis (32 route files)
- Frontend: React + Shadcn/UI
- Integrations: OpenAI, Stripe, Resend, CJ Dropshipping, Shopify, WooCommerce, Etsy, BigCommerce, Squarespace, Meta, TikTok, Google Ads

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456

## Backlog
- P3: Real-time WebSocket notifications (replace SSE with WebSocket for bidirectional comms)
- P3: Redis pub/sub for multi-instance SSE event distribution
