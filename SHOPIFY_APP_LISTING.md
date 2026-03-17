# TrendScout — Shopify App Store Listing

## App Name
TrendScout — AI Product Intelligence

## Tagline
Find winning products, validate before you launch, push directly to your store.

## Short Description (80 chars)
AI-powered product scoring and competitor intelligence for dropshippers.

## Detailed Description
TrendScout is the decision engine built for dropshippers. Stop guessing which products to sell — let AI analyse trends, competition, ad activity, and profit margins to give you a clear launch score for every product.

**What TrendScout does:**
- Scores products using a 7-Signal Launch Score (trend momentum, profit margin, competition density, ad saturation, supplier demand, search growth, and social buzz)
- Searches real supplier inventory on CJ Dropshipping with live pricing and stock levels
- Analyses competitor stores — revenue estimates, pricing strategy, and supplier risk
- Monitors ads across TikTok, Meta, and Pinterest to find proven winners
- Calculates profitability with a built-in simulator — know your unit economics before you spend on ads
- Sends real-time radar alerts when products cross your scoring thresholds

**Shopify integration:**
- 1-click product import: push any product directly to your Shopify store as a draft with title, description, images, pricing, and tags
- Embedded dashboard: view trending products and push to store without leaving Shopify Admin
- Export history: track every product you've pushed to your store

**Who is it for:**
- Dropshippers looking for data-driven product decisions
- Shopify store owners who want to validate products before launching
- Ecommerce entrepreneurs scaling from 1 to 10+ stores

## Key Features (for App Store listing)
1. 7-Signal Launch Score — AI product scoring
2. CJ Dropshipping Sourcing — live supplier data
3. 1-Click Product Import to Shopify
4. Ad Intelligence — TikTok, Meta, Pinterest
5. Competitor Store Analysis
6. Profitability Simulator
7. Real-time Radar Alerts
8. Embedded Shopify Dashboard

## Categories
- Finding products
- Dropshipping

## Pricing
- Free plan: 5 product analyses per day
- Starter: $29/month
- Pro: $79/month
- Elite: $149/month

## API Scopes Required
- `read_products` — to check existing catalogue before importing
- `write_products` — to push product drafts to the store
- `read_inventory` — to display inventory levels
- `write_inventory` — to set inventory for imported products

## GDPR Compliance Endpoints
- Customer data request: `POST /api/shopify/app/webhooks/customers/data_request`
- Customer data erasure: `POST /api/shopify/app/webhooks/customers/redact`
- Shop data erasure: `POST /api/shopify/app/webhooks/shop/redact`
- All webhooks verified via HMAC-SHA256

## Webhook API Version
2026-01

## URLs
- App URL: https://trendscout.click/shopify-app
- Privacy Policy: https://trendscout.click/privacy
- Terms of Service: https://trendscout.click/terms
- Support: info@trendscout.click
- Help Centre: https://trendscout.click/help

## Test Account for Reviewers
- Email: reviewer@trendscout.click
- Password: (to be created before submission)
- Pre-connected test store with sample data

## App Icon
- 1200x1200 PNG required
- TrendScout logo on indigo (#4F46E5) background

## Screenshots Required (1600x900 or 800x600)
1. Dashboard — showing trending products with launch scores
2. Product Detail — 7-Signal Score Breakdown
3. CJ Sourcing — search results with real supplier data
4. Ad Intelligence — ad spy across platforms
5. Push to Shopify — 1-click import flow
6. Embedded Dashboard — inside Shopify Admin

## Submission Checklist
- [x] App manifest (shopify.app.toml) with scopes, webhooks, auth config
- [x] GDPR compliance endpoints (3 mandatory webhooks)
- [x] App lifecycle webhooks (app/uninstalled)
- [x] HMAC-SHA256 webhook verification
- [x] Embedded app with App Bridge
- [x] Session token authentication for embedded mode
- [x] Privacy policy with Shopify-specific sections
- [x] Terms of service with Shopify integration terms
- [x] Public app info page (/shopify-app)
- [x] Installation guide (4-step flow)
- [x] API documentation (10 endpoints)
- [x] Encrypted token storage (Fernet)
- [x] Support email configured (info@trendscout.click)
- [ ] App icon (1200x1200) — generate before submission
- [ ] Screenshots (6 required) — capture before submission
- [ ] Test reviewer account — create before submission
- [ ] Final QA on production domain
