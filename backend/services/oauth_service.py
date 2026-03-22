"""
Generic OAuth 2.0 service for multi-platform integrations.
Handles state management, token exchange, and encrypted storage.
"""
import secrets
import logging
import httpx
from typing import Optional, Dict
from datetime import datetime, timezone
from urllib.parse import urlencode

from common.database import db
from common.encryption import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)


# ==================== PLATFORM CONFIGS ====================

OAUTH_PLATFORMS = {
    "shopify": {
        "name": "Shopify",
        "auth_url": "https://{shop}/admin/oauth/authorize",
        "token_url": "https://{shop}/admin/oauth/access_token",
        "scopes": "read_products,write_products,read_inventory,write_inventory",
        "requires_shop_domain": True,
        "connection_type": "store",
        "setup_url": "https://partners.shopify.com",
        "setup_instructions": "1. Go to partners.shopify.com and create a Partner account\n2. Create a new App\n3. Under 'App setup', note your Client ID and Client Secret\n4. Add your redirect URI: {redirect_uri}\n5. Select scopes: read_products, write_products, read_inventory, write_inventory",
    },
    "etsy": {
        "name": "Etsy",
        "auth_url": "https://www.etsy.com/oauth/connect",
        "token_url": "https://api.etsy.com/v3/public/oauth/token",
        "scopes": "listings_r listings_w shops_r",
        "requires_shop_domain": False,
        "connection_type": "store",
        "uses_pkce": True,
        "setup_url": "https://www.etsy.com/developers",
        "setup_instructions": "1. Go to etsy.com/developers and sign in\n2. Click 'Create a New App'\n3. Fill in app name: TrendScout, description: Ecommerce intelligence\n4. Note your Keystring (Client ID)\n5. Add redirect URI: {redirect_uri}",
    },
    "amazon_seller": {
        "name": "Amazon Seller",
        "auth_url": "https://sellercentral.amazon.co.uk/apps/authorize/consent",
        "token_url": "https://api.amazon.co.uk/auth/o2/token",
        "scopes": "",
        "requires_shop_domain": False,
        "connection_type": "social",
        "setup_url": "https://sellercentral.amazon.co.uk/apps/manage",
        "setup_instructions": "1. Go to sellercentral.amazon.co.uk → Apps & Services → Develop Apps\n2. Register as a developer if not already\n3. Create a new app, select SP-API\n4. Note your Client ID (LWA App ID) and Client Secret\n5. Add redirect URI: {redirect_uri}",
    },
    "tiktok_shop": {
        "name": "TikTok Shop",
        "auth_url": "https://auth.tiktok-shops.com/oauth/authorize",
        "token_url": "https://auth.tiktok-shops.com/api/v2/token/get",
        "scopes": "product.read,product.edit,order.read",
        "requires_shop_domain": False,
        "connection_type": "social",
        "setup_url": "https://partner.tiktokshop.com",
        "setup_instructions": "1. Go to partner.tiktokshop.com and register as a developer\n2. Create a new app\n3. Note your App Key (Client ID) and App Secret\n4. Add redirect URI: {redirect_uri}\n5. Request permissions: product.read, product.edit, order.read",
    },
    "meta": {
        "name": "Meta (Facebook & Instagram)",
        "auth_url": "https://www.facebook.com/v21.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v21.0/oauth/access_token",
        "scopes": "pages_manage_posts,instagram_basic,instagram_content_publish,ads_management,catalog_management",
        "requires_shop_domain": False,
        "connection_type": "ads",
        "setup_url": "https://developers.facebook.com",
        "setup_instructions": "1. Go to developers.facebook.com → My Apps → Create App\n2. Select 'Business' type\n3. Add Facebook Login product\n4. Under Settings → Basic, note your App ID (Client ID) and App Secret\n5. Under Facebook Login → Settings, add redirect URI: {redirect_uri}\n6. Under Permissions, request: pages_manage_posts, instagram_basic, ads_management",
    },
    "google_ads": {
        "name": "Google Ads",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": "https://www.googleapis.com/auth/adwords",
        "requires_shop_domain": False,
        "connection_type": "ads",
        "setup_url": "https://console.cloud.google.com",
        "setup_instructions": "1. Go to console.cloud.google.com → Create/select a project\n2. Enable the Google Ads API\n3. Go to Credentials → Create Credentials → OAuth 2.0 Client ID\n4. Select 'Web application'\n5. Add redirect URI: {redirect_uri}\n6. Note your Client ID and Client Secret\n7. Apply for a Google Ads developer token at ads.google.com → Tools → API Centre",
    },
    "tiktok_ads": {
        "name": "TikTok Ads",
        "auth_url": "https://business-api.tiktok.com/portal/auth",
        "token_url": "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/",
        "scopes": "",
        "requires_shop_domain": False,
        "connection_type": "ads",
        "setup_url": "https://business-api.tiktok.com/portal/apps",
        "setup_instructions": "1. Go to business-api.tiktok.com → Create an app\n2. Select Marketing API\n3. Note your App ID and Secret\n4. Add redirect URI: {redirect_uri}\n5. Submit for review",
    },
}


