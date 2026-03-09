# ViralScout Production Blockers Analysis

## Summary
This document identifies all remaining blockers preventing ViralScout from being a fully live production product.

---

## 1. CAN BE FIXED IN CODE NOW

These items can be implemented immediately without external dependencies:

### 1.1 Frontend-Backend Data Sync
**Issue:** Frontend uses localStorage (Demo Mode) while backend has MongoDB
**Fix:** Update frontend services to fetch from backend API instead of localStorage
**Files to modify:**
- `/app/frontend/src/services/productService.js` - Use `/api/products` endpoints
- `/app/frontend/src/services/alertService.js` - Use `/api/alerts` endpoints  
- `/app/frontend/src/services/automationLogService.js` - Use `/api/automation/logs` endpoints
**Effort:** 2-3 hours

### 1.2 User Registration Backend
**Issue:** Backend has no user registration endpoint
**Fix:** Add `/api/auth/register` and `/api/auth/login` endpoints to server.py
**Files to modify:**
- `/app/backend/server.py` - Add auth routes with password hashing
**Effort:** 1-2 hours

### 1.3 Saved Products Backend Persistence
**Issue:** Saved products only persist in localStorage
**Fix:** Add `/api/saved-products` CRUD endpoints
**Files to modify:**
- `/app/backend/server.py` - Add saved_products collection routes
- `/app/frontend/src/services/savedProductService.js` - Use API
**Effort:** 1 hour

### 1.4 Plan Enforcement on Backend
**Issue:** Plan-based access only enforced on frontend
**Fix:** Add middleware to check user plan on protected routes
**Files to modify:**
- `/app/backend/server.py` - Add auth middleware with plan checks
**Effort:** 1-2 hours

### 1.5 Error Handling & Validation
**Issue:** Limited input validation on API endpoints
**Fix:** Add Pydantic validation, error responses, rate limiting
**Files to modify:**
- `/app/backend/server.py` - Enhanced validation
**Effort:** 2-3 hours

---

## 2. REQUIRES CREDENTIALS

These items need external API keys or secrets to function:

### 2.1 Stripe Payment Processing ⭐ HIGH PRIORITY
**Required credentials:**
- `STRIPE_SECRET_KEY` - From Stripe Dashboard > Developers > API Keys
- `STRIPE_WEBHOOK_SECRET` - From Stripe Dashboard > Webhooks
- `STRIPE_PRO_PRICE_ID` - Create in Stripe > Products
- `STRIPE_ELITE_PRICE_ID` - Create in Stripe > Products

**Setup steps:**
1. Create Stripe account at stripe.com
2. Create Products (Pro $49/mo, Elite $99/mo)
3. Add price IDs to environment
4. Configure webhook endpoint URL
5. Test with Stripe test mode first

**Files ready:**
- `/app/backend/server.py` - Stripe routes implemented
- `/app/frontend/src/services/subscriptionService.js` - Frontend service ready

### 2.2 Supabase Database & Auth (OPTIONAL)
**Required credentials:**
- `REACT_APP_SUPABASE_URL` - From Supabase project settings
- `REACT_APP_SUPABASE_ANON_KEY` - From Supabase project settings

**Note:** Current MongoDB backend works. Supabase is optional for:
- Social auth (Google, GitHub login)
- Real-time subscriptions
- Edge functions for scheduled jobs

### 2.3 OpenAI API for AI Summaries ⭐ HIGH PRIORITY
**Required credentials:**
- `REACT_APP_OPENAI_API_KEY` or `OPENAI_API_KEY`

**Setup steps:**
1. Create OpenAI account at platform.openai.com
2. Generate API key
3. Add to environment variables
4. Uncomment AI API code in `/app/frontend/src/lib/automation/ai-summary.js`

**Current state:** Rules-based summaries work, but real AI would be much better

### 2.4 Live Data Source APIs (FUTURE)
These are optional but would make the product much more valuable:

**TikTok Creative Center API:**
- Access requires TikTok for Business account
- Provides real trending product data
- May require partnership agreement

**Amazon Product Advertising API:**
- Requires Amazon Associates account
- 5% commission potential
- Rate limited

**AliExpress Affiliate API:**
- Requires Portals account
- Product sourcing data
- Supplier pricing

