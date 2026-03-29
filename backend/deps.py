"""
Shared dependencies used across route modules.
"""
import re
import time as _time
from fastapi import HTTPException
from common.database import db
from auth import AuthenticatedUser

# ── Cache ──────────────────────────────────────────
_public_cache = {}
_CACHE_TTL = 300  # 5 minutes


def _get_cached(key):
    entry = _public_cache.get(key)
    if entry and (_time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["data"]
    return None


def _set_cached(key, data):
    _public_cache[key] = {"data": data, "ts": _time.time()}


# ── Slugify ────────────────────────────────────────
def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


# ── Plan helpers ───────────────────────────────────
async def get_user_plan(user_id: str) -> str:
    profile = await db.profiles.find_one({"id": user_id}, {"_id": 0, "plan": 1, "is_admin": 1})
    if not profile:
        return "free"
    if profile.get("is_admin"):
        return "elite"
    return profile.get("plan", "free").lower()


async def require_plan(user: AuthenticatedUser, minimum_plan: str, feature_name: str = "this feature"):
    from services.subscription_service import FeatureGate
    plan = await get_user_plan(user.user_id)
    if not FeatureGate.requires_at_least(plan, minimum_plan):
        raise HTTPException(
            status_code=403,
            detail=f"Upgrade to {minimum_plan.title()} to access {feature_name}. Your current plan: {plan}."
        )


async def require_admin(current_user: AuthenticatedUser):
    profile = await db.profiles.find_one({"email": current_user.email})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
