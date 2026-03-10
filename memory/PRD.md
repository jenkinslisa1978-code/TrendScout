# ViralScout - Product Requirements Document

## Project Overview
ViralScout is a full-stack SaaS platform for product research and e-commerce store launching. Users can discover trending products, analyze opportunities, and build complete Shopify-ready stores with AI-generated content.

**Default Currency: GBP (£)**

**CRITICAL DATA POLICY**: The platform NEVER fabricates numbers. If signals are unavailable, display null, unknown, or a confidence score.

## Original Problem Statement
Build a platform that helps dropshippers and e-commerce entrepreneurs:
1. Find trending products before they go viral
2. Analyze product opportunities with data-driven insights
3. Build complete store concepts with AI-generated content
4. Export stores directly to Shopify

## Tech Stack
- **Frontend**: React + TailwindCSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Auth**: Supabase (configured)
- **Payments**: Stripe (scaffolded, requires credentials)
- **Currency**: GBP (British Pound Sterling)

## Architecture (Three-Layer Design)

### Layer 1: Data Pipeline Layer
Background workers for data collection and processing.
- `/app/backend/services/data_pipeline/` - External data ingestion
- `/app/backend/services/data_sources/` - Source connectors
- Jobs run via APScheduler, write to database

### Layer 2: Application API Layer
User-facing SaaS platform - reads precomputed data only.
- `/app/backend/server.py` - Main API routes
- `/app/backend/routes/` - Modular route handlers

### Layer 3: Intelligence & Prediction Layer (NEW)
Converts raw data into actionable insights.
- `/app/backend/services/intelligence/` - Analysis modules

## Core Features (Implemented)

### Product Validation Engine (NEW - March 2026)
**Answers the key question: "Should I launch this product?"**

#### API Endpoints
- `GET /api/intelligence/validate/{id}` - Full product validation
- `GET /api/intelligence/success-prediction/{id}` - Success probability
- `GET /api/intelligence/trend-analysis/{id}` - Trend analysis
- `GET /api/intelligence/complete-analysis/{id}` - All-in-one analysis
- `GET /api/intelligence/opportunities` - Launch opportunities
- `GET /api/intelligence/early-opportunities` - Early trend opportunities

#### Validation Signals (6-Factor Model)
1. **Trend Velocity (20%)** - Is demand growing?
2. **Profit Margin (25%)** - Can you make money?
3. **Competition (20%)** - Is market saturated?
4. **Ad Activity (10%)** - How hard to compete?
5. **Supplier Demand (10%)** - Is supply reliable?
6. **Engagement (15%)** - Social proof

#### Recommendations
- `LAUNCH_OPPORTUNITY` (Score ≥70) - Strong signals, go ahead
- `PROMISING_MONITOR` (Score 50-69) - Watch closely
- `HIGH_RISK` (Score <50) - Consider alternatives
- `INSUFFICIENT_DATA` - Need more signals

#### Success Prediction
- Calculates `success_probability` (0-100%)
- Outcome classifications: HIGH_SUCCESS | MODERATE_SUCCESS | UNCERTAIN | LIKELY_FAILURE
- Shows contributing factors with explanations

#### Trend Analysis
- `trend_velocity` - Rate of change
- `trend_stage` - exploding | rising | early_trend | stable | declining
- `is_early_opportunity` - First-mover advantage detection
- `days_until_saturation` - Market timeline estimate

#### Frontend Components
- `/app/frontend/src/components/intelligence/` - Validation UI
  - `LaunchRecommendationBadge` - Visual recommendation
  - `ProductValidationCard` - Complete analysis display
  - `SuccessPredictionCard` - Probability visualization
  - `TrendAnalysisCard` - Trend details
- ProductDetailPage updated with "Should You Launch?" card

### Data Integrity System
**CRITICAL**: Ensures platform never presents fabricated data as real insights.

#### Backend Services
- `/app/backend/services/data_integrity.py` - Signal provenance tracking, confidence scoring
- `/app/backend/services/source_health.py` - Data source health monitoring

#### API Endpoints
- `GET /api/data-integrity/platform-health` - Overall platform data health
- `GET /api/data-integrity/source-health` - All data source statuses
- `GET /api/data-integrity/source-health/{source}` - Single source health
- `GET /api/data-integrity/product/{id}` - Product data integrity details
- `GET /api/data-integrity/products/confidence` - Products filtered by confidence
- `GET /api/data-integrity/data-freshness` - Data freshness report
- `GET /api/data-integrity/simulated-data-report` - Simulated vs real data breakdown

