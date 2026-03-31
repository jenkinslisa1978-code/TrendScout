"""
Avasam UK Supplier API routes — product sourcing and supplier enrichment.
Mirrors the CJ Dropshipping route structure.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import Optional
from datetime import datetime, timezone

from auth import get_current_user, AuthenticatedUser
from common.database import db
from services.avasam import search_products, get_product_detail, get_categories, get_stock

avasam_router = APIRouter(prefix="/api/avasam")


@avasam_router.get("/search")
async def avasam_search(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    category_id: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Search Avasam for products by name."""
    result = await search_products(q, page, page_size, category_id or "")
    return result


@avasam_router.get("/product/{product_id}")
async def avasam_product_detail(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get detailed product info from Avasam."""
    result = await get_product_detail(product_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Product not found"))
    return result


@avasam_router.get("/categories")
async def avasam_categories(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get Avasam product categories."""
    return await get_categories()


@avasam_router.get("/stock/{product_id}")
async def avasam_stock(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get live stock levels for an Avasam product."""
    result = await get_stock(product_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Stock not found"))
    return result


@avasam_router.post("/import/{product_id}")
async def import_avasam_product(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Import an Avasam product into TrendScout for tracking and analysis.
    Fetches live data from Avasam and creates a product entry.
    """
    # Check if already imported
    existing = await db.products.find_one(
        {"avasam_pid": product_id},
        {"_id": 0, "id": 1, "product_name": 1},
    )
    if existing:
        return {"success": True, "message": "Product already imported", "product_id": existing["id"], "already_existed": True}

    # Fetch from Avasam
    result = await get_product_detail(product_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Could not fetch product from Avasam"))

    avasam_product = result["product"]
    import uuid

    product_id_internal = str(uuid.uuid4())
    sell_price = avasam_product.get("sell_price", 0)
    supplier_cost = avasam_product.get("supplier_cost", 0)
    retail_price = sell_price if sell_price > 0 else round(supplier_cost * 2.5, 2)
    margin = round(((retail_price - supplier_cost) / retail_price) * 100, 1) if retail_price > 0 and supplier_cost > 0 else 0

    product = {
        "id": product_id_internal,
        "avasam_pid": avasam_product["avasam_pid"],
        "product_name": avasam_product["product_name"],
        "slug": avasam_product["product_name"].lower().replace(" ", "-")[:80],
        "category": avasam_product["category"],
        "image_url": avasam_product["image_url"],
        "images": avasam_product.get("images", []),
        "estimated_retail_price": retail_price,
        "estimated_cost": supplier_cost,
        "estimated_margin": margin,
        "supplier_cost": supplier_cost,
        "currency": avasam_product.get("currency", "GBP"),
        "data_source": "avasam",
        "source_url": avasam_product.get("source_url", ""),
        "stock_status": avasam_product.get("stock_status", "in_stock"),
        "shipping_weight": avasam_product.get("shipping_weight", 0),
        "description": avasam_product.get("description", ""),
        "variants_count": avasam_product.get("variants_count", 0),
        "sku": avasam_product.get("sku", ""),
        "brand": avasam_product.get("brand", ""),
        "ean": avasam_product.get("ean", ""),
        "suppliers": [{
            "name": "Avasam",
            "country": "GB",
            "rating": 4.5,
            "unit_cost": supplier_cost,
            "min_order": 1,
            "lead_time_days": 2,
            "shipping_cost": 0,
        }],
        # Initial scores
        "trend_score": 55,
        "margin_score": min(100, max(0, round(margin))),
        "competition_score": 50,
        "ad_activity_score": 30,
        "supplier_demand_score": 75,
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
        "message": f"Imported '{avasam_product['product_name']}'",
        "product_id": product_id_internal,
        "launch_score": score,
        "already_existed": False,
    }


@avasam_router.post("/sync")
async def trigger_avasam_sync(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Manually trigger an Avasam product sync.
    Accepts API key (for cron-job.org).
    """
    expected_key = os.environ.get("AUTOMATION_API_KEY", "vs_automation_key_2024")
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    from services.jobs.tasks import sync_avasam_products
    result = await sync_avasam_products(db, {})
    return {
        "success": True,
        "message": f"Avasam sync complete: {result['details']['created']} new products imported",
        **result,
    }


@avasam_router.get("/sync/history")
async def avasam_sync_history(
    limit: int = Query(10, ge=1, le=50),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get Avasam sync run history."""
    cursor = db.automation_logs.find(
        {"job_name": "sync_avasam_products"},
        {"_id": 0},
    ).sort("run_time", -1).limit(limit)
    logs = await cursor.to_list(limit)
    return {"success": True, "history": logs}


routers = [avasam_router]
