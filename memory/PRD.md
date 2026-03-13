# TrendScout - Product Requirements Document

## Positioning
**TrendScout — The Early Trend Intelligence Platform for Ecommerce**
"Discover winning products before they go viral."

## Tech Stack
- Frontend: React, TailwindCSS, Shadcn/UI, react-helmet-async
- Backend: FastAPI, MongoDB, APScheduler, aiohttp
- Auth: Custom JWT | Payments: Stripe (GBP, live) | Email: Resend
- LLM: Emergent LLM Key via emergentintegrations

## Completed Phases

### Phase 1-32: Foundation through Live API Integrations (DONE)

### Phase 33: Production Readiness (DONE - March 2026)
- Hardcoded URLs removed, SITE_URL env var, dynamic sitemap/robots.txt

### Phase 34: Landing Page Repositioning & Product Discovery (DONE - March 2026)
- **Landing Page Rewrite**: New "Early Trend Intelligence" positioning, hero with "Discover Winning Products Before They Go Viral", How It Works (3 steps), Winning Products (live API data), Built For (4 audiences), Pricing (4 tiers), Testimonials (3), Social Proof bar, Final CTA
- **Enhanced Trending Products Page**: Category filter pills (22), sort dropdown (5 options: Score/Growth/Margin/Newest/Cost), margin filter panel (Any/30%/50%/60%/70%+), enhanced product cards with confidence score badges (High Confidence/Emerging/Experimental), stage badges, supplier cost, retail price, margin %, growth rate
- **Backend**: Public API now returns supplier_cost, retail_price, growth_rate, tiktok_views, detected_at
- **Verified**: iteration_46 — 100% pass (17/17 backend, all frontend)

## Upcoming Tasks (Phase C — Viral & Upgrade Features)
- Daily Winning Product Feed on dashboard
- Viral product leaderboard on public page
- Free user unlock limits (3/day) with upgrade prompts
- Enhanced shareable product pages with trend graphs

## Future Phases
- **Phase D**: Shopify Store Analyzer (paste URL → analyze)
- **Phase E**: Competitor Store Tracker, TikTok Ad Intelligence
- **Phase F**: Chrome Extension architecture
- **Phase G**: Creator spotlight, community features
- Server.py refactoring (when needed)

## Integration Status
| Source | Status | Mode |
|--------|--------|------|
| CJ Dropshipping | LIVE | api |
| TikTok | LIVE | scraper |
| Meta Ad Library | Configured | estimation (awaiting permission) |
| Zendrop | Wired | estimation |
| AliExpress | Not configured | estimation |
