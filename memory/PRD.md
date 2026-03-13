# TrendScout - Product Requirements Document

## Positioning
**TrendScout — The AI Operating System for Discovering & Launching Winning Ecommerce Products**

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI, react-helmet-async
- Backend: FastAPI, MongoDB, APScheduler, aiohttp, Pillow
- Auth: Custom JWT | Payments: Stripe (GBP, live) | Email: Resend
- LLM: GPT 5.2 via emergentintegrations (Emergent LLM Key)

## Feature Inventory (All Implemented)

### Core Intelligence
- **AI Trend Score (0-100)**: Dead/Weak/Emerging/Strong/Viral categories, displayed on all cards
- **AI Launch Simulator (GPT 5.2)**: 3-phase strategy, target audience, revenue projections, risk assessment
- **AI Ad Creative Generator (GPT 5.2)**: 3 TikTok ad concepts (Unboxing/Problem-Solution/Curiosity) with scenes, hooks, music
- **Trend Timeline Chart**: SVG 7-day trend visualization with score/TikTok/Google metrics
- **Product Saturation Meter**: Competition level, stores detected, ad saturation

### Discovery & Feed
- **Daily Picks**: 5 curated daily products, deterministic rotation
- **Viral Leaderboard**: /top-trending-products — Top 50 products ranked by score, SEO optimized
- **Trending Products**: Advanced filters (category, margin, sort), confidence badges
- **TikTok Intelligence Dashboard**: Viral products, category performance, ad patterns

### Tools
- **Shopify Store Analyzer**: /tools/shopify-analyzer — paste any URL for instant analysis
- **Competitor Store Tracker**: Track stores, refresh scans, product change detection
- **Product Profit Calculator**: Break-even CPA, margin, daily profit
- **Saved Products Workspace**: /saved — save, note, track

### Viral Growth Engine
- **Public SEO pages**: /trending/{slug} with full OG tags, Twitter cards, JSON-LD structured data
- **Creator Share Feature**: Twitter/X, Facebook, LinkedIn, Reddit, WhatsApp + copy link
- **Viral Leaderboard**: Top 50 daily-updated public page targeting SEO keywords
- **AI SEO Blog**: /blog — Auto-generated weekly articles by product category using GPT-5.2, /blog/:slug with structured data

### Monetisation
- **Freemium Gating**: Supplier & Ad sections locked for free users, UpgradeModal
- **Daily Insight Limits**: Free=2/day, Starter=5, Pro=unlimited
- **Competitor Tracking Limits**: Free=2, Starter=5, Pro=15, Elite=unlimited
- **Threshold Alert Subscriptions**: User-defined score alerts with email/in-app delivery

### Scheduled Tasks (19 total)
- weekly_competitor_scan (Monday 6AM)
- weekly_blog_generation (Monday 8AM) — generates blog posts for top 8 product categories
- scan_threshold_subscriptions (every 6h)
- generate_alerts (hourly)
- Plus 15 data ingestion/enrichment tasks

### Image System
- Fixed 61 broken Amazon placeholder images with curated Unsplash URLs by category
- Image enrichment pipeline: Amazon + DuckDuckGo, Pillow optimization
- Local CDN at /api/images/

## API Endpoints Summary
| Endpoint | Auth | Description |
|----------|------|-------------|
| GET /api/public/top-trending | No | 50 products ranked by score |
| GET /api/public/daily-picks | No | 5 curated daily products |
| GET /api/public/trending-products | No | Paginated trending products |
| GET /api/tools/tiktok-intelligence | No | TikTok viral data |
| POST /api/tools/analyze-store | No | Shopify store analysis |
| GET /api/blog/posts | No | List published blog posts |
| GET /api/blog/posts/{slug} | No | Single blog post with full content |
| POST /api/blog/generate/{category} | Admin | Generate AI blog post for category |
| POST /api/blog/generate-all | Admin | Generate for top 8 categories |
| GET /api/ad-tests/ad-creatives/{id} | Yes | 3 AI ad concepts |
| GET /api/ad-tests/ai-simulate/{id} | Yes | AI launch simulation |
| GET/POST/DELETE /api/competitor-stores | Yes | Competitor tracking |
| GET/PUT /api/notifications/threshold-subscription | Yes | Alert settings |

## Upcoming Tasks
- Saved Product Workspace (Part 9) — /workspace page for saving products, notes, launch tracking
- Weekly Trend Report email (Monday digest via Resend)
- Chrome Extension — "TrendScout – Product & Store Analyzer" (deferred)
- Backend modularization — extract routes from server.py

## Future / Backlog
- CDN migration (Cloudflare R2/S3) for image storage
- Redis cache for multi-instance scaling
- Community growth features
- Advanced competitor diff tracking (product-level changes)

## DB Collections
products, daily_usage, threshold_subscriptions, competitor_stores,
notifications, profiles, subscriptions, stores, product_outcomes, blog_posts

## Testing Status
- iteration_48: Phase C features — 100% (14/14)
- iteration_49: Trend alerts + conversion — 100% (17/17)
- iteration_50: Shopify analyzer + competitor tracker — 100% (15/15)
- iteration_51: AI simulator + TikTok intel — 100% (23/23)
- iteration_52: Growth upgrade (leaderboard, ad generator, images, SEO) — 100% (15/15 + all frontend)
- iteration_53: AI SEO Blog System — 100% (12/12 backend + all frontend verified)
