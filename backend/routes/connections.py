from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
import logging
import httpx

from auth import get_current_user, AuthenticatedUser
from common.database import db

logger = logging.getLogger(__name__)

connections_router = APIRouter(prefix="/api/connections")


# ==================== MODELS ====================

class StoreConnectionRequest(BaseModel):
    platform: str  # shopify, woocommerce, etsy, bigcommerce, squarespace
    store_url: str
    api_key: Optional[str] = None
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

SUPPORTED_SUPPLIERS = {
    "aliexpress": {
        "name": "AliExpress",
        "fields": ["api_key", "api_secret"],
        "help": "Register at portals.aliexpress.com → Create an app → Get your App Key and App Secret from the API console.",
        "url": "https://portals.aliexpress.com",
    },
    "cj_dropshipping": {
        "name": "CJ Dropshipping",
        "fields": ["api_key"],
        "help": "Log in to cjdropshipping.com → My CJ → API Management → Generate your API Key.",
        "url": "https://cjdropshipping.com",
    },
    "zendrop": {
        "name": "Zendrop",
        "fields": ["api_key"],
        "help": "Log in to app.zendrop.com → Settings → API → Generate API Key.",
        "url": "https://app.zendrop.com",
    },
}

SUPPORTED_SOCIAL = {
    "tiktok_shop": {
        "name": "TikTok Shop",
        "fields": ["store_url", "api_key", "api_secret"],
        "help": "Go to seller.tiktok.com → Settings → Developer → Create an app → Get your App Key and App Secret.",
        "url": "https://seller.tiktok.com",
    },
    "instagram_shopping": {
        "name": "Instagram Shopping",
        "fields": ["access_token", "account_id"],
        "help": "Connect via business.facebook.com → Commerce Manager → Link your Instagram account and generate a token.",
        "url": "https://business.facebook.com/commerce",
    },
    "amazon_seller": {
        "name": "Amazon Seller",
        "fields": ["store_url", "api_key", "api_secret"],
        "help": "Go to sellercentral.amazon.co.uk → Settings → User Permissions → Developer → Get your SP-API credentials.",
        "url": "https://sellercentral.amazon.co.uk",
    },
}


