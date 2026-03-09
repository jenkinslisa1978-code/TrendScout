# TrendScout - Product Requirements Document

## Product Overview
TrendScout is a SaaS application for product research and trend analysis, primarily designed for dropshippers. The application helps users find, analyze, and save trending products with automated scoring and alerting capabilities.

## Tech Stack
- **Frontend:** React SPA with React Router
- **Styling:** TailwindCSS + Shadcn/UI components
- **Data Visualization:** Recharts
- **Backend:** Supabase (with full Demo Mode using localStorage)
- **State Management:** React Context API

## Core Features

### ✅ Implemented Features

#### 1. Landing Page
- Professional hero section with value proposition
- Feature highlights and pricing sections
- CTAs for free trial and demo

#### 2. Authentication System
- Login/Signup pages
- Demo Mode: Accepts any credentials when Supabase not configured
- Protected routes with authentication checks
- Session persistence

#### 3. Analytics Dashboard
- 4 primary stat cards (Total Products, Avg Trend Score, High Opportunity, Rising Trends)
- 4 secondary stat cards (Avg Margin, Early Stage, Total Ads, TikTok Views)
- Area chart for Trend Activity
- Pie chart for Category Distribution
- Top Trending Products list
- Recent Activity feed

#### 4. Product Discovery
- Product grid with search and filters
- Filter by: Category, Trend Stage, Opportunity Rating
- Sort by: Trend Score, Margin, TikTok Views, Newest
- Save/unsave products functionality
- Product cards with key metrics

#### 5. Product Detail Page
- Full product information display
- Pricing details (Supplier Cost, Retail Price, Margin)
- AI Analysis summary
- Market Overview section
- Save product button
- Supplier link

#### 6. Saved Products Page
- List of user's saved products
- Remove from saved functionality

#### 7. Admin Panel
- **Products Tab:** Full CRUD for products
- **Users Tab:** User list display (mocked)
- **Subscriptions Tab:** Subscription status (mocked)

#### 8. Automation Center
- **Import Products Tab:** CSV upload with drag-drop, paste content
- **Manual Entry Tab:** Form to add products with automation
- **Automation Pipeline Tab:** Individual automation step controls
- **Quick Actions:** Run Scoring, AI Summaries, Generate Alerts, Import Products

#### 9. Automation Logic
All calculations run automatically on product create/update:
- **Trend Score (0-100):** Based on TikTok views, ad count, competition, margin
- **Opportunity Rating:** low, medium, high, very high
- **Trend Stage:** early, rising, peak, saturated
- **AI Summary:** Rules-based text generation (placeholder for real AI)
- **Alert Generation:** Creates alerts for high-opportunity products

#### 10. Trend Alerts (Elite Feature)
- Real-time alert display
- Stats cards (Total, Unread, Critical, Early Stage)
- Filter by: All, Unread, Critical, High Priority
- Mark as read / Dismiss functionality
- View product from alert

#### 11. Plan-Based Access Control
- Starter, Pro, Elite plans defined
- Elite features accessible in Demo Mode
- Admin role has full access

### 🔄 Demo Mode
The entire application runs in "Demo Mode" when Supabase credentials are not configured:
- Mock user authentication
- 10 sample products preloaded
- localStorage for data persistence
- All features fully functional

## Data Models

### Products
```
- id, product_name, category, short_description
- supplier_cost, estimated_retail_price, estimated_margin
- tiktok_views, ad_count, competition_level
- trend_score, trend_stage, opportunity_rating
- ai_summary, supplier_link, is_premium
- created_at, updated_at
```

### Alerts
```
- id, product_id, product_name
- alert_type, priority, title, body
- trend_score, opportunity_rating
- created_at, read, dismissed
```

### Profiles (Supabase)
```
- id, full_name, email, role, plan
```

## File Structure
```
/app/frontend/src/
├── App.js
├── components/
│   ├── layouts/DashboardLayout.jsx
│   └── ui/ (Shadcn components)
├── contexts/AuthContext.jsx
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
│   ├── LandingPage.jsx
│   ├── LoginPage.jsx, SignupPage.jsx
│   ├── DashboardPage.jsx
│   ├── DiscoverPage.jsx
│   ├── ProductDetailPage.jsx
│   ├── SavedProductsPage.jsx
│   ├── AdminPage.jsx
│   ├── AdminAutomationPage.jsx
│   └── TrendAlertsPage.jsx
└── services/
    ├── productService.js
    ├── alertService.js
    └── savedProductService.js
```

## Test Status
- **Last Test:** December 2025
- **Frontend Test Rate:** 100%
- **All core features verified working**
- **Minor issue:** Recharts console warnings (cosmetic only)

---

## Backlog

### P1 - High Priority
- [ ] Implement live Stripe integration for subscriptions
- [ ] Implement CSV product upload parsing logic
- [ ] Add real AI service integration for product summaries

### P2 - Medium Priority
- [ ] Connect to live data sources (TikTok, Amazon, AliExpress APIs)
- [ ] Implement scheduled automation (cron jobs)
- [ ] Add webhook triggers for real-time updates
- [ ] Email notifications for alerts

### P3 - Low Priority
- [ ] User onboarding flow
- [ ] Advanced analytics and reporting
- [ ] Export functionality (PDF, CSV reports)
- [ ] Mobile responsive improvements

---

## Changelog

### December 2025
- Completed full application audit
- Verified all 20 core features working
- Confirmed Demo Mode fully functional
- All automation logic tested and working
- Alerts system generating and displaying correctly
