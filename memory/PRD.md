# TrendScout - Product Requirements Document

## Overview
TrendScout is a comprehensive e-commerce intelligence SaaS platform providing data-driven insights for product discovery and validation.

## Architecture
- **Frontend:** React, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI, MongoDB, APScheduler
- **Auth:** Custom JWT-based authentication (bcrypt + python-jose)
- **Payments:** Stripe (Live keys configured)
- **Email:** Resend (verified domain trendscout.click)

## Auth Credentials (Test)
- Admin: jenkinslisa1978@gmail.com / admin123456
- Regular: testuser@test.com / test123456

## Implemented Features

### Core (Complete)
- Product intelligence dashboard with Daily Winners
- Discover page with product images, filters, sorting
- Watchlist, saved products, trend alerts
- Store builder with Shopify export
- Data scraping pipeline, Launch Score calculation
- Weekly/Monthly reports with PDF export

### Product Images (Complete - Mar 2026)
- Added `image_url` field to all 79 products in MongoDB
- Stock photos from Unsplash mapped by category
- Updated DiscoverPage, SavedProductsPage, ProductDetailPage to display images
- Graceful fallback to Package icon when image fails to load
- TrendingProductsPage and PublicProductPage already supported image_url

### Auth System (Complete - Mar 2026)
- Custom JWT auth replaces Supabase
- /api/auth/register, /api/auth/login, /api/auth/profile endpoints
- Error Boundary prevents blank pages from crashes

### Blank Page Bug Fix (Complete - Mar 2026)
- Fixed formatNumber()/formatCurrency() crashing on undefined values

### Monetization (Complete)
- 4-tier Stripe subscription: Free, Starter, Pro, Elite
- Feature gating by plan, admin bypass

### Growth & Marketing (Complete)
- Public Trending Products Page, Referral System
- Product of the Week email digest, Newsletter capture

## Known Issues
- **P0:** SSL certificate error on www.trendscout.click (external)
- **P1:** Re-deployment needed to push fixes to production
- **P3:** CJ Dropshipping scraper blocked
- **P3:** Gateway timeout on full scrape

## Backlog
- P1: Re-deploy to production
- P3: Product Outcome Learning System
- P3: Architecture refactor (break down server.py)
- P3: Forgot Password flow via Resend
