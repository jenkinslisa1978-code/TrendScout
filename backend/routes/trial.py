"""
Free Trial Routes

Allows free-plan users to unlock ONE premium feature for 24 hours after signup.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from common.database import db
from routes.auth_routes import get_current_user, AuthenticatedUser

trial_router = APIRouter(prefix="/api/trial")

# Features available for trial unlock
TRIAL_FEATURES = {
    "ad_intelligence": {
        "label": "Ad Intelligence",
        "description": "Search and analyze competitor ads across TikTok, Meta, and Pinterest",
        "icon": "target",
        "unlocks": ["ad_spy"],
    },
    "tiktok_intel": {
        "label": "TikTok Intelligence",
        "description": "Full viral product rankings, category performance, and trending patterns",
        "icon": "video",
        "unlocks": ["tiktok_intelligence"],
    },
    "competitor_intel": {
        "label": "Competitor Intelligence",
        "description": "Deep-analyse any Shopify store with unlimited analyses",
        "icon": "store",
        "unlocks": ["competitor_intel"],
    },
    "product_deep_dive": {
        "label": "Product Deep Dive",
        "description": "Unlock Saturation Radar, Competitor Intel, Ad Patterns, and Blueprints on product pages",
        "icon": "layers",
        "unlocks": ["saturation", "competitor", "ad_patterns", "ad_blueprint", "ad_performance"],
    },
    "profit_simulator": {
        "label": "Profit Simulator",
        "description": "Run unlimited profitability simulations with detailed projections",
        "icon": "calculator",
        "unlocks": ["profit_simulator"],
    },
}

TRIAL_DURATION_HOURS = 24


class ActivateTrialRequest(BaseModel):
    feature: str


@trial_router.get("/status")
async def get_trial_status(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Get the user's trial status and available features."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    plan = profile.get("plan", "free") if profile else "free"

    # Only free users are eligible
    if plan != "free":
        return {
            "eligible": False,
            "reason": "paid_plan",
            "active_trial": None,
            "available_features": [],
        }

    trial = await db.trials.find_one({"user_id": current_user.user_id}, {"_id": 0})

    if not trial:
        # Never used trial — eligible
        return {
            "eligible": True,
            "reason": "new_user",
            "active_trial": None,
            "available_features": [
                {"id": k, **{fk: fv for fk, fv in v.items() if fk != "unlocks"}}
                for k, v in TRIAL_FEATURES.items()
            ],
        }

    # Check if trial is still active
    activated_at = datetime.fromisoformat(trial["activated_at"])
    expires_at = activated_at + timedelta(hours=TRIAL_DURATION_HOURS)
    now = datetime.now(timezone.utc)

    if now < expires_at:
        remaining_seconds = int((expires_at - now).total_seconds())
        feature_info = TRIAL_FEATURES.get(trial["feature"], {})
        return {
            "eligible": False,
            "reason": "trial_active",
            "active_trial": {
                "feature": trial["feature"],
                "feature_label": feature_info.get("label", trial["feature"]),
                "unlocks": feature_info.get("unlocks", []),
                "activated_at": trial["activated_at"],
                "expires_at": expires_at.isoformat(),
                "remaining_seconds": remaining_seconds,
                "remaining_hours": round(remaining_seconds / 3600, 1),
            },
            "available_features": [],
        }

    # Trial expired
    return {
        "eligible": False,
        "reason": "trial_expired",
        "active_trial": {
            "feature": trial["feature"],
            "feature_label": TRIAL_FEATURES.get(trial["feature"], {}).get("label", ""),
            "expired": True,
            "expired_at": expires_at.isoformat(),
        },
        "available_features": [],
    }


@trial_router.post("/activate")
async def activate_trial(
    body: ActivateTrialRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Activate a 24-hour free trial for one premium feature."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    plan = profile.get("plan", "free") if profile else "free"

    if plan != "free":
        raise HTTPException(status_code=400, detail="Trials are only available for free-plan users.")

    # Check if already used
    existing = await db.trials.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="You've already used your free trial.")

    if body.feature not in TRIAL_FEATURES:
        raise HTTPException(status_code=400, detail=f"Invalid feature. Choose from: {', '.join(TRIAL_FEATURES.keys())}")

    now = datetime.now(timezone.utc)
    trial_doc = {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "feature": body.feature,
        "activated_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=TRIAL_DURATION_HOURS)).isoformat(),
    }
    await db.trials.insert_one(trial_doc)

    feature_info = TRIAL_FEATURES[body.feature]
    return {
        "success": True,
        "message": f"{feature_info['label']} unlocked for {TRIAL_DURATION_HOURS} hours!",
        "trial": {
            "feature": body.feature,
            "feature_label": feature_info["label"],
            "unlocks": feature_info["unlocks"],
            "activated_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=TRIAL_DURATION_HOURS)).isoformat(),
            "remaining_hours": TRIAL_DURATION_HOURS,
        },
    }


routers = [trial_router]
