"""
CJ Dropshipping API routes — product sourcing and supplier enrichment.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone

from auth import get_current_user, AuthenticatedUser
from common.database import db
from services.cj_dropshipping import search_products, get_product_detail, get_categories

cj_router = APIRouter(prefix="/api/cj")


@cj_router.get("/search")
async def cj_search(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    category_id: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Search CJ Dropshipping for products by name."""
    result = await search_products(q, page, page_size, category_id or "")
    return result


@cj_router.get("/product/{pid}")
async def cj_product_detail(
    pid: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get detailed product info from CJ Dropshipping."""
    result = await get_product_detail(pid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Product not found"))
    return result


@cj_router.get("/categories")
async def cj_categories(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get CJ Dropshipping product categories."""
    return await get_categories()


@cj_router.post("/import/{pid}")
async def import_cj_product(
    pid: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Import a CJ product into TrendScout for tracking and analysis.
    Fetches live data from CJ and creates a product entry.
    """
    # Check if already imported
    existing = await db.products.find_one(
        {"cj_pid": pid},
        {"_id": 0, "id": 1, "product_name": 1},
    )
    if existing:
        return {"success": True, "message": "Product already imported", "product_id": existing["id"], "already_existed": True}

    # Fetch from CJ
    result = await get_product_detail(pid)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Could not fetch product from CJ"))

    cj_product = result["product"]
    import uuid

    product_id = str(uuid.uuid4())
    product = {
        "id": product_id,
        "cj_pid": cj_product["cj_pid"],
        "product_name": cj_product["product_name"],
        "slug": cj_product["product_name"].lower().replace(" ", "-")[:80],
        "category": cj_product["category"],
        "image_url": cj_product["image_url"],
        "images": cj_product.get("images", []),
        "estimated_retail_price": round(cj_product["sell_price"] * 2.5, 2),
        "estimated_cost": cj_product["sell_price"],
        "estimated_margin": round((cj_product["sell_price"] * 2.5 - cj_product["sell_price"]) / (cj_product["sell_price"] * 2.5) * 100, 1) if cj_product["sell_price"] > 0 else 0,
        "supplier_cost": cj_product["sell_price"],
        "currency": cj_product["currency"],
        "data_source": "cj_dropshipping",
        "source_url": cj_product["source_url"],
        "stock_status": cj_product["stock_status"],
        "shipping_weight": cj_product.get("shipping_weight", 0),
        "description": cj_product.get("description", ""),
        "variants_count": cj_product.get("variants_count", 0),
        "suppliers": [{
            "name": "CJ Dropshipping",
            "country": "CN",
            "rating": 4.3,
            "unit_cost": cj_product["sell_price"],
            "min_order": 1,
            "lead_time_days": 8,
            "shipping_cost": 3.50,
        }],
        # Initial scores — will be calculated
        "trend_score": 50,
        "margin_score": min(100, max(0, round(cj_product.get("estimated_margin", 60)))),
        "competition_score": 50,
        "ad_activity_score": 30,
        "supplier_demand_score": 70,
        "launch_score": 0,
        "launch_score_label": "",
        "launch_score_reasoning": "",
        "tiktok_views": 0,
        "ad_count": 0,
        "competition_level": "unknown",
        "market_saturation": 0,
        "active_competitor_stores": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "imported_by": current_user.user_id,
    }

    # Calculate launch score
    from common.scoring import calculate_launch_score
    score, label, reasoning = calculate_launch_score(product)
    product["launch_score"] = score
    product["launch_score_label"] = label
    product["launch_score_reasoning"] = reasoning

    await db.products.insert_one(product)
    product.pop("_id", None)

    return {
        "success": True,
        "message": f"Imported '{cj_product['product_name']}'",
        "product_id": product_id,
        "launch_score": score,
        "already_existed": False,
    }


routers = [cj_router]
