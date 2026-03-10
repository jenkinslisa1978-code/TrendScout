# ViralScout - Product Requirements Document

## Project Overview
ViralScout is a full-stack SaaS platform for product research and e-commerce store launching. Users can discover trending products, analyze opportunities, and build complete Shopify-ready stores with AI-generated content.

**Default Currency: GBP (£)**

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

## Core Features (Implemented)

### Product Research Platform
- ✅ Product database with trend scoring
- ✅ TikTok views and ad count tracking
- ✅ Opportunity rating algorithm (low/medium/high/very high)
- ✅ Trend stage classification (early/rising/peak/saturated)
- ✅ **Early Trend Detection System** (NEW)
  - early_trend_score (0-100)
  - Labels: 🔥 Exploding, 📈 Rising, 🌱 Early Trend, Stable
  - Signals: view growth velocity, engagement rate, supplier orders, ad activity, competition
  - Automatic alert generation for high early_trend_score
- ✅ AI-generated product summaries
- ✅ Alert generation for high-potential products
- ✅ Data ingestion from multiple sources

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

### Future Enhancements (Backlog)
- P1: Connect live data sources (TikTok, Amazon scrapers)
- P2: Integrate real LLM for content generation
- P2: Implement live Stripe payments
- P3: Analytics dashboard with conversion tracking
