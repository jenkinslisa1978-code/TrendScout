"""
Public API — Keyed access for power users.
Rate-limited, key-authenticated endpoints for product search, scores, and trends.
"""
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from typing import Optional
from datetime import datetime, timezone
import uuid
import hashlib
import logging

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.cache import get_cached, set_cached, slugify

api_access_router = APIRouter(prefix="/api/v1")
api_keys_router = APIRouter(prefix="/api/api-keys")


# ── API Key Authentication ──────────────────────────────────────

async def get_api_key_user(x_api_key: str = Header(None)):
    """Validate API key and return the associated user."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header required")

    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    key_doc = await db.api_keys.find_one(
        {"key_hash": key_hash, "active": True}, {"_id": 0}
    )
    if not key_doc:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    # Rate limit: 100 req/min per key
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    minute_ago = (now - timedelta(minutes=1)).isoformat()
    recent_calls = await db.api_usage.count_documents(
        {"key_id": key_doc["id"], "called_at": {"$gte": minute_ago}}
    )
    if recent_calls >= key_doc.get("rate_limit", 100):
        raise HTTPException(status_code=429, detail="Rate limit exceeded (100 req/min)")

    # Track usage
    await db.api_usage.insert_one({
        "key_id": key_doc["id"],
        "user_id": key_doc["user_id"],
        "called_at": now.isoformat(),
        "endpoint": "api_v1",
    })

    # Update last used
    await db.api_keys.update_one(
        {"id": key_doc["id"]},
        {"$set": {"last_used": now.isoformat()}, "$inc": {"total_calls": 1}},
    )

    return key_doc


# ── API Key Management ──────────────────────────────────────────

@api_keys_router.post("/generate")
async def generate_api_key(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Generate a new API key for the current user."""
    body = await request.json()
    name = body.get("name", "Default Key")

    # Limit to 3 keys per user
    existing = await db.api_keys.count_documents({"user_id": current_user.user_id, "active": True})
    if existing >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 active API keys allowed")

    raw_key = f"ts_{uuid.uuid4().hex}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    key_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.user_id,
        "name": name,
        "key_hash": key_hash,
        "key_prefix": raw_key[:12] + "...",
        "active": True,
        "rate_limit": 100,
        "total_calls": 0,
        "last_used": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.api_keys.insert_one(key_doc)
    key_doc.pop("_id", None)

    return {
        "key": raw_key,
        "key_id": key_doc["id"],
        "name": name,
        "message": "Save this key — it won't be shown again.",
    }


@api_keys_router.get("/")
async def list_api_keys(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """List all API keys for the current user."""
    keys = await db.api_keys.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "key_hash": 0}
    ).sort("created_at", -1).to_list(10)
    return {"keys": keys}


@api_keys_router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Revoke an API key."""
    result = await db.api_keys.update_one(
        {"id": key_id, "user_id": current_user.user_id},
        {"$set": {"active": False, "revoked_at": datetime.now(timezone.utc).isoformat()}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"revoked": True}


# ── Public API v1 Endpoints ─────────────────────────────────────

@api_access_router.get("/products/search")
async def api_search_products(
    q: str = "",
    category: Optional[str] = None,
    min_score: int = 0,
    limit: int = 20,
    key_doc: dict = Depends(get_api_key_user),
):
    """Search products by name, category, and minimum launch score."""
    query = {"launch_score": {"$gte": min_score}}
    if q:
        query["product_name"] = {"$regex": q, "$options": "i"}
    if category:
        query["category"] = category

    products = await db.products.find(
        query,
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "launch_score": 1,
         "trend_stage": 1, "estimated_retail_price": 1, "image_url": 1,
         "competition_level": 1, "tiktok_views": 1, "engagement_rate": 1}
    ).sort("launch_score", -1).limit(min(limit, 50)).to_list(min(limit, 50))

    return {"products": products, "total": len(products), "query": q}


@api_access_router.get("/products/{product_id}/score")
async def api_get_product_score(
    product_id: str,
    key_doc: dict = Depends(get_api_key_user),
):
    """Get detailed launch score breakdown for a product."""
    product = await db.products.find_one(
        {"id": product_id},
        {"_id": 0, "id": 1, "product_name": 1, "launch_score": 1,
         "trend_score": 1, "margin_score": 1, "competition_score": 1,
         "ad_activity_score": 1, "supplier_demand_score": 1,
         "search_growth_score": 1, "social_buzz_score": 1,
         "trend_stage": 1, "competition_level": 1}
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}


@api_access_router.get("/trends/categories")
async def api_get_trending_categories(
    key_doc: dict = Depends(get_api_key_user),
):
    """Get trending categories with average scores and product counts."""
    pipeline = [
        {"$match": {"launch_score": {"$gte": 40}}},
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$launch_score"},
            "max_score": {"$max": "$launch_score"},
        }},
        {"$sort": {"avg_score": -1}},
        {"$limit": 25},
    ]
    results = await db.products.aggregate(pipeline).to_list(25)
    categories = [
        {
            "category": r["_id"],
            "product_count": r["count"],
            "avg_score": round(r["avg_score"], 1),
            "max_score": r["max_score"],
        }
        for r in results if r["_id"]
    ]
    return {"categories": categories}


@api_access_router.get("/trends/top")
async def api_get_top_products(
    limit: int = 10,
    category: Optional[str] = None,
    key_doc: dict = Depends(get_api_key_user),
):
    """Get top trending products by launch score."""
    query = {"launch_score": {"$gte": 50}}
    if category:
        query["category"] = category

    products = await db.products.find(
        query,
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "launch_score": 1,
         "trend_stage": 1, "estimated_retail_price": 1, "estimated_cost": 1,
         "competition_level": 1, "tiktok_views": 1}
    ).sort("launch_score", -1).limit(min(limit, 50)).to_list(min(limit, 50))

    return {"products": products, "total": len(products)}


routers = [api_access_router, api_keys_router]
