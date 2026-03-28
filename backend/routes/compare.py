"""
Product Comparison API.
Allows users to compare 2-3 products side-by-side and share via public URL.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from auth import get_current_user, AuthenticatedUser
from common.database import db

compare_router = APIRouter(prefix="/api/compare")


class CompareRequest(BaseModel):
    product_ids: List[str]
    title: Optional[str] = None


@compare_router.post("")
async def create_comparison(
    req: CompareRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Create a product comparison and get a shareable link."""
    if len(req.product_ids) < 2 or len(req.product_ids) > 4:
        raise HTTPException(status_code=400, detail="Compare 2 to 4 products")

    # Fetch products
    products = []
    for pid in req.product_ids:
        p = await db.products.find_one({"id": pid}, {"_id": 0})
        if not p:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
        products.append(_format_product(p))

    share_id = str(uuid.uuid4())[:8]
    comparison = {
        "share_id": share_id,
        "user_id": current_user.user_id,
        "title": req.title or f"Product Comparison",
        "product_ids": req.product_ids,
        "products": products,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.comparisons.insert_one({**comparison, "_id": share_id})

    return {
        "success": True,
        "share_id": share_id,
        "comparison": comparison,
    }


@compare_router.get("/shared/{share_id}")
async def get_shared_comparison(share_id: str):
    """Public: Get a shared comparison by ID."""
    doc = await db.comparisons.find_one({"share_id": share_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return {"success": True, "comparison": doc}


@compare_router.get("/my")
async def list_my_comparisons(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """List all comparisons created by the current user."""
    comps = []
    cursor = db.comparisons.find(
        {"user_id": current_user.user_id},
        {"_id": 0},
    ).sort("created_at", -1).limit(20)
    async for doc in cursor:
        comps.append(doc)
    return {"success": True, "comparisons": comps}


@compare_router.delete("/{share_id}")
async def delete_comparison(
    share_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Delete a comparison."""
    result = await db.comparisons.delete_one(
        {"share_id": share_id, "user_id": current_user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return {"success": True}


@compare_router.post("/quick")
async def quick_compare(
    req: CompareRequest,
):
    """Quick compare without saving (no auth required). Returns product data."""
    if len(req.product_ids) < 2 or len(req.product_ids) > 4:
        raise HTTPException(status_code=400, detail="Compare 2 to 4 products")

    products = []
    for pid in req.product_ids:
        p = await db.products.find_one({"id": pid}, {"_id": 0})
        if not p:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
        products.append(_format_product(p))

    return {"success": True, "products": products}


def _format_product(p: dict) -> dict:
    """Format product for comparison view."""
    return {
        "id": p.get("id", ""),
        "product_name": p.get("product_name", "Unknown"),
        "category": p.get("category", ""),
        "image_url": p.get("image_url", ""),
        "gallery_images": p.get("gallery_images", [])[:3],
        "launch_score": p.get("launch_score", 0),
        "trend_stage": p.get("trend_stage", p.get("early_trend_label", "Unknown")),
        "margin_percent": p.get("estimated_margin", p.get("margin_percent", 0)),
        "supplier_cost": p.get("supplier_cost", 0),
        "retail_price": p.get("retail_price", 0),
        "competition_level": p.get("competition_level", "Unknown"),
        "growth_rate": p.get("growth_rate", 0),
        "tiktok_views": p.get("tiktok_views", 0),
        "data_source": p.get("data_source", ""),
        "detected_at": p.get("detected_at", ""),
        "metrics": {
            "demand_score": p.get("metrics", {}).get("demand_score", p.get("launch_score", 0)),
            "trend_label": p.get("metrics", {}).get("trend_label", p.get("trend_stage", "")),
            "estimated_margin": p.get("metrics", {}).get("estimated_margin", p.get("estimated_margin", 0)),
            "uk_search_volume": p.get("metrics", {}).get("uk_search_volume", 0),
            "competition_score": p.get("metrics", {}).get("competition_score", 0),
        },
    }


routers = [compare_router]
