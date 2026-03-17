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

import aiohttp

tools_router = APIRouter(prefix="/api/tools")
competitor_router = APIRouter(prefix="/api/competitor-stores")

@tools_router.post("/analyze-store")
async def analyze_shopify_store(req: StoreAnalyzeRequest):
    """
    Analyze a Shopify store by fetching its /products.json endpoint.
    Public endpoint — works without auth for the free tools page.
    """
    import re

    url = req.url.strip().rstrip("/")
    # Normalize URL
    if not url.startswith("http"):
        url = "https://" + url
    # Extract domain
    domain_match = re.match(r"https?://([^/]+)", url)
    if not domain_match:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    domain = domain_match.group(1)

    products_url = f"https://{domain}/products.json?limit=250"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                products_url,
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"User-Agent": "TrendScout/1.0 Store Analyzer"}
            ) as resp:
                if resp.status == 404:
                    raise HTTPException(status_code=400, detail="This doesn't appear to be a Shopify store or the products endpoint is disabled.")
                if resp.status != 200:
                    raise HTTPException(status_code=400, detail=f"Could not reach store (HTTP {resp.status}). Ensure the URL is a Shopify store.")
                data = await resp.json()
    except aiohttp.ClientError:
        raise HTTPException(status_code=400, detail="Could not connect to store. Check the URL and try again.")

    raw_products = data.get("products", [])
    if not raw_products:
        return {
            "store_url": f"https://{domain}",
            "domain": domain,
            "product_count": 0,
            "products": [],
            "categories": [],
            "price_range": {"min": 0, "max": 0, "avg": 0},
            "newest_products": [],
            "analysis": {"status": "empty", "message": "No products found on this store."},
        }

    # Process products
    products = []
    all_prices = []
    category_counts = {}
    for p in raw_products:
        variants = p.get("variants", [])
        prices = [float(v.get("price", 0)) for v in variants if v.get("price")]
        avg_price = sum(prices) / len(prices) if prices else 0
        all_prices.extend(prices)

        product_type = p.get("product_type", "").strip() or "Uncategorized"
        category_counts[product_type] = category_counts.get(product_type, 0) + 1

        img = p.get("images", [{}])
        image_url = img[0].get("src", "") if img else ""

        products.append({
            "title": p.get("title", ""),
            "product_type": product_type,
            "vendor": p.get("vendor", ""),
            "price": round(avg_price, 2),
            "variants_count": len(variants),
            "image_url": image_url,
            "created_at": p.get("created_at", ""),
            "updated_at": p.get("updated_at", ""),
            "tags": p.get("tags", "").split(", ")[:5] if isinstance(p.get("tags"), str) else [],
        })

    # Sort by newest
    products.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    newest = products[:5]

    # Categories sorted by count
    categories = sorted(
        [{"name": k, "count": v} for k, v in category_counts.items()],
        key=lambda c: c["count"],
        reverse=True,
    )

    # Price analysis
    min_price = min(all_prices) if all_prices else 0
    max_price = max(all_prices) if all_prices else 0
    avg_price = sum(all_prices) / len(all_prices) if all_prices else 0

    # Store assessment
    count = len(raw_products)
    if count > 100:
        store_size = "Large"
        assessment = "Established store with a wide product catalog. Likely a strong competitor."
    elif count > 30:
        store_size = "Medium"
        assessment = "Growing store with moderate product range. Active and worth monitoring."
    elif count > 5:
        store_size = "Small"
        assessment = "Early-stage store. Could be a niche player or new entrant."
    else:
        store_size = "Micro"
        assessment = "Very small catalog. Likely testing products or just launched."

    return {
        "store_url": f"https://{domain}",
        "domain": domain,
        "product_count": count,
        "store_size": store_size,
        "categories": categories[:10],
        "price_range": {
            "min": round(min_price, 2),
            "max": round(max_price, 2),
            "avg": round(avg_price, 2),
            "currency": "USD",
        },
        "newest_products": newest,
        "top_vendors": sorted(
            [{"name": k, "count": v} for k, v in
             {p["vendor"]: sum(1 for x in products if x["vendor"] == p["vendor"]) for p in products if p["vendor"]}.items()],
            key=lambda v: v["count"], reverse=True
        )[:5],
        "analysis": {
            "status": "success",
            "store_size": store_size,
            "assessment": assessment,
            "total_categories": len(categories),
        },
    }


