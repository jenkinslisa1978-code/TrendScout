# TrendScout - Product Requirements Document

## Overview
TrendScout is a comprehensive e-commerce intelligence SaaS platform providing data-driven insights for product discovery and validation.

## Core Requirements
- **Product Intelligence Dashboard:** Daily Winners, watchlist, alerts, market radar, Live Opportunity Feed
- **Data Pipeline:** Multi-source ingestion, deduplication, proprietary "Launch Score" calculation
- **Reporting:** Automated weekly/monthly market intelligence reports with PDF export
- **Monetization:** Stripe integration for 4-tier subscription (Free, Starter £19, Pro £39, Elite £99 in GBP)
- **User Management:** Supabase auth, onboarding flow, notification system (in-app & email via Resend)
- **Admin System:** Admin role bypasses billing, grants Elite access
- **Growth & Marketing:** Public trending pages, referral system, shareable product cards

## User Personas
- **Dropshippers:** Need product discovery and validation tools
- **E-commerce Entrepreneurs:** Need market intelligence and trend detection
- **Admin (jenkinslisa1978@gmail.com):** Full access for testing and management

## Architecture
- **Frontend:** React, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI, MongoDB, APScheduler
- **Auth:** Supabase (JWT-based)
- **Payments:** Stripe (Live keys configured)
- **Email:** Resend (verified domain trendscout.click)
- **Deployment:** Custom domain trendscout.click (SSL pending)

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
- 4-tier Stripe subscription: Free, Starter (£19), Pro (£39), Elite (£99)
- Checkout, webhooks, customer portal
- Feature gating by plan
- Admin bypass for jenkinslisa1978@gmail.com

### User Management (Complete)
- Supabase authentication
- Multi-step onboarding
- Notification system (in-app + email via Resend)
- User preferences

### Growth & Marketing (Complete - Feb 2026)
- Public Trending Products Page (/trending-products) with SEO meta tags
- Homepage Landing Page (/) with hero, features, pricing
- Public Product Pages (/p/{id}) with SEO-friendly detail pages
- Shareable Product Cards with social media sharing (Twitter, Facebook, WhatsApp, Copy Link)
- Referral System with code generation, tracking, and bonus store slots (up to 5)
- Referral dashboard page (/referrals)
- Signup referral tracking (/signup?ref=CODE)
- Product of the Week email digest with personalized referral viral loop
- Product of the Week highlight section on landing page
- All email templates rebranded from ViralScout to TrendScout

## Known Issues
- **P0:** SSL certificate error on www.trendscout.click (BLOCKED - external)
- **P1:** Production deployment is outdated (missing Starter plan + admin system)
- **P2:** Supabase rate limiting (429 errors intermittent)
- **P3:** CJ Dropshipping scraper blocked
- **P3:** Gateway timeout on full scrape

## Backlog
- P1: Re-deploy after SSL fix
- P3: Product Outcome Learning System
- P3: Full architecture refactor (services-oriented)
