"""
Multi-platform product sync endpoints.
Handles syncing products from Etsy, WooCommerce, and other connected stores.
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import httpx
import logging

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.encryption import decrypt_token

logger = logging.getLogger(__name__)

platform_sync_router = APIRouter(prefix="/api/sync")


async def _get_connection(user_id: str, platform: str):
    """Get active connection for a user and platform."""
    conn = await db.platform_connections.find_one(
        {"user_id": user_id, "platform": platform, "status": "active"},
        {"_id": 0},
    )
    if not conn:
        raise HTTPException(status_code=404, detail=f"No active {platform} connection found")
    return conn


async def _decrypt_access_token(conn: dict) -> str:
    """Safely decrypt an access token from a connection."""
    token = conn.get("access_token", "")
    if not token:
        raise HTTPException(status_code=400, detail="Connection has no access token")
    try:
        return decrypt_token(token)
    except Exception:
        return token


# ==================== UNIFIED SYNCED PRODUCTS ====================

@platform_sync_router.get("/products")
async def get_all_synced_products(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get all synced products across all platforms for the current user."""
    products = []
    cursor = db.synced_products.find(
        {"user_id": current_user.user_id},
        {"_id": 0},
    ).sort("synced_at", -1).limit(500)
    async for doc in cursor:
        products.append(doc)

    # Group by platform
    by_platform = {}
    for p in products:
        plat = p.get("platform", "unknown")
        if plat not in by_platform:
            by_platform[plat] = []
        by_platform[plat].append(p)

    return {
        "success": True,
        "products": products,
        "total": len(products),
        "by_platform": {k: len(v) for k, v in by_platform.items()},
    }


# ==================== ETSY SYNC ====================

@platform_sync_router.post("/etsy/products")
async def sync_etsy_products(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Sync products from connected Etsy shop."""
    conn = await _get_connection(current_user.user_id, "etsy")
    access_token = await _decrypt_access_token(conn)
    shop_id = conn.get("shop_id") or conn.get("store_url", "")

    if not shop_id:
        raise HTTPException(status_code=400, detail="Etsy shop ID not found in connection")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/active",
                headers={"Authorization": f"Bearer {access_token}", "x-api-key": conn.get("client_id", "")},
                params={"limit": 100},
            )

            if resp.status_code == 401:
                await db.platform_connections.update_one(
                    {"user_id": current_user.user_id, "platform": "etsy"},
                    {"$set": {"status": "expired"}},
                )
                raise HTTPException(status_code=401, detail="Etsy token expired. Please reconnect.")

            if resp.status_code != 200:
                logger.warning(f"Etsy API error: {resp.status_code} - {resp.text[:200]}")
                raise HTTPException(status_code=502, detail="Failed to fetch products from Etsy")

            data = resp.json()
            listings = data.get("results", [])

        synced = 0
        for listing in listings:
            product_doc = {
                "user_id": current_user.user_id,
                "platform": "etsy",
                "platform_id": str(listing.get("listing_id", "")),
                "title": listing.get("title", ""),
                "description": listing.get("description", "")[:500],
                "price": str(listing.get("price", {}).get("amount", 0) / listing.get("price", {}).get("divisor", 100)),
                "currency": listing.get("price", {}).get("currency_code", "GBP"),
                "status": listing.get("state", "active"),
                "quantity": listing.get("quantity", 0),
                "tags": listing.get("tags", []),
                "url": listing.get("url", ""),
                "image_url": "",
                "shop_name": conn.get("shop_name", shop_id),
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }

            await db.synced_products.update_one(
                {"user_id": current_user.user_id, "platform": "etsy", "platform_id": product_doc["platform_id"]},
                {"$set": product_doc},
                upsert=True,
            )
            synced += 1

        return {"success": True, "synced_count": synced, "platform": "etsy", "shop": shop_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Etsy sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Etsy sync failed: {str(e)}")


# ==================== WOOCOMMERCE SYNC ====================

@platform_sync_router.post("/woocommerce/products")
async def sync_woocommerce_products(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Sync products from connected WooCommerce store."""
    conn = await _get_connection(current_user.user_id, "woocommerce")
    store_url = conn.get("store_url", "").rstrip("/")

    if not store_url:
        raise HTTPException(status_code=400, detail="WooCommerce store URL not found")

    api_key = conn.get("api_key", "")
    api_secret = conn.get("api_secret", "")

    if not api_key or not api_secret:
        # Try encrypted tokens
        try:
            api_key = decrypt_token(api_key) if api_key else ""
            api_secret = decrypt_token(api_secret) if api_secret else ""
        except Exception:
            pass

    if not api_key or not api_secret:
        raise HTTPException(status_code=400, detail="WooCommerce API credentials not found")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{store_url}/wp-json/wc/v3/products",
                auth=(api_key, api_secret),
                params={"per_page": 100, "status": "publish"},
            )

            if resp.status_code == 401:
                raise HTTPException(status_code=401, detail="WooCommerce credentials invalid. Please reconnect.")

            if resp.status_code != 200:
                logger.warning(f"WooCommerce API error: {resp.status_code}")
                raise HTTPException(status_code=502, detail="Failed to fetch products from WooCommerce")

            products = resp.json()

        synced = 0
        for prod in products:
            images = prod.get("images", [])
            product_doc = {
                "user_id": current_user.user_id,
                "platform": "woocommerce",
                "platform_id": str(prod.get("id", "")),
                "title": prod.get("name", ""),
                "description": prod.get("short_description", "")[:500],
                "price": prod.get("price", "0"),
                "currency": "GBP",
                "status": prod.get("status", "publish"),
                "quantity": prod.get("stock_quantity") or 0,
                "categories": [c.get("name", "") for c in prod.get("categories", [])],
                "url": prod.get("permalink", ""),
                "image_url": images[0].get("src", "") if images else "",
                "shop_name": store_url.replace("https://", "").replace("http://", ""),
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }

            await db.synced_products.update_one(
                {"user_id": current_user.user_id, "platform": "woocommerce", "platform_id": product_doc["platform_id"]},
                {"$set": product_doc},
                upsert=True,
            )
            synced += 1

        return {"success": True, "synced_count": synced, "platform": "woocommerce", "shop": store_url}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WooCommerce sync error: {e}")
        raise HTTPException(status_code=500, detail=f"WooCommerce sync failed: {str(e)}")


