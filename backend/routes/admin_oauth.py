"""
Admin OAuth Credential Management.
Allows admins to configure platform OAuth app credentials via the UI,
stored encrypted in MongoDB. These take priority over env vars.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import logging

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.helpers import require_admin
from common.encryption import encrypt_token, decrypt_token
from services.oauth_service import OAUTH_PLATFORMS, is_oauth_ready, refresh_credentials_cache

logger = logging.getLogger(__name__)

admin_oauth_router = APIRouter(prefix="/api/admin/oauth")


class OAuthCredentialRequest(BaseModel):
    platform: str
    client_id: str
    client_secret: str


@admin_oauth_router.get("/credentials")
async def list_oauth_credentials(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """List all platform OAuth credential status (configured or not)."""
    await require_admin(current_user)

    results = {}
    for key, config in OAUTH_PLATFORMS.items():
        db_cred = await db.oauth_credentials.find_one(
            {"platform": key}, {"_id": 0, "client_secret_encrypted": 0}
        )
        ready = is_oauth_ready(key)
        results[key] = {
            "platform": key,
            "name": config["name"],
            "connection_type": config["connection_type"],
            "configured": ready,
            "source": db_cred["source"] if db_cred else ("env" if ready else "none"),
            "client_id_preview": (db_cred["client_id"][:8] + "...") if db_cred and db_cred.get("client_id") else "",
            "updated_at": db_cred.get("updated_at") if db_cred else None,
            "setup_url": config.get("setup_url", ""),
            "setup_instructions": config.get("setup_instructions", ""),
            "requires_shop_domain": config.get("requires_shop_domain", False),
        }

    return {"credentials": results}


@admin_oauth_router.post("/credentials")
async def save_oauth_credential(
    req: OAuthCredentialRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Save or update OAuth app credentials for a platform."""
    await require_admin(current_user)

    if req.platform not in OAUTH_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown platform: {req.platform}. Supported: {list(OAUTH_PLATFORMS.keys())}",
        )

    if not req.client_id.strip() or not req.client_secret.strip():
        raise HTTPException(status_code=400, detail="Both client_id and client_secret are required")

    encrypted_secret = encrypt_token(req.client_secret.strip())

    await db.oauth_credentials.update_one(
        {"platform": req.platform},
        {"$set": {
            "platform": req.platform,
            "client_id": req.client_id.strip(),
            "client_secret_encrypted": encrypted_secret,
            "source": "admin_ui",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": current_user.user_id,
        }},
        upsert=True,
    )

    logger.info(f"Admin {current_user.email} configured OAuth credentials for {req.platform}")

    # Refresh in-memory cache
    await refresh_credentials_cache(req.platform)

    return {
        "success": True,
        "platform": req.platform,
        "message": f"{OAUTH_PLATFORMS[req.platform]['name']} credentials saved successfully",
    }


@admin_oauth_router.delete("/credentials/{platform}")
async def delete_oauth_credential(
    platform: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Remove stored OAuth credentials for a platform (falls back to env vars)."""
    await require_admin(current_user)

    result = await db.oauth_credentials.delete_one({"platform": platform})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No stored credentials found for this platform")

    logger.info(f"Admin {current_user.email} removed OAuth credentials for {platform}")

    # Refresh in-memory cache
    await refresh_credentials_cache(platform)

    return {
        "success": True,
        "platform": platform,
        "message": f"Credentials removed. Will fall back to environment variables if configured.",
    }


@admin_oauth_router.post("/credentials/{platform}/test")
async def test_oauth_credential(
    platform: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Test if OAuth credentials are valid by checking the oauth_ready status."""
    await require_admin(current_user)

    if platform not in OAUTH_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")

    ready = is_oauth_ready(platform)
    config = OAUTH_PLATFORMS[platform]

    return {
        "platform": platform,
        "name": config["name"],
        "oauth_ready": ready,
        "message": "Credentials configured and ready" if ready else "No valid credentials found",
    }


routers = [admin_oauth_router]