#### Confidence Score Calculation (0-100)
- **Completeness (30%)**: Critical fields filled (supplier_cost, retail_price, views, ads, competitors)
- **Source Quality (40%)**: Live API (100) vs Simulated (20)
- **Freshness (20%)**: <1hr (100), 1-24hr (60), >24hr (20)
- **Consistency (10%)**: Signal validation (margin logic, competition vs ads)

#### Confidence Levels
- **High (80-100)**: Live API data with multiple verified sources
- **Medium (50-79)**: Single live source or good estimation
- **Low (25-49)**: Estimation with limited signals
- **Very Low (0-24)**: Simulated or highly uncertain

#### Data Freshness Categories
- **Real-time**: < 1 minute old
- **Fresh**: < 1 hour old
- **Recent**: 1-24 hours old
- **Stale**: > 24 hours old

#### Frontend Components
- `/app/frontend/src/components/data-integrity/` - UI components for data quality
  - `ConfidenceBadge` - Shows confidence level with color coding
  - `DataSourceBadge` - Shows data source (live/simulated)
  - `DataFreshnessBadge` - Shows data age
  - `DataIntegrityWarning` - Warning banner for low quality data
  - `DataIntegritySummary` - Full data quality card

#### Enhanced Product API
- `GET /api/products?include_integrity=true` - Returns products with integrity metadata
- `GET /api/products/{id}?include_integrity=true` - Single product with data quality info

### Product Research Platform
- ✅ Product database with trend scoring
- ✅ TikTok views and ad count tracking
- ✅ Opportunity rating algorithm (low/medium/high/very high)
- ✅ Trend stage classification (early/rising/peak/saturated)
- ✅ **Early Trend Detection System**
- ✅ **Competitor & Market Intelligence System** (NEW - Dec 2025)
- ✅ AI-generated product summaries
- ✅ Alert generation for high-potential products
- ✅ Data ingestion from multiple sources

### Competitor & Market Intelligence System (Updated Dec 2025)

#### Live Data Pipeline Architecture
The system now uses a **modular hybrid architecture** supporting both simulated and live data sources:

```
/services/
├── data_sources/
│   ├── base.py              # Abstract base class with caching, rate limiting
│   ├── trend_sources.py     # TikTok, Amazon trending
│   ├── supplier_data.py     # AliExpress, CJ Dropshipping
│   ├── competitor_analysis.py  # Store detection
│   └── ad_signals.py        # Ad activity estimation
├── scoring/
│   └── __init__.py          # 5-component scoring engine
├── jobs/
│   ├── queue.py             # MongoDB-backed job queue
│   ├── worker.py            # Background async worker
│   ├── scheduler.py         # APScheduler cron scheduling
│   └── tasks.py             # Task definitions
└── pipeline.py              # Orchestrator for all sources
```

### Background Job System (Dec 2025)

Heavy processing now runs in background jobs instead of blocking API requests.

#### Scheduled Jobs
| Job | Schedule | Description |
|-----|----------|-------------|
| `ingest_trending_products` | Every 4 hours | Fetch TikTok, Amazon trends |
| `update_market_scores` | Every 2 hours | Recalculate all product scores |
| `update_competitor_data` | Every 6 hours | Refresh competitor intelligence |
| `update_ad_activity` | Every 4 hours | Update ad activity signals |
| `update_supplier_data` | Every 6 hours | Merge supplier pricing |
| `generate_alerts` | Every hour | Create opportunity alerts |
| `cleanup_stale_jobs` | Every 15 min | Clean up stuck jobs |

#### Job Features
- **Automatic scheduling** via APScheduler (cron-style)
- **Manual trigger** via API for testing/debugging
- **Duplicate prevention**: Same job type cannot run concurrently
- **Comprehensive logging**: start/end time, status, records processed, errors
- **Trigger source tracking**: "scheduled" or "manual"
- **Stale job cleanup**: Auto-fail jobs running >30 minutes

#### Job API Endpoints
- `GET /api/jobs/status` - Worker, scheduler, queue status
- `GET /api/jobs/history` - Job execution history
- `GET /api/jobs/running` - Currently running/pending jobs
- `GET /api/jobs/{job_id}` - Specific job details
- `POST /api/jobs/trigger/{task_name}` - Manual trigger
- `POST /api/jobs/{job_id}/cancel` - Cancel pending job
- `GET /api/jobs/scheduled/list` - Scheduled jobs with next run times
- `POST /api/jobs/scheduled/{task_name}/pause` - Pause scheduled job
- `POST /api/jobs/scheduled/{task_name}/resume` - Resume paused job