async def initiate_oauth(
    platform: str,
    user_id: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    shop_domain: str = None,
) -> dict:
    """
    Generate the OAuth authorization URL and store state for validation.
    """
    config = OAUTH_PLATFORMS.get(platform)
    if not config:
        raise ValueError(f"Unsupported OAuth platform: {platform}")

    state = secrets.token_urlsafe(32)

    # Store state + encrypted credentials
    state_doc = {
        "state": state,
        "platform": platform,
        "user_id": user_id,
        "client_id": client_id,
        "client_secret_encrypted": encrypt_token(client_secret),
        "redirect_uri": redirect_uri,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if shop_domain:
        state_doc["shop_domain"] = shop_domain

    # Handle PKCE if needed
    code_verifier = None
    if config.get("uses_pkce"):
        import hashlib, base64
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        state_doc["code_verifier"] = code_verifier

    await db.oauth_states.insert_one(state_doc)

    # Build auth URL
    auth_url = config["auth_url"]
    if config.get("requires_shop_domain") and shop_domain:
        auth_url = auth_url.format(shop=shop_domain)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "response_type": "code",
    }
    if config["scopes"]:
        params["scope"] = config["scopes"]

    if config.get("uses_pkce") and code_verifier:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = "S256"

    # Platform-specific param names
    if platform == "tiktok_shop":
        params["app_key"] = client_id
        del params["client_id"]
        del params["response_type"]
    elif platform == "tiktok_ads":
        params["app_id"] = client_id
        del params["client_id"]
        del params["response_type"]
    elif platform == "amazon_seller":
        params["application_id"] = client_id
        del params["client_id"]

    oauth_url = f"{auth_url}?{urlencode(params)}"

    return {"oauth_url": oauth_url, "state": state, "platform": platform}


async def handle_oauth_callback(
    platform: str,
    code: str,
    state: str,
) -> dict:
    """
    Exchange authorization code for access token and store the connection.
    """
    config = OAUTH_PLATFORMS.get(platform)
    if not config:
        raise ValueError(f"Unsupported OAuth platform: {platform}")

    # Retrieve and delete state record
    state_record = await db.oauth_states.find_one_and_delete({"state": state, "platform": platform})
    if not state_record:
        raise ValueError("Invalid or expired state token")

    user_id = state_record["user_id"]
    client_id = state_record["client_id"]
    client_secret = decrypt_token(state_record["client_secret_encrypted"])
    redirect_uri = state_record["redirect_uri"]
    shop_domain = state_record.get("shop_domain")

    # Build token exchange payload
    token_url = config["token_url"]
    if config.get("requires_shop_domain") and shop_domain:
        token_url = token_url.format(shop=shop_domain)

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    # PKCE verifier
    if state_record.get("code_verifier"):
        payload["code_verifier"] = state_record["code_verifier"]

    # Platform-specific token exchange
    if platform == "tiktok_shop":
        payload = {"app_key": client_id, "app_secret": client_secret, "auth_code": code, "grant_type": "authorized_code"}
    elif platform == "tiktok_ads":
        payload = {"app_id": client_id, "secret": client_secret, "auth_code": code}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(token_url, json=payload)
        if resp.status_code not in (200, 201):
            logger.error(f"Token exchange failed for {platform}: {resp.text}")
            raise ValueError(f"Token exchange failed: {resp.text[:200]}")
        token_data = resp.json()

    # Extract access token (different platforms use different keys)
    access_token = (
        token_data.get("access_token")
        or token_data.get("data", {}).get("access_token")
        or token_data.get("access_token_token")
    )
    refresh_token = (
        token_data.get("refresh_token")
        or token_data.get("data", {}).get("refresh_token")
    )

    if not access_token:
        raise ValueError(f"No access token received from {platform}")

    # Store encrypted connection
    connection = {
        "user_id": user_id,
        "platform": platform,
        "connection_type": config["connection_type"],
        "access_token": access_token,
        "access_token_encrypted": encrypt_token(access_token),
        "status": "active",
        "connected_at": datetime.now(timezone.utc).isoformat(),
        "oauth_data": {
            "scope": token_data.get("scope", config["scopes"]),
            "token_type": token_data.get("token_type", "bearer"),
            "expires_in": token_data.get("expires_in"),
        },
    }
    if refresh_token:
        connection["refresh_token_encrypted"] = encrypt_token(refresh_token)
    if shop_domain:
        connection["store_url"] = shop_domain

    await db.platform_connections.update_one(
        {"user_id": user_id, "platform": platform, "connection_type": config["connection_type"]},
        {"$set": connection},
        upsert=True,
    )

    logger.info(f"OAuth completed for user {user_id}, platform {platform}")
    return {"success": True, "platform": platform, "user_id": user_id}


def get_platform_setup_info(platform: str, site_url: str) -> dict:
    """Get setup instructions for a platform with the correct redirect URI."""
    config = OAUTH_PLATFORMS.get(platform)
    if not config:
        return {}
    redirect_uri = f"{site_url}/api/oauth/{platform}/callback"
    return {
        "platform": platform,
        "name": config["name"],
        "setup_url": config["setup_url"],
        "redirect_uri": redirect_uri,
        "instructions": config["setup_instructions"].format(redirect_uri=redirect_uri),
        "connection_type": config["connection_type"],
    }
