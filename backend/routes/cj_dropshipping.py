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


@cj_router.get("/supplier-comparison")
async def supplier_comparison(
    q: str = Query(..., min_length=2),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Compare a product across multiple suppliers.
    Returns CJ (live), AliExpress (estimation), and Zendrop (estimation) data.
    """
    from services.api_clients.aliexpress_client import AliExpressClient
    from services.api_clients.zendrop_client import zendrop_client

    suppliers = []

    # CJ Dropshipping (live)
    try:
        cj_result = await search_products(q, page=1, page_size=3)
        if cj_result.get("success") and cj_result.get("products"):
            for p in cj_result["products"][:3]:
                retail = round(p["sell_price"] * 2.5, 2)
                margin = round(((retail - p["sell_price"]) / retail) * 100) if p["sell_price"] > 0 and retail > 0 else 0
                suppliers.append({
                    "source": "cj_dropshipping",
                    "source_label": "CJ Dropshipping",
                    "mode": "live",
                    "product_name": p["product_name"],
                    "image_url": p.get("image_url", ""),
                    "supplier_cost": p["sell_price"],
                    "estimated_retail": retail,
                    "margin_pct": margin,
                    "shipping_days": 8,
                    "shipping_cost": 3.50,
                    "stock_status": p.get("stock_status", "unknown"),
                    "moq": 1,
                    "variants_count": p.get("variants_count", 0),
                    "source_id": p.get("cj_pid", ""),
                    "source_url": p.get("source_url", ""),
                })
    except Exception:
        pass

    # AliExpress (live if configured, else estimation)
    try:
        ali = AliExpressClient()
        ali_products = await ali.search_products(q, limit=3)
        if ali_products:
            for p in ali_products[:3]:
                cost = p.get("supplier_cost", 0)
                retail = round(cost * 2.8, 2) if cost > 0 else 0
                margin = round(((retail - cost) / retail) * 100) if cost > 0 and retail > 0 else 0
                suppliers.append({
                    "source": "aliexpress",
                    "source_label": "AliExpress",
                    "mode": "live",
                    "product_name": p.get("product_name", q),
                    "image_url": p.get("image_url", ""),
                    "supplier_cost": cost,
                    "estimated_retail": retail,
                    "margin_pct": margin,
                    "shipping_days": p.get("shipping_days", 14),
                    "shipping_cost": 0,
                    "stock_status": p.get("availability", "unknown"),
                    "moq": 1,
                    "variants_count": p.get("variants_count", 1),
                    "source_id": p.get("aliexpress_id", ""),
                    "source_url": p.get("product_url", ""),
                    "orders_30d": p.get("orders_30d", 0),
                    "rating": p.get("rating", 0),
                })
        else:
            # Estimation mode
            suppliers.append({
                "source": "aliexpress",
                "source_label": "AliExpress",
                "mode": "estimation",
                "product_name": q,
                "image_url": "",
                "supplier_cost": 0,
                "estimated_retail": 0,
                "margin_pct": 60,
                "shipping_days": 14,
                "shipping_cost": 0,
                "stock_status": "likely_available",
                "moq": 1,
                "variants_count": 0,
                "source_id": "",
                "source_url": f"https://www.aliexpress.com/w/wholesale-{q.replace(' ', '-')}.html",
                "note": "Add ALIEXPRESS_API_KEY to .env for live pricing",
            })
    except Exception:
        pass

    # Zendrop (live if configured, else estimation)
    try:
        zd_products = await zendrop_client.search_products(q, limit=3)
        if zd_products:
            for p in zd_products[:3]:
                cost = float(p.get("price", 0))
                retail = round(cost * 2.5, 2) if cost > 0 else 0
                margin = round(((retail - cost) / retail) * 100) if cost > 0 and retail > 0 else 0
                suppliers.append({
                    "source": "zendrop",
                    "source_label": "Zendrop",
                    "mode": "live",
                    "product_name": p.get("title", q),
                    "image_url": p.get("image_url", ""),
                    "supplier_cost": cost,
                    "estimated_retail": retail,
                    "margin_pct": margin,
                    "shipping_days": 5,
                    "shipping_cost": 3.50,
                    "stock_status": "in_stock" if p.get("in_stock") else "limited",
                    "moq": 1,
                    "variants_count": 0,
                    "source_id": p.get("sku", ""),
                    "source_url": "",
                })
        else:
            # Estimation mode
            suppliers.append({
                "source": "zendrop",
                "source_label": "Zendrop",
                "mode": "estimation",
                "product_name": q,
                "image_url": "",
                "supplier_cost": 0,
                "estimated_retail": 0,
                "margin_pct": 55,
                "shipping_days": 5,
                "shipping_cost": 3.50,
                "stock_status": "likely_available",
                "moq": 1,
                "variants_count": 0,
                "source_id": "",
                "source_url": "https://www.zendrop.com",
                "note": "Add ZENDROP_API_KEY to .env for live pricing",
            })
    except Exception:
        pass

    return {
        "success": True,
        "query": q,
        "suppliers": suppliers,
        "supplier_count": len(suppliers),
    }


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
