# TrendScout - Product Requirements Document

## Product Vision
AI operating system for e-commerce product discovery. TrendScout scans TikTok, Amazon, and ecommerce stores with AI to identify products ready to scale before competitors find them.

## Pricing Model (LIVE)
| Plan | Price | Stripe Price ID Env |
|------|-------|---------------------|
| Free | £0/mo | N/A |
| Starter | £19/mo | STRIPE_STARTER_PRICE_ID |
| Pro | £39/mo | STRIPE_PRO_PRICE_ID |
| Elite | £79/mo | STRIPE_ELITE_PRICE_ID |

## Completed Features (30-Part Spec) - ALL DONE

## Production Launch (COMPLETED - March 2026)
- Pricing aligned: Starter £19, Pro £39, Elite £79
- Stripe Live Mode, Resend configured with trendscout.click
- Rate limiting, legal pages, favicon, SEO meta tags

## UX Fixes (March 13, 2026) - ALL VERIFIED
- Currency: Supplier prices now show £ instead of $
- Score tooltips: Info icons on Launch Score, Trend Score, Margin, Competitors with plain English explanations
- Score breakdown: Added beginner-friendly descriptions ("Is this product getting more popular?", etc.)
- Removed generic "View Supplier" button from product header
- Supplier section: "Search on AliExpress/CJ" (honest about it being a search)
- Trend alerts: Updated to match validation engine (no more "EXPLODING" contradicting "High Risk")
- Validation engine: Fixed field name lookups (view_growth_rate, supplier_order_velocity), adjusted confidence
- Product images: Fixed wrong images (car→pump, chalk→tablet), cleared test placeholders

## 3rd Party Integrations
- OpenAI GPT-5.2, MongoDB, Stripe (live), Resend, CJ Dropshipping API
- Amazon, TikTok, Google Trends (scrapers)

## Test Credentials
- Admin: jenkinslisa1978@gmail.com / admin123456 (auto elite plan)

## Backlog
- P0: Further beginner-friendly UX improvements (guided flow: "what to sell → set up shop → make ads")
- P1: API rate limiting per subscription tier
- P2: Redis cache migration
- P3: Real-time WebSocket notifications