#### Data Sources
| Source | Status | Data Provided |
|--------|--------|---------------|
| TikTok Trends | Simulated | Views, engagement, hashtags |
| Amazon BSR | Simulated | Sales rank, reviews, rating |
| AliExpress | Simulated | Supplier cost, orders, shipping |
| CJ Dropshipping | Simulated | Fast shipping suppliers |
| Competitor Intelligence | Estimated | Store count, pricing |
| Ad Activity | Estimated | Ad spend, platform distribution |

**Note:** All sources are designed for easy swap to live APIs (SerpAPI, TikTok API, etc.)

#### Market Score Calculation (5 Components)
```
market_score = (
  trend_score * 0.25 +
  margin_score * 0.25 +
  competition_score * 0.20 +
  ad_activity_score * 0.15 +
  supplier_demand_score * 0.15
)
```

#### Score Components
| Component | Weight | Signals |
|-----------|--------|---------|
| Trend | 25% | TikTok views, view growth, engagement, stage |
| Margin | 25% | Absolute margin (GBP), margin percentage |
| Competition | 20% | Active stores, saturation, new entrants |
| Ad Activity | 15% | Ad count sweet spot, growth, validation |
| Supplier Demand | 15% | Order velocity, 30-day orders, fulfillment |

#### Market Labels
| Score Range | Label | Badge |
|------------|-------|-------|
| 90+ | Massive Opportunity | Purple |
| 75-89 | Strong Opportunity | Green |
| 60-74 | Competitive | Amber |
| <60 | Saturated | Gray |

#### Data Freshness Tracking
All products include:
- `last_updated`: When data was last refreshed
- `data_source`: Source name (tiktok_trends, aliexpress, etc.)
- `confidence_score`: Data quality score (0-100)
- `scores_updated_at`: When scores were recalculated

#### Pipeline API Endpoints
- `POST /api/automation/pipeline/full` - Run complete pipeline
- `POST /api/automation/pipeline/quick-refresh` - Update scores only
- `POST /api/automation/pipeline/source/{name}` - Run single source
- `GET /api/automation/pipeline/status` - Get pipeline health

#### Automation
The daily automation job (`POST /api/automation/scheduled/daily`) now:
1. Fetches from all trend sources (TikTok, Amazon)
2. Merges supplier data (AliExpress, CJ)
3. Updates competitor intelligence
4. Updates ad activity signals
5. Recalculates all 5 component scores
6. Generates opportunity alerts (score ≥75)

### Store-Launch Platform
- ✅ Product-to-store workflow
- ✅ AI content generation (store names, taglines, descriptions)
- ✅ Branding style suggestions
- ✅ Pricing recommendations in GBP
- ✅ Store management dashboard
- ✅ Shopify-compatible JSON export with currency: "GBP"

### User Management
- ✅ Supabase authentication (configured)
- ✅ Demo mode fallback
- ✅ User data isolation
- ✅ Plan-based feature gating

## Early Trend Detection System

### Calculation Formula
```
early_trend_score = (
  view_growth_rate_score * 0.25 +
  engagement_rate_score * 0.20 +
  supplier_order_velocity_score * 0.20 +
  ad_activity_score * 0.20 +
  competition_score * 0.15 +
  stage_bonus
)
```

### Labels
| Score Range | Label | Icon |
|------------|-------|------|
| 85-100 | Exploding | 🔥 |
| 65-84 | Rising | 📈 |
| 45-64 | Early Trend | 🌱 |
| 0-44 | Stable | — |

### Dashboard Features
- Early Trend Opportunities section
- Early Score column in product listings
- Filter by early_trend_label
- Sort by early_trend_score
- Automatic early trend alerts

## API Endpoints

### Products
- GET /api/products - List products (supports early_trend_label filter)
- GET /api/products/{id} - Get product details

### Alerts
- Now includes early trend alerts (exploding_trend, rising_early_trend, early_trend_detected)

## Dashboard Design

### Simplified 3-Section Layout
1. **Winning Products Today** - Top products by win_score with "Build Store" buttons
2. **Early Trend Opportunities** - Products with exploding/rising momentum
3. **Your Stores** - User's created stores with status badges