---

## 3. REQUIRES DEPLOYMENT SETUP

These items need infrastructure configuration:

### 3.1 Scheduled Automation (Cron Jobs) ⭐ HIGH PRIORITY
**Current state:** `/api/automation/scheduled/daily` endpoint exists with API key auth

**Options:**

**Option A: External Cron Service (Recommended)**
- Use cron-job.org (free)
- Configure: `POST https://your-domain.com/api/automation/scheduled/daily`
- Header: `X-API-Key: vs_automation_key_2024`
- Schedule: Daily at 2:00 AM UTC

**Option B: Supabase Edge Functions**
- Create edge function with pg_cron
- Requires Supabase setup

**Option C: Cloud Scheduler**
- AWS EventBridge / Google Cloud Scheduler
- More complex but more reliable

### 3.2 Production Domain & SSL
**Required:**
- Custom domain (e.g., viralscout.com)
- SSL certificate (usually auto with hosting)
- DNS configuration

### 3.3 Environment Variables in Production
**Required env vars for production:**
```
# Backend
MONGO_URL=mongodb+srv://...
DB_NAME=viralscout_prod
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
AUTOMATION_API_KEY=<strong-random-key>
CORS_ORIGINS=https://viralscout.com

# Frontend
REACT_APP_BACKEND_URL=https://api.viralscout.com
REACT_APP_SUPABASE_URL=https://xxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJ...
REACT_APP_STRIPE_PRO_PRICE_ID=price_...
REACT_APP_STRIPE_ELITE_PRICE_ID=price_...
```

### 3.4 Database Migration
**Steps:**
1. Set up MongoDB Atlas cluster (or keep local for testing)
2. Run seed script on production database
3. Configure connection string

### 3.5 Stripe Webhook Configuration
**Steps:**
1. In Stripe Dashboard > Webhooks > Add endpoint
2. URL: `https://api.viralscout.com/api/stripe/webhook`
3. Select events: checkout.session.completed, customer.subscription.*
4. Copy signing secret to `STRIPE_WEBHOOK_SECRET`

---

## 4. REQUIRES FUTURE PRODUCT IMPROVEMENT

These are enhancements for a more complete product:

### 4.1 Email Notifications
- Alert notifications via email
- Subscription confirmations
- Password reset emails
- Requires: SendGrid/Resend API key

### 4.2 Real-Time Updates
- WebSocket for live dashboard updates
- Push notifications for alerts
- Requires: Socket.io or Supabase Realtime

### 4.3 Data Export
- CSV export of products
- PDF reports
- Saved searches

### 4.4 Team/Organization Support
- Multiple users per account
- Role-based permissions
- Shared saved products

### 4.5 Advanced Analytics
- Trend prediction models
- Historical data charts
- Custom alerts rules

### 4.6 Mobile App
- React Native companion app
- Push notifications
- Quick product scanning

### 4.7 API Access for Elite Users
- Public API with rate limiting
- Webhook notifications
- Integration documentation

---

## Quick Start Checklist for Production Launch

### Minimum Viable Production (1-2 days)
- [ ] Add Stripe credentials (test mode first)
- [ ] Set up cron job for daily automation
- [ ] Deploy to production domain
- [ ] Test checkout flow end-to-end

### Recommended Before Launch (1 week)
- [ ] Add OpenAI for real AI summaries
- [ ] Sync frontend with backend API (remove Demo Mode)
- [ ] Add proper user authentication to backend
- [ ] Configure production MongoDB
- [ ] Set up error monitoring (Sentry)

### Nice to Have (2-4 weeks)
- [ ] Email notifications
- [ ] TikTok API integration
- [ ] Team accounts
- [ ] Mobile responsive improvements

---

## Cost Estimates

| Service | Free Tier | Production Cost |
|---------|-----------|-----------------|
| MongoDB Atlas | 512MB free | $9/mo (M2) |
| Stripe | 2.9% + $0.30 per transaction | - |
| OpenAI | $5 free credit | ~$10-50/mo |
| Hosting (Vercel/Railway) | Free tier | $20/mo |
| Domain | - | $12/year |
| **Total** | ~$0/mo | ~$50-100/mo |