# ── Competitor Store Tracker ──

class CompetitorStoreCreate(BaseModel):
    url: str
    name: Optional[str] = None
    notes: Optional[str] = None


@competitor_router.get("")
async def list_competitor_stores(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """List all tracked competitor stores for the user."""
    stores = await db.competitor_stores.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"stores": stores, "count": len(stores)}


@competitor_router.post("")
async def add_competitor_store(
    req: CompetitorStoreCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Add a competitor store to track."""
    import re

    url = req.url.strip().rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url
    domain_match = re.match(r"https?://([^/]+)", url)
    if not domain_match:
        raise HTTPException(status_code=400, detail="Invalid URL")
    domain = domain_match.group(1)

    # Check duplicate
    existing = await db.competitor_stores.find_one({
        "user_id": current_user.user_id,
        "domain": domain
    })
    if existing:
        raise HTTPException(status_code=400, detail="You're already tracking this store.")

    # Check plan limits (free=2, starter=5, pro=15, elite=unlimited)
    from services.subscription_service import FeatureGate
    plan = await get_user_plan(current_user.user_id)
    limits = {"free": 2, "starter": 5, "pro": 15, "elite": 999}
    current_count = await db.competitor_stores.count_documents({"user_id": current_user.user_id})
    limit = limits.get(plan, 2)
    if current_count >= limit:
        raise HTTPException(status_code=403, detail=f"Your {plan} plan allows tracking up to {limit} stores. Upgrade to track more.")

    # Do initial scan
    try:
        scan_data = await _scan_shopify_store(domain)
    except Exception:
        scan_data = {"product_count": 0, "error": "Could not scan store"}

    store_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.user_id,
        "url": f"https://{domain}",
        "domain": domain,
        "name": req.name or domain.split(".")[0].title(),
        "notes": req.notes or "",
        "product_count": scan_data.get("product_count", 0),
        "categories": scan_data.get("categories", [])[:5],
        "price_range": scan_data.get("price_range", {}),
        "last_scan_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scan_history": [{
            "date": datetime.now(timezone.utc).isoformat(),
            "product_count": scan_data.get("product_count", 0),
        }],
    }
    await db.competitor_stores.insert_one(store_doc)
    store_doc.pop("_id", None)
    return store_doc


@competitor_router.post("/{store_id}/refresh")
async def refresh_competitor_store(
    store_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Re-scan a tracked competitor store."""
    store = await db.competitor_stores.find_one(
        {"id": store_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    try:
        scan_data = await _scan_shopify_store(store["domain"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scan failed: {str(e)}")

    prev_count = store.get("product_count", 0)
    new_count = scan_data.get("product_count", 0)
    change = new_count - prev_count

    scan_entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "product_count": new_count,
        "change": change,
    }

    await db.competitor_stores.update_one(
        {"id": store_id},
        {"$set": {
            "product_count": new_count,
            "categories": scan_data.get("categories", [])[:5],
            "price_range": scan_data.get("price_range", {}),
            "last_scan_at": datetime.now(timezone.utc).isoformat(),
            "product_change": change,
        }, "$push": {
            "scan_history": {"$each": [scan_entry], "$slice": -30}
        }}
    )

    updated = await db.competitor_stores.find_one({"id": store_id}, {"_id": 0})
    return updated


@competitor_router.delete("/{store_id}")
async def remove_competitor_store(
    store_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Remove a competitor store from tracking."""
    result = await db.competitor_stores.delete_one({
        "id": store_id,
        "user_id": current_user.user_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Store not found")
    return {"status": "deleted"}


async def _scan_shopify_store(domain: str) -> dict:
    """Internal: fetch products.json from a Shopify store."""
    url = f"https://{domain}/products.json?limit=250"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=15),
            headers={"User-Agent": "TrendScout/1.0"}
        ) as resp:
            if resp.status != 200:
                return {"product_count": 0, "categories": [], "price_range": {}}
            data = await resp.json()

    raw = data.get("products", [])
    prices = []
    cats = {}
    for p in raw:
        for v in p.get("variants", []):
            try:
                prices.append(float(v.get("price", 0)))
            except (ValueError, TypeError):
                pass
        pt = (p.get("product_type") or "").strip() or "Uncategorized"
        cats[pt] = cats.get(pt, 0) + 1

    return {
        "product_count": len(raw),
        "categories": sorted([{"name": k, "count": v} for k, v in cats.items()], key=lambda c: c["count"], reverse=True),
        "price_range": {
            "min": round(min(prices), 2) if prices else 0,
            "max": round(max(prices), 2) if prices else 0,
            "avg": round(sum(prices) / len(prices), 2) if prices else 0,
        },
    }



@tools_router.get("/tiktok-intelligence")
async def get_tiktok_intelligence():
    """
    TikTok Ad Intelligence dashboard data.
    Aggregates TikTok-related product data from the database.
    Public endpoint - cached for 30 minutes.
    """
    cached = get_cached("tiktok_intelligence")
    if cached:
        return cached

    # Get products with TikTok data, sorted by views
    products = await db.products.find(
        {"tiktok_views": {"$gt": 0}},
        {"_id": 0}
    ).sort("tiktok_views", -1).limit(150).to_list(150)

    # Build category performance from TikTok data
    category_perf = {}
    for p in products:
        cat = p.get("category", "Other")
        if cat not in category_perf:
            category_perf[cat] = {"views": 0, "products": 0, "total_score": 0, "trend_stages": []}
        category_perf[cat]["views"] += p.get("tiktok_views", 0)
        category_perf[cat]["products"] += 1
        category_perf[cat]["total_score"] += p.get("launch_score", 0)
        ts = p.get("trend_stage") or p.get("early_trend_label")
        if ts:
            category_perf[cat]["trend_stages"].append(ts)

    categories = sorted([
        {
            "name": k,
            "total_views": v["views"],
            "product_count": v["products"],
            "avg_score": round(v["total_score"] / v["products"]) if v["products"] > 0 else 0,
            "dominant_stage": max(set(v["trend_stages"]), key=v["trend_stages"].count) if v["trend_stages"] else "Unknown",
        }
        for k, v in category_perf.items()
    ], key=lambda c: c["total_views"], reverse=True)

    # Top viral products
    viral = []
    for p in products[:10]:
        margin = p.get("estimated_margin", 0)
        retail = p.get("estimated_retail_price", 1)
        margin_pct = int((margin / retail) * 100) if retail > 0 else 0
        viral.append({
            "id": p.get("id"),
            "slug": slugify(p.get("product_name", "")),
            "product_name": p.get("product_name", "Unknown")[:80],
            "category": p.get("category", ""),
            "image_url": p.get("image_url", ""),
            "tiktok_views": p.get("tiktok_views", 0),
            "launch_score": p.get("launch_score", 0),
            "trend_stage": p.get("trend_stage") or p.get("early_trend_label", "Unknown"),
            "margin_percent": margin_pct,
            "growth_rate": round(p.get("growth_rate") or p.get("trend_velocity") or 0, 1),
            "google_trend_score": p.get("google_trend_score", 0),
        })

    # Trending hashtags / pattern insights
    trending_patterns = [
        {"pattern": "TikTok Made Me Buy It", "relevance": "high", "description": "Products trending through viral TikTok reviews and unboxings"},
        {"pattern": "Oddly Satisfying", "relevance": "high", "description": "Products with satisfying visual demonstrations that get high engagement"},
        {"pattern": "Life Hack Products", "relevance": "medium", "description": "Problem-solving gadgets that simplify daily tasks"},
        {"pattern": "Before/After", "relevance": "medium", "description": "Transformation products (skincare, cleaning, organization) with visual results"},
        {"pattern": "Dupes & Alternatives", "relevance": "medium", "description": "Affordable alternatives to luxury or popular products"},
    ]

    # Summary stats
    total_views = sum(p.get("tiktok_views", 0) for p in products)
    avg_score = round(sum(p.get("launch_score", 0) for p in products) / len(products)) if products else 0

    result = {
        "viral_products": viral,
        "categories": categories[:8],
        "trending_patterns": trending_patterns,
        "stats": {
            "total_tiktok_views": total_views,
            "products_tracked": len(products),
            "avg_launch_score": avg_score,
            "top_category": categories[0]["name"] if categories else "N/A",
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    set_cached("tiktok_intelligence", result)
    return result



# =====================
# WORKSPACE (Saved Products)
# =====================

workspace_router = APIRouter(prefix="/api/workspace")



routers = [tools_router, competitor_router]
