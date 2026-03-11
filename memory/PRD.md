# TrendScout - Product Requirements Document

## Overview
TrendScout is a comprehensive e-commerce intelligence SaaS platform providing data-driven insights for product discovery and validation.

## Core Requirements
- **Product Intelligence Dashboard:** Daily Winners, watchlist, alerts, market radar, Live Opportunity Feed
- **Data Pipeline:** Multi-source ingestion, deduplication, proprietary "Launch Score" calculation
- **Reporting:** Automated weekly/monthly market intelligence reports with PDF export
- **Monetization:** Stripe integration for 4-tier subscription (Free, Starter, Pro, Elite in GBP)
- **User Management:** Custom JWT auth, onboarding flow, notification system (in-app & email via Resend)
- **Admin System:** Admin role bypasses billing, grants Elite access
- **Growth & Marketing:** Public trending pages, referral system, shareable product cards

## Architecture
- **Frontend:** React, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI, MongoDB, APScheduler
- **Auth:** Custom JWT-based authentication (bcrypt + python-jose). Supabase REMOVED.
- **Payments:** Stripe (Live keys configured)
- **Email:** Resend (verified domain trendscout.click)

## Auth Credentials (Test)
- Admin: jenkinslisa1978@gmail.com / admin123456
- Regular: testuser@test.com / test123456

## Implemented Features

### Core (Complete)
- Product intelligence dashboard with Daily Winners
- Watchlist and saved products
- Trend alerts (Elite feature)
- Market radar and opportunity feed
- Store builder with Shopify export
- Data scraping pipeline (multiple sources)
- Launch Score calculation
- Weekly/Monthly reports with PDF export

### Monetization (Complete)
- 4-tier Stripe subscription: Free, Starter, Pro, Elite
- Checkout, webhooks, customer portal
- Feature gating by plan
- Admin bypass for jenkinslisa1978@gmail.com

### Auth System (Complete - Mar 2026)
- Custom JWT auth replaces Supabase entirely
- /api/auth/register, /api/auth/login, /api/auth/profile endpoints
- Fixed load_dotenv order bug (JWT_SECRET was None)
- Removed ALL Supabase imports from frontend
- Upgraded JWT secret to 64-char hex
- Error Boundary added to prevent blank pages from crashes

### Blank Page Bug Fix (Complete - Mar 2026)
- Root cause: formatNumber() and formatCurrency() crashed on undefined values
- Fixed null/undefined guards in both utility functions
- Added global React ErrorBoundary component
- Verified all major pages work: Dashboard, Discover, Reports, Saved Products

### Growth & Marketing (Complete)
- Public Trending Products Page, Referral System
- Product of the Week email digest
- Newsletter capture form

## Known Issues
- **P0:** SSL certificate error on www.trendscout.click (BLOCKED - external)
- **P1:** Re-deployment needed to push all fixes to production
- **P3:** CJ Dropshipping scraper blocked
- **P3:** Gateway timeout on full scrape

## Backlog
- P1: Re-deploy to production (all fixes ready in codebase)
- P3: Product Outcome Learning System (feedback loop)
- P3: Full architecture refactor (break down server.py into services)
- P3: Forgot Password flow with email reset via Resend
