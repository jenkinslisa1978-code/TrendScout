# TrendScout - Product Requirements Document

## Original Problem Statement
Build "TrendScout", a comprehensive e-commerce intelligence SaaS platform that helps entrepreneurs find winning products, generate stores with AI, and export to Shopify.

## Core Requirements
- Real-time product trend data from multiple e-commerce sources
- AI-powered product scoring (trend score, launch score, market opportunity)
- Store builder with Shopify export
- Supplier link generation (AliExpress search URLs)
- Subscription plans with Stripe payments
- Email notifications via Resend

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI
- Backend: FastAPI, MongoDB
- Auth: Custom JWT
- Payments: Stripe
- Email: Resend
- Scraping: curl_cffi (browser TLS fingerprint impersonation)
- Scheduling: APScheduler

## What's Been Implemented

### Authentication (DONE)
- Custom JWT auth (replaced Supabase)
- Login, Register, Profile endpoints
- Admin role via email whitelist

### Data Scraping Pipeline (DONE - Mar 2026)
- Amazon UK Movers & Shakers scraper using curl_cffi
- Scrapes 12+ categories: Home & Kitchen, Electronics, Beauty, Health, Sports, Garden, Pet Supplies, Toys, Fashion, Baby, DIY, Automotive
- Extracts: product name, price, BSR change %, rating, reviews, images
- Auto-generates AliExpress supplier search URLs
- Computes trend_score, trend_stage, opportunity_rating
- Scheduler runs every 4 hours (scrape_real_data task)
- 137+ products in database with real data

### UI/Frontend (DONE)
- Landing page, Dashboard, Discover, Product Detail pages
- AI-generated product images for original 79 products
- Data freshness indicator on Dashboard ("Live data · Last updated...")
- Error Boundary to prevent blank pages
- Product cards with images, prices, scores
- View Supplier button links to AliExpress

### Other Features (DONE)
- Store Builder with Shopify export
- Pricing page with Stripe integration
- Admin panel for product management
- Product deduplication system
- Market scoring and launch score computation
- Weekly/Monthly report generation

## Known Limitations
- AliExpress direct scraping blocked by CAPTCHA (supplier links are generated search URLs)
- TikTok Creative Center scraping blocked
- CJ Dropshipping scraping blocked (human verification)
- Only Amazon UK is scraped as live data source

## Backlog
- P3: Product Outcome Learning System
- P3: Full architecture refactor (break down server.py)
- P3: Forgot Password flow via Resend
- P3: Gateway timeout optimization for large batch scrapes
- P3: Add more scraping sources (when anti-bot solutions available)
