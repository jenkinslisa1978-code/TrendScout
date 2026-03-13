# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. TrendScout scans TikTok, Amazon, and ecommerce stores with AI to identify products ready to scale before competitors find them.

## Architecture

### Backend (FastAPI + MongoDB)
```
/app/backend/
├── server.py              # Slim 178-line entrypoint (middleware, startup/shutdown, router includes)
├── auth.py                # JWT auth middleware
├── common/
│   ├── database.py        # MongoDB client & db instance
│   ├── models.py          # All Pydantic request/response models
│   ├── scoring.py         # Product scoring/calculation functions
│   ├── cache.py           # In-memory cache utilities
│   └── helpers.py         # Auth helpers, product tracking, automation helpers
├── routes/
│   ├── health.py          # GET /api/, /api/health
│   ├── auth_routes.py     # POST /api/auth/register, /login, GET /profile
│   ├── user.py            # Onboarding, admin, daily usage
│   ├── stripe_routes.py   # Checkout, portal, webhook, plans, feature-access
│   ├── products.py        # Products CRUD, launch score, proven winners, saturation
│   ├── automation.py      # Automation pipeline run, logs, stats
│   ├── jobs.py            # Job queue status, history, trigger, cancel
│   ├── viral.py           # Referral system, public product views, sharing
│   ├── public.py          # Daily picks, top-trending, platform-stats, SEO pages
│   ├── seo.py             # Sitemap.xml, robots.txt
│   ├── data_quality.py    # Data integrity, source health, confidence
│   ├── intelligence.py    # Product validation, trend analysis, success prediction
│   ├── dashboard.py       # Daily winners, opportunity feed, watchlist, radar, summary
│   ├── reports.py         # Weekly/monthly reports, PDF downloads
│   ├── email.py           # Email subscriptions, digest, newsletter
│   ├── notifications.py   # In-app notifications, radar scan, threshold subscriptions
│   ├── ingestion.py       # TikTok/Amazon/Supplier imports, scraping, dedup
│   ├── stores.py          # Store CRUD, generation, export, launch
│   ├── shopify.py         # Shopify OAuth, publish, disconnect
│   ├── suppliers.py       # Supplier endpoints
│   ├── ads.py             # Ad creatives, discovery, outcomes, A/B testing, engine
│   ├── radar.py           # Live market radar events
│   ├── optimizer.py       # Budget optimizer settings, recommendations
│   ├── system_health.py   # System health, data integration
│   ├── tools.py           # Shopify analyzer, competitor store tracker
│   ├── workspace.py       # Saved products workspace
│   ├── blog.py            # AI-generated blog posts
│   ├── admin.py           # Image review, analytics dashboard
│   └── images.py          # Image enrichment
└── services/              # Business logic services
```

### Frontend (React)
```
/app/frontend/src/
├── pages/                 # Page components
├── components/            # Reusable UI components
│   ├── ui/               # Shadcn components
│   └── specific/         # App-specific components
├── services/             # API service layer
└── App.jsx               # Router configuration
```

## Completed Features (30-Part Spec)

| # | Feature | Status |
|---|---------|--------|
| 1 | Product Vision | Done |
| 2 | Landing Page CRO | Done |
| 3 | Pricing Page (3-tier) | Done |
| 4 | Signup Flow | Done |
| 5 | Onboarding Checklist | Done |
| 6 | Advanced Discovery Filters | Done |
| 7 | AI Trend Score Engine | Done |
| 8 | Trend Timeline Charts | Done |
| 9 | Product Saturation Meter | Done |
| 10 | Profit Calculator | Done |
| 11 | AI Launch Simulator | Done |
| 12 | AI Ad Creative Generator | Done |
| 13 | TikTok Intelligence | Done |
| 14 | Competitor Store Scanner | Done |
| 15 | Saved Product Workspace | Done |
| 16 | Weekly Trend Report | Done |
| 17 | Viral Product Alerts | Done |
| 18 | SEO Growth Engine | Done |
| 19 | Top Trending Page | Done |
| 20 | Image Resolution Pipeline | Done |
| 21 | Image Candidate Sources | Done |
| 22 | Image Validation | Done |
| 23 | Admin Image Review | Done |
| 24 | Image Review Detail | Done |
| 25 | Bulk Image Review | Done |
| 26 | Image QA Metrics | Done |
| 27 | Performance (GZip) | Done |
| 28 | Analytics Pipeline | Done |
| 29 | UX Philosophy | Adhered |
| 30 | Success Metrics | Defined |

## Launch Readiness (COMPLETED - March 2026)
- Favicon, apple-touch-icon, OG meta tags for SEO
- Rate limiting (slowapi): 200/min global, 5/min register, 10/min login
- 404 catch-all page with navigation
- Terms of Service page (/terms)
- Privacy Policy page (/privacy)
- Site footer with legal links
- Production cleanup (removed backup files)

## Backend Modularization (COMPLETED - March 2026)
- Refactored 10,754-line monolithic server.py into 30 route files + 6 common modules
- server.py reduced to 178-line slim entrypoint
- 41/41 regression tests passed
- No breaking changes to any API endpoint

## Key DB Collections
- products, profiles, auth_users, stores, store_products
- subscriptions, trend_alerts, automation_logs
- reports, workspaces, blog_posts
- analytics_events, notifications, ad_tests
- optimization_events, optimizer_alerts

## 3rd Party Integrations
- OpenAI GPT-5.2 (via emergentintegrations)
- MongoDB (primary DB)
- Stripe (subscriptions)
- Resend (emails)
- CJ Dropshipping API (live)
- Amazon, TikTok, Google Trends (scrapers)

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456 (auto elite plan)
- Test user: test_refactor@test.com / test123456

## Upcoming Tasks
1. Redis cache migration (replace in-memory cache with distributed cache)

## Backlog
- API rate limiting per plan tier
- Real-time WebSocket notifications
- A/B test analytics dashboard improvements
