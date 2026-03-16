"""
Shopify App — GDPR webhooks, app lifecycle webhooks, and manifest endpoints.
Required for Shopify App Store submission.
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import hmac
import hashlib
import json
import logging
import os

from common.database import db

logger = logging.getLogger(__name__)

shopify_app_router = APIRouter(prefix="/api/shopify/app")

SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "")


def _verify_webhook_hmac(body: bytes, hmac_header: str) -> bool:
    """Verify Shopify webhook HMAC-SHA256 signature."""
    if not SHOPIFY_CLIENT_SECRET or not hmac_header:
        return False
    computed = hmac.new(
        SHOPIFY_CLIENT_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed, hmac_header)


# ═══════════════════════════════════════════════════════════════
# GDPR Mandatory Webhooks (required for Shopify App Store)
# ═══════════════════════════════════════════════════════════════

@shopify_app_router.post("/webhooks/customers/data_request")
async def customer_data_request(request: Request):
    """
    Shopify GDPR: Customer data request.
    When a customer requests their data, Shopify notifies us.
    We respond with any data we store about the customer.
    """
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    if SHOPIFY_CLIENT_SECRET and not _verify_webhook_hmac(body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    payload = json.loads(body)
    shop_domain = payload.get("shop_domain", "")
    customer = payload.get("customer", {})
    customer_email = customer.get("email", "")

    logger.info(f"GDPR customer data request from {shop_domain} for {customer_email}")

    # Log the request for compliance tracking
    await db.gdpr_requests.insert_one({
        "type": "customer_data_request",
        "shop_domain": shop_domain,
        "customer_email": customer_email,
        "customer_id": customer.get("id"),
        "orders_requested": payload.get("orders_requested", []),
        "received_at": datetime.now(timezone.utc).isoformat(),
        "status": "received",
    })

    return JSONResponse(content={"status": "ok"}, status_code=200)


@shopify_app_router.post("/webhooks/customers/redact")
async def customer_data_redact(request: Request):
    """
    Shopify GDPR: Customer data erasure request.
    We must delete all data associated with this customer within 30 days.
    """
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    if SHOPIFY_CLIENT_SECRET and not _verify_webhook_hmac(body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    payload = json.loads(body)
    shop_domain = payload.get("shop_domain", "")
    customer = payload.get("customer", {})
    customer_email = customer.get("email", "")

    logger.info(f"GDPR customer redact from {shop_domain} for {customer_email}")

    # Log the request
    await db.gdpr_requests.insert_one({
        "type": "customer_redact",
        "shop_domain": shop_domain,
        "customer_email": customer_email,
        "customer_id": customer.get("id"),
        "received_at": datetime.now(timezone.utc).isoformat(),
        "status": "processing",
    })

    # TrendScout doesn't store end-customer PII from Shopify stores,
    # but we still acknowledge and log the request for compliance
    await db.gdpr_requests.update_one(
        {"type": "customer_redact", "customer_email": customer_email, "shop_domain": shop_domain},
        {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}},
    )

    return JSONResponse(content={"status": "ok"}, status_code=200)


@shopify_app_router.post("/webhooks/shop/redact")
async def shop_data_redact(request: Request):
    """
    Shopify GDPR: Shop data erasure request.
    Sent 48 hours after a store uninstalls the app.
    We must erase all data associated with the shop.
    """
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    if SHOPIFY_CLIENT_SECRET and not _verify_webhook_hmac(body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    payload = json.loads(body)
    shop_domain = payload.get("shop_domain", "")
    shop_id = payload.get("shop_id")

    logger.info(f"GDPR shop redact for {shop_domain} (id={shop_id})")

    # Remove all data associated with this shop
    await db.shopify_connections.delete_many({"shop_domain": shop_domain})
    await db.platform_connections.delete_many({"platform": "shopify", "store_url": {"$regex": shop_domain}})
    await db.shopify_exports.delete_many({"shopify_domain": {"$regex": shop_domain}})
    await db.oauth_states.delete_many({"shop": shop_domain})

    await db.gdpr_requests.insert_one({
        "type": "shop_redact",
        "shop_domain": shop_domain,
        "shop_id": shop_id,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
    })

    return JSONResponse(content={"status": "ok"}, status_code=200)


# ═══════════════════════════════════════════════════════════════
# App Lifecycle Webhooks
# ═══════════════════════════════════════════════════════════════

@shopify_app_router.post("/webhooks/app/uninstalled")
async def app_uninstalled(request: Request):
    """
    Handle app/uninstalled webhook.
    Clean up connection data when a merchant uninstalls the app.
    """
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    if SHOPIFY_CLIENT_SECRET and not _verify_webhook_hmac(body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    payload = json.loads(body)
    shop_domain = payload.get("domain", payload.get("myshopify_domain", ""))

    logger.info(f"App uninstalled by {shop_domain}")

    # Revoke access — mark connections inactive
    await db.shopify_connections.update_many(
        {"shop_domain": {"$regex": shop_domain}},
        {"$set": {"verified": False, "uninstalled_at": datetime.now(timezone.utc).isoformat()}},
    )
    await db.platform_connections.update_many(
        {"platform": "shopify", "store_url": {"$regex": shop_domain}},
        {"$set": {"status": "uninstalled", "disconnected_at": datetime.now(timezone.utc).isoformat()}},
    )

    return JSONResponse(content={"status": "ok"}, status_code=200)


# ═══════════════════════════════════════════════════════════════
# App Info / Manifest
# ═══════════════════════════════════════════════════════════════

@shopify_app_router.get("/info")
async def app_info():
    """
    Public endpoint returning app metadata for Shopify App Store listing.
    """
    return {
        "name": "TrendScout",
        "version": "1.0.0",
        "description": "AI-powered product validation and launch intelligence for dropshippers. Find winning products, analyze competitors, and push products directly to your store.",
        "features": [
            "7-Signal Launch Score — AI product scoring",
            "Ad Intelligence — spy on TikTok, Meta, Pinterest ads",
            "Competitor Store Analysis — revenue estimates, pricing strategy",
            "1-Click Product Import — push products as drafts to your store",
            "Real-time Radar Alerts — trend spikes, score changes",
            "Profitability Simulator — unit economics calculator",
            "Verified Winners Community — crowd-sourced winning products",
            "API Access — programmatic access for power users",
        ],
        "scopes_required": [
            "read_products",
            "write_products",
            "read_inventory",
            "write_inventory",
        ],
        "gdpr_endpoints": {
            "customer_data_request": "/api/shopify/app/webhooks/customers/data_request",
            "customer_redact": "/api/shopify/app/webhooks/customers/redact",
            "shop_redact": "/api/shopify/app/webhooks/shop/redact",
        },
        "webhooks": {
            "app_uninstalled": "/api/shopify/app/webhooks/app/uninstalled",
        },
        "support_email": "support@trendscout.click",
        "privacy_policy": "/privacy",
        "terms_of_service": "/terms",
    }


# ═══════════════════════════════════════════════════════════════
# Embedded App Endpoints
# ═══════════════════════════════════════════════════════════════

@shopify_app_router.post("/session-token")
async def verify_session_token(request: Request):
    """
    Verify a Shopify session token from an embedded app.
    Returns a TrendScout JWT for the authenticated shop.
    """
    import jwt as pyjwt

    body = await request.json()
    session_token = body.get("session_token", "")
    if not session_token:
        raise HTTPException(status_code=400, detail="session_token required")

    try:
        payload = pyjwt.decode(
            session_token,
            SHOPIFY_CLIENT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token")

    shop = payload.get("dest", "").replace("https://", "")
    if not shop:
        raise HTTPException(status_code=400, detail="No shop in token")

    # Find or create user connection for this shop
    conn = await db.shopify_connections.find_one(
        {"shop_domain": {"$regex": shop}},
        {"_id": 0, "user_id": 1, "shop_domain": 1, "shop_name": 1},
    )

    if not conn:
        # Auto-register shop connection stub
        await db.shopify_connections.insert_one({
            "shop_domain": shop,
            "user_id": None,
            "shop_name": shop.split(".")[0],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "verified": False,
            "source": "embedded_app",
        })
        conn = {"shop_domain": shop, "shop_name": shop.split(".")[0], "user_id": None}

    # Issue a short-lived internal token
    jwt_secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    internal_token = pyjwt.encode(
        {
            "sub": conn.get("user_id") or f"shopify:{shop}",
            "shop": shop,
            "type": "shopify_embedded",
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": (datetime.now(timezone.utc) + __import__("datetime").timedelta(hours=1)).timestamp(),
        },
        jwt_secret,
        algorithm="HS256",
    )

    return {
        "token": internal_token,
        "shop": shop,
        "shop_name": conn.get("shop_name", shop),
        "user_id": conn.get("user_id"),
        "connected": conn.get("user_id") is not None,
    }


@shopify_app_router.get("/embedded/dashboard")
async def embedded_dashboard(shop: str = ""):
    """
    Return dashboard data for the embedded Shopify app panel.
    Shows trending products, recent radar alerts, and export stats.
    """
    if not shop:
        raise HTTPException(status_code=400, detail="shop param required")

    # Get top trending products
    products = await db.products.find(
        {"launch_score": {"$gte": 50}},
        {"_id": 0, "id": 1, "product_name": 1, "launch_score": 1,
         "category": 1, "early_trend_label": 1, "estimated_retail_price": 1,
         "estimated_margin": 1, "image_url": 1},
    ).sort("launch_score", -1).limit(10).to_list(10)

    # Get recent exports for this shop
    conn = await db.shopify_connections.find_one(
        {"shop_domain": {"$regex": shop}},
        {"_id": 0, "user_id": 1},
    )
    user_id = conn.get("user_id") if conn else None

    exports = []
    if user_id:
        exports = await db.shopify_exports.find(
            {"user_id": user_id},
            {"_id": 0},
        ).sort("exported_at", -1).limit(5).to_list(5)

    # Get recent radar detections
    radar = await db.products.find(
        {"radar_detected": True},
        {"_id": 0, "id": 1, "product_name": 1, "launch_score": 1,
         "category": 1, "radar_detected_at": 1},
    ).sort("radar_detected_at", -1).limit(5).to_list(5)

    return {
        "trending_products": products,
        "recent_exports": exports,
        "radar_detections": radar,
        "shop": shop,
        "connected": user_id is not None,
    }


routers = [shopify_app_router]
