"""
Shopify OAuth routes — proper OAuth 2.0 flow with HMAC verification,
state validation, and encrypted token storage.
"""
from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import RedirectResponse
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import os
import hmac
import hashlib
import secrets
import logging

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.encryption import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)

shopify_oauth_router = APIRouter(prefix="/api/shopify")

SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID", "")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "")
SHOPIFY_SCOPES = os.environ.get("SHOPIFY_SCOPES", "read_products,write_products,read_inventory,write_inventory")
SITE_URL = os.environ.get("SITE_URL", "")


def _verify_hmac(query_params: dict) -> bool:
    """Verify Shopify HMAC signature on the callback."""
    if not SHOPIFY_CLIENT_SECRET:
        return False
    received_hmac = query_params.get("hmac", "")
    params_to_sign = {k: v for k, v in query_params.items() if k != "hmac"}
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params_to_sign.items()))
    computed = hmac.new(
        SHOPIFY_CLIENT_SECRET.encode(),
        sorted_params.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed, received_hmac)


class ShopifyOAuthInitRequest(BaseModel):
    shop_domain: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


@shopify_oauth_router.post("/oauth/init")
async def init_oauth(
    req: ShopifyOAuthInitRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Start Shopify OAuth. Uses TrendScout's app credentials by default.
    User only needs to provide their shop domain.
    """
    shop = req.shop_domain.strip().lower()
    if not shop.endswith(".myshopify.com"):
        shop = f"{shop}.myshopify.com"

    # Use app-level credentials, fallback to user-provided
    client_id = SHOPIFY_CLIENT_ID or req.client_id
    client_secret = SHOPIFY_CLIENT_SECRET or req.client_secret

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=400,
            detail="Shopify app credentials not configured. Please contact support.",
        )

    state = secrets.token_urlsafe(32)

    # Encrypt and store credentials + state for the callback
    await db.oauth_states.insert_one({
        "state": state,
        "user_id": current_user.user_id,
        "shop": shop,
        "client_id": client_id,
        "client_secret_encrypted": encrypt_token(client_secret),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    redirect_uri = f"{SITE_URL}/api/shopify/oauth/callback"
    scopes = SHOPIFY_SCOPES

    oauth_url = (
        f"https://{shop}/admin/oauth/authorize?"
        f"client_id={client_id}"
        f"&scope={scopes}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )

    return {"oauth_url": oauth_url, "state": state}


@shopify_oauth_router.get("/oauth/callback")
async def oauth_callback(request: Request):
    """
    Handle Shopify OAuth callback.
    1. Verify HMAC signature
    2. Validate state token
    3. Exchange code for access token
    4. Encrypt & store access token in shopify_connections collection
    5. Redirect user to connections page
    """
    params = dict(request.query_params)
    code = params.get("code")
    shop = params.get("shop")
    state = params.get("state")

    if not code or not shop or not state:
        raise HTTPException(status_code=400, detail="Missing required OAuth parameters")

    # 2. State validation — also retrieves user's stored credentials
    state_record = await db.oauth_states.find_one_and_delete({"state": state})
    if not state_record:
        raise HTTPException(status_code=403, detail="Invalid or expired state token")

    user_id = state_record["user_id"]
    client_id = state_record.get("client_id", SHOPIFY_CLIENT_ID)
    client_secret = decrypt_token(state_record["client_secret_encrypted"]) if state_record.get("client_secret_encrypted") else SHOPIFY_CLIENT_SECRET

    # 1. HMAC verification (uses the user's client_secret)
    if client_secret:
        received_hmac = params.get("hmac", "")
        params_to_sign = {k: v for k, v in params.items() if k != "hmac"}
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params_to_sign.items()))
        computed = hmac.new(client_secret.encode(), sorted_params.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(computed, received_hmac):
            logger.warning(f"HMAC verification failed for shop {shop}")
            raise HTTPException(status_code=403, detail="HMAC verification failed")

    # 3. Exchange code for access token
    import httpx
    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(token_url, json=payload)
        if resp.status_code != 200:
            logger.error(f"Token exchange failed: {resp.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        token_data = resp.json()

    access_token = token_data.get("access_token")
    scope = token_data.get("scope", "")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")

    # 4. Encrypt and store
    encrypted = encrypt_token(access_token)

    # Verify the connection works
    async with httpx.AsyncClient(timeout=10) as client:
        verify_resp = await client.get(
            f"https://{shop}/admin/api/2024-01/shop.json",
            headers={"X-Shopify-Access-Token": access_token},
        )
        shop_info = verify_resp.json().get("shop", {}) if verify_resp.status_code == 200 else {}

    await db.shopify_connections.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "shop_domain": shop,
            "access_token_encrypted": encrypted,
            "scope": scope,
            "shop_name": shop_info.get("name", shop),
            "shop_email": shop_info.get("email", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "verified": verify_resp.status_code == 200,
        }},
        upsert=True,
    )

    # Also upsert into platform_connections for unified view
    await db.platform_connections.update_one(
        {"user_id": user_id, "platform": "shopify", "connection_type": "store"},
        {"$set": {
            "user_id": user_id,
            "platform": "shopify",
            "connection_type": "store",
            "store_url": shop,
            "access_token": access_token,
            "status": "active",
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )

    logger.info(f"Shopify OAuth completed for user {user_id}, shop {shop}")

    # 5. Register webhooks for real-time sync
    try:
        from routes.shopify_webhooks import register_webhooks
        registered = await register_webhooks(shop, access_token)
        logger.info(f"Registered {len(registered)} webhooks for {shop}: {registered}")
    except Exception as e:
        logger.warning(f"Webhook registration failed for {shop}: {e}")

    # 6. Redirect to frontend connections page with success
    frontend_url = os.environ.get("SITE_URL", "")
    return RedirectResponse(url=f"{frontend_url}/settings/connections?oauth_success=shopify")


@shopify_oauth_router.get("/oauth/status")
async def get_shopify_connection(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get user's Shopify connection status."""
    conn = await db.shopify_connections.find_one(
        {"user_id": current_user.user_id}, {"_id": 0, "access_token_encrypted": 0}
    )
    if not conn:
        return {"connected": False}
    return {"connected": True, **conn}


@shopify_oauth_router.delete("/oauth/disconnect")
async def disconnect_shopify(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Disconnect Shopify store."""
    user_id = current_user.user_id
    await db.shopify_connections.delete_one({"user_id": user_id})
    await db.platform_connections.delete_one({"user_id": user_id, "platform": "shopify", "connection_type": "store"})
    return {"success": True, "message": "Shopify disconnected"}


@shopify_oauth_router.post("/sync-products")
async def sync_shopify_products(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Pull products from the user's connected Shopify store into TrendScout."""
    import httpx

    user_id = current_user.user_id

    # Get connection with decryptable token
    conn = await db.shopify_connections.find_one({"user_id": user_id}, {"_id": 0})
    if not conn:
        # Fall back to platform_connections
        conn = await db.platform_connections.find_one(
            {"user_id": user_id, "platform": "shopify", "connection_type": "store"},
            {"_id": 0},
        )
    if not conn:
        return {"success": False, "error": "No Shopify store connected"}

    # Decrypt access token
    access_token = None
    if conn.get("access_token_encrypted"):
        access_token = decrypt_token(conn["access_token_encrypted"])
    elif conn.get("access_token"):
        access_token = conn["access_token"]

    if not access_token:
        return {"success": False, "error": "No access token found. Please reconnect your Shopify store."}

    shop = conn.get("shop_domain") or conn.get("store_url", "")
    if not shop:
        return {"success": False, "error": "No shop domain found"}

    # Clean domain
    shop = shop.replace("https://", "").replace("http://", "").rstrip("/")
    if not shop.endswith(".myshopify.com"):
        shop = f"{shop}.myshopify.com"

    # Fetch products from Shopify
    api_url = f"https://{shop}/admin/api/2024-07/products.json?limit=50&status=active"
    headers = {"X-Shopify-Access-Token": access_token}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(api_url, headers=headers)
            if resp.status_code == 401:
                return {"success": False, "error": "Access token expired or revoked. Please reconnect your store."}
            if resp.status_code != 200:
                return {"success": False, "error": f"Shopify API error ({resp.status_code})"}
            data = resp.json()
    except httpx.RequestError as e:
        return {"success": False, "error": f"Could not reach Shopify: {str(e)}"}

    shopify_products = data.get("products", [])
    synced = []

    for sp in shopify_products:
        product_doc = {
            "shopify_id": str(sp["id"]),
            "user_id": user_id,
            "shop_domain": shop,
            "title": sp.get("title", ""),
            "product_type": sp.get("product_type", ""),
            "vendor": sp.get("vendor", ""),
            "status": sp.get("status", "active"),
            "tags": sp.get("tags", ""),
            "image_url": sp.get("image", {}).get("src") if sp.get("image") else None,
            "variants_count": len(sp.get("variants", [])),
            "price": sp["variants"][0]["price"] if sp.get("variants") else None,
            "inventory_quantity": sum(v.get("inventory_quantity", 0) for v in sp.get("variants", [])),
            "created_at_shopify": sp.get("created_at"),
            "updated_at_shopify": sp.get("updated_at"),
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.shopify_synced_products.update_one(
            {"shopify_id": str(sp["id"]), "user_id": user_id},
            {"$set": product_doc},
            upsert=True,
        )
        synced.append({"shopify_id": str(sp["id"]), "title": sp.get("title", "")})

    return {
        "success": True,
        "synced_count": len(synced),
        "products": synced,
        "shop": shop,
    }


@shopify_oauth_router.get("/synced-products")
async def get_synced_products(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get the user's synced Shopify products."""
    products = await db.shopify_synced_products.find(
        {"user_id": current_user.user_id},
        {"_id": 0},
    ).sort("synced_at", -1).to_list(100)
    return {"success": True, "products": products, "count": len(products)}


routers = [shopify_oauth_router]
