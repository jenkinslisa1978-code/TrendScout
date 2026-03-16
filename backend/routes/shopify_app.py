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


routers = [shopify_app_router]
