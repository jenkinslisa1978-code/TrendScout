# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. TrendScout scans TikTok, Amazon, and ecommerce stores with AI to identify products ready to scale before competitors find them.

## Pricing Model (LIVE)
| Plan | Price |
|------|-------|
| Free | £0/mo |
| Starter | £19/mo |
| Pro | £39/mo |
| Elite | £79/mo |

## Key Features

### Quick Launch Flow (NEW - March 13, 2026)
- "Launch a Product in 3 Clicks" widget at top of dashboard
- Step 1: AI recommends top product with clear profit breakdown
- Step 2: One-click shop creation
- Step 3: One-click ad generation
- Completion: "View My Shop" to customise and publish

### Beginner-Friendly UX (March 13, 2026)
- Score tooltips explain what Launch Score, Trend Score, Margin, Competitors mean
- Score breakdown has plain English descriptions ("How much profit can you make per sale?")
- Trend alerts use friendly labels (Top Pick / Recommended / Worth a Look)
- Removed broken generic supplier external links
- Currency is £ throughout (not $)
- Fixed wrong product images in database

### Product Intelligence
- AI-powered validation engine (Launch Opportunity / Promising / High Risk)
- Trend Timeline with interactive charts
- Saturation Meter visualization
- Pre-filled Profit Calculator
- Success probability scoring

### Full 30-Part Spec (ALL COMPLETED)
- Product discovery with advanced filters
- Subscription billing (Stripe live)
- Email notifications (Resend)
- Competitor tracking, TikTok intelligence
- Store builder, ad creative generator
- SEO engine, referral system

## Architecture
- Backend: FastAPI + MongoDB (30+ modular route files)
- Frontend: React + Shadcn/UI
- Integrations: OpenAI GPT-5.2, Stripe, Resend, CJ Dropshipping

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456 (auto elite plan)

## Backlog
- P1: API rate limiting per subscription tier
- P2: Redis cache migration
- P3: Real-time WebSocket notifications
