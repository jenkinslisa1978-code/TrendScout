# TrendScout Changelog

## March 19, 2026 - Free Trial Mechanic + Pexels API
- Built 24-hour free trial system: free users pick ONE premium feature to unlock (5 options)
- Trial banner on dashboard (eligible/active/expired states), inline "Try free" on locked overlays
- Rate limits fixed: free=120/min, core endpoints exempted from rate limiting
- Pexels API key configured for admin image refresh tool
- All verified: 100% backend + frontend — iteration_97


## March 19, 2026 - Free Plan Content Gating
- Implemented blurred preview + upgrade CTAs across: Ad Intelligence (2 free), TikTok Intel (5 free), Profit Sim (2 free), Competitor Intel (1 free), Product Detail (7 sections locked)
- Similar Products limited to 3 for free, 6 for paid
- All verified: 100% backend + frontend — iteration_96


## March 19, 2026 - Score Fix, Similar Products & Data Freshness
- Fixed score inconsistency: intelligence API now uses authoritative `launch_score` from DB (was showing 72 vs 42)
- Added Similar Products section on product detail pages (6 related products by category/price)
- Added Data Freshness indicators: source badges, "Updated Xm ago", freshness card, and summary API
- Added freshness indicator on Discover page product cards
- All verified: 100% backend (13/13), 100% frontend (7/7) — iteration_95

## March 19, 2026 - Product Image Quality Fix (P0)
- Replaced all 26 mismatched Unsplash product images with AI-generated, product-accurate images
- Products affected: LED Sunset Lamp, Cloud Pillow Slides, Neck Fan, Ice Roller, Galaxy Projector, Scalp Massager, Mini Projector, MagSafe Mount, Desk Organizer, ANC Earbuds, Posture Corrector, Pet Hair Remover, Blender Cup, RGB LED Strips, Heated Lunch Box, Wireless Charging Pad, Smart Water Bottle, Thermal Printer, Sleep Mask, Laptop Stand, Milk Frother, Storage Bins, Ceramic Coating Spray, Yoga Wheels, Magnetic Spice Jars, Self-Watering Pots
- Zero Unsplash URLs remaining in database (verified via testing agent iteration_94)
- All 179 products now have contextually accurate images


## March 13, 2026 - Production Launch Readiness
- **Fixed pricing alignment**: Frontend updated from incorrect Growth £49/Pro £99 to match backend Starter £19/Pro £39/Elite £79
- Updated PricingPage.jsx: plan IDs, names, prices, feature comparison table
- Updated LandingPage.jsx: pricing cards section
- Updated subscriptionService.js: added starter plan, fixed elite price from £99 to £79
- Updated accessControlService.js: added starter to PERMISSION_MAP and planOrder
- Full test suite passed: 19/19 backend, 13/13 frontend checks
- Safety audit: no hardcoded secrets in frontend, all env vars properly managed

## March 2026 - Launch Hardening
- Added favicon, apple-touch-icon, OG meta tags
- Implemented API rate limiting (slowapi)
- Created 404 page, Terms of Service, Privacy Policy
- Added site footer with legal links
- Production cleanup (removed backup files)

## March 2026 - Backend Modularization
- Refactored 10,754-line monolithic server.py into 30 route files + 6 common modules
- server.py reduced to 178-line slim entrypoint
- 41/41 regression tests passed

## March 2026 - Product Detail Enhancements
- Interactive Trend Timeline with recharts
- Upgraded Saturation Meter visualization
- Pre-filled Profit Calculator

## March 2026 - Advanced Discovery
- Advanced product discovery filters (competition, trend score, price range)
- Image resolution pipeline (backend logic, scheduled tasks, API endpoints)

## Feb-March 2026 - Full 30-Part Spec Implementation
- All 30 features from original spec implemented and tested
