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
│   ├── stores.py          # Store CRUD, generation, export, launch
│   ├── suppliers.py       # Supplier endpoints
│   ├── ads.py             # Ad creatives, discovery, outcomes, A/B testing, engine
│   └── ...                # 20+ more route files
└── services/              # Business logic services
```

## Pricing Model (LIVE)
| Plan | Price | Stripe Price ID Env |
|------|-------|---------------------|
| Free | £0/mo | N/A |
| Starter | £19/mo | STRIPE_STARTER_PRICE_ID |
| Pro | £39/mo | STRIPE_PRO_PRICE_ID |
| Elite | £79/mo | STRIPE_ELITE_PRICE_ID |

## Completed Features (30-Part Spec) - ALL DONE

## Production Launch (COMPLETED - March 2026)
- Pricing aligned: Starter £19, Pro £39, Elite £79 (frontend + backend)
- Stripe Live Mode configured with real Price IDs
- Resend email configured with trendscout.click domain
- Favicon, apple-touch-icon, OG meta tags for SEO
- Rate limiting (slowapi): 200/min global, 5/min register, 10/min login
- 404 catch-all page, Terms of Service, Privacy Policy
- Site footer with legal links
- No hardcoded secrets in frontend code

## Bug Fixes (March 13, 2026)
- LaunchPad: Fixed supplier endpoint mismatch (frontend called wrong URL)
- LaunchPad: Fixed missing imports in stores.py (StoreGenerator, etc.)
- LaunchPad: All 5 steps now work end-to-end

## Key DB Collections
- products, profiles, auth_users, stores, store_products
- subscriptions, trend_alerts, automation_logs, ad_creatives
- reports, workspaces, blog_posts, product_suppliers

## 3rd Party Integrations
- OpenAI GPT-5.2 (via emergentintegrations)
- MongoDB (primary DB)
- Stripe (live subscriptions)
- Resend (production emails via trendscout.click)
- CJ Dropshipping API (live)
- Amazon, TikTok, Google Trends (scrapers)

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456 (auto elite plan)
- Test user: test_refactor@test.com / test123456

## Backlog
- P1: API rate limiting per subscription tier
- P2: Redis cache migration (replace in-memory cache)
- P3: Real-time WebSocket notifications
