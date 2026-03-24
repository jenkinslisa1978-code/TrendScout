"""
Shopify webhook handlers for real-time product/store updates.
Registers webhooks after successful OAuth and handles incoming events.
"""
import hashlib
import hmac
import base64
import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException
from database import db

logger = logging.getLogger(__name__)

shopify_webhook_router = APIRouter(prefix="/api/shopify/webhooks")

SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "")


def verify_shopify_webhook(body: bytes, hmac_header: str) -> bool:
    """Verify that a webhook actually came from Shopify using HMAC."""
    if not SHOPIFY_CLIENT_SECRET or not hmac_header:
        return False
    digest = hmac.new(
        SHOPIFY_CLIENT_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    computed = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(computed, hmac_header)


async def register_webhooks(shop: str, access_token: str):
    """Register Shopify webhooks after successful OAuth connection."""
    import httpx

    site_url = os.environ.get("SITE_URL", os.environ.get("REACT_APP_BACKEND_URL", ""))
    base_url = f"{site_url}/api/shopify/webhooks"
    api_url = f"https://{shop}/admin/api/2024-07/webhooks.json"
    headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}

    topics = [
        "products/create",
        "products/update",
        "products/delete",
        "app/uninstalled",
    ]

    registered = []
    async with httpx.AsyncClient(timeout=15) as client:
        for topic in topics:
            callback_url = f"{base_url}/{topic.replace('/', '-')}"
            payload = {
                "webhook": {
                    "topic": topic,
                    "address": callback_url,
                    "format": "json",
                }
            }
            try:
                resp = await client.post(api_url, json=payload, headers=headers)
                if resp.status_code in (201, 200):
                    registered.append(topic)
                    logger.info(f"Registered webhook {topic} for {shop}")
                elif resp.status_code == 422:
                    # Already registered
                    registered.append(topic)
                else:
                    logger.warning(f"Failed to register webhook {topic} for {shop}: {resp.status_code} {resp.text[:200]}")
            except Exception as e:
                logger.error(f"Error registering webhook {topic} for {shop}: {e}")

    return registered


@shopify_webhook_router.post("/products-create")
async def handle_product_create(request: Request):
    """Handle products/create webhook from Shopify."""
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    if not verify_shopify_webhook(body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    import json
    product = json.loads(body)
    shop_domain = request.headers.get("X-Shopify-Shop-Domain", "")

    # Find the user associated with this shop
    conn = await db.shopify_connections.find_one({"shop_domain": shop_domain}, {"_id": 0, "user_id": 1})
    if not conn:
        conn = await db.platform_connections.find_one(
            {"platform": "shopify", "store_url": {"$regex": shop_domain}},
            {"_id": 0, "user_id": 1},
        )
    if not conn:
        logger.warning(f"Webhook for unknown shop: {shop_domain}")
        return {"status": "ok"}

    user_id = conn["user_id"]
    product_doc = _build_product_doc(product, user_id, shop_domain)
    await db.shopify_synced_products.update_one(
        {"shopify_id": str(product["id"]), "user_id": user_id},
        {"$set": product_doc},
        upsert=True,
    )
    logger.info(f"Webhook: Created product {product.get('title')} for {shop_domain}")
    return {"status": "ok"}


@shopify_webhook_router.post("/products-update")
async def handle_product_update(request: Request):
    """Handle products/update webhook from Shopify."""
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    if not verify_shopify_webhook(body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    import json
    product = json.loads(body)
    shop_domain = request.headers.get("X-Shopify-Shop-Domain", "")

    conn = await db.shopify_connections.find_one({"shop_domain": shop_domain}, {"_id": 0, "user_id": 1})
    if not conn:
        conn = await db.platform_connections.find_one(
            {"platform": "shopify", "store_url": {"$regex": shop_domain}},
            {"_id": 0, "user_id": 1},
        )
    if not conn:
        return {"status": "ok"}

    user_id = conn["user_id"]
    product_doc = _build_product_doc(product, user_id, shop_domain)
    await db.shopify_synced_products.update_one(
        {"shopify_id": str(product["id"]), "user_id": user_id},
        {"$set": product_doc},
        upsert=True,
    )
    logger.info(f"Webhook: Updated product {product.get('title')} for {shop_domain}")
    return {"status": "ok"}


@shopify_webhook_router.post("/products-delete")
async def handle_product_delete(request: Request):
    """Handle products/delete webhook from Shopify."""
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    if not verify_shopify_webhook(body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    import json
    data = json.loads(body)
    shop_domain = request.headers.get("X-Shopify-Shop-Domain", "")
    product_id = str(data.get("id", ""))

    if product_id:
        result = await db.shopify_synced_products.delete_one(
            {"shopify_id": product_id, "shop_domain": shop_domain}
        )
        logger.info(f"Webhook: Deleted product {product_id} from {shop_domain} (deleted={result.deleted_count})")

    return {"status": "ok"}


@shopify_webhook_router.post("/app-uninstalled")
async def handle_app_uninstalled(request: Request):
    """Handle app/uninstalled webhook — clean up all data for this shop."""
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256", "")
    if not verify_shopify_webhook(body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    shop_domain = request.headers.get("X-Shopify-Shop-Domain", "")
    logger.info(f"Webhook: App uninstalled from {shop_domain}")

    # Remove connection and synced products
    await db.shopify_connections.delete_many({"shop_domain": shop_domain})
    await db.platform_connections.delete_many({"platform": "shopify", "store_url": {"$regex": shop_domain}})
    await db.shopify_synced_products.delete_many({"shop_domain": shop_domain})

    return {"status": "ok"}


def _build_product_doc(product: dict, user_id: str, shop_domain: str) -> dict:
    """Build a normalized product document from Shopify's webhook payload."""
    return {
        "shopify_id": str(product["id"]),
        "user_id": user_id,
        "shop_domain": shop_domain,
        "title": product.get("title", ""),
        "product_type": product.get("product_type", ""),
        "vendor": product.get("vendor", ""),
        "status": product.get("status", "active"),
        "tags": product.get("tags", ""),
        "image_url": product.get("image", {}).get("src") if product.get("image") else None,
        "variants_count": len(product.get("variants", [])),
        "price": product["variants"][0]["price"] if product.get("variants") else None,
        "inventory_quantity": sum(v.get("inventory_quantity", 0) for v in product.get("variants", [])),
        "created_at_shopify": product.get("created_at"),
        "updated_at_shopify": product.get("updated_at"),
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }


routers = [shopify_webhook_router]
