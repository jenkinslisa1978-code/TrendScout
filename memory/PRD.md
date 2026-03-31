# TrendScout PRD

## Product Vision
UK Product Validation Tool for ecommerce sellers. Scores products across demand, competition, margins, and UK-specific factors so sellers launch smarter.

## Architecture
- **Backend**: FastAPI + Motor (Async MongoDB) + APScheduler. Serves APIs and static React SPA.
- **Frontend**: React + TailwindCSS + Shadcn UI. Dark theme with emerald accents.
- **Deployment**: Single-service monolith on Render (render.yaml). FastAPI serves /api routes + static files.
- **Integrations**: CJ Dropshipping (live API), Avasam UK (live API), OpenAI GPT-5.2 (Emergent LLM Key), Resend (email), Stripe (payments).

## Core Features

### Free Public Tools (No Auth)
- **Product Validator**: POST /api/public/validate-product
- **Profit Simulator**: POST /api/public/profit-simulator
- **Trending Products**: GET /api/public/trending-products

### Premium Features (Auth Required)
- **One-Click Launch**: POST /api/products/{id}/quick-launch
- **AI Deep Analysis**: POST /api/products/deep-analysis
- **CJ Dropshipping Sync**: Auto-imports every 6h, POST /api/cj/sync
- **Avasam UK Sync**: Auto-imports UK products every 6h, POST /api/avasam/sync
- **Supplier Comparison**: GET /api/cj/supplier-comparison (CJ, AliExpress, Zendrop, Avasam UK)
- **UK Suppliers Only Filter**: Toggle on trending products page
- **Competitor Intelligence**: Ad spend, pricing, saturation data

### Scoring
- **UK Supplier Bonus**: +15 points added to launch_score for uk_supplier=true products
- **is_uk_supplier()**: Returns true if avasam_pid, data_source=avasam, or any supplier has country=GB/UK

### UI/UX
- Premium dark theme (bg #09090b) with emerald-500 accents
- UK Shipping Time Indicator badges on all product cards (green/yellow/red)
- "UK SUPPLIER" badge on all product cards when uk_supplier=true
- "UK Suppliers Only" filter toggle on trending products page

## Key Files
- /app/backend/server.py — Main FastAPI app
- /app/backend/routes/public.py — Public endpoints
- /app/backend/routes/products.py — Product CRUD + quick-launch
- /app/backend/routes/cj_dropshipping.py — CJ API + supplier comparison
- /app/backend/routes/avasam.py — Avasam UK supplier routes
- /app/backend/services/cj_dropshipping.py — CJ service layer
- /app/backend/services/avasam.py — Avasam UK service layer
- /app/backend/services/jobs/tasks.py — Scheduled tasks
- /app/backend/common/scoring.py — Scoring (launch_score, uk_shipping_tier, is_uk_supplier)
- /app/frontend/src/pages/LandingPage.jsx — Landing page (ProductCard + ShippingBadge + UK Supplier badge)
- /app/frontend/src/pages/TrendingProductsPage.jsx — Trending page (UK filter toggle + badges)
- /app/frontend/src/pages/ProductDetailPage.jsx — Product detail (all badges)
- /app/frontend/src/components/ShareableProductCard.jsx — Shareable card (all badges)

## DB Schema
- products: {id, cj_pid, avasam_pid, product_name, category, launch_score, supplier_cost, suppliers, data_source, ...}
- auth_users: {id, email, password_hash}
- trend_alerts: {id, user_id, categories, min_score, active}
- automation_logs: {id, job_name, status, run_time, details}

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
- Automation API Key: vs_automation_key_2024

## What's Implemented
- UK Supplier badge + filter toggle + launch_score +15 boost — March 31, 2026
- Avasam UK Supplier Integration (service, routes, sync task, supplier comparison) — March 31, 2026
- UK Shipping Time Indicator (3-tier badges on all product cards) — March 31, 2026
- Weekly email digest, TikTok Viral Predictor, Competitor Store Spy — March 30, 2026
- CJ Dropshipping API integration, Product Validator, Profit Simulator — March 30, 2026
- One-Click Launch, Premium dark-mode UI/UX redesign — March 30, 2026
- Product Alert Emails, Lazy-loading, Render deployment — March 29, 2026

## Avasam Integration
- **Auth**: POST https://app.avasam.com/api/auth/request-token
- **Env**: AVASAM_CONSUMER_KEY, AVASAM_CONSUMER_SECRET (in Render)
- **Endpoints**: /api/avasam/search, /product/{id}, /categories, /stock/{id}, /import/{id}, /sync, /sync/history
- **Shipping**: Green "UK Warehouse" tier (1-3 days)
- **Scoring**: +15 launch_score bonus

## Remaining Tasks
- P1: Configure GA4 tag in GTM (user task)
- P1: Configure Resend webhook URL (user task)
- P1: Create OAuth apps for Shopify/Meta/TikTok
- P2: Stripe payment configuration for live subscriptions
