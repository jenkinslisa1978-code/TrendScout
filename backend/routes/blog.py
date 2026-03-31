from fastapi import APIRouter, HTTPException, Request, Depends, Header, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import uuid
import json
import logging
import re

from auth import get_current_user, get_optional_user, AuthenticatedUser
from common.database import db
from common.cache import get_cached, set_cached, slugify, get_margin_range
from common.helpers import (
    get_user_plan, require_plan, require_admin, build_winning_reasons,
    track_product_store_created, track_product_exported, run_automation_on_products,
)
from common.scoring import (
    calculate_trend_score, calculate_trend_stage, calculate_opportunity_rating,
    generate_ai_summary, calculate_early_trend_score, calculate_market_score,
    calculate_launch_score, generate_mock_competitor_data, calculate_success_probability,
    should_generate_alert, generate_alert, run_full_automation, generate_early_trend_alert,
    should_generate_early_trend_alert,
)
from common.models import *

blog_router = APIRouter(prefix="/api/blog")

@blog_router.get("/posts")
async def list_blog_posts(limit: int = 20):
    """List published blog posts, newest first."""
    cached = get_cached("blog_posts_list")
    if cached:
        return cached

    posts = await db.blog_posts.find(
        {"status": "published"},
        {"_id": 0, "content": 0}
    ).sort("published_at", -1).limit(limit).to_list(limit)

    result = {"posts": posts, "count": len(posts)}
    set_cached("blog_posts_list", result)
    return result


