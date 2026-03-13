"""User routes: onboarding, admin status, daily usage."""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from datetime import datetime, timezone
import os

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.helpers import get_user_plan

user_router = APIRouter(prefix="/api/user")


@user_router.get("/onboarding-status")
async def get_onboarding_status(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    profile = await db.profiles.find_one(
        {"id": current_user.user_id},
        {"_id": 0, "onboarding_completed": 1, "onboarding_completed_at": 1}
    )
    return {
        "onboarding_completed": profile.get("onboarding_completed", False) if profile else False,
        "onboarding_completed_at": profile.get("onboarding_completed_at") if profile else None,
    }


@user_router.post("/complete-onboarding")
async def complete_onboarding(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    await db.profiles.update_one(
        {"id": current_user.user_id},
        {
            "$set": {
                "onboarding_completed": True,
                "onboarding_completed_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    return {"status": "success", "onboarding_completed": True}


@user_router.post("/reset-onboarding")
async def reset_onboarding(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    await db.profiles.update_one(
        {"id": current_user.user_id},
        {"$set": {"onboarding_completed": False, "onboarding_completed_at": None}}
    )
    return {"status": "success", "onboarding_completed": False}


@user_router.get("/admin-status")
async def get_admin_status(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    profile = await db.profiles.find_one(
        {"id": current_user.user_id},
        {"_id": 0, "is_admin": 1, "email": 1}
    )
    is_admin = profile.get("is_admin", False) if profile else False
    return {"is_admin": is_admin, "user_id": current_user.user_id}


@user_router.post("/set-admin")
async def set_admin_status(
    email: str,
    is_admin: bool = True,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    valid_key = os.environ.get('ADMIN_API_KEY', 'vs_admin_key_2024')
    if api_key != valid_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    profile = await db.profiles.find_one({"email": email}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail=f"User with email {email} not found")
    await db.profiles.update_one(
        {"email": email},
        {"$set": {
            "is_admin": is_admin,
            "admin_set_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"status": "success", "email": email, "is_admin": is_admin}


@user_router.get("/daily-usage")
async def get_daily_usage(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    from services.subscription_service import FeatureGate
    plan = await get_user_plan(current_user.user_id)
    features = FeatureGate.get_plan_features(plan)
    daily_limit = features.get("max_analyses_daily", 2)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    usage_doc = await db.daily_usage.find_one(
        {"user_id": current_user.user_id, "date": today}, {"_id": 0}
    )
    used = usage_doc.get("insights_used", 0) if usage_doc else 0
    return {
        "plan": plan,
        "daily_limit": daily_limit,
        "insights_used": used,
        "remaining": max(0, daily_limit - used) if daily_limit != -1 else -1,
        "is_unlimited": daily_limit == -1,
    }


@user_router.post("/track-insight")
async def track_insight_usage(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    from services.subscription_service import FeatureGate
    plan = await get_user_plan(current_user.user_id)
    features = FeatureGate.get_plan_features(plan)
    daily_limit = features.get("max_analyses_daily", 2)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = await db.daily_usage.find_one_and_update(
        {"user_id": current_user.user_id, "date": today},
        {"$inc": {"insights_used": 1}, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
        return_document=True,
        projection={"_id": 0}
    )
    used = result.get("insights_used", 1) if result else 1
    return {
        "plan": plan,
        "daily_limit": daily_limit,
        "insights_used": used,
        "remaining": max(0, daily_limit - used) if daily_limit != -1 else -1,
        "is_unlimited": daily_limit == -1,
        "limit_reached": daily_limit != -1 and used >= daily_limit,
    }


routers = [user_router]