# ==================== AMAZON SYNC ====================

@platform_sync_router.post("/amazon/products")
async def sync_amazon_products(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Sync products from connected Amazon Seller account."""
    conn = await _get_connection(current_user.user_id, "amazon_seller")
    access_token = await _decrypt_access_token(conn)

    # Amazon SP-API is complex - return placeholder for now
    return {
        "success": True,
        "synced_count": 0,
        "platform": "amazon_seller",
        "message": "Amazon SP-API sync is in beta. Products will appear here once available.",
    }


# ==================== SYNC HISTORY ====================

@platform_sync_router.get("/history")
async def get_sync_history(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get sync history for the current user."""
    history = []
    cursor = db.sync_history.find(
        {"user_id": current_user.user_id},
        {"_id": 0},
    ).sort("completed_at", -1).limit(50)
    async for doc in cursor:
        history.append(doc)

    return {"success": True, "history": history, "total": len(history)}


@platform_sync_router.get("/history/summary")
async def get_sync_summary(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get a summary of sync activity across all platforms."""
    # Get latest sync per platform
    pipeline = [
        {"$match": {"user_id": current_user.user_id}},
        {"$sort": {"completed_at": -1}},
        {"$group": {
            "_id": "$platform",
            "last_sync": {"$first": "$completed_at"},
            "last_status": {"$first": "$status"},
            "last_count": {"$first": "$synced_count"},
            "total_syncs": {"$sum": 1},
            "total_products": {"$sum": "$synced_count"},
            "error_count": {"$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}},
        }},
    ]
    summaries = {}
    async for doc in db.sync_history.aggregate(pipeline):
        plat = doc["_id"]
        summaries[plat] = {
            "platform": plat,
            "last_sync": doc["last_sync"],
            "last_status": doc["last_status"],
            "last_count": doc["last_count"],
            "total_syncs": doc["total_syncs"],
            "total_products": doc["total_products"],
            "error_count": doc["error_count"],
        }

    # Count synced products per platform
    product_pipeline = [
        {"$match": {"user_id": current_user.user_id}},
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
    ]
    async for doc in db.synced_products.aggregate(product_pipeline):
        plat = doc["_id"]
        if plat in summaries:
            summaries[plat]["current_products"] = doc["count"]

    return {"success": True, "summary": summaries}


# ==================== MANUAL SYNC WITH HISTORY LOGGING ====================

async def _log_sync(user_id: str, platform: str, shop: str, count: int, error: str = None):
    """Log a sync event to history."""
    await db.sync_history.insert_one({
        "user_id": user_id,
        "platform": platform,
        "shop": shop,
        "synced_count": count,
        "status": "success" if not error else "error",
        "error": error,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "trigger": "manual",
    })


routers = [platform_sync_router]
