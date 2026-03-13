from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
import logging

from auth import get_current_user, AuthenticatedUser
from common.database import db

logger = logging.getLogger(__name__)

connections_router = APIRouter(prefix="/api/connections")


# ==================== MODELS ====================

class StoreConnectionRequest(BaseModel):
    platform: str  # shopify, woocommerce, etsy, bigcommerce, squarespace
    store_url: str
    api_key: str
    api_secret: Optional[str] = None
    access_token: Optional[str] = None

class AdConnectionRequest(BaseModel):
    platform: str  # meta, tiktok, google
    access_token: str
    account_id: Optional[str] = None
    pixel_id: Optional[str] = None

class DisconnectRequest(BaseModel):
    platform: str
    connection_type: str  # store or ads


# ==================== STORE CONNECTIONS ====================

SUPPORTED_STORES = {
    "shopify": {
        "name": "Shopify",
        "fields": ["store_url", "access_token"],
        "help": "Go to your Shopify Admin → Settings → Apps → Develop apps → Create an app → Get API access token",
        "url": "https://admin.shopify.com",
    },
    "woocommerce": {
        "name": "WooCommerce",
        "fields": ["store_url", "api_key", "api_secret"],
        "help": "Go to your WordPress Admin → WooCommerce → Settings → Advanced → REST API → Add key",
        "url": "https://woocommerce.com",
    },
    "etsy": {
        "name": "Etsy",
        "fields": ["store_url", "api_key", "access_token"],
        "help": "Go to etsy.com/developers → Create a new app → Get your API key (Keystring) and OAuth2 access token. Your Shop ID is in your shop URL (e.g. etsy.com/shop/YourShop → use the numeric Shop ID from Shop Manager).",
        "url": "https://www.etsy.com/developers",
    },
    "bigcommerce": {
        "name": "BigCommerce",
        "fields": ["store_url", "api_key", "access_token"],
        "help": "Go to your BigCommerce Admin → Advanced Settings → API Accounts → Create API Account",
        "url": "https://www.bigcommerce.com",
    },
    "squarespace": {
        "name": "Squarespace",
        "fields": ["store_url", "api_key"],
        "help": "Go to your Squarespace Admin → Settings → Advanced → Developer API Keys",
        "url": "https://www.squarespace.com",
    },
}

SUPPORTED_AD_PLATFORMS = {
    "meta": {
        "name": "Meta (Facebook & Instagram)",
        "fields": ["access_token", "account_id", "pixel_id"],
        "help": "Go to business.facebook.com → Business Settings → Users → System Users → Generate token. Get Ad Account ID from Ads Manager.",
        "url": "https://business.facebook.com",
    },
    "tiktok": {
        "name": "TikTok Ads",
        "fields": ["access_token", "account_id"],
        "help": "Go to ads.tiktok.com → Assets → Developer → Create an app → Get access token and Advertiser ID",
        "url": "https://ads.tiktok.com",
    },
    "google": {
        "name": "Google Ads",
        "fields": ["access_token", "account_id"],
        "help": "Go to ads.google.com → Tools → API Centre → Get your developer token and customer ID",
        "url": "https://ads.google.com",
    },
}


@connections_router.get("/platforms")
async def get_supported_platforms():
    """Get all supported platforms for stores and ads"""
    return {
        "stores": {k: {"name": v["name"], "fields": v["fields"], "help": v["help"], "url": v["url"]} for k, v in SUPPORTED_STORES.items()},
        "ads": {k: {"name": v["name"], "fields": v["fields"], "help": v["help"], "url": v["url"]} for k, v in SUPPORTED_AD_PLATFORMS.items()},
    }


