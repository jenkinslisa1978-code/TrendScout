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
    client_id: str
    client_secret: str


@shopify_oauth_router.post("/oauth/init")
async def init_oauth(
    req: ShopifyOAuthInitRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Start Shopify OAuth using the user's own client_id and client_secret.
    Stores credentials encrypted in DB for the callback phase.
    """
    shop = req.shop_domain.strip().lower()
    if not shop.endswith(".myshopify.com"):
        shop = f"{shop}.myshopify.com"

    state = secrets.token_urlsafe(32)

    # Encrypt and store the user's credentials + state for the callback
    await db.oauth_states.insert_one({
        "state": state,
        "user_id": current_user.user_id,
        "shop": shop,
        "client_id": req.client_id,
        "client_secret_encrypted": encrypt_token(req.client_secret),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    redirect_uri = f"{SITE_URL}/api/shopify/oauth/callback"
    scopes = SHOPIFY_SCOPES

    oauth_url = (
        f"https://{shop}/admin/oauth/authorize?"
        f"client_id={req.client_id}"
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

    # 5. Redirect to frontend connections page
    frontend_url = os.environ.get("SITE_URL", "")
    return RedirectResponse(url=f"{frontend_url}/settings/connections?shopify=connected")


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


routers = [shopify_oauth_router]
