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
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        llm_key = os.environ.get("EMERGENT_LLM_KEY")
        if not llm_key:
            return

        chat = LlmChat(
            api_key=llm_key,
            session_id=f"blog-gen-{category_slug}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
            system_message="You are TrendScout's content strategist. Write engaging, SEO-optimized blog articles about trending ecommerce products. Use British English. Be data-driven and practical."
        ).with_model("openai", "gpt-5.2")

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

        response = await chat.send_message(UserMessage(text=prompt))

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


routers = [blog_router, digest_router]
