# TrendScout PRD

## Product Vision
UK Product Validation Tool for ecommerce sellers. Scores products across demand, competition, margins, and UK-specific factors so sellers launch smarter.

## Architecture
- **Backend**: FastAPI + Motor (Async MongoDB) + APScheduler. Serves APIs and static React SPA.
- **Frontend**: React + TailwindCSS + Shadcn UI. Dark theme with emerald accents.
- **Deployment**: Single-service monolith on Render (render.yaml). FastAPI serves /api routes + static files.
- **Integrations**: CJ Dropshipping (live API), OpenAI GPT-5.2 (Emergent LLM Key), Resend (email), Stripe (payments).

## Core Features

### Free Public Tools (No Auth)
- **Product Validator**: POST /api/public/validate-product — instant scoring via CJ search + scoring engine
- **Profit Simulator**: POST /api/public/profit-simulator — unit economics + 30/60/90 day projections with UK VAT
- **Trending Products**: GET /api/public/trending-products — browse scored products

### Premium Features (Auth Required)
- **One-Click Launch**: POST /api/products/{id}/quick-launch — AI ad copy (GPT-5.2), target audience, profit projections, platform exports (Shopify/WooCommerce/Etsy)
- **AI Deep Analysis**: POST /api/products/deep-analysis — GPT-5.2 powered product intelligence
- **CJ Dropshipping Sync**: Auto-imports products every 6h, manual trigger POST /api/cj/sync
- **Product Alerts**: Email notifications via Resend for trending products matching criteria
- **Launch Wizard**: Multi-step product launch flow
- **Competitor Intelligence**: Ad spend, pricing, saturation data

### UI/UX
- Premium dark theme (bg #09090b) with emerald-500 accents
- Glassmorphic header, dark footer
- Product validator embedded in hero section
- Bento grid features layout
- Interactive slider-based profit simulator

## Key Files
- /app/backend/server.py — Main FastAPI app, serves SPA
- /app/backend/routes/public.py — Public endpoints (validator, simulator)
- /app/backend/routes/products.py — Product CRUD + quick-launch
- /app/backend/routes/cj_dropshipping.py — CJ API integration
- /app/backend/services/cj_dropshipping.py — CJ service layer
- /app/backend/services/jobs/tasks.py — Scheduled tasks (CJ sync, scoring)
- /app/backend/common/scoring.py — Launch score calculation
- /app/frontend/src/pages/LandingPage.jsx — Dark premium landing page
- /app/frontend/src/components/ProductValidator.jsx — Hero search component
- /app/frontend/src/pages/ProfitSimulatorPage.jsx — Interactive profit simulator
- /app/frontend/src/pages/QuickLaunchPage.jsx — One-click launch results
- /app/frontend/src/components/layouts/LandingLayout.jsx — Dark layout wrapper

## DB Schema
- products: {id, cj_pid, product_name, category, launch_score, supplier_cost, ...}
- auth_users: {id, email, password_hash}
- trend_alerts: {id, user_id, categories, min_score, active}
- automation_logs: {id, job_name, status, run_time, details}
- quick_launches: {id, product_id, user_id, created_at, status}

## Credentials
- Admin: reviewer@trendscout.click / ShopifyReview2026!
- Demo: demo@trendscout.click / DemoReview2026!
- Automation API Key: vs_automation_key_2024

## What's Implemented
- CJ Dropshipping API integration (auth, search, import, sync) — March 30, 2026
- Free Public Product Validator with CJ live data — March 30, 2026
- AI Profit Simulator with 30/60/90 day projections + UK VAT — March 30, 2026
- One-Click Launch with AI ad copy + Shopify/WooCommerce/Etsy exports — March 30, 2026
- Premium dark-mode UI/UX redesign — March 30, 2026
- Product Alert Emails via Resend — March 29, 2026
- Lazy-loading DB + LLM for fast startup — March 29, 2026
- Render single-service deployment config — March 29, 2026

## Remaining Tasks
- P1: Configure GA4 tag in GTM (user task)
- P1: Configure Resend webhook URL (user task)
- P1: Create OAuth apps for Shopify/Meta/TikTok
- P2: Stripe payment configuration for live subscriptions
- P2: Cleanup obsolete frontend/serve.js and frontend/start.js
