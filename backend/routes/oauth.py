"""
Generic OAuth routes for all supported platforms.
Supports two modes per platform:
  1. App-level credentials (env vars) — user just clicks Connect
  2. User-provided credentials — user enters their own client_id/secret
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os
import logging

from auth import get_current_user, AuthenticatedUser
from services.oauth_service import (
    OAUTH_PLATFORMS,
    initiate_oauth,
    handle_oauth_callback,
    get_platform_setup_info,
    get_platform_credentials,
    is_oauth_ready,
)

logger = logging.getLogger(__name__)

oauth_router = APIRouter(prefix="/api/oauth")

SITE_URL = os.environ.get("SITE_URL", os.environ.get("REACT_APP_BACKEND_URL", ""))


class OAuthInitRequest(BaseModel):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    shop_domain: Optional[str] = None


@oauth_router.get("/platforms")
async def get_oauth_platforms():
    """List all supported OAuth platforms with setup instructions and readiness status."""
    site_url = SITE_URL
    platforms = {}
    for key, config in OAUTH_PLATFORMS.items():
        info = get_platform_setup_info(key, site_url)
        oauth_ready = is_oauth_ready(key)

        platforms[key] = {
            **info,
            "configured": oauth_ready,
            "oauth_ready": oauth_ready,
            "requires_shop_domain": config.get("requires_shop_domain", False),
            "connection_type": config.get("connection_type", "store"),
        }
    return {"platforms": platforms}


@oauth_router.post("/{platform}/init")
async def init_platform_oauth(
    platform: str,
    req: OAuthInitRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Start OAuth flow for a platform.
    If TrendScout has app-level credentials, user doesn't need to provide any.
    Otherwise, user provides their own client_id and client_secret.
    """
    if platform not in OAUTH_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}. Supported: {list(OAUTH_PLATFORMS.keys())}")

    config = OAUTH_PLATFORMS[platform]
    if config.get("requires_shop_domain") and not req.shop_domain:
        raise HTTPException(status_code=400, detail="shop_domain is required for this platform")

    # Try app-level credentials first, then user-provided
    env_cid, env_csec = get_platform_credentials(platform)
    client_id = env_cid or req.client_id
    client_secret = env_csec or req.client_secret

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=400,
            detail="This platform requires credentials. Provide client_id and client_secret, or ask your admin to configure them.",
        )

    redirect_uri = f"{SITE_URL}/api/oauth/{platform}/callback"

    try:
        result = await initiate_oauth(
            platform=platform,
            user_id=current_user.user_id,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            shop_domain=req.shop_domain,
        )
        return result
    except Exception as e:
        logger.error(f"OAuth init failed for {platform}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@oauth_router.get("/{platform}/callback")
async def platform_oauth_callback(
    platform: str,
    request: Request,
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    error_description: str = Query(None),
):
    """
    Handle OAuth callback from platform.
    Exchanges the authorization code for tokens and stores the connection.
    Redirects user back to the connections page.
    """
    if platform not in OAUTH_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")

    # Handle OAuth errors
    if error:
        logger.warning(f"OAuth error for {platform}: {error} - {error_description}")
        frontend_url = SITE_URL
        return RedirectResponse(
            url=f"{frontend_url}/settings/connections?oauth_error={error}&platform={platform}"
        )

    if not code or not state:
        params = dict(request.query_params)
        code = code or params.get("auth_code") or params.get("authorization_code")
        state = state or params.get("state")
        if not code or not state:
            raise HTTPException(status_code=400, detail="Missing authorization code or state")

    try:
        await handle_oauth_callback(platform, code, state)
        frontend_url = SITE_URL
        return RedirectResponse(
            url=f"{frontend_url}/settings/connections?oauth_success={platform}"
        )
    except ValueError as e:
        logger.error(f"OAuth callback failed for {platform}: {e}")
        frontend_url = SITE_URL
        return RedirectResponse(
            url=f"{frontend_url}/settings/connections?oauth_error={str(e)[:100]}&platform={platform}"
        )
    except Exception as e:
        logger.error(f"OAuth callback error for {platform}: {e}")
        frontend_url = SITE_URL
        return RedirectResponse(
            url=f"{frontend_url}/settings/connections?oauth_error=unexpected_error&platform={platform}"
        )


@oauth_router.get("/{platform}/setup")
async def get_platform_setup(platform: str):
    """Get setup instructions for a specific platform."""
    if platform not in OAUTH_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")
    return get_platform_setup_info(platform, SITE_URL)


routers = [oauth_router]
