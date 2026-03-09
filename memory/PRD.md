# TrendScout - Product Research Platform PRD

## Project Overview
TrendScout is a SaaS platform for dropshippers to discover trending products before they go viral. The application helps users analyze market trends, competition levels, and profit margins.

## Original Problem Statement
Build a full-stack web app for a trending product research platform using the provided Supabase schema (profiles, products, saved_products, subscriptions, trend_alerts). Features include landing page, authentication, dashboard, product discovery with filters, product details with AI analysis, saved products, and admin panel.

## Architecture
- **Frontend**: React 19 with React Router, Tailwind CSS, Shadcn/UI components
- **Backend**: Supabase (PostgreSQL + Auth + Row Level Security)
- **Demo Mode**: Mock data when Supabase credentials not configured
- **State Management**: React Context for Auth, localStorage for saved products (demo mode)

## User Personas
1. **Dropshipping Beginner** - Starter plan, exploring product research
2. **Scaling Dropshipper** - Pro plan, needs AI insights and supplier links
3. **Agency/Power Seller** - Elite plan, requires API access and team features
4. **Admin** - Platform managers who add/edit products

## Core Requirements (Static)
- [x] Landing page with hero, features, pricing (£19/£49/£99)
- [x] User authentication (signup/login/logout)
- [x] Dashboard with stats and top products
- [x] Product discovery with filters (category, stage, opportunity, sort)
- [x] Product detail with pricing, AI analysis, market overview
- [x] Saved products functionality
- [x] Admin panel (products, users, subscriptions tabs)
- [x] Responsive design with modern SaaS aesthetic
- [x] Demo mode when Supabase not configured

## What's Been Implemented (Jan 2026)

### Automation Architecture (Latest)
Complete automation-ready infrastructure:

**Automation Modules** (`/frontend/src/lib/automation/`):
- `trend-score.js` - Rules-based trend score calculation (0-100) using TikTok views, ad count, competition, margin
- `opportunity-score.js` - Opportunity rating calculation (low/medium/high/very high) with weighted factors
- `trend-stage.js` - Automatic stage classification (early/rising/peak/saturated) based on signals
- `ai-summary.js` - Template-based AI summary generation (OpenAI API placeholder ready)
- `alerts.js` - Alert generation for high-opportunity products (trend score ≥75, high/very high opportunity)
- `product-import.js` - CSV parser with column mapping and batch processing
- `index.js` - Central exports with `runFullAutomation()` and `batchRunAutomation()`

**New Pages**:
- `AdminAutomationPage.jsx` - Import products (CSV/manual), run automation pipelines
- `TrendAlertsPage.jsx` - Real-time alerts for Elite users with stats and filtering

**New Services**:
- `alertService.js` - Alert CRUD with localStorage persistence for demo mode

**Updated Components**:
- Sidebar with Elite section (Trend Alerts with badge) and Admin section (Admin Panel, Automation)
- Product creation/update auto-triggers full automation pipeline

### Dashboard Enhancements (Previous)
- **Stats Cards with Trends**: Show % change vs last period with up/down indicators
- **Trend Activity Chart**: Interactive area chart showing products & opportunities over time
- **Category Distribution**: Donut chart showing product distribution by category
- **Secondary Stats Bar**: Avg Margin, Early Stage count, Total Ads Tracked, TikTok Views
- **Enhanced Product Table**: Numbered rankings, margin display, hover effects
- **Activity Feed**: Real-time activity showing new products, trend changes, warnings
- **Quick Actions CTA**: Prominent call-to-action at bottom
- **Time Range Selector**: Filter dashboard data by 24h, 7d, 30d, 90d

### Pages Created
1. **LandingPage.jsx** - Hero, features grid, pricing cards, CTA sections
2. **LoginPage.jsx** - Split layout, demo mode banner, form with validation
3. **SignupPage.jsx** - Split layout with feature list, form with validation
4. **DashboardPage.jsx** - Stats cards, TikTok views banner, top products table
5. **DiscoverPage.jsx** - Product grid, search bar, filter dropdowns, save toggle
6. **ProductDetailPage.jsx** - Full product info, pricing details, AI analysis, market overview
7. **SavedProductsPage.jsx** - Saved products grid, remove functionality
8. **AdminPage.jsx** - Tabs for products/users/subscriptions, product form dialog

### Components Created
- **DashboardLayout.jsx** - Sidebar navigation, user profile section
- **LandingLayout.jsx** - Sticky header, footer, mobile menu

### Services Created
- **productService.js** - CRUD operations with mock data fallback
- **savedProductService.js** - Save/unsave with localStorage persistence

### Context Created
- **AuthContext.jsx** - Auth state, demo mode detection, user profile

## Prioritized Backlog

### P0 - Critical (Next)
- [ ] Connect real Supabase credentials
- [ ] Implement Stripe checkout for subscriptions
- [ ] Add OpenAI API key for real AI summaries

### P1 - High Priority
- [ ] TikTok Creative Center API integration for auto-import
- [ ] Amazon/AliExpress API for supplier data
- [ ] Scheduled cron jobs for automated scoring (Supabase Edge Functions)
- [ ] Email/push notifications for critical alerts
- [ ] Product image uploads

### P2 - Medium Priority
- [ ] User settings page
- [ ] Plan upgrade flow
- [ ] API access for Elite
- [ ] Team collaboration features
- [ ] Product scraping automation

### P3 - Nice to Have
- [ ] Dark mode toggle
- [ ] Analytics dashboard
- [ ] White-label reports
- [ ] Mobile app (React Native)

## Tech Stack
- React 19.0.0
- React Router DOM 7.5.1
- Tailwind CSS 3.4.17
- Shadcn/UI components
- Supabase JS 2.99.0
- Framer Motion 12.35.2
- Recharts 3.6.0
- Lucide React icons
- Sonner for toasts

## Environment Variables Required
```
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_anon_key
```

## Next Tasks
1. Add Supabase credentials to enable real database
2. Implement Stripe checkout for subscription management
3. Add product image upload to Supabase storage
4. Create email templates for verification and notifications
