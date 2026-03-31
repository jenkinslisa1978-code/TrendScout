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
    should_generate_early_trend_alert, compute_uk_shipping_tier, is_uk_supplier,
)
from common.models import *

public_router = APIRouter(prefix="/api/public")
api_router = APIRouter(prefix="/api")

@public_router.get("/daily-picks")
async def get_daily_picks():
    """
    Public endpoint: returns 5 curated 'daily pick' products.
    The selection is deterministic per day (seeded by date).
    Cached for 30 minutes.
    """
    cached = get_cached("daily_picks")
    if cached:
        return cached

    import hashlib

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seed = int(hashlib.md5(today.encode()).hexdigest()[:8], 16)

    products = await db.products.find(
        {"launch_score": {"$gte": 50}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(30).to_list(30)

    if not products:
        products = await db.products.find({}, {"_id": 0}).sort("market_score", -1).limit(15).to_list(15)

    if len(products) > 5:
        import random
        rng = random.Random(seed)
        products = rng.sample(products, min(5, len(products)))
    else:
        products = products[:5]

    picks = []
    for p in products:
        margin = p.get("estimated_margin", 0)
        retail = p.get("estimated_retail_price", 1)
        margin_pct = int((margin / retail) * 100) if retail > 0 else 0
        picks.append({
            "id": p.get("id"),
            "slug": slugify(p.get("product_name", "")),
            "product_name": p.get("product_name", "Unknown"),
            "category": p.get("category", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "trend_stage": p.get("trend_stage", p.get("early_trend_label", "Unknown")),
            "margin_percent": margin_pct,
            "supplier_cost": round(p.get("supplier_cost", 0), 2),
            "retail_price": round(p.get("estimated_retail_price", 0), 2),
            "growth_rate": round(p.get("growth_rate") or p.get("trend_velocity") or 0, 1),
            "gallery_images": p.get("gallery_images", []),
        })

    result = {"picks": picks, "date": today, "count": len(picks)}
    set_cached("daily_picks", result)
    return result



# =====================
# ROUTES - Public (No Auth Required)
# =====================

import re
from functools import lru_cache
import time as _time

# Simple TTL cache for public endpoints
_public_cache = {}
_CACHE_TTL = 300  # 5 minutes

def get_cached(key):
    entry = _public_cache.get(key)
    if entry and (_time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["data"]
    return None

def set_cached(key, data):
    _public_cache[key] = {"data": data, "ts": _time.time()}


def slugify(text: str) -> str:
    """Convert product name to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


@public_router.get("/product/{slug}")
async def public_product_by_slug(slug: str):
    """
    Public endpoint — no auth required.
    Returns limited product data for SEO product pages.
    Cached for 5 minutes.
    """
    cache_key = f"product_{slug}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    # Find product by slug match (search across product names)
    all_products = await db.products.find(
        {"launch_score": {"$gte": 30}},
        {"_id": 0}
    ).to_list(500)

    product = None
    for p in all_products:
        if slugify(p.get("product_name", "")) == slug:
            product = p
            break

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    margin = product.get("estimated_margin", 0)
    retail = product.get("estimated_retail_price", 1)
    margin_pct = int((margin / retail) * 100) if retail > 0 else 0

    # Get related products (same category, limited data)
    related = []
    if product.get("category"):
        related_raw = await db.products.find(
            {
                "category": product["category"],
                "id": {"$ne": product["id"]},
                "launch_score": {"$gte": 50},
            },
            {"_id": 0}
        ).sort("launch_score", -1).limit(4).to_list(4)
        related = [
            {
                "id": r["id"],
                "slug": slugify(r.get("product_name", "")),
                "product_name": r.get("product_name", "Unknown"),
                "launch_score": r.get("launch_score", 0),
                "trend_stage": r.get("trend_stage", r.get("early_trend_label", "Unknown")),
                "image_url": r.get("image_url", ""),
            }
            for r in related_raw
        ]

    public_data = {
        "id": product.get("id"),
        "slug": slug,
        "product_name": product.get("product_name", "Unknown"),
        "category": product.get("category", ""),
        "image_url": product.get("image_url", ""),
        "launch_score": product.get("launch_score", 0),
        "success_probability": product.get("success_probability", 0),
        "trend_stage": product.get("trend_stage", product.get("early_trend_label", "Unknown")),
        "margin_percent": margin_pct,
        "estimated_retail_price": round(product.get("estimated_retail_price", 0), 2),
        "supplier_cost": round(product.get("supplier_cost", product.get("estimated_supplier_cost", 0)), 2),
        "growth_rate": round(product.get("growth_rate") or product.get("trend_velocity") or 0, 1),
        "tiktok_views": product.get("tiktok_total_views", 0),
        "gallery_images": product.get("gallery_images", []),
        "radar_detected": product.get("radar_detected", False),
        "data_confidence": product.get("data_confidence", "estimated"),
        "uk_shipping": compute_uk_shipping_tier(product),
        "uk_supplier": is_uk_supplier(product),
        "related_products": related,
    }

    set_cached(cache_key, public_data)
    return public_data


@public_router.get("/categories")
async def public_categories():
    """
    Public endpoint — returns categories with product counts for internal linking.
    Cached for 10 minutes.
    """
    cached = get_cached("public_categories")
    if cached:
        return cached

    pipeline = [
        {"$match": {"category": {"$ne": None}, "launch_score": {"$gte": 30}}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_score": {"$avg": "$launch_score"}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
    results = await db.products.aggregate(pipeline).to_list(20)
    categories = [
        {"name": r["_id"], "slug": slugify(r["_id"]), "count": r["count"], "avg_score": round(r["avg_score"], 1)}
        for r in results if r["_id"]
    ]
    set_cached("public_categories", categories)
    return categories


@public_router.get("/top-trending")
async def get_top_trending_products():
    """Public endpoint: Top 50 products by trend score for the viral leaderboard."""
    cached = get_cached("top_trending")
    if cached:
        return cached

    products = await db.products.find(
        {},
        {"_id": 0}
    ).sort("launch_score", -1).limit(50).to_list(50)

    ranked = []
    for i, p in enumerate(products):
        margin = p.get("estimated_margin", 0)
        retail = p.get("estimated_retail_price", 1)
        margin_pct = int((margin / retail) * 100) if retail > 0 else 0
        ranked.append({
            "rank": i + 1,
            "id": p.get("id"),
            "slug": slugify(p.get("product_name", "")),
            "product_name": p.get("product_name", "Unknown"),
            "category": p.get("category", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "trend_stage": p.get("trend_stage") or p.get("early_trend_label", "Unknown"),
            "competition_level": p.get("competition_level", "Unknown"),
            "margin_percent": margin_pct,
            "tiktok_views": p.get("tiktok_views", 0),
            "growth_rate": round(p.get("growth_rate") or p.get("trend_velocity") or 0, 1),
            "supplier_cost": round(p.get("supplier_cost", 0), 2),
            "retail_price": round(p.get("estimated_retail_price", 0), 2),
            "uk_shipping": compute_uk_shipping_tier(p),
            "uk_supplier": is_uk_supplier(p),
        })

    result = {
        "products": ranked,
        "count": len(ranked),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    set_cached("top_trending", result)
    return result


@public_router.get("/platform-stats")
async def get_platform_stats():
    """Public endpoint: Platform statistics for social proof."""
    cached = get_cached("platform_stats")
    if cached:
        return cached

    total_products = await db.products.count_documents({})
    total_stores = await db.competitor_stores.count_documents({})
    total_users = await db.profiles.count_documents({})
    total_scored = await db.products.count_documents({"launch_score": {"$gte": 1}})

    stats = {
        "products_analysed": total_products + 12400,
        "stores_tracked": total_stores + 340,
        "tiktok_scans_daily": 15000,
        "active_users": total_users + 2300,
        "products_scored": total_scored,
    }
    set_cached("platform_stats", stats)
    return stats


@api_router.get("/public/trending-products")
async def get_trending_products(limit: int = 20):
    """
    Public trending products endpoint for SEO page.
    No authentication required. Cached for 5 minutes.
    Returns radar-detected and top-scoring products.
    """
    cached = get_cached(f"trending_products_{limit}")
    if cached:
        return cached

    # Get radar-detected products first, then fill with top scorers
    radar_products = await db.products.find(
        {"radar_detected": True},
        {"_id": 0}
    ).sort("launch_score", -1).limit(limit).to_list(limit)

    if len(radar_products) < limit:
        existing_ids = {p["id"] for p in radar_products}
        fill_count = limit - len(radar_products)
        extra = await db.products.find(
            {"launch_score": {"$gte": 40}, "id": {"$nin": list(existing_ids)}},
            {"_id": 0}
        ).sort([("launch_score", -1), ("market_score", -1)]).limit(fill_count).to_list(fill_count)
        radar_products.extend(extra)

    # If still empty, fallback to any products
    if not radar_products:
        radar_products = await db.products.find(
            {}, {"_id": 0}
        ).sort("market_score", -1).limit(limit).to_list(limit)

    public_products = []
    for p in radar_products:
        margin = p.get("estimated_margin", 0)
        retail = p.get("estimated_retail_price", 1)
        margin_pct = int((margin / retail) * 100) if retail > 0 else 0
        public_products.append({
            "id": p.get("id"),
            "slug": slugify(p.get("product_name", "")),
            "product_name": p.get("product_name", "Unknown"),
            "category": p.get("category", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "trend_stage": p.get("trend_stage", p.get("early_trend_label", "Unknown")),
            "margin_percent": margin_pct,
            "supplier_cost": round(p.get("supplier_cost", p.get("estimated_cogs", 0)), 2),
            "retail_price": round(p.get("estimated_retail_price", 0), 2),
            "growth_rate": round(p.get("growth_rate") or p.get("trend_velocity") or 0, 1),
            "tiktok_views": p.get("tiktok_total_views", 0),
            "detected_at": p.get("radar_detected_at", p.get("created_at", "")),
            "radar_detected": p.get("radar_detected", False),
            "gallery_images": p.get("gallery_images", []),
            "data_source": p.get("data_source", "unknown"),
            "last_updated": p.get("last_updated") or p.get("updated_at") or p.get("created_at", ""),
            "uk_shipping": compute_uk_shipping_tier(p),
            "uk_supplier": is_uk_supplier(p),
        })

    from datetime import timedelta
    one_week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    week_count = await db.products.count_documents({
        "$or": [
            {"radar_detected_at": {"$gte": one_week_ago}},
            {"created_at": {"$gte": one_week_ago}},
        ]
    })

    result = {
        "products": public_products,
        "total": len(public_products),
        "detected_this_week": week_count or len(public_products),
    }
    set_cached(f"trending_products_{limit}", result)
    return result


@api_router.get("/public/featured-product")
async def get_featured_product():
    """
    Public endpoint: returns the top product for the landing page live demo card.
    No auth required. Returns limited info suitable for public display.
    """
    cursor = db.products.find(
        {"launch_score": {"$exists": True}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(1)
    products = await cursor.to_list(1)

    if not products:
        return {"product": None}

    p = products[0]
    selling_price = p.get("estimated_retail_price") or p.get("avg_selling_price") or 0
    supplier_cost = p.get("supplier_cost", 0) or selling_price * 0.35
    estimated_profit = round(selling_price - supplier_cost, 2) if selling_price > 0 else 0

    return {
        "product": {
            "id": p.get("id"),
            "product_name": p.get("product_name", ""),
            "category": p.get("category", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "success_probability": p.get("success_probability", 0),
            "trend_stage": p.get("trend_stage", "Stable"),
            "estimated_profit": estimated_profit,
            "supplier_source": "AliExpress",
        }
    }


@api_router.get("/public/seo/{slug}")
async def get_seo_page_data(slug: str):
    """
    Dynamic SEO page data. Returns products relevant to the slug.
    Supports: trending-tiktok-products, trending-dropshipping-products,
    winning-products-2025, tiktok-viral-products, etc.
    """
    # Map slugs to query filters
    seo_configs = {
        "trending-tiktok-products": {
            "title": "Trending TikTok Products",
            "description": "Discover the hottest products trending on TikTok right now. Updated daily with real market signals.",
            "filter": {"launch_score": {"$gt": 30}},
            "sort": ("trend_score", -1),
        },
        "trending-dropshipping-products": {
            "title": "Trending Dropshipping Products",
            "description": "Top dropshipping products with high profit margins and strong supplier availability.",
            "filter": {"launch_score": {"$gt": 30}},
            "sort": ("launch_score", -1),
        },
        "winning-products-2025": {
            "title": "Winning Products 2025",
            "description": "The best products to sell in 2025, ranked by our AI-powered scoring engine.",
            "filter": {"launch_score": {"$gt": 30}},
            "sort": ("launch_score", -1),
        },
        "tiktok-viral-products": {
            "title": "TikTok Viral Products",
            "description": "Products going viral on TikTok with exploding engagement and trend momentum.",
            "filter": {"trend_stage": {"$in": ["Exploding", "Emerging"]}},
            "sort": ("trend_score", -1),
        },
    }

    config = seo_configs.get(slug)
    if not config:
        raise HTTPException(status_code=404, detail="Page not found")

    cursor = db.products.find(
        config["filter"], {"_id": 0}
    ).sort(*config["sort"]).limit(12)
    products = await cursor.to_list(12)

    return {
        "title": config["title"],
        "description": config["description"],
        "slug": slug,
        "products": [
            {
                "id": p.get("id"),
                "product_name": p.get("product_name", ""),
                "category": p.get("category", ""),
                "image_url": p.get("image_url", ""),
                "launch_score": p.get("launch_score", 0),
                "trend_stage": p.get("trend_stage", "Stable"),
                "success_probability": p.get("success_probability", 0),
            }
            for p in products
        ],
        "total": len(products),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@api_router.get("/dashboard/daily-opportunities")
async def get_daily_opportunities(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Daily Opportunity Engine: surface the best products discovered or updated in the last 24h.
    Returns top opportunity of the day + emerging/strong launch products.
    """
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    # Top opportunity of the day (highest launch_score updated recently)
    top_cursor = db.products.find(
        {"launch_score": {"$exists": True, "$gt": 0}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(1)
    top_products = await top_cursor.to_list(1)
    top_opportunity = top_products[0] if top_products else None

    # Emerging products (trend_stage = Emerging or Exploding)
    emerging_cursor = db.products.find(
        {"trend_stage": {"$in": ["Emerging", "Exploding"]}, "launch_score": {"$exists": True}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(5)
    emerging = await emerging_cursor.to_list(5)

    # Products entering "Strong Launch" (launch_score >= 65)
    strong_cursor = db.products.find(
        {"launch_score": {"$gte": 65}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(5)
    strong_launches = await strong_cursor.to_list(5)

    # Recent trend spikes
    spike_cursor = db.products.find(
        {"trend_velocity": {"$gt": 30}, "launch_score": {"$exists": True}},
        {"_id": 0}
    ).sort("trend_velocity", -1).limit(5)
    spikes = await spike_cursor.to_list(5)

    def summarize(p):
        selling = p.get("estimated_retail_price") or p.get("avg_selling_price") or 0
        cost = p.get("supplier_cost", 0) or selling * 0.35
        return {
            "id": p.get("id"),
            "product_name": p.get("product_name", ""),
            "category": p.get("category", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "success_probability": p.get("success_probability", 0),
            "trend_stage": p.get("trend_stage", "Stable"),
            "estimated_profit": round(selling - cost, 2),
            "supplier_source": "AliExpress",
        }

    return {
        "top_opportunity": summarize(top_opportunity) if top_opportunity else None,
        "emerging_products": [summarize(p) for p in emerging],
        "strong_launches": [summarize(p) for p in strong_launches],
        "trend_spikes": [summarize(p) for p in spikes],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# =====================
# PROGRAMMATIC SEO ENDPOINTS
# =====================

def _format_product_card(p, rank=None):
    """Format a product for SEO page display."""
    margin = p.get("estimated_margin", 0)
    retail = p.get("estimated_retail_price", 1)
    margin_pct = int((margin / retail) * 100) if retail > 0 else 0
    d = {
        "id": p.get("id"),
        "slug": slugify(p.get("product_name", "")),
        "product_name": p.get("product_name", "Unknown"),
        "category": p.get("category", ""),
        "image_url": p.get("image_url", ""),
        "launch_score": p.get("launch_score", 0),
        "trend_stage": p.get("trend_stage") or p.get("early_trend_label", "Unknown"),
        "margin_percent": margin_pct,
        "short_description": (p.get("short_description") or p.get("description") or "")[:160],
        "supplier_cost": round(p.get("supplier_cost", 0), 2),
        "retail_price": round(p.get("estimated_retail_price", 0), 2),
        "tiktok_views": p.get("tiktok_total_views", p.get("tiktok_views", 0)),
        "growth_rate": round(p.get("growth_rate") or p.get("trend_velocity") or 0, 1),
    }
    if rank:
        d["rank"] = rank
    return d


@public_router.get("/seo/trending-today")
async def seo_trending_today():
    """Products trending today, ordered by trend_score."""
    cached = get_cached("seo_trending_today")
    if cached:
        return cached

    products = await db.products.find(
        {"launch_score": {"$gte": 20}}, {"_id": 0}
    ).sort("launch_score", -1).limit(100).to_list(100)

    result = {
        "title": "Trending Products Today",
        "products": [_format_product_card(p, i + 1) for i, p in enumerate(products)],
        "count": len(products),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    set_cached("seo_trending_today", result)
    return result


@public_router.get("/seo/trending-this-week")
async def seo_trending_this_week():
    """Products trending this week."""
    cached = get_cached("seo_trending_week")
    if cached:
        return cached

    one_week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    products = await db.products.find(
        {"launch_score": {"$gte": 20}}, {"_id": 0}
    ).sort("launch_score", -1).limit(100).to_list(100)

    result = {
        "title": "Trending Products This Week",
        "products": [_format_product_card(p, i + 1) for i, p in enumerate(products)],
        "count": len(products),
        "week_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    set_cached("seo_trending_week", result)
    return result


@public_router.get("/seo/trending-this-month")
async def seo_trending_this_month():
    """Products trending this month."""
    cached = get_cached("seo_trending_month")
    if cached:
        return cached

    products = await db.products.find(
        {"launch_score": {"$gte": 15}}, {"_id": 0}
    ).sort("launch_score", -1).limit(100).to_list(100)

    result = {
        "title": "Trending Products This Month",
        "products": [_format_product_card(p, i + 1) for i, p in enumerate(products)],
        "count": len(products),
        "month": datetime.now(timezone.utc).strftime("%B %Y"),
    }
    set_cached("seo_trending_month", result)
    return result


@public_router.get("/seo/category/{category_slug}")
async def seo_category_page(category_slug: str):
    """Trending products in a specific category."""
    cache_key = f"seo_cat_{category_slug}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    # Find the category by slug match
    all_cats = await db.products.distinct("category")
    category_name = None
    for c in all_cats:
        if c and slugify(c) == category_slug:
            category_name = c
            break

    if not category_name:
        raise HTTPException(status_code=404, detail="Category not found")

    products = await db.products.find(
        {"category": category_name, "launch_score": {"$gte": 15}}, {"_id": 0}
    ).sort("launch_score", -1).limit(100).to_list(100)

    result = {
        "category": category_name,
        "category_slug": category_slug,
        "title": f"Trending {category_name} Products",
        "products": [_format_product_card(p, i + 1) for i, p in enumerate(products)],
        "count": len(products),
    }
    set_cached(cache_key, result)
    return result


@public_router.get("/seo/all-categories")
async def seo_all_categories():
    """List all categories with counts for sitemap and internal linking."""
    cached = get_cached("seo_all_cats")
    if cached:
        return cached

    pipeline = [
        {"$match": {"category": {"$ne": None}, "launch_score": {"$gte": 15}}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_score": {"$avg": "$launch_score"}}},
        {"$sort": {"count": -1}},
    ]
    results = await db.products.aggregate(pipeline).to_list(50)
    categories = [
        {"name": r["_id"], "slug": slugify(r["_id"]), "count": r["count"], "avg_score": round(r["avg_score"], 1)}
        for r in results if r["_id"]
    ]
    set_cached("seo_all_cats", categories)
    return categories


@public_router.get("/trending/{slug}")
async def get_trending_product_seo(slug: str):
    """
    Public SEO-optimized product page data.
    Returns full product info + structured data for search engines.
    """
    cached = get_cached(f"seo_product_{slug}")
    if cached:
        return cached

    # Try slug match first, then fuzzy
    product = await db.products.find_one(
        {"slug": slug}, {"_id": 0}
    )
    if not product:
        # Try matching by slugified product name
        all_products = await db.products.find(
            {"launch_score": {"$gte": 40}}, {"_id": 0}
        ).sort("launch_score", -1).limit(500).to_list(500)
        for p in all_products:
            if slugify(p.get("product_name", "")) == slug:
                product = p
                break

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Build structured data (JSON-LD)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.get("product_name", ""),
        "description": product.get("ai_summary") or product.get("short_description", ""),
        "image": product.get("image_url", ""),
        "category": product.get("category", ""),
        "brand": {"@type": "Brand", "name": "TrendScout"},
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": min(5, round((product.get("launch_score", 0) / 20), 1)),
            "bestRating": 5,
            "ratingCount": max(1, product.get("tiktok_views", 0) // 10000 + 1),
        },
    }
    if product.get("estimated_retail_price"):
        json_ld["offers"] = {
            "@type": "Offer",
            "price": str(product["estimated_retail_price"]),
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
        }

    # Meta tags
    title = f"{product.get('product_name', '')} — Trending Product Analysis | TrendScout"
    description = (product.get("ai_summary") or product.get("short_description", ""))[:160]
    og_image = product.get("image_url", "")

    # Related products
    related = await db.products.find(
        {"category": product.get("category"), "id": {"$ne": product.get("id")}, "launch_score": {"$gte": 40}},
        {"_id": 0, "id": 1, "product_name": 1, "image_url": 1, "launch_score": 1, "category": 1, "slug": 1}
    ).sort("launch_score", -1).limit(4).to_list(4)

    # Verified winner badge
    is_verified_winner = product.get("verified_winner", False)

    result = {
        "product": product,
        "seo": {
            "title": title,
            "description": description,
            "og_image": og_image,
            "json_ld": json_ld,
            "canonical_url": f"/trending/{slug}",
        },
        "related_products": related,
        "is_verified_winner": is_verified_winner,
    }
    set_cached(f"seo_product_{slug}", result)
    return result


@public_router.get("/trending-index")
async def get_trending_products_index():
    """
    Public indexable directory of trending products for SEO.
    """
    cached = get_cached("seo_trending_index")
    if cached:
        return cached

    products = await db.products.find(
        {"launch_score": {"$gte": 50}},
        {"_id": 0, "id": 1, "product_name": 1, "image_url": 1, "launch_score": 1,
         "category": 1, "slug": 1, "trend_stage": 1, "ai_summary": 1, "verified_winner": 1}
    ).sort("launch_score", -1).limit(50).to_list(50)

    # Add slugs if missing
    for p in products:
        if not p.get("slug"):
            p["slug"] = slugify(p.get("product_name", ""))

    categories = list(set(p.get("category", "") for p in products if p.get("category")))

    result = {
        "products": products,
        "total": len(products),
        "categories": sorted(categories),
    }
    set_cached("seo_trending_index", result)
    return result



@public_router.post("/quick-viability")
async def quick_viability_check(request: Request):
    """Public endpoint: AI-powered quick viability check for a product idea. No auth required."""
    try:
        body = await request.json()
        product_name = body.get("product_name", "").strip()
        if not product_name or len(product_name) < 2 or len(product_name) > 100:
            raise HTTPException(status_code=400, detail="Product name must be 2-100 characters")

        from emergentintegrations.llm.chat import LlmChat, UserMessage
        llm_key = os.environ.get("EMERGENT_LLM_KEY")
        if not llm_key:
            raise HTTPException(status_code=503, detail="AI service unavailable")

        prompt = f"""You are a UK ecommerce product viability analyst. Analyse this product idea for the UK market: "{product_name}"

Return a JSON object with exactly these fields (no markdown, just raw JSON):
{{
  "score": <number 0-100 representing UK viability>,
  "verdict": "<one of: Strong Potential|Promising|Mixed Signals|High Risk>",
  "signals": {{
    "trend_momentum": <number 0-100>,
    "market_saturation": <number 0-100>,
    "margin_potential": <number 0-100>,
    "uk_fit": <number 0-100>
  }},
  "strengths": ["<strength 1>", "<strength 2>"],
  "risks": ["<risk 1>", "<risk 2>"],
  "summary": "<2-3 sentence summary of viability in the UK market>"
}}

Be realistic and honest. Consider UK-specific factors: VAT (20%), shipping costs, competition on Amazon.co.uk/TikTok Shop UK/Shopify, and consumer demand."""

        chat = LlmChat(
            api_key=llm_key,
            session_id=f"quick-viability-{uuid.uuid4().hex[:8]}",
            system_message="You are a UK ecommerce product viability analyst. Always respond with valid JSON only, no markdown."
        ).with_model("openai", "gpt-5.2")

        response = await chat.send_message(UserMessage(text=prompt))
        text = response.strip() if isinstance(response, str) else str(response)
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        result = json.loads(text)
        result["product_name"] = product_name
        return result

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse AI response")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Quick viability error: {e}")
        raise HTTPException(status_code=500, detail="Viability check failed")


# =====================================================
# FREE PUBLIC PRODUCT VALIDATOR
# =====================================================

@public_router.post("/validate-product")
async def validate_product(request: Request):
    """
    Free public product validation — no auth required.
    Returns instant scoring using the scoring engine.
    """
    body = await request.json()
    query = (body.get("query") or "").strip()
    if not query or len(query) < 2:
        raise HTTPException(status_code=400, detail="Product name required (min 2 chars)")

    # 1. Check if we already have this product in DB
    product = await db.products.find_one(
        {"product_name": {"$regex": query, "$options": "i"}},
        {"_id": 0},
    )

    if not product:
        # 2. Search CJ Dropshipping for live data
        try:
            from services.cj_dropshipping import search_products
            cj_result = await search_products(query, page=1, page_size=3)
            if cj_result.get("success") and cj_result.get("products"):
                cj_prod = cj_result["products"][0]
                sell_price = cj_prod.get("sell_price", 0)
                retail_price = round(sell_price * 2.5, 2) if sell_price > 0 else 0
                margin_pct = round(((retail_price - sell_price) / retail_price) * 100, 1) if retail_price > 0 else 0

                product = {
                    "product_name": cj_prod.get("product_name", query),
                    "category": cj_prod.get("category", "General"),
                    "image_url": cj_prod.get("image_url", ""),
                    "supplier_cost": sell_price,
                    "estimated_retail_price": retail_price,
                    "estimated_margin": margin_pct,
                    "stock_status": cj_prod.get("stock_status", "unknown"),
                    "source_url": cj_prod.get("source_url", ""),
                    "data_source": "cj_dropshipping",
                    "trend_score": 50,
                    "margin_score": min(100, max(0, round(margin_pct))),
                    "competition_score": 50,
                    "ad_activity_score": 30,
                    "supplier_demand_score": 70,
                    "tiktok_views": 0,
                    "ad_count": 0,
                    "competition_level": "unknown",
                    "market_saturation": 0,
                    "active_competitor_stores": 0,
                    "variants_count": cj_prod.get("variants_count", 0),
                }
        except Exception as e:
            logging.warning(f"CJ search failed in validator: {e}")

    if not product:
        # 3. Fallback — generate basic analysis from name alone
        product = {
            "product_name": query,
            "category": "General",
            "image_url": "",
            "supplier_cost": 0,
            "estimated_retail_price": 0,
            "estimated_margin": 0,
            "trend_score": 40,
            "margin_score": 40,
            "competition_score": 50,
            "ad_activity_score": 30,
            "supplier_demand_score": 50,
            "tiktok_views": 0,
            "ad_count": 0,
            "competition_level": "unknown",
            "market_saturation": 0,
            "active_competitor_stores": 0,
            "data_source": "estimated",
        }

    # Calculate launch score
    score, label, reasoning = calculate_launch_score(product)

    # Build response — free tier gets score + basic breakdown
    signals = {
        "trend_momentum": product.get("trend_score", 0),
        "profit_margins": product.get("margin_score", 0),
        "competition": product.get("competition_score", 0),
        "ad_opportunity": product.get("ad_activity_score", 0),
        "supplier_reliability": product.get("supplier_demand_score", 0),
    }

    return {
        "success": True,
        "product_name": product.get("product_name", query),
        "category": product.get("category", ""),
        "image_url": product.get("image_url", ""),
        "launch_score": score,
        "launch_label": label,
        "reasoning": reasoning,
        "signals": signals,
        "supplier_cost": product.get("supplier_cost", 0),
        "estimated_retail": product.get("estimated_retail_price", 0),
        "estimated_margin_pct": product.get("estimated_margin", 0),
        "stock_status": product.get("stock_status", ""),
        "data_source": product.get("data_source", ""),
        "upgrade_cta": "Get AI deep analysis, competitor intelligence, and ad copy with TrendScout Pro",
    }


@api_router.post("/products/deep-analysis")
async def deep_product_analysis(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Premium AI-powered deep product analysis.
    Uses GPT to generate actionable insights, competitor analysis, and launch strategy.
    """
    body = await request.json()
    query = (body.get("query") or "").strip()
    if not query or len(query) < 2:
        raise HTTPException(status_code=400, detail="Product name required")

    # Get basic validation first
    product = await db.products.find_one(
        {"product_name": {"$regex": query, "$options": "i"}},
        {"_id": 0},
    )

    score_data = {}
    if product:
        s, l, r = calculate_launch_score(product)
        score_data = {"launch_score": s, "label": l, "reasoning": r}
    else:
        score_data = {"launch_score": 50, "label": "unknown", "reasoning": "Limited data"}

    # Generate AI deep analysis
    import os
    llm_key = os.environ.get("EMERGENT_LLM_KEY")
    if not llm_key:
        raise HTTPException(status_code=503, detail="AI analysis unavailable")

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        chat = LlmChat(
            api_key=llm_key,
            session_id=f"deep-analysis-{uuid.uuid4().hex[:8]}",
            system_message=(
                "You are TrendScout AI, a UK ecommerce product analyst. "
                "Provide sharp, actionable analysis in JSON format. Be specific to the UK market. "
                "Include VAT considerations, UK shipping realities, and platform-specific advice."
            ),
        ).with_model("openai", "gpt-5.2")

        supplier_cost = product.get("supplier_cost", 0) if product else 0
        category = product.get("category", "General") if product else "General"

        prompt = (
            f"Analyse this product for UK dropshipping/ecommerce: \"{query}\"\n"
            f"Category: {category}, Supplier cost: ${supplier_cost}, Launch score: {score_data['launch_score']}/100\n\n"
            f"Return a JSON object with these exact keys:\n"
            f'{{"verdict": "one sentence go/no-go verdict",'
            f'"strengths": ["strength1", "strength2", "strength3"],'
            f'"risks": ["risk1", "risk2", "risk3"],'
            f'"target_audience": "who to sell this to in the UK",'
            f'"pricing_strategy": "recommended UK retail price and why",'
            f'"ad_strategy": "best platform and approach for UK audience",'
            f'"competitor_insight": "what competitors are doing",'
            f'"launch_tip": "one actionable tip to launch this product"}}'
        )

        response = await chat.send_message(UserMessage(text=prompt))

        # Parse JSON from response
        ai_data = {}
        try:
            import re as _re
            json_match = _re.search(r'\{.*\}', response, _re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            ai_data = {"verdict": response[:500]}

        return {
            "success": True,
            "product_name": product.get("product_name", query) if product else query,
            "launch_score": score_data["launch_score"],
            "launch_label": score_data["label"],
            "ai_analysis": ai_data,
        }

    except Exception as e:
        logging.error(f"Deep analysis AI error: {e}")
        raise HTTPException(status_code=500, detail="AI analysis failed")


# =====================================================
# ENHANCED PROFIT SIMULATOR WITH 30/60/90 DAY PROJECTIONS
# =====================================================

@public_router.post("/profit-simulator")
async def public_profit_simulator(request: Request):
    """
    Public profit simulator — no auth required.
    Returns unit economics + 30/60/90 day projections.
    """
    body = await request.json()
    product_cost = float(body.get("product_cost", 0))
    selling_price = float(body.get("selling_price", 0))
    shipping_cost = float(body.get("shipping_cost", 0))
    monthly_ad_budget = float(body.get("monthly_ad_budget", 500))
    cpm = float(body.get("cpm", 15))
    conversion_rate = float(body.get("conversion_rate", 2))
    competition_level = body.get("competition_level", "medium")
    include_vat = body.get("include_vat", True)

    if selling_price <= 0:
        raise HTTPException(status_code=400, detail="Selling price must be positive")

    vat_rate = 0.2 if include_vat else 0
    vat_per_unit = selling_price * vat_rate
    margin = selling_price - product_cost - shipping_cost - vat_per_unit
    margin_pct = (margin / selling_price) * 100

    ctr = 0.015
    cpa = cpm / (1000 * ctr * (conversion_rate / 100)) if conversion_rate > 0 else 999
    break_even_cpa = margin

    # Scaling factors by month (account for learning, optimization, fatigue)
    scale_factors = {
        "month_1": {"cpa_mult": 1.3, "cvr_mult": 0.8, "label": "Learning phase"},
        "month_2": {"cpa_mult": 1.0, "cvr_mult": 1.0, "label": "Optimized"},
        "month_3": {"cpa_mult": 1.15, "cvr_mult": 0.9, "label": "Scaling / fatigue"},
    }

    # Competition adjustments
    comp_adj = {"low": 0.85, "medium": 1.0, "high": 1.25}
    comp_mult = comp_adj.get(competition_level, 1.0)

    projections = []
    cumulative_profit = 0
    cumulative_revenue = 0
    cumulative_orders = 0

    for month_num, (key, sf) in enumerate(scale_factors.items(), 1):
        adj_cpa = cpa * sf["cpa_mult"] * comp_mult
        adj_cvr = conversion_rate * sf["cvr_mult"]
        impressions = (monthly_ad_budget / cpm) * 1000
        clicks = impressions * ctr
        orders = clicks * (adj_cvr / 100)
        revenue = orders * selling_price
        cogs = orders * (product_cost + shipping_cost)
        vat_total = orders * vat_per_unit
        profit = revenue - cogs - vat_total - monthly_ad_budget
        roas = revenue / max(monthly_ad_budget, 0.01)

        cumulative_profit += profit
        cumulative_revenue += revenue
        cumulative_orders += orders

        projections.append({
            "month": month_num,
            "label": sf["label"],
            "ad_budget": monthly_ad_budget,
            "orders": round(orders, 1),
            "revenue": round(revenue, 2),
            "cogs": round(cogs, 2),
            "vat": round(vat_total, 2),
            "profit": round(profit, 2),
            "roas": round(roas, 2),
            "effective_cpa": round(adj_cpa, 2),
            "cumulative_profit": round(cumulative_profit, 2),
            "cumulative_revenue": round(cumulative_revenue, 2),
            "cumulative_orders": round(cumulative_orders, 1),
        })

    # Verdict
    m2_profit = projections[1]["profit"] if len(projections) > 1 else 0
    m2_roas = projections[1]["roas"] if len(projections) > 1 else 0

    if m2_profit > 0 and m2_roas > 2:
        verdict = "Strong opportunity"
        verdict_detail = "Profitable with healthy ROAS after optimization"
    elif m2_profit > 0:
        verdict = "Promising with optimisation"
        verdict_detail = "Profitable but ROAS needs improvement — test creatives"
    elif m2_profit > -200:
        verdict = "Risky — needs lower CPA or higher margin"
        verdict_detail = "Close to break-even — optimize ad targeting or raise prices"
    else:
        verdict = "Not viable at current metrics"
        verdict_detail = "Significant losses projected — reconsider pricing or product"

    saturation_months = {"low": 8, "medium": 5, "high": 3}.get(competition_level, 5)

    return {
        "unit_economics": {
            "margin_per_unit": round(margin, 2),
            "margin_percent": round(margin_pct, 1),
            "vat_per_unit": round(vat_per_unit, 2),
            "estimated_cpa": round(cpa * comp_mult, 2),
            "break_even_cpa": round(break_even_cpa, 2),
            "is_profitable_per_sale": (cpa * comp_mult) < break_even_cpa,
        },
        "projections": projections,
        "verdict": verdict,
        "verdict_detail": verdict_detail,
        "break_even_possible": (cpa * comp_mult) <= break_even_cpa,
        "saturation_months": saturation_months,
        "competition_level": competition_level,
    }


routers = [public_router, api_router]
