# TrendScout — Owner's Operations Manual

> Your reference guide for running, maintaining, and troubleshooting TrendScout.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [How Each Feature Works](#2-how-each-feature-works)
3. [Environment Variables](#3-environment-variables)
4. [Database](#4-database)
5. [Common Issues & Fixes](#5-common-issues--fixes)
6. [API Keys & Third-Party Services](#6-api-keys--third-party-services)
7. [Shopify App](#7-shopify-app)
8. [Deployment & Updates](#8-deployment--updates)
9. [Monitoring & Logs](#9-monitoring--logs)
10. [User Management](#10-user-management)
11. [Data Management](#11-data-management)
12. [Quick Reference](#12-quick-reference)

---

## 1. Architecture Overview

```
Frontend (React)  -->  Kubernetes Ingress  -->  Backend (FastAPI)  -->  MongoDB
     :3000               /api -> :8001              :8001              :27017
```

- **Frontend:** React app at port 3000. Uses Shadcn/UI components, React Router, and Tailwind CSS.
- **Backend:** FastAPI (Python) at port 8001. All API routes start with `/api/`.
- **Database:** MongoDB. Connection via `MONGO_URL` in `backend/.env`.
- **Process manager:** Supervisor manages both frontend and backend processes.
- **Hot reload:** Both frontend and backend auto-restart when code changes. Only restart supervisor manually for `.env` changes or new dependency installs.

### Key Directories

| Path | What's there |
|------|-------------|
| `/app/frontend/src/pages/` | All page components (one per route) |
| `/app/frontend/src/components/` | Reusable UI components |
| `/app/backend/routes/` | API route files (one per feature area) |
| `/app/backend/services/` | Business logic and external API clients |
| `/app/backend/common/` | Shared utilities (cache, scoring, helpers) |
| `/app/memory/PRD.md` | Product requirements and changelog |
| `/app/SHOPIFY_APP_LISTING.md` | Shopify App Store submission details |

---

## 2. How Each Feature Works

### Product Discovery & Launch Scores
- **What it does:** Every product gets a 7-Signal Launch Score (0-100) based on trend momentum, profit margin, competition density, ad saturation, supplier demand, search growth, and social buzz.
- **Where the scoring lives:** `/app/backend/common/scoring.py` -> `calculate_launch_score()`
- **How scores update:** Scores recalculate when product data changes. The algorithm heavily penalises ad competition to give realistic "launch opportunity" ratings.
- **Frontend:** `/discover` page shows all products sorted by score. `/product/:id` shows the full breakdown.

### CJ Dropshipping (Live Supplier Data)
- **What it does:** Searches CJ Dropshipping's real inventory — live prices, stock levels, variants.
- **API key:** `CJ_DROPSHIPPING_API_KEY` in `backend/.env`
- **Rate limit:** 1 authentication request per 5 minutes. Token is cached in `/tmp/cj_api_token.json` and lasts 14 days.
- **Frontend:** `/cj-sourcing` page with "CJ Search" and "Compare Suppliers" tabs.
- **Import flow:** User clicks "Import" -> backend fetches full product details from CJ -> creates a product in MongoDB -> calculates launch score -> redirects to product detail page.

### Ad Intelligence
- **What it does:** Shows ads running across TikTok, Meta, and Pinterest with spend estimates and engagement data.
- **Where:** `/ad-spy` page. Backend: `/app/backend/routes/ads.py`
- **Meta Ad Library:** Uses `META_AD_LIBRARY_TOKEN` for live Meta ad data.

### TikTok Intelligence
- **What it does:** Ranks products by TikTok views and shows category performance.
- **Where:** `/tiktok-intelligence` page. Backend: `/app/backend/routes/tools.py` -> `get_tiktok_intelligence()`
- **Data:** `tiktok_views` field on each product in MongoDB. Currently populated for all 151 products.
- **Cache:** Results cached for 5 minutes (in-memory). Backend restart clears cache.

### Profitability Simulator
- **What it does:** Users input product cost, selling price, ad spend, and shipping to see profit projections.
- **Where:** `/profitability-simulator` page. Calculations happen on the frontend — no backend needed.

### Competitor Intelligence
- **What it does:** Tracks competitor stores — estimated revenue, pricing strategy, supplier risk.
- **Where:** `/competitor-intel` page. Backend: `/app/backend/routes/intelligence.py`

### Radar Alerts
- **What it does:** Users set thresholds and get notified when products cross them.
- **Where:** `/radar-alerts` page. Backend: `/app/backend/routes/radar.py`
- **Notifications:** Delivered via WebSocket at `/ws/notifications`. Backend: `/app/backend/routes/notifications.py`

### Verified Winners
- **What it does:** Community-submitted proof of successful products.
- **Where:** `/verified-winners` page. Backend: `/app/backend/routes/winners.py`

### Shopify Integration
- **What it does:** Push products to Shopify stores as drafts. Embedded dashboard inside Shopify Admin.
- **Where:** `/stores` (connect store), `/settings/connections` (manage). Backend: `/app/backend/routes/shopify.py`, `/app/backend/routes/shopify_app.py`
- **Credentials:** `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET` in `backend/.env`

### Stripe Billing
- **What it does:** Subscription management with 3 paid tiers (Starter $29, Pro $79, Elite $149).
- **Where:** `/pricing` page, `/settings` for subscription management.
- **Credentials:** `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and price IDs in `backend/.env`
- **Webhook:** Stripe sends events to `/api/stripe/webhook`. This handles subscription changes, payment confirmations, and cancellations.

### Email (Resend)
- **What it does:** Transactional emails (welcome, password reset, alerts).
- **Credentials:** `RESEND_API_KEY` and `SENDER_EMAIL` in `backend/.env`
- **Sender domain:** `noreply@trendscout.click`

---

## 3. Environment Variables

All config lives in `/app/backend/.env`. Never hardcode values.

| Variable | What it does | Where to get a new one |
|----------|-------------|----------------------|
| `MONGO_URL` | MongoDB connection string | Pre-configured, don't change |
| `DB_NAME` | Database name | Pre-configured |
| `STRIPE_SECRET_KEY` | Stripe payments | https://dashboard.stripe.com/apikeys |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook verification | Stripe Dashboard -> Webhooks |
| `STRIPE_STARTER_PRICE_ID` | Starter plan price | Stripe Dashboard -> Products |
| `STRIPE_PRO_PRICE_ID` | Pro plan price | Stripe Dashboard -> Products |
| `STRIPE_ELITE_PRICE_ID` | Elite plan price | Stripe Dashboard -> Products |
| `RESEND_API_KEY` | Email sending | https://resend.com/api-keys |
| `SENDER_EMAIL` | From address for emails | Must match verified Resend domain |
| `CJ_DROPSHIPPING_API_KEY` | CJ supplier data | https://developers.cjdropshipping.com |
| `META_AD_LIBRARY_TOKEN` | Meta ad data | https://developers.facebook.com |
| `SHOPIFY_CLIENT_ID` | Shopify App | https://partners.shopify.com |
| `SHOPIFY_CLIENT_SECRET` | Shopify App | https://partners.shopify.com |
| `EMERGENT_LLM_KEY` | AI features (GPT) | Emergent platform (Profile -> Universal Key) |
| `SENTRY_DSN` | Error monitoring | https://sentry.io |
| `SITE_URL` | Your production domain | Set to your live URL |
| `SUPABASE_JWT_SECRET` | JWT token signing | Generated, don't change |

**After changing any `.env` value:** Restart the backend:
```bash
sudo supervisorctl restart backend
```

---

## 4. Database

**MongoDB** stores everything. Database name: `test_database` (configured via `DB_NAME`).

### Key Collections

| Collection | What's in it |
|-----------|-------------|
| `products` | All 151+ products with scores, images, TikTok views, supplier data |
| `users` | User accounts (email, hashed password, subscription tier) |
| `notifications` | Alert history per user |
| `stores` | Connected Shopify stores |
| `radar_alerts` | User-configured alert rules |
| `winners` | Verified winner submissions |
| `cache` | Cached API responses |
| `ad_creatives` | Generated ad copy and variants |
| `competitors` | Tracked competitor stores |

### Useful Database Commands

Connect to MongoDB:
```bash
mongosh "mongodb://localhost:27017/test_database"
```

Count products:
```javascript
db.products.countDocuments()
```

Find a product by name:
```javascript
db.products.findOne({product_name: /pillow/i}, {_id:0, product_name:1, launch_score:1, tiktok_views:1})
```

List all users:
```javascript
db.users.find({}, {_id:0, email:1, full_name:1, subscription_tier:1}).sort({created_at:-1})
```

Update a product's TikTok views:
```javascript
db.products.updateOne({id: "PRODUCT_ID"}, {$set: {tiktok_views: 5000000}})
```

---

## 5. Common Issues & Fixes

### "Page shows blank / 'No data available'"
- **Cause:** Backend may have restarted and cleared the in-memory cache.
- **Fix:** Refresh the page. Data loads from MongoDB on first request after cache expires.

### "CJ Dropshipping search returns error"
- **Cause:** CJ API rate limit (1 auth request per 5 minutes).
- **Fix:** Wait 5 minutes and try again. The token is cached in `/tmp/cj_api_token.json` for 14 days, so this only happens after a server restart or token expiry.
- **Check token:** `cat /tmp/cj_api_token.json`

### "Backend won't start"
- **Check logs:** `tail -n 50 /var/log/supervisor/backend.err.log`
- **Common causes:**
  - Missing Python dependency: `pip install <package> && pip freeze > /app/backend/requirements.txt`
  - Syntax error in a route file: check the error log for the file and line number
  - `.env` issue: verify no comments or trailing spaces in `/app/backend/.env`
- **Restart:** `sudo supervisorctl restart backend`

### "Frontend won't load"
- **Check logs:** `tail -n 50 /var/log/supervisor/frontend.err.log`
- **Common causes:**
  - Missing npm package: `cd /app/frontend && yarn add <package>`
  - Import error in a component: check the browser console (F12)
- **Restart:** `sudo supervisorctl restart frontend`

### "Stripe payments not working"
- **Check:** Is `STRIPE_SECRET_KEY` correct in `backend/.env`?
- **Webhooks:** Stripe events go to `YOUR_DOMAIN/api/stripe/webhook`. Make sure the webhook URL is configured in Stripe Dashboard -> Webhooks.
- **Test mode vs live:** The current key starts with `sk_live_` — it's a live key. For testing, replace with a `sk_test_` key from Stripe Dashboard.

### "Shopify connection fails"
- **Check:** `SHOPIFY_CLIENT_ID` and `SHOPIFY_CLIENT_SECRET` in `backend/.env`.
- **OAuth callback:** Must point to `YOUR_DOMAIN/api/shopify/callback`.
- **Scopes:** Currently set to `read_products,write_products,read_inventory,write_inventory`.

### "Emails not sending"
- **Check:** `RESEND_API_KEY` in `backend/.env`.
- **Domain:** The sender email (`noreply@trendscout.click`) must have DNS records configured in Resend.
- **Test:** `curl -X POST YOUR_DOMAIN/api/email/test` (if the test endpoint exists).

### "AI features not working"
- **Check:** `EMERGENT_LLM_KEY` in `backend/.env`.
- **Budget:** If the key runs low, go to Emergent Platform -> Profile -> Universal Key -> Add Balance.

---

## 6. API Keys & Third-Party Services

### Renewals & Expiry

| Service | Key expires? | How to renew |
|---------|-------------|-------------|
| CJ Dropshipping | Token refreshes every 14 days automatically | Only renew the API key if CJ revokes it |
| Stripe | No expiry | Rotate keys in Stripe Dashboard if compromised |
| Resend | No expiry | Regenerate in Resend dashboard if compromised |
| Meta Ad Library | Token expires periodically | Generate a new long-lived token at developers.facebook.com |
| Shopify | No expiry | Regenerate in Shopify Partners dashboard |
| Emergent LLM | Balance-based | Add balance at Profile -> Universal Key |
| Sentry | No expiry | DSN is permanent per project |

### AliExpress & Zendrop (Not Required)
These are shown as "Compare externally" in the supplier comparison tab. They link users directly to those platforms. No API keys needed — CJ Dropshipping handles all live supplier data.

---

## 7. Shopify App

### Current State
The Shopify App is technically complete with:
- GDPR compliance webhooks (3 mandatory endpoints)
- Embedded App Bridge dashboard
- Session token authentication
- Product import (push to store as draft)

### App Store Submission
See `/app/SHOPIFY_APP_LISTING.md` for the full submission checklist. Key items:
- App icon generated (1024x1024)
- 6 screenshots captured
- Reviewer account: `reviewer@trendscout.click` / `ShopifyReview2026!`
- Privacy policy and Terms updated with Shopify-specific sections
- API version: 2026-01

### GDPR Webhooks
These are mandatory and already implemented:
- `POST /api/shopify/app/webhooks/customers/data_request`
- `POST /api/shopify/app/webhooks/customers/redact`
- `POST /api/shopify/app/webhooks/shop/redact`

---

## 8. Deployment & Updates

### On Emergent Platform
- Click **"Deploy"** in the chat interface to push to production.
- Click **"Save to Github"** to back up your code.
- Use **"Rollback"** to revert to any previous checkpoint (free).

### After Deployment
1. Verify the health endpoint: `curl YOUR_DOMAIN/api/health`
2. Log in and check the dashboard loads
3. Verify CJ search works (may need 5 min after restart for rate limit)
4. Check Stripe webhook is configured for the production URL

### Updating Environment Variables in Production
1. Update the value in `backend/.env`
2. Restart: `sudo supervisorctl restart backend`
3. Verify: `curl YOUR_DOMAIN/api/health`

---

## 9. Monitoring & Logs

### Log Locations
```bash
# Backend logs (errors and warnings)
tail -f /var/log/supervisor/backend.err.log

# Backend stdout
tail -f /var/log/supervisor/backend.out.log

# Frontend logs
tail -f /var/log/supervisor/frontend.err.log
```

### Sentry (Error Monitoring)
- Dashboard: https://sentry.io (log in with the account that owns the DSN)
- Captures unhandled exceptions in the backend automatically
- DSN configured in `backend/.env` as `SENTRY_DSN`

### Health Check
```bash
curl YOUR_DOMAIN/api/health
# Should return: {"status": "ok"}
```

### Check All Services
```bash
sudo supervisorctl status
# Should show:
# backend    RUNNING
# frontend   RUNNING
```

---

## 10. User Management

### Test Accounts
| Email | Password | Role |
|-------|----------|------|
| jenkinslisa1978@gmail.com | admin123456 | Main test user (Elite tier) |
| reviewer@trendscout.click | ShopifyReview2026! | Shopify reviewer account |

### Create a New User
Users self-register at `/signup`. Or via API:
```bash
curl -X POST YOUR_DOMAIN/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!","name":"User Name"}'
```

### Check User's Subscription
```javascript
// In mongosh:
db.users.findOne({email: "user@example.com"}, {_id:0, email:1, subscription_tier:1, stripe_customer_id:1})
```

### Manually Upgrade a User
```javascript
db.users.updateOne(
  {email: "user@example.com"},
  {$set: {subscription_tier: "elite"}}
)
```

---

## 11. Data Management

### Adding New Products
Products can be added by:
1. **CJ Import:** Users search on `/cj-sourcing` and click "Import"
2. **API:** `POST /api/products` with product data (requires auth)
3. **Database:** Insert directly into `products` collection

### Refreshing Product Images
Admin endpoint (requires the main test user token):
```bash
TOKEN=$(curl -s -X POST YOUR_DOMAIN/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jenkinslisa1978@gmail.com","password":"admin123456"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -X POST YOUR_DOMAIN/api/admin/refresh-product-images \
  -H "Authorization: Bearer $TOKEN"
```

### Backup Database
```bash
mongodump --uri="mongodb://localhost:27017" --db=test_database --out=/tmp/backup
```

### Restore Database
```bash
mongorestore --uri="mongodb://localhost:27017" --db=test_database /tmp/backup/test_database
```

---

## 12. Quick Reference

### Restart Services
```bash
sudo supervisorctl restart backend    # After .env changes or pip installs
sudo supervisorctl restart frontend   # After yarn add or .env changes
sudo supervisorctl restart all        # Nuclear option
```

### Check What's Running
```bash
sudo supervisorctl status
```

### Install a Python Package
```bash
pip install <package-name> && pip freeze > /app/backend/requirements.txt
sudo supervisorctl restart backend
```

### Install a Frontend Package
```bash
cd /app/frontend && yarn add <package-name>
sudo supervisorctl restart frontend
```

### Key URLs (replace with your production domain)
| URL | What |
|-----|------|
| `/` | Landing page |
| `/dashboard` | Main dashboard (authenticated) |
| `/discover` | Product discovery |
| `/product/:id` | Product detail with launch score |
| `/cj-sourcing` | CJ Dropshipping search & import |
| `/ad-spy` | Ad intelligence |
| `/tiktok-intelligence` | TikTok trending products |
| `/profitability-simulator` | Profit calculator |
| `/competitor-intel` | Competitor analysis |
| `/radar-alerts` | Alert configuration |
| `/verified-winners` | Community winners |
| `/pricing` | Subscription plans |
| `/shopify-app` | Public Shopify App page |
| `/privacy` | Privacy policy |
| `/terms` | Terms of service |
| `/help` | Help & FAQ |
| `/api/health` | Backend health check |

---

## 13. Marketing & Analytics Setup

Your marketing team can set up tracking **themselves** via GitHub — no developer needed.

### Google Analytics 4 (Simplest)
1. Go to https://analytics.google.com → Admin → Create Property
2. Set up a Web data stream for your domain
3. Copy the **Measurement ID** (looks like `G-XXXXXXXXXX`)
4. In GitHub, edit `/frontend/.env` and set:
   ```
   REACT_APP_GA4_ID=G-XXXXXXXXXX
   ```
5. Deploy — tracking starts automatically

### Google Tag Manager (Full Control)
If the team wants to manage multiple pixels (GA4 + Meta + TikTok etc.):
1. Go to https://tagmanager.google.com → Create Account & Container
2. Copy the **Container ID** (looks like `GTM-XXXXXXX`)
3. In GitHub, edit `/frontend/.env` and set:
   ```
   REACT_APP_GTM_ID=GTM-XXXXXXX
   ```
4. Deploy — the team can then add any tags from the GTM dashboard

### Both at Once
You can set both `REACT_APP_GA4_ID` and `REACT_APP_GTM_ID`. GA4 gives you basic analytics immediately, while GTM gives the marketing team a dashboard to add more tracking later.

### What Gets Tracked Automatically
- Page views (every route change)
- User sessions and demographics
- Referral sources
- Device and browser info

The team can then set up custom events (e.g. signup conversions, product views) from their Google Analytics or GTM dashboard.

---

*Last updated: March 18, 2026*
*Contact: info@trendscout.click*
