# ViralScout/TrendScout - Product Requirements Document

## Product Overview
ViralScout is a SaaS application for product research and trend analysis, designed for dropshippers and e-commerce entrepreneurs. The platform automatically scores products, calculates opportunity ratings, assigns trend stages, generates AI-style summaries, and creates alerts for high-potential opportunities.

## Tech Stack
- **Frontend:** React SPA with React Router, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI with MongoDB
- **Data Visualization:** Recharts
- **State Management:** React Context API
- **Payments:** Stripe-ready architecture

---

## Stage 3 Completion Status (December 2025)

### A. What Was Fully Implemented

#### 1. Backend API (FastAPI + MongoDB)
- **Products API:** Full CRUD with automatic automation on create/update
- **Alerts API:** Create, read, mark read, dismiss with stats
- **Automation API:** Run pipeline, get logs, get stats
- **Scheduled Automation:** Cron-ready endpoint with API key authentication
- **Stripe API:** Checkout session, portal session, webhook handler (scaffolded)

#### 2. Automation Engine
- **Trend Score Calculator:** Weighted algorithm based on TikTok views (35%), ad count (20%), competition (20%), margin (25%)
- **Trend Stage Classifier:** Assigns early/rising/peak/saturated based on signals
- **Opportunity Rating:** Calculates low/medium/high/very high based on composite score
- **AI Summary Generator:** Rules-based summary generation (placeholder for real AI)
- **Alert Generator:** Creates alerts for products with score >= 75 and opportunity >= high

#### 3. Automation Logging System
- Full logging of all automation runs
- Tracks job type, status, products processed, alerts generated
- Duration tracking with timestamps
- Error message capture for failures
- UI display in Automation Center Logs tab

#### 4. Subscription Service
- Plan definitions (Starter, Pro, Elite) with feature limits
- Stripe checkout session creation (scaffolded)
- Stripe customer portal (scaffolded)
- Webhook event handler structure
- Plan-based feature gating

#### 5. Access Control Service
- Permission definitions and checks
- Plan-based access rules
- Admin-only route protection
- Feature availability by plan

#### 6. Database Seeding
- 15 realistic products with full automation data
- 4+ alerts generated from qualifying products
- Demo profile and subscription
- Automation log entry

### B. What Was Fixed

1. **MongoDB ObjectId Serialization:** Fixed JSON serialization error when creating products
2. **Tab Duplication:** Fixed duplicate tabs in AdminAutomationPage
3. **Linting Issues:** Fixed unused variables in backend server.py

### C. What Is Still Blocked

1. **Live Stripe Integration:** Requires actual Stripe API keys (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, price IDs)
2. **Real AI Summaries:** Requires OpenAI or similar LLM API key
3. **Live Data Sources:** TikTok, Amazon, AliExpress APIs not integrated (placeholders)
4. **Supabase Live Mode:** Frontend designed for Supabase but runs in Demo Mode with localStorage

### D. What Requires External Credentials

| Service | Required Credentials | Purpose |
|---------|---------------------|---------|
| Stripe | STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, Price IDs | Live payment processing |
| Supabase | REACT_APP_SUPABASE_URL, REACT_APP_SUPABASE_ANON_KEY | Production database & auth |
| OpenAI | OPENAI_API_KEY | Real AI summaries |
| TikTok API | API credentials | Live trend data |

### E. Final Status of All Areas

| Area | Status | Notes |
|------|--------|-------|
| **Auth** | ✅ Working | Demo Mode with localStorage; Supabase ready |
| **Supabase** | ⚠️ Scaffolded | Frontend structured for Supabase, runs in Demo Mode |
| **Dashboard** | ✅ Working | Premium UI with charts, stats, product list |
| **Product Detail** | ✅ Working | Full product info with AI summary |
| **Saved Products** | ✅ Working | Save/unsave with localStorage persistence |
| **Admin Panel** | ✅ Working | Products/Users/Subscriptions tabs |
| **Automation Panel** | ✅ Working | Quick actions, CSV import, manual entry, logs |
| **Automation Engine** | ✅ Working | Full pipeline: scoring, stages, opportunity, summaries, alerts |
| **Alerts** | ✅ Working | Generation, display, read/dismiss, stats |
| **Access Control** | ✅ Working | Plan-based permissions, admin checks |
| **Stripe Readiness** | ⚠️ Scaffolded | Endpoints exist, returns demo_mode without keys |
| **Scheduled Jobs** | ✅ Ready | /api/automation/scheduled/daily with API key auth |
| **End-to-End** | ✅ Working | Products flow through automation pipeline correctly |

