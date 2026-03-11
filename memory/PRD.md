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

## User Personas
- **Dropshippers:** Need product discovery and validation tools
- **E-commerce Entrepreneurs:** Need market intelligence and trend detection
- **Admin (jenkinslisa1978@gmail.com):** Full access for testing and management

## Architecture
- **Frontend:** React, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI, MongoDB, APScheduler
- **Auth:** Custom JWT-based authentication (bcrypt + python-jose). Supabase REMOVED.
- **Payments:** Stripe (Live keys configured)
- **Email:** Resend (verified domain trendscout.click)
- **Deployment:** Custom domain trendscout.click (SSL pending)

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

### User Management (Complete)
- Custom JWT authentication (replaced Supabase)
- Multi-step onboarding
- Notification system (in-app + email via Resend)
- User preferences

### Growth & Marketing (Complete - Feb 2026)
- Public Trending Products Page (/trending-products) with SEO meta tags
- Homepage Landing Page (/) with hero, features, pricing
- Public Product Pages (/p/{id}) with SEO-friendly detail pages
- Shareable Product Cards with social media sharing
- Referral System with code generation, tracking, and bonus store slots
- Product of the Week email digest with personalized referral viral loop
- Newsletter email capture on landing page

### Auth Migration (Complete - Mar 2026)
- Replaced Supabase auth with custom JWT auth system
- Added /api/auth/register, /api/auth/login, /api/auth/profile endpoints
- Fixed load_dotenv order (was causing JWT_SECRET=None)
- Removed Supabase imports from AuthContext, savedProductService, subscriptionService
- Upgraded JWT secret to 64-char hex for proper security
- All auth tests passing (15/15 backend, full frontend flow)

## Known Issues
- **P0:** SSL certificate error on www.trendscout.click (BLOCKED - external)
- **P1:** Re-deployment needed to push all fixes to production
- **P3:** CJ Dropshipping scraper blocked
- **P3:** Gateway timeout on full scrape

## Backlog
- P1: Re-deploy after SSL fix to production
- P3: Product Outcome Learning System (feedback loop)
- P3: Full architecture refactor (break down server.py into services)
- P3: Clean up remaining Supabase references in comments/code
