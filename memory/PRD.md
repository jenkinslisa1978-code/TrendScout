# ViralScout/TrendScout - Product Requirements Document

## Product Overview
ViralScout is a SaaS platform for product research, trend analysis, and **store creation**, designed for dropshippers and e-commerce entrepreneurs. Users can discover trending products, generate AI-powered store concepts, and manage multiple shops from a single dashboard. The platform supports Shopify integration for seamless product export.

## Tech Stack
- **Frontend:** React SPA with React Router, TailwindCSS, Shadcn/UI
- **Backend:** FastAPI with MongoDB
- **Data Visualization:** Recharts
- **State Management:** React Context API
- **Payments:** Stripe-ready architecture
- **Data Ingestion:** Modular importer architecture
- **Store Builder:** AI-powered rules-based generation (LLM-ready)

---

## Store-Launch Platform (NEW - March 2026)

### Overview
Users can create and manage stores directly from trending products. The system generates store names, taglines, product copy, pricing suggestions, and branding automatically.

### Features
| Feature | Status | Description |
|---------|--------|-------------|
| Multi-user stores | ✅ Complete | Each user owns their stores, isolated by owner_id |
| Plan-based limits | ✅ Complete | Starter: 1, Pro: 5, Elite: unlimited |
| AI Store Builder | ✅ Complete | Rules-based generation (LLM-ready) |
| Product-to-Store | ✅ Complete | One-click store creation from any product |
| Store Preview | ✅ Complete | Public storefront preview page |
| Store Management | ✅ Complete | Edit, delete, publish stores |
| Shopify Export | ✅ Complete | Export store/products in Shopify format |

### Database Schema

**stores collection:**
```json
{
  "id": "uuid",
  "owner_id": "user-id",
  "name": "Store Name",
  "tagline": "Generated tagline",
  "headline": "Homepage headline",
  "category": "Home Decor",
  "status": "draft|published|archived",
  "branding": {
    "style_name": "Modern Minimal",
    "primary_color": "#0f172a",
    "secondary_color": "#3b82f6",
    "accent_color": "#10b981",
    "font_family": "Inter"
  },
  "faqs": [...],
  "policies": {...}
}
```

**store_products collection:**
```json
{
  "id": "uuid",
  "store_id": "store-uuid",
  "original_product_id": "product-uuid",
  "title": "Generated product title",
  "description": "Generated description",
  "bullet_points": ["..."],
  "price": 34.99,
  "compare_at_price": 48.99,
  "is_featured": true
}
```

### API Endpoints
```
GET    /api/stores              - List user's stores
GET    /api/stores/:id          - Get store details
POST   /api/stores              - Create store from product
PUT    /api/stores/:id          - Update store
DELETE /api/stores/:id          - Delete store
POST   /api/stores/generate     - Generate store content (AI)
GET    /api/stores/:id/products - List store products
POST   /api/stores/:id/products - Add product to store
PUT    /api/stores/:id/products/:pid - Update store product
POST   /api/stores/:id/regenerate/:pid - Regenerate product copy
GET    /api/stores/:id/export   - Export for Shopify
GET    /api/stores/:id/preview  - Get store preview data
GET    /api/stores/limits       - Get plan limits
```

### User Flow
1. User discovers trending product
2. Clicks "Build Shop" button
3. AI generates store name suggestions + content
4. User selects/customizes name
5. Preview store concept
6. Create store
7. Edit/manage from My Stores dashboard
8. Export to Shopify when ready

---

## Data Ingestion Architecture

### Supported Data Sources

| Source | Description | API Status | Data Types |
|--------|-------------|------------|------------|
| **TikTok Creative Center** | Viral product trends from TikTok | Curated + API-ready | Views, engagement, hashtags |
| **Amazon Movers & Shakers** | Fast-rising Amazon products | Curated + API-ready | Rank, reviews, ratings |
| **Supplier Feeds** | AliExpress, CJ Dropshipping | Curated + API-ready | Pricing, orders, suppliers |

### Data Flow
```
External Source → Importer → Normalizer → Deduplicator → Database → Automation Pipeline → Alerts
```

### API Endpoints
```
GET  /api/ingestion/sources        - List available data sources
POST /api/ingestion/tiktok         - Import from TikTok
POST /api/ingestion/amazon         - Import from Amazon
POST /api/ingestion/supplier       - Import from Supplier feeds
POST /api/ingestion/supplier/csv   - Import from CSV upload
POST /api/ingestion/full-sync      - Run full data sync from all sources
```

### Admin Controls
- Run TikTok Import
- Run Amazon Import
- Run Supplier Import
- Run Full Data Sync
- Configure product limit (10/20/50/100)
- View import results and alerts generated