---

## Architecture

### Backend Structure
```
/app/backend/
├── server.py           # Main FastAPI app with all routes
├── seed_database.py    # Database seeding script
├── requirements.txt
└── tests/
    └── test_viralscout_api.py
```

### Frontend Structure
```
/app/frontend/src/
├── App.js
├── components/
│   ├── automation/
│   │   └── AutomationLogs.jsx
│   ├── layouts/
│   │   └── DashboardLayout.jsx
│   └── ui/ (Shadcn components)
├── contexts/
│   └── AuthContext.jsx
├── lib/
│   ├── automation/
│   │   ├── index.js
│   │   ├── trend-score.js
│   │   ├── opportunity-score.js
│   │   ├── trend-stage.js
│   │   ├── ai-summary.js
│   │   ├── alerts.js
│   │   └── product-import.js
│   ├── supabase.js
│   └── utils.js
├── pages/
│   ├── DashboardPage.jsx
│   ├── DiscoverPage.jsx
│   ├── AdminPage.jsx
│   ├── AdminAutomationPage.jsx
│   ├── TrendAlertsPage.jsx
│   └── ...
└── services/
    ├── productService.js
    ├── alertService.js
    ├── automationLogService.js
    ├── subscriptionService.js
    ├── accessControlService.js
    └── savedProductService.js
```

### API Endpoints
```
GET  /api/health                    - Health check
GET  /api/products                  - List products with filters
POST /api/products                  - Create product (auto-scored)
GET  /api/products/{id}             - Get single product
PUT  /api/products/{id}             - Update product (re-scored)
DELETE /api/products/{id}           - Delete product

GET  /api/alerts                    - List alerts with stats
PUT  /api/alerts/{id}/read          - Mark alert as read
PUT  /api/alerts/{id}/dismiss       - Dismiss alert

POST /api/automation/run            - Run automation pipeline
GET  /api/automation/logs           - Get automation history
GET  /api/automation/stats          - Get automation statistics
POST /api/automation/scheduled/daily - Scheduled job endpoint (API key required)

POST /api/stripe/create-checkout-session  - Start checkout
POST /api/stripe/create-portal-session    - Customer portal
POST /api/stripe/webhook                   - Handle webhooks
POST /api/stripe/cancel-subscription       - Cancel subscription
```

---

## Backlog

### P0 - Critical for Production
- [ ] Add Stripe live credentials and test checkout flow
- [ ] Configure Supabase and migrate from Demo Mode
- [ ] Set up actual scheduled cron job for daily automation

### P1 - High Priority
- [ ] Integrate OpenAI for real AI summaries
- [ ] Add user registration with email verification
- [ ] Implement password reset flow
- [ ] Add data export functionality (CSV/PDF)

### P2 - Medium Priority
- [ ] TikTok Creative Center API integration
- [ ] Amazon Product API integration
- [ ] AliExpress supplier API integration
- [ ] Email notifications for alerts
- [ ] Webhook triggers for real-time updates

### P3 - Low Priority
- [ ] User onboarding flow
- [ ] Advanced analytics dashboard
- [ ] Team/organization support
- [ ] API rate limiting and quotas

---

## Test Status

- **Last Test:** December 2025
- **Backend Tests:** 22/22 passed (100%)
- **Frontend Tests:** 95% (Demo Mode working)
- **Test Report:** /app/test_reports/iteration_4.json

---

## Changelog

### December 9, 2025 - Stage 3 Completion
- Implemented backend API with FastAPI + MongoDB
- Created automation logging system with full tracking
- Built subscription service with Stripe scaffolding
- Added access control service for plan-based permissions
- Created database seeding script with 15 products
- Fixed MongoDB ObjectId serialization bug
- Updated Admin Automation page with Logs tab
- All 22 backend API tests passing
- End-to-end automation pipeline fully functional