@connections_router.get("/platforms")
async def get_supported_platforms():
    """Get all supported platforms for stores, ads, suppliers, and social"""
    return {
        "stores": {k: {"name": v["name"], "fields": v["fields"], "help": v["help"], "url": v["url"]} for k, v in SUPPORTED_STORES.items()},
        "ads": {k: {"name": v["name"], "fields": v["fields"], "help": v["help"], "url": v["url"]} for k, v in SUPPORTED_AD_PLATFORMS.items()},
        "suppliers": {k: {"name": v["name"], "fields": v["fields"], "help": v["help"], "url": v["url"]} for k, v in SUPPORTED_SUPPLIERS.items()},
        "social": {k: {"name": v["name"], "fields": v["fields"], "help": v["help"], "url": v["url"]} for k, v in SUPPORTED_SOCIAL.items()},
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
    supplier_connections = [c for c in connections if c.get("connection_type") == "supplier"]
    social_connections = [c for c in connections if c.get("connection_type") == "social"]

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
        "suppliers": [
            {
                "platform": c["platform"],
                "name": SUPPORTED_SUPPLIERS.get(c["platform"], {}).get("name", c["platform"]),
                "connected": True,
                "connected_at": c.get("connected_at"),
                "status": c.get("status", "active"),
            }
            for c in supplier_connections
        ],
        "social": [
            {
                "platform": c["platform"],
                "name": SUPPORTED_SOCIAL.get(c["platform"], {}).get("name", c["platform"]),
                "connected": True,
                "connected_at": c.get("connected_at"),
                "status": c.get("status", "active"),
                "store_url": c.get("store_url", ""),
            }
            for c in social_connections
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

    # Verify Shopify token before saving
    if req.platform == "shopify":
        if not req.access_token:
            return JSONResponse(content={"success": False, "error": {"code": "VALIDATION", "message": "Admin API access token is required for Shopify"}})
        domain = req.store_url.replace("https://", "").replace("http://", "").rstrip("/")
        if not domain.endswith(".myshopify.com"):
            domain = f"{domain}.myshopify.com"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"https://{domain}/admin/api/2024-01/shop.json",
                    headers={"X-Shopify-Access-Token": req.access_token},
                )
            if resp.status_code == 401:
                return JSONResponse(content={"success": False, "error": {"code": "AUTH_FAILED", "message": "Invalid access token. Please check your token and try again."}})
            if resp.status_code == 404:
                return JSONResponse(content={"success": False, "error": {"code": "NOT_FOUND", "message": f"Store '{domain}' not found. Please check your store domain."}})
            if resp.status_code != 200:
                return JSONResponse(content={"success": False, "error": {"code": "SHOPIFY_ERROR", "message": f"Could not verify store connection (Shopify returned {resp.status_code})"}})
            shop_data = resp.json().get("shop", {})
            logger.info(f"Verified Shopify store: {shop_data.get('name', domain)}")
        except httpx.RequestError:
            return JSONResponse(content={"success": False, "error": {"code": "UNREACHABLE", "message": f"Could not reach Shopify store '{domain}'. Please check the domain."}})

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


class SupplierConnectionRequest(BaseModel):
    platform: str  # aliexpress, cj_dropshipping, zendrop
    api_key: str
    api_secret: Optional[str] = None


class SocialConnectionRequest(BaseModel):
    platform: str  # tiktok_shop, instagram_shopping, amazon_seller
    store_url: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    account_id: Optional[str] = None


@connections_router.post("/supplier")
async def connect_supplier(
    req: SupplierConnectionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Connect a supplier platform"""
    user_id = current_user.user_id

    if req.platform not in SUPPORTED_SUPPLIERS:
        raise HTTPException(status_code=400, detail=f"Unsupported supplier: {req.platform}. Supported: {list(SUPPORTED_SUPPLIERS.keys())}")

    connection = {
        "user_id": user_id,
        "connection_type": "supplier",
        "platform": req.platform,
        "api_key": req.api_key,
        "api_secret": req.api_secret,
        "status": "active",
        "connected_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.platform_connections.update_one(
        {"user_id": user_id, "platform": req.platform, "connection_type": "supplier"},
        {"$set": connection},
        upsert=True,
    )

    logger.info(f"User {user_id} connected supplier: {req.platform}")

    return {
        "success": True,
        "platform": req.platform,
        "message": f"{SUPPORTED_SUPPLIERS[req.platform]['name']} connected successfully",
    }


@connections_router.post("/social")
async def connect_social(
    req: SocialConnectionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Connect a social/marketplace platform"""
    user_id = current_user.user_id

    if req.platform not in SUPPORTED_SOCIAL:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {req.platform}. Supported: {list(SUPPORTED_SOCIAL.keys())}")

    connection = {
        "user_id": user_id,
        "connection_type": "social",
        "platform": req.platform,
        "store_url": req.store_url,
        "api_key": req.api_key,
        "api_secret": req.api_secret,
        "access_token": req.access_token,
        "account_id": req.account_id,
        "status": "active",
        "connected_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.platform_connections.update_one(
        {"user_id": user_id, "platform": req.platform, "connection_type": "social"},
        {"$set": connection},
        upsert=True,
    )

    logger.info(f"User {user_id} connected social: {req.platform}")

    return {
        "success": True,
        "platform": req.platform,
        "message": f"{SUPPORTED_SOCIAL[req.platform]['name']} connected successfully",
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


# ==================== CONNECTION HEALTH CHECK ====================

@connections_router.post("/health-check")
async def check_connection_health(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Verify all connected platforms are still accessible.
    Pings each connected platform API with a lightweight request.
    """
    user_id = current_user.user_id
    connections = await db.platform_connections.find(
        {"user_id": user_id, "status": "active"}, {"_id": 0}
    ).to_list(20)

    if not connections:
        return {"results": [], "message": "No connected platforms"}

    import httpx
    import base64

    results = []
    async with httpx.AsyncClient(timeout=10) as client:
        for conn in connections:
            platform = conn["platform"]
            conn_type = conn["connection_type"]
            status = "unknown"
            message = ""

            try:
                if platform == "shopify":
                    url = f"https://{conn.get('store_url', '').rstrip('/')}/admin/api/2024-07/shop.json"
                    r = await client.get(url, headers={"X-Shopify-Access-Token": conn.get("access_token", "")})
                    status = "healthy" if r.status_code == 200 else "error"
                    message = "Store accessible" if status == "healthy" else f"HTTP {r.status_code}"

                elif platform == "woocommerce":
                    base = conn.get("store_url", "").rstrip("/")
                    if not base.startswith("http"):
                        base = f"https://{base}"
                    auth = base64.b64encode(f"{conn.get('api_key', '')}:{conn.get('api_secret', '')}".encode()).decode()
                    r = await client.get(f"{base}/wp-json/wc/v3/system_status", headers={"Authorization": f"Basic {auth}"})
                    status = "healthy" if r.status_code == 200 else "error"
                    message = "Store accessible" if status == "healthy" else f"HTTP {r.status_code}"

                elif platform == "etsy":
                    r = await client.get(
                        f"https://openapi.etsy.com/v3/application/shops/{conn.get('store_url', '')}",
                        headers={"x-api-key": conn.get("api_key", ""), "Authorization": f"Bearer {conn.get('access_token', '')}"},
                    )
                    status = "healthy" if r.status_code == 200 else "error"
                    message = "Shop accessible" if status == "healthy" else f"HTTP {r.status_code}"

                elif platform == "bigcommerce":
                    store_hash = conn.get("store_url", "").replace("https://", "").replace("http://", "").split(".")[0]
                    if store_hash.startswith("store-"):
                        store_hash = store_hash[6:]
                    r = await client.get(
                        f"https://api.bigcommerce.com/stores/{store_hash}/v3/catalog/summary",
                        headers={"X-Auth-Token": conn.get("access_token", ""), "Accept": "application/json"},
                    )
                    status = "healthy" if r.status_code == 200 else "error"
                    message = "Store accessible" if status == "healthy" else f"HTTP {r.status_code}"

                elif platform == "squarespace":
                    r = await client.get(
                        "https://api.squarespace.com/1.0/commerce/inventory",
                        headers={"Authorization": f"Bearer {conn.get('api_key', '')}", "User-Agent": "TrendScout/1.0"},
                    )
                    status = "healthy" if r.status_code == 200 else "error"
                    message = "Store accessible" if status == "healthy" else f"HTTP {r.status_code}"

                elif platform == "meta" and conn_type == "ads":
                    r = await client.get(f"https://graph.facebook.com/v21.0/me?access_token={conn.get('access_token', '')}")
                    status = "healthy" if r.status_code == 200 else "error"
                    message = "Token valid" if status == "healthy" else "Token expired or invalid"

                elif platform == "tiktok" and conn_type == "ads":
                    r = await client.get(
                        "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/",
                        headers={"Access-Token": conn.get("access_token", "")},
                        params={"app_id": "", "secret": ""},
                    )
                    data = r.json()
                    status = "healthy" if data.get("code") == 0 else "error"
                    message = "Token valid" if status == "healthy" else data.get("message", "Check credentials")

                elif platform == "google" and conn_type == "ads":
                    status = "draft"
                    message = "Google Ads uses manual setup — no health check needed"

                else:
                    status = "unknown"
                    message = "Health check not implemented for this platform"

            except httpx.RequestError as e:
                status = "unreachable"
                message = f"Connection failed: {str(e)[:100]}"
            except Exception as e:
                status = "error"
                message = str(e)[:100]

            # Update connection status in DB
            await db.platform_connections.update_one(
                {"user_id": user_id, "platform": platform, "connection_type": conn_type},
                {"$set": {"health_status": status, "health_checked_at": datetime.now(timezone.utc).isoformat(), "health_message": message}},
            )

            results.append({
                "platform": platform,
                "connection_type": conn_type,
                "status": status,
                "message": message,
            })

    healthy_count = sum(1 for r in results if r["status"] == "healthy")
    return {
        "results": results,
        "total": len(results),
        "healthy": healthy_count,
        "message": f"{healthy_count}/{len(results)} connections healthy",
    }


routers = [connections_router]