### Win Score Calculation
```
win_score = (
  trend_score * 0.30 +
  early_trend_score * 0.30 +
  success_probability * 0.40
)
```

### Product Cards (Discover Page)
- Trend Score, Early Score, Success %, Est. Margin
- "X stores built" indicator
- Early trend badges
- Full-width "Build Store" button

## Landing Page

### Outcome-Focused Messaging
- Headline: "Launch your next winning ecommerce store in minutes"
- Badge: "Launch Stores in Minutes"
- CTA: "Start Building Free"
- Subtext: "No credit card required • Launch your first store today"

### Dashboard Preview
- Shows "Winning Products Today" section
- Stats: Winning Products, Avg Win Score, Stores Launched, Early Trends
- "Build Store" buttons on products

## Product Success Tracking System

### Calculation Formula
```
success_probability = (
  stores_created_score * 0.30 +
  exports_count_score * 0.20 +
  success_signals_score * 0.20 +
  trend_metrics_score * 0.15 +
  margin_score * 0.15
)
```

### Tracked Metrics
- **stores_created**: Number of stores built with this product
- **exports_count**: Number of Shopify exports
- **success_signals**: Estimated sales/conversion signals
- **user_engagement_score**: Combined user interaction score
- **proven_winner**: Boolean flag for high-performing products

### Proven Winner Criteria
- success_probability >= 70%
- stores_created >= 3
- exports_count >= 2 OR success_signals >= 10

### Dashboard Features
- "Proven Winning Products" section with aggregate stats
- Success Rate column in product listings
- "X stores built" indicator
- "✓ Proven Winner" badge

### API Endpoints
- GET /api/products/proven-winners/list - Get top performing products
- Automatic tracking on store creation and export

## Changelog

### March 2025
- Added Product Success Tracking system
- Added success_probability, stores_created, exports_count fields
- Added "Proven Winning Products" dashboard section
- Track store creation and exports automatically
- Added Early Trend Detection system
- Added early_trend_score and early_trend_label to Product model
- Added view_growth_rate, engagement_rate, supplier_order_velocity fields
- Added Early Trend Opportunities section to dashboard
- Added Early Trend filter to Discover page
- Added Early Trend Score column to product cards
- Updated alert generation for early trends
- Fixed Supabase "body stream already read" error
- Implemented GBP currency throughout the app

## Core Features (Implemented)

### Product Research Platform
- ✅ Product database with trend scoring
- ✅ TikTok views and ad count tracking
- ✅ Opportunity rating algorithm (low/medium/high/very high)
- ✅ Trend stage classification (early/rising/peak/saturated)
- ✅ AI-generated product summaries
- ✅ Alert generation for high-potential products
- ✅ Data ingestion from multiple sources (TikTok, Amazon, Suppliers)
- ✅ Admin panel for automation management

### Store-Launch Platform
- ✅ Product-to-store workflow
- ✅ AI content generation (store names, taglines, descriptions, bullet points)
- ✅ Branding style suggestions
- ✅ Pricing recommendations
- ✅ FAQ and policy generation
- ✅ Store management dashboard
- ✅ Plan-based store limits (starter: 1, pro: 5, elite: unlimited)
- ✅ Store status workflow (draft → ready → exported → published)
- ✅ Visual launch progress indicator
- ✅ Public store preview page with product images
- ✅ Shopify-compatible JSON export

### User Management
- ✅ Demo mode for testing without credentials
- ✅ User isolation (each user sees only their stores)
- ✅ Access control for update/delete operations
- ✅ Plan-based feature gating

## API Endpoints

### Products
- GET /api/products - List products with filters
- GET /api/products/{id} - Get product details
- POST /api/products - Create product
- PUT /api/products/{id} - Update product
- DELETE /api/products/{id} - Delete product

### Stores
- GET /api/stores?user_id= - List user's stores
- GET /api/stores/{id} - Get store details
- POST /api/stores - Create store
- POST /api/stores/generate - Generate store content
- PUT /api/stores/{id} - Update store
- DELETE /api/stores/{id} - Delete store
- PUT /api/stores/{id}/status - Update store status
- GET /api/stores/{id}/export - Export for Shopify
- GET /api/stores/{id}/preview - Get preview data

### Automation
- POST /api/automation/run - Run automation pipeline
- GET /api/automation/logs - Get automation logs
- GET /api/automation/stats - Get automation statistics
- POST /api/automation/scheduled/daily - Scheduled daily sync (protected)