@blog_router.get("/posts/{slug}")
async def get_blog_post(slug: str):
    """Get a single blog post by slug."""
    post = await db.blog_posts.find_one({"slug": slug, "status": "published"}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post


@blog_router.post("/generate/{category_slug}")
async def generate_blog_post(
    category_slug: str,
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Admin: Generate an AI blog post for a product category."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    background_tasks.add_task(_generate_blog_post, category_slug)
    return {"status": "generating", "category": category_slug}


async def _generate_blog_post(category_slug: str):
    """Background task: Generate a blog post for a category."""
    # Find the category
    category_name = category_slug.replace("-", " ").title()

    # Get top products in this category
    products = await db.products.find(
        {"category": {"$regex": category_name, "$options": "i"}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(5).to_list(5)

    if not products:
        # Try broader match
        products = await db.products.find(
            {"category": {"$regex": category_slug.split("-")[0], "$options": "i"}},
            {"_id": 0}
        ).sort("launch_score", -1).limit(5).to_list(5)

    if not products:
        logging.warning(f"No products found for category: {category_name}")
        return

    # Build product context
    product_list = []
    for p in products:
        margin = p.get("estimated_margin", 0)
        retail = p.get("estimated_retail_price", 1)
        margin_pct = int((margin / retail) * 100) if retail > 0 else 0
        product_list.append(
            f"- {p.get('product_name','?')} | Score: {p.get('launch_score',0)}/100 | "
            f"Margin: {margin_pct}% | TikTok Views: {p.get('tiktok_views',0):,} | "
            f"Stage: {p.get('trend_stage') or p.get('early_trend_label','Unknown')}"
        )
    products_text = "\n".join(product_list)

    try:
        from openai import AsyncOpenAI
        llm_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        if not llm_key:
            return
        _blog_client = AsyncOpenAI(api_key=llm_key)

        today = datetime.now(timezone.utc).strftime("%B %d, %Y")
        prompt = f"""Write a blog article titled "Top Trending {category_name} Products This Week" for ecommerce entrepreneurs.

Date: {today}
Category: {category_name}

Top products data:
{products_text}

Write in this JSON format (raw JSON, no markdown):
{{
  "title": "Top Trending {category_name} Products This Week — {today}",
  "meta_description": "SEO meta description under 160 chars targeting keywords like trending {category_name.lower()} products, winning dropshipping products",
  "intro": "2-3 sentence engaging intro paragraph",
  "sections": [
    {{
      "heading": "section heading",
      "content": "2-4 paragraph section with analysis and insights. Use markdown for bold and lists."
    }}
  ],
  "product_highlights": [
    {{
      "name": "product name exactly as given",
      "why_trending": "1 sentence reason",
      "opportunity": "1 sentence seller opportunity"
    }}
  ],
  "conclusion": "closing paragraph with CTA",
  "tags": ["tag1", "tag2", "tag3"]
}}

Include sections for: Market Overview, Top Products Analysis, Seller Opportunities, Tips for Launching. Be specific and actionable."""

        _blog_completion = await _blog_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are TrendScout's content strategist. Write engaging, SEO-optimized blog articles about trending ecommerce products. Use British English. Be data-driven and practical."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        response = _blog_completion.choices[0].message.content

        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if not json_match:
            logging.error("Blog generation: could not parse response")
            return
        article = json.loads(json_match.group())

    except Exception as e:
        logging.error(f"Blog generation error: {e}")
        return

    # Build embedded products
    embedded_products = []
    for p in products:
        margin = p.get("estimated_margin", 0)
        retail = p.get("estimated_retail_price", 1)
        margin_pct = int((margin / retail) * 100) if retail > 0 else 0
        embedded_products.append({
            "id": p.get("id"),
            "slug": slugify(p.get("product_name", "")),
            "product_name": p.get("product_name", "Unknown"),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "margin_percent": margin_pct,
            "trend_stage": p.get("trend_stage") or p.get("early_trend_label", "Unknown"),
        })

    slug = slugify(article.get("title", f"trending-{category_slug}-products"))
    # Ensure unique slug
    existing = await db.blog_posts.find_one({"slug": slug})
    if existing:
        slug = f"{slug}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

    post_doc = {
        "id": str(uuid.uuid4()),
        "slug": slug,
        "title": article.get("title", f"Trending {category_name} Products"),
        "meta_description": article.get("meta_description", ""),
        "category": category_name,
        "category_slug": category_slug,
        "content": {
            "intro": article.get("intro", ""),
            "sections": article.get("sections", []),
            "product_highlights": article.get("product_highlights", []),
            "conclusion": article.get("conclusion", ""),
        },
        "tags": article.get("tags", []),
        "products": embedded_products,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ai_generated": True,
    }

    await db.blog_posts.insert_one(post_doc)
    post_doc.pop("_id", None)
    logging.info(f"Blog post generated: {post_doc['title']}")

    # Clear cache
    set_cached("blog_posts_list", None)


@blog_router.post("/generate-all")
async def generate_all_blog_posts(
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Admin: Generate blog posts for top categories."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    # Get top categories
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_score": {"$avg": "$launch_score"}}},
        {"$match": {"count": {"$gte": 3}}},
        {"$sort": {"avg_score": -1}},
        {"$limit": 8},
    ]
    categories = await db.products.aggregate(pipeline).to_list(8)

    for cat in categories:
        cat_name = cat["_id"]
        if not cat_name:
            continue
        cat_slug = slugify(cat_name)
        background_tasks.add_task(_generate_blog_post, cat_slug)

    return {"status": "generating", "categories": len(categories)}


# =====================
# ADMIN IMAGE REVIEW
# =====================

image_review_router = APIRouter(prefix="/api/admin/image-review")


async def require_admin(current_user: AuthenticatedUser):
    profile = await db.profiles.find_one({"email": current_user.email})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")




# ═══════════════════════════════════════════════════════════════════
# Weekly SEO Digest — Auto-generated trending product roundups
# ═══════════════════════════════════════════════════════════════════

digest_router = APIRouter(prefix="/api/digest")


@digest_router.get("/latest")
async def get_latest_digest():
    """Get the most recent weekly digest (public)."""
    digest = await db.weekly_digests.find_one(
        {"status": "published"}, {"_id": 0}
    , sort=[("published_at", -1)])
    if not digest:
        raise HTTPException(status_code=404, detail="No digests published yet")
    return digest


@digest_router.get("/archive")
async def get_digest_archive(limit: int = 12):
    """Get past weekly digests (public)."""
    digests = await db.weekly_digests.find(
        {"status": "published"},
        {"_id": 0, "products": 0}
    ).sort("published_at", -1).limit(min(limit, 24)).to_list(min(limit, 24))
    return {"digests": digests, "total": len(digests)}


@digest_router.get("/subscriber-count")
async def get_subscriber_count():
    """Public: Get active subscriber count for social proof."""
    count = await db.digest_subscribers.count_documents({"active": True})
    return {"count": count}


@digest_router.get("/subscribers")
async def get_digest_subscribers(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Admin: Get subscriber list and count."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    active_count = await db.digest_subscribers.count_documents({"active": True})
    total_count = await db.digest_subscribers.count_documents({})
    recent = await db.digest_subscribers.find(
        {"active": True}, {"_id": 0}
    ).sort("subscribed_at", -1).limit(20).to_list(20)

    return {"active_count": active_count, "total_count": total_count, "recent": recent}


@digest_router.get("/{digest_id}")
async def get_digest_by_id(digest_id: str):
    """Get a specific digest by ID (public)."""
    digest = await db.weekly_digests.find_one(
        {"id": digest_id, "status": "published"}, {"_id": 0}
    )
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    return digest


@digest_router.post("/generate")
async def generate_weekly_digest(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Admin: Generate a new weekly digest from top rising products."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    # Get top 5 rising products (high score + recent activity)
    products = await db.products.find(
        {"launch_score": {"$gte": 50}},
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "launch_score": 1,
         "trend_stage": 1, "image_url": 1, "ai_summary": 1, "tiktok_views": 1,
         "competition_level": 1, "estimated_retail_price": 1, "engagement_rate": 1,
         "slug": 1, "verified_winner": 1}
    ).sort("launch_score", -1).limit(20).to_list(20)

    # Pick top 5 with diversity (different categories preferred)
    seen_cats = set()
    top5 = []
    for p in products:
        cat = p.get("category", "")
        if cat not in seen_cats or len(top5) < 3:
            top5.append(p)
            seen_cats.add(cat)
        if len(top5) >= 5:
            break
    # Fill remaining if needed
    for p in products:
        if len(top5) >= 5:
            break
        if p not in top5:
            top5.append(p)

    if not top5:
        raise HTTPException(status_code=400, detail="Not enough products to generate digest")

    # Add slugs
    for p in top5:
        if not p.get("slug"):
            p["slug"] = slugify(p.get("product_name", ""))

    now = datetime.now(timezone.utc)
    week_label = now.strftime("Week of %B %d, %Y")

    # Build digest
    avg_score = round(sum(p.get("launch_score", 0) for p in top5) / len(top5), 1)
    categories_featured = list(set(p.get("category", "") for p in top5 if p.get("category")))

    # Generate intro text
    intro = (
        f"This week's top trending products for dropshipping, scored by our AI-powered 7-signal analysis. "
        f"Average launch score: {avg_score}/100 across {len(categories_featured)} categories. "
        f"These products show strong signals in ad activity, search growth, and social buzz."
    )

    # Generate per-product insights
    enriched = []
    for i, p in enumerate(top5):
        insight = []
        if p.get("tiktok_views", 0) > 100000:
            insight.append(f"Strong TikTok presence with {p['tiktok_views']:,} views")
        if p.get("competition_level") in ("low", "medium"):
            insight.append(f"{p['competition_level'].capitalize()} competition — good entry window")
        if p.get("engagement_rate", 0) > 0.05:
            insight.append(f"High engagement rate ({p['engagement_rate']*100:.1f}%)")
        if p.get("trend_stage") == "emerging":
            insight.append("Emerging trend — early mover advantage")
        if p.get("verified_winner"):
            insight.append("Community-verified winner")

        enriched.append({
            **p,
            "rank": i + 1,
            "insight": " | ".join(insight) if insight else f"Launch score: {p.get('launch_score', 0)}/100",
        })

    digest = {
        "id": str(uuid.uuid4()),
        "title": f"Top 5 Trending Products — {week_label}",
        "slug": slugify(f"top-5-trending-products-{now.strftime('%Y-%m-%d')}"),
        "week_label": week_label,
        "intro": intro,
        "products": enriched,
        "avg_score": avg_score,
        "categories_featured": categories_featured,
        "product_count": len(enriched),
        "status": "published",
        "published_at": now.isoformat(),
        "seo": {
            "title": f"Top 5 Trending Dropshipping Products — {week_label} | TrendScout",
            "description": f"AI-scored trending products for {week_label}. Average launch score: {avg_score}/100. Discover the best dropshipping opportunities this week.",
            "og_image": enriched[0].get("image_url", "") if enriched else "",
        },
    }

    await db.weekly_digests.insert_one(digest)
    digest.pop("_id", None)
    return {"digest": digest}


# ── Digest Email Subscription ──────────────────────────────────

@digest_router.post("/subscribe")
async def subscribe_to_digest(request: Request):
    """Subscribe an email to the weekly digest (public)."""
    body = await request.json()
    email = (body.get("email") or "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")

    existing = await db.digest_subscribers.find_one({"email": email})
    if existing:
        if existing.get("active"):
            return {"subscribed": True, "message": "Already subscribed"}
        # Reactivate
        await db.digest_subscribers.update_one(
            {"email": email},
            {"$set": {"active": True, "resubscribed_at": datetime.now(timezone.utc).isoformat()}},
        )
        return {"subscribed": True, "message": "Re-subscribed successfully"}

    doc = {
        "id": str(uuid.uuid4()),
        "email": email,
        "active": True,
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.digest_subscribers.insert_one(doc)
    doc.pop("_id", None)
    return {"subscribed": True, "message": "Subscribed! You'll get the weekly digest every Monday."}


@digest_router.post("/unsubscribe")
async def unsubscribe_from_digest(request: Request):
    """Unsubscribe from the weekly digest."""
    body = await request.json()
    email = (body.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    result = await db.digest_subscribers.update_one(
        {"email": email},
        {"$set": {"active": False, "unsubscribed_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"unsubscribed": result.matched_count > 0}


routers = [blog_router, digest_router]



@blog_router.post("/seed")
async def seed_blog_articles():
    """Seed starter blog articles. Skips articles that already exist by slug."""
    seeded = 0
    now = datetime.now(timezone.utc)

    for i, article in enumerate(SEED_ARTICLES):
        exists = await db.blog_posts.find_one({"slug": article["slug"]})
        if exists:
            continue
        doc = {
            "id": str(uuid.uuid4()),
            "slug": article["slug"],
            "title": article["title"],
            "meta_description": article["meta_description"],
            "category": article["category"],
            "category_slug": slugify(article["category"]),
            "content": article["content"],
            "tags": article["tags"],
            "products": [],
            "status": "published",
            "published_at": (now - timedelta(days=(len(SEED_ARTICLES) - i) * 3)).isoformat(),
            "created_at": now.isoformat(),
            "ai_generated": False,
        }
        try:
            await db.blog_posts.insert_one(doc)
            seeded += 1
        except Exception:
            pass

    set_cached("blog_posts_list", None)
    return {"status": "ok", "seeded": seeded}


# ── Blog Seed Articles ──────────────────────────────────────
SEED_ARTICLES = [
    {
        "title": "How to Validate a Product Idea Before Spending a Penny",
        "slug": "how-to-validate-product-idea-uk",
        "meta_description": "Learn the 7-step framework UK ecommerce sellers use to validate product ideas before investing. Avoid costly mistakes with data-driven research.",
        "category": "Guides",
        "tags": ["product-validation", "uk-ecommerce", "dropshipping", "beginners"],
        "content": {
            "intro": "Every successful UK ecommerce seller knows that the difference between a winning product and a money pit comes down to validation. Before you spend on stock, ads, or suppliers, here is a proven framework to test whether your product idea has real potential in the UK market.",
            "sections": [
                {
                    "heading": "Why Most Product Ideas Fail",
                    "content": "Research from the British Retail Consortium shows that over 60% of new product launches underperform expectations. The common thread? Sellers rely on gut feeling instead of data.\n\nThe UK market has unique characteristics — VAT at 20%, higher shipping costs, different seasonal patterns, and a customer base that values quality over rock-bottom pricing. What works on Amazon.com does not automatically translate to Amazon.co.uk or Shopify stores targeting UK buyers."
                },
                {
                    "heading": "The 7-Signal Validation Framework",
                    "content": "At TrendScout, we score every product across 7 key signals:\n\n1. **Demand Signal** — Is there growing search volume and social buzz?\n2. **Competition Level** — How saturated is the market?\n3. **Margin Potential** — Can you make 30%+ after VAT, shipping, and returns?\n4. **Trend Direction** — Is this emerging, peaking, or declining?\n5. **Supplier Availability** — Can you source reliably with good MOQs?\n6. **Ad Viability** — Is the CPA reasonable for this product type?\n7. **UK Market Fit** — Does this product resonate with UK buyers specifically?\n\nA product needs to score well on at least 5 of these 7 signals to be worth pursuing."
                },
                {
                    "heading": "Free Tools to Start Validating Today",
                    "content": "You do not need a paid subscription to begin. Our free tools can help:\n\n- **Profit Margin Calculator** — Factor in UK VAT, shipping, and platform fees\n- **ROAS Calculator** — Check if your ad spend makes sense\n- **UK VAT Calculator** — Understand your real costs\n- **Product Pricing Tool** — Find the right price point for UK buyers\n\nThese give you a solid starting point before committing to deeper research."
                },
                {
                    "heading": "What Separates Winners from the Rest",
                    "content": "After analysing thousands of UK product launches, the pattern is clear: winners validate with data, losers follow hype.\n\nThe best sellers spend 2-3 weeks researching before placing a single order. They check competitor reviews for gaps, test ad creatives with small budgets, and calculate their true margin including returns (which average 15-20% for UK ecommerce).\n\nIf you want to see what a thorough product analysis looks like, check our sample product report — it shows exactly the kind of data you should gather before committing to any product."
                }
            ],
            "product_highlights": [],
            "conclusion": "Product validation is not glamorous, but it is the single highest-ROI activity for any ecommerce seller. Start with our free calculators, review the sample analysis to understand what good research looks like, and only commit money when the data supports your decision."
        },
    },
    {
        "title": "UK VAT for Ecommerce Sellers: The Complete 2026 Guide",
        "slug": "uk-vat-ecommerce-sellers-guide-2026",
        "meta_description": "Everything UK ecommerce sellers need to know about VAT in 2026. Registration thresholds, rates, margin calculation, and common mistakes to avoid.",
        "category": "Guides",
        "tags": ["vat", "uk-tax", "ecommerce", "dropshipping", "margins"],
        "content": {
            "intro": "VAT is the single biggest factor that separates UK ecommerce profitability from US numbers. If you are running — or planning to run — an online store in the UK, understanding VAT is not optional. Here is everything you need to know for 2026.",
            "sections": [
                {
                    "heading": "VAT Registration: When and Why",
                    "content": "You must register for VAT when your taxable turnover exceeds the threshold (currently around 90,000 pounds). However, many sellers register voluntarily before hitting this threshold because:\n\n- You can reclaim VAT on business purchases\n- It looks more professional to B2B buyers\n- Some platforms require it\n\nThe key decision is whether the administrative overhead is worth the benefits at your current stage."
                },
                {
                    "heading": "How VAT Affects Your Real Margins",
                    "content": "Here is where most new sellers get caught out. If you sell a product for 24.99 pounds including VAT, your actual revenue is only 20.83 pounds. That 20% immediately comes off the top.\n\nWhen calculating margins, you must work with ex-VAT numbers. A product that looks like it has a 40% margin on paper might only have 20% after VAT is properly accounted for.\n\nUse our free UK VAT Calculator to see the real numbers for your products."
                },
                {
                    "heading": "Common VAT Mistakes to Avoid",
                    "content": "**Mistake 1: Ignoring VAT in margin calculations.** Always calculate margins on ex-VAT figures.\n\n**Mistake 2: Not accounting for import VAT.** If you source from outside the UK, you pay import VAT at the border.\n\n**Mistake 3: Mixing up inclusive and exclusive pricing.** UK consumers expect VAT-inclusive prices. Your advertised price must include VAT.\n\n**Mistake 4: Forgetting about the flat rate scheme.** For smaller sellers, the flat rate VAT scheme can simplify things and sometimes save money."
                },
                {
                    "heading": "VAT and Dropshipping",
                    "content": "Dropshipping adds complexity because the goods often ship directly from overseas suppliers. Since Brexit, UK VAT rules require that the seller (you) is responsible for VAT on goods under 135 pounds.\n\nThis means you need to charge VAT to your UK customers and remit it to HMRC, even if your supplier is in China. Factor this into your pricing from day one."
                }
            ],
            "product_highlights": [],
            "conclusion": "VAT is a fact of UK ecommerce life, but it does not have to be a profit killer. Build it into your pricing model from the start, use accurate calculators, and you will avoid the nasty surprises that catch out less prepared sellers."
        },
    },
    {
        "title": "TikTok Shop UK: Is It Worth It for Product Sellers in 2026?",
        "slug": "tiktok-shop-uk-worth-it-2026",
        "meta_description": "Is TikTok Shop UK a viable sales channel in 2026? We analyse the pros, cons, fees, and which products actually sell well on TikTok Shop.",
        "category": "Channels",
        "tags": ["tiktok-shop", "uk-ecommerce", "social-commerce", "viral-products"],
        "content": {
            "intro": "TikTok Shop has gone from a novelty to a serious sales channel for UK ecommerce sellers. But is it right for your products? We break down the reality of selling on TikTok Shop UK based on data from thousands of product listings.",
            "sections": [
                {
                    "heading": "The TikTok Shop Opportunity",
                    "content": "TikTok Shop UK has seen explosive growth. The platform combines entertainment with impulse buying in a way no other channel does. Products that demonstrate well on video — gadgets, beauty, fitness, home organisation — can go from zero to thousands of sales in days.\n\nThe key advantage is organic reach. Unlike Shopify (where you pay for every visitor) or Amazon (where you compete on keywords), TikTok can deliver massive free traffic if your content hits."
                },
                {
                    "heading": "Which Products Work on TikTok Shop UK",
                    "content": "Based on our analysis of top-performing TikTok Shop products in the UK:\n\n- **Price point:** 10-30 pounds performs best. High enough for decent margins, low enough for impulse buys.\n- **Visual appeal:** Products that look satisfying or surprising on camera.\n- **Problem-solvers:** Items that fix a relatable everyday annoyance.\n- **Before/after potential:** Products where the transformation is visible.\n\nProducts that require explanation, have complex sizing, or lack visual appeal struggle on TikTok regardless of how good they are."
                },
                {
                    "heading": "The Fees and Margins Reality",
                    "content": "TikTok Shop takes a commission (currently around 5-8% depending on category), plus you need to factor in:\n\n- Shipping costs (TikTok users expect fast delivery)\n- Sample costs for creators\n- Content creation time or costs\n- Returns (higher than average due to impulse buying)\n\nAfter all costs, aim for a minimum 25% net margin to make TikTok Shop worthwhile. Use our Profit Margin Calculator to model your specific numbers."
                },
                {
                    "heading": "Getting Started: A Practical Approach",
                    "content": "Do not go all-in on TikTok Shop immediately. Instead:\n\n1. Research what is trending using TrendScout's trend data\n2. Test 2-3 products with small inventory\n3. Create or commission 5-10 short videos per product\n4. Engage with TikTok Shop affiliates who will promote for commission\n5. Scale what works, cut what does not\n\nThe sellers who win on TikTok treat it as a content game first and a selling game second."
                }
            ],
            "product_highlights": [],
            "conclusion": "TikTok Shop UK is a genuine opportunity in 2026, but it is not for every product or every seller. If your products are visual, affordable, and solve a clear problem, it is worth testing. Use data to guide your product selection and start small before scaling."
        },
    },
]