### Scheduled Automation
Configure a cron job to call `/api/ingestion/full-sync` daily:
```bash
curl -X POST https://your-domain.com/api/ingestion/full-sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 100}'
```

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
- [x] ~~Multi-user store creation~~ (COMPLETED March 2026)
- [x] ~~AI store builder with content generation~~ (COMPLETED March 2026)
- [x] ~~Store preview pages~~ (COMPLETED March 2026)
- [x] ~~Shopify export~~ (COMPLETED March 2026)
- [ ] Add Stripe live credentials and test checkout flow
- [ ] Configure Supabase and migrate from Demo Mode
- [ ] Set up actual scheduled cron job for daily automation

### P1 - High Priority
- [ ] Live Shopify API integration (OAuth, push products)
- [ ] Integrate OpenAI for enhanced AI summaries
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

- **Last Test:** March 2026
- **Backend Tests:** All endpoints passing (100%)
- **Frontend Tests:** Full integration with backend API
- **Test Report:** /app/test_reports/iteration_4.json
- **Launch Guide:** /app/LAUNCH_GUIDE.md

---

## Beta Launch Readiness

### ✅ FULLY LIVE AND USABLE - No Credentials Needed
| Component | Status |
|-----------|--------|
| Backend API | Fully functional |
| MongoDB persistence | Working |
| Frontend-Backend integration | Complete |
| Automation engine | Working |
| Data ingestion | Working with images |
| Protected routes | Working |
| Admin routes | Working |
| Demo mode | Fully functional |
| Store Launch Platform | **Complete** |
| AI Store Builder | **Complete** |
| Store Preview Pages | **Complete with images** |
| Shopify Export | **Complete with instructions** |
| Product Images | **65/65 products have images** |

### ⏳ REQUIRES YOUR CREDENTIALS
| Component | What's Needed | When |
|-----------|---------------|------|
| Live Auth | Supabase URL + anon key | For real user accounts |
| Shopify Direct Publish | SHOPIFY_API_KEY + SECRET | For one-click publish |
| Daily Automation | Cron job setup | For automated syncs |

---

## Changelog

### March 10, 2026 - Store Launch Platform
**MAJOR FEATURE: Multi-User Store Creation**

**Store Status System:**
- `draft` → Initial state after creation
- `ready` → Reviewed and ready for export
- `exported` → Exported to Shopify format
- `published` → Live on Shopify

**New Backend Components:**
- `/app/backend/services/store_service.py` - StoreGenerator class with AI generation
- Store API routes: CRUD, generate, export, preview, regenerate
- `PUT /api/stores/:id/status` - Update store status with timestamps
- Plan-based store limits (Starter: 1, Pro: 5, Elite: unlimited)
- Shopify-compatible export format
- Auto-status update on export

**New Frontend Features:**
- **Launch Progress Indicator** - 4-step visual progress (Create → Review → Export → Launch)
- **Status-based Actions** - Dynamic buttons based on current status
- **Progress in Store Cards** - Mini progress indicator in My Stores dashboard
- Status badges with color coding (Draft=gray, Ready=blue, Exported=amber, Published=green)

**New Frontend Pages:**
- `/app/frontend/src/pages/StoresPage.jsx` - My Stores dashboard
- `/app/frontend/src/pages/StoreDetailPage.jsx` - Store management with 4 tabs
- `/app/frontend/src/pages/StorePreviewPage.jsx` - Public storefront preview
- `/app/frontend/src/components/store/StoreBuilderModal.jsx` - AI store creation wizard
- `/app/frontend/src/services/storeService.js` - Store API client

**Updated Files:**
- `/app/frontend/src/pages/ProductDetailPage.jsx` - Added "Build Shop" button
- `/app/frontend/src/components/layouts/DashboardLayout.jsx` - Added "My Stores" nav
- `/app/frontend/src/App.js` - Added store routes

**Test Results:**
- Backend: 21/21 tests passed (100%)
- Frontend: All store flows working (100%)
- Test Report: /app/test_reports/iteration_5.json

**AI Generation Features:**
- Store name suggestions (5 options)
- Store tagline generation
- Homepage headline generation
- Product title optimization
- Product description generation
- Bullet points (5 features)
- Pricing suggestions with compare-at
- Branding style (colors, fonts)
- FAQ placeholders (5 questions)
- Policy templates (shipping, returns, privacy)

---

### March 9, 2026 - Beta Launch Preparation
**Major Updates:**
- Connected all frontend services to backend API (products, alerts, logs)
- Prepared AuthContext for seamless Supabase transition
- Added AdminRoute wrapper for admin-only pages
- Verified scheduled automation endpoint is secure and functional
- Created comprehensive LAUNCH_GUIDE.md with step-by-step setup

**Files Modified:**
- `/app/frontend/src/services/automationLogService.js`
- `/app/frontend/src/services/alertService.js`
- `/app/frontend/src/services/productService.js`
- `/app/frontend/src/contexts/AuthContext.jsx`
- `/app/frontend/src/App.js`
- `/app/frontend/src/components/automation/AutomationLogs.jsx`

**Verified Working:**
- Login/Logout flow (Demo mode)
- Dashboard with real data (65 products)
- Alerts page with real data (112 alerts)
- Automation logs with real data (17 runs)
- Scheduled automation endpoint (secure with API key)
- All data ingestion sources

---

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