### Shopify
- GET /api/shopify/status - Check integration status
- POST /api/shopify/connect/init - Start OAuth flow
- POST /api/shopify/connect/callback - Complete OAuth
- POST /api/shopify/publish/{store_id} - Direct publish

## Database Schema

### Collections
- `products` - Product data with trend scores
- `stores` - User stores with branding and content
- `store_products` - Products added to stores
- `trend_alerts` - Generated alerts
- `automation_logs` - Automation run history
- `subscriptions` - User subscription data
- `profiles` - User profiles

## Deployment Requirements

### Environment Variables (Backend)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
AUTOMATION_API_KEY=<secure-key-for-cron>
STRIPE_SECRET_KEY=<stripe-key>  # Optional
STRIPE_WEBHOOK_SECRET=<webhook-secret>  # Optional
SHOPIFY_API_KEY=<shopify-key>  # Optional
SHOPIFY_API_SECRET=<shopify-secret>  # Optional
```

### Environment Variables (Frontend)
```
REACT_APP_BACKEND_URL=<api-url>
REACT_APP_SUPABASE_URL=<supabase-url>
REACT_APP_SUPABASE_ANON_KEY=<supabase-anon-key>
```

### Cron Job Setup
Daily automation endpoint:
```
POST /api/automation/scheduled/daily
Header: X-API-Key: <AUTOMATION_API_KEY>
```

## Verification Status (March 2025)

### Verified Working
1. ✅ Product research dashboard with live data
2. ✅ Product filtering, sorting, and search
3. ✅ Trend scoring and opportunity rating
4. ✅ Alert generation and management
5. ✅ Store creation from products
6. ✅ AI content generation (rules-based)
7. ✅ Store management and status workflow
8. ✅ User isolation and access control
9. ✅ Plan-based store limits
10. ✅ Public store preview with images
11. ✅ Shopify-compatible JSON export
12. ✅ Scheduled automation endpoint (protected)
13. ✅ Demo mode authentication

### Requires Credentials
1. 🔑 Supabase - Live user authentication
2. 🔑 Shopify - Direct store publishing
3. 🔑 Stripe - Paid subscriptions

### Security Audit (December 2025) ✅
**Status:** COMPLETED - CRITICAL VULNERABILITY FIXED (March 2026)

**Previous Issue (FIXED):**
- API endpoints were accepting `user_id` from query parameters/request body, allowing any user to potentially access another user's data by manipulating the user_id parameter.

**Security Fix Implementation (March 2026):**
1. ✅ Created `/app/backend/auth.py` - JWT verification module for Supabase tokens
2. ✅ Refactored ALL protected endpoints to use `Depends(get_current_user)` 
3. ✅ User ID now extracted exclusively from JWT token (server-side validated)
4. ✅ Created `/app/frontend/src/lib/api.js` - Centralized API client with auth headers
5. ✅ Updated all frontend services to use authenticated API calls
6. ✅ Proper HTTP status codes: 401 (unauthenticated), 403 (unauthorized)

**Protected Endpoints (Refactored):**
- `GET/POST /api/stores` - User's stores
- `GET/PUT/DELETE /api/stores/{id}` - Store CRUD with ownership check
- `POST /api/stores/generate` - AI store generation
- `POST/PUT/DELETE /api/stores/{id}/products` - Store products
- `GET /api/stores/{id}/export` - Store export
- `PUT /api/stores/{id}/status` - Status updates
- `GET /api/viral/referral/stats` - Referral stats
- `GET /api/viral/referral/history` - Referral history
- `POST /api/stripe/*` - Stripe endpoints
- `GET/POST/DELETE /api/shopify/*` - Shopify integration

**Verification Tests Passed:**
1. ✅ Unauthenticated requests return 401
2. ✅ Demo mode authentication works (Bearer demo_{user_id})
3. ✅ Cross-user access blocked with 403
4. ✅ Old query param pattern rejected with 401
5. ✅ Public endpoints still accessible without auth

**Configuration Required for Production:**
- Add `SUPABASE_JWT_SECRET` to `/app/backend/.env`
- Get JWT secret from: Supabase Dashboard → Project Settings → API → JWT Secret

### Future Enhancements (Backlog)
- P0: Complete Viral Sharing Features (share buttons, social cards, referrals)
- P1: Connect live data sources (TikTok, Amazon scrapers)
- P2: Integrate real LLM for content generation
- P2: Implement live Stripe payments
- P3: Analytics dashboard with conversion tracking