@connections_router.get("/")
async def get_user_connections(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get all platform connections for the current user"""
    user_id = current_user.user_id
    connections = await db.platform_connections.find(
        {"user_id": user_id}, {"_id": 0}
    ).to_list(50)

    store_connections = [c for c in connections if c.get("connection_type") == "store"]
    ad_connections = [c for c in connections if c.get("connection_type") == "ads"]

    return {
        "stores": [
            {
                "platform": c["platform"],
                "name": SUPPORTED_STORES.get(c["platform"], {}).get("name", c["platform"]),
                "store_url": c.get("store_url", ""),
                "connected": True,
                "connected_at": c.get("connected_at"),
                "status": c.get("status", "active"),
            }
            for c in store_connections
        ],
        "ads": [
            {
                "platform": c["platform"],
                "name": SUPPORTED_AD_PLATFORMS.get(c["platform"], {}).get("name", c["platform"]),
                "connected": True,
                "connected_at": c.get("connected_at"),
                "status": c.get("status", "active"),
                "account_id": c.get("account_id", ""),
            }
            for c in ad_connections
        ],
    }


@connections_router.post("/store")
async def connect_store(
    req: StoreConnectionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Connect an e-commerce store platform"""
    user_id = current_user.user_id

    if req.platform not in SUPPORTED_STORES:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {req.platform}. Supported: {list(SUPPORTED_STORES.keys())}")

    # Upsert the connection
    connection = {
        "user_id": user_id,
        "connection_type": "store",
        "platform": req.platform,
        "store_url": req.store_url.rstrip("/"),
        "api_key": req.api_key,
        "api_secret": req.api_secret,
        "access_token": req.access_token,
        "status": "active",
        "connected_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.platform_connections.update_one(
        {"user_id": user_id, "platform": req.platform, "connection_type": "store"},
        {"$set": connection},
        upsert=True,
    )

    logger.info(f"User {user_id} connected {req.platform} store: {req.store_url}")

    return {
        "success": True,
        "platform": req.platform,
        "store_url": req.store_url,
        "message": f"{SUPPORTED_STORES[req.platform]['name']} connected successfully",
    }


@connections_router.post("/ads")
async def connect_ad_platform(
    req: AdConnectionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Connect an advertising platform"""
    user_id = current_user.user_id

    if req.platform not in SUPPORTED_AD_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {req.platform}. Supported: {list(SUPPORTED_AD_PLATFORMS.keys())}")

    connection = {
        "user_id": user_id,
        "connection_type": "ads",
        "platform": req.platform,
        "access_token": req.access_token,
        "account_id": req.account_id,
        "pixel_id": req.pixel_id,
        "status": "active",
        "connected_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.platform_connections.update_one(
        {"user_id": user_id, "platform": req.platform, "connection_type": "ads"},
        {"$set": connection},
        upsert=True,
    )

    logger.info(f"User {user_id} connected {req.platform} ads: account={req.account_id}")

    return {
        "success": True,
        "platform": req.platform,
        "message": f"{SUPPORTED_AD_PLATFORMS[req.platform]['name']} connected successfully",
    }


@connections_router.delete("/{connection_type}/{platform}")
async def disconnect_platform(
    connection_type: str,
    platform: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Disconnect a platform"""
    user_id = current_user.user_id

    result = await db.platform_connections.delete_one(
        {"user_id": user_id, "platform": platform, "connection_type": connection_type}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Connection not found")

    return {"success": True, "message": f"{platform} disconnected"}


from services.platform_integrations import (
    publish_to_shopify,
    publish_to_woocommerce,
    publish_to_etsy,
    publish_to_bigcommerce,
    publish_to_squarespace,
    post_ads_to_meta,
    post_ads_to_tiktok,
    post_ads_to_google,
)


@connections_router.post("/publish/{store_id}")
async def auto_publish_to_store(
    store_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Auto-publish a TrendScout store to the user's connected e-commerce platform"""
    user_id = current_user.user_id

    store_conn = await db.platform_connections.find_one(
        {"user_id": user_id, "connection_type": "store", "status": "active"},
        {"_id": 0},
    )

    if not store_conn:
        raise HTTPException(
            status_code=400,
            detail="No store platform connected. Go to Settings → Platform Connections to connect your store.",
        )

    store = await db.stores.find_one({"id": store_id, "owner_id": user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    store_products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    if not store_products:
        # Fall back to main product
        product = await db.products.find_one({"id": store.get("product_id")}, {"_id": 0})
        store_products = [product] if product else []

    platform = store_conn["platform"]
    store_url = store_conn.get("store_url", "")

    # Call real API based on platform
    api_result = None
    try:
        if platform == "shopify":
            api_result = await publish_to_shopify(
                store_url=store_url,
                access_token=store_conn.get("access_token", ""),
                product=store,
                products=store_products,
            )
        elif platform == "woocommerce":
            api_result = await publish_to_woocommerce(
                store_url=store_url,
                api_key=store_conn.get("api_key", ""),
                api_secret=store_conn.get("api_secret", ""),
                products=store_products,
            )
        elif platform == "etsy":
            api_result = await publish_to_etsy(
                api_key=store_conn.get("api_key", ""),
                access_token=store_conn.get("access_token", ""),
                shop_id=store_conn.get("store_url", ""),
                products=store_products,
            )
        elif platform == "bigcommerce":
            api_result = await publish_to_bigcommerce(
                store_url=store_url,
                api_key=store_conn.get("api_key", ""),
                access_token=store_conn.get("access_token", ""),
                products=store_products,
            )
        elif platform == "squarespace":
            api_result = await publish_to_squarespace(
                store_url=store_url,
                api_key=store_conn.get("api_key", ""),
                products=store_products,
            )
        else:
            api_result = {
                "platform": platform,
                "total_created": len(store_products),
                "message": f"Product data prepared for {SUPPORTED_STORES.get(platform,{}).get('name', platform)}.",
                "products": [{"title": p.get("product_name", p.get("title", "")), "success": True} for p in store_products],
            }
    except Exception as e:
        logger.error(f"Publish to {platform} failed: {e}")
        api_result = {"platform": platform, "total_created": 0, "error": str(e)}

    # Update store status
    await db.stores.update_one(
        {"id": store_id},
        {
            "$set": {
                "status": "published",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "published_to": platform,
                "published_store_url": store_url,
                "publish_result": api_result,
            }
        },
    )

    return {
        "success": True,
        "platform": platform,
        "store_url": store_url,
        "products_published": api_result.get("total_created", len(store_products)),
        "api_result": api_result,
        "message": api_result.get("message", f"Published to {platform}"),
    }


@connections_router.post("/post-ads/{product_id}")
async def auto_post_ads(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Auto-post generated ad creatives to the user's connected ad platforms using real APIs"""
    user_id = current_user.user_id

    ad_conns = await db.platform_connections.find(
        {"user_id": user_id, "connection_type": "ads", "status": "active"},
        {"_id": 0},
    ).to_list(10)

    if not ad_conns:
        raise HTTPException(
            status_code=400,
            detail="No ad platform connected. Go to Settings → Platform Connections to connect your ad account.",
        )

    # Get ad creatives
    creative_doc = await db.ad_creatives.find_one(
        {"product_id": product_id}, {"_id": 0}
    )

    if not creative_doc:
        raise HTTPException(status_code=404, detail="No ad creatives found. Generate ads first.")

    # Get product data
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    creatives = creative_doc.get("creatives", [])

    # Get user's store URL for ad links
    store_conn = await db.platform_connections.find_one(
        {"user_id": user_id, "connection_type": "store", "status": "active"},
        {"_id": 0},
    )
    store_url = store_conn.get("store_url", "") if store_conn else ""

    posted_to = []
    for conn in ad_conns:
        platform = conn["platform"]
        platform_name = SUPPORTED_AD_PLATFORMS.get(platform, {}).get("name", platform)

        # Call real API based on platform
        api_result = None
        try:
            if platform == "meta":
                api_result = await post_ads_to_meta(
                    access_token=conn.get("access_token", ""),
                    account_id=conn.get("account_id", ""),
                    product=product,
                    creatives=creatives,
                    store_url=store_url,
                )
            elif platform == "tiktok":
                api_result = await post_ads_to_tiktok(
                    access_token=conn.get("access_token", ""),
                    account_id=conn.get("account_id", ""),
                    product=product,
                    creatives=creatives,
                )
            elif platform == "google":
                api_result = await post_ads_to_google(
                    access_token=conn.get("access_token", ""),
                    account_id=conn.get("account_id", ""),
                    product=product,
                    creatives=creatives,
                )
        except Exception as e:
            logger.error(f"Post ads to {platform} failed: {e}")
            api_result = {"platform": platform, "success": False, "error": str(e)}

        # Record the posting
        await db.ad_postings.insert_one({
            "user_id": user_id,
            "product_id": product_id,
            "platform": platform,
            "account_id": conn.get("account_id"),
            "creatives_count": len(creatives),
            "status": "submitted" if api_result and api_result.get("success") else "failed",
            "api_result": api_result,
            "posted_at": datetime.now(timezone.utc).isoformat(),
        })

        posted_to.append({
            "platform": platform,
            "name": platform_name,
            "success": api_result.get("success", False) if api_result else False,
            "message": api_result.get("message", "") if api_result else "Failed",
            "campaign_id": api_result.get("campaign_id") if api_result else None,
        })

    return {
        "success": True,
        "posted_to": posted_to,
        "creatives_count": len(creatives),
        "message": f"Ads processed for {len(posted_to)} platform(s)",
    }


routers = [connections_router]
