"""
Admin — Image refresh tool for products.
Allows regenerating product images using AI image generation.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from datetime import datetime, timezone
import os
import logging
import aiohttp

from auth import get_current_user, AuthenticatedUser
from common.database import db

logger = logging.getLogger(__name__)

admin_images_router = APIRouter(prefix="/api/admin/images")

ADMIN_EMAIL = "jenkinslisa1978@gmail.com"


def _require_admin(user: AuthenticatedUser):
    if user.email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access required")


@admin_images_router.post("/refresh/{product_id}")
async def refresh_product_image(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Refresh a single product's image using AI generation.
    Searches for a relevant image from Pexels based on product name.
    """
    _require_admin(current_user)

    product = await db.products.find_one(
        {"id": product_id},
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "image_url": 1},
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Use Pexels API to find a relevant image
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if not pexels_key:
        # Fallback: just acknowledge the request
        return {
            "success": False,
            "message": "No PEXELS_API_KEY configured. Set this environment variable to enable image refresh.",
            "product_id": product_id,
        }

    search_query = product["product_name"].split(" - ")[0].split(",")[0][:50]
    new_url = await _search_pexels_image(pexels_key, search_query)

    if new_url:
        await db.products.update_one(
            {"id": product_id},
            {"$set": {
                "image_url": new_url,
                "image_refreshed_at": datetime.now(timezone.utc).isoformat(),
            }},
        )
        return {
            "success": True,
            "product_id": product_id,
            "product_name": product["product_name"],
            "old_image": product.get("image_url", ""),
            "new_image": new_url,
        }

    return {
        "success": False,
        "message": f"No matching image found for '{search_query}'",
        "product_id": product_id,
    }


@admin_images_router.post("/refresh-batch")
async def refresh_batch_images(
    background_tasks: BackgroundTasks,
    category: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Queue a batch image refresh for products.
    Optionally filter by category.
    """
    _require_admin(current_user)

    query = {}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}

    count = await db.products.count_documents(query)

    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if not pexels_key:
        return {
            "success": False,
            "message": "No PEXELS_API_KEY configured. Set this environment variable to enable image refresh.",
        }

    background_tasks.add_task(_batch_refresh_images, pexels_key, query)

    return {
        "success": True,
        "message": f"Queued image refresh for {count} products",
        "category": category or "all",
    }


@admin_images_router.get("/stats")
async def image_stats(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get statistics about product images."""
    _require_admin(current_user)

    total = await db.products.count_documents({})
    has_image = await db.products.count_documents({"image_url": {"$ne": "", "$exists": True, "$ne": None}})
    no_image = total - has_image
    refreshed = await db.products.count_documents({"image_refreshed_at": {"$exists": True}})

    return {
        "total_products": total,
        "with_images": has_image,
        "without_images": no_image,
        "recently_refreshed": refreshed,
    }


async def _search_pexels_image(api_key: str, query: str) -> str:
    """Search Pexels for a product image."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.pexels.com/v1/search",
                params={"query": query, "per_page": 1, "size": "medium"},
                headers={"Authorization": api_key},
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    photos = data.get("photos", [])
                    if photos:
                        return photos[0]["src"]["medium"]
    except Exception as e:
        logger.error(f"Pexels search failed: {e}")
    return ""


async def _batch_refresh_images(api_key: str, query: dict):
    """Background task to refresh images for multiple products."""
    products = await db.products.find(
        query,
        {"_id": 0, "id": 1, "product_name": 1},
    ).to_list(500)

    updated = 0
    for product in products:
        search = product["product_name"].split(" - ")[0].split(",")[0][:50]
        new_url = await _search_pexels_image(api_key, search)
        if new_url:
            await db.products.update_one(
                {"id": product["id"]},
                {"$set": {
                    "image_url": new_url,
                    "image_refreshed_at": datetime.now(timezone.utc).isoformat(),
                }},
            )
            updated += 1

    logger.info(f"Batch image refresh: updated {updated}/{len(products)} products")


routers = [admin_images_router]
