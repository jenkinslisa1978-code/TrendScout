"""
API Rate Limiting Middleware — per-user, per-plan enforcement.
Uses in-memory storage (suitable for single-instance; migrate to Redis for multi-instance).
"""
import time
import logging
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from common.database import db

logger = logging.getLogger(__name__)

# Requests per minute per plan
PLAN_LIMITS = {
    "free": 30,
    "starter": 120,
    "pro": 300,
    "elite": 600,
    "admin": 1000,
}

# Paths exempt from rate limiting
EXEMPT_PATHS = {
    "/api/health",
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/forgot-password",
    "/api/scoring/methodology",
}

# In-memory rate limit store: {user_id: {"count": int, "window_start": float}}
_rate_store = {}
WINDOW_SECONDS = 60


def _get_rate_entry(user_id: str):
    now = time.time()
    entry = _rate_store.get(user_id)
    if entry is None or (now - entry["window_start"]) >= WINDOW_SECONDS:
        _rate_store[user_id] = {"count": 0, "window_start": now}
        return _rate_store[user_id]
    return entry


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip non-API routes and exempt paths
        if not path.startswith("/api") or path in EXEMPT_PATHS:
            return await call_next(request)

        # Extract user from auth header
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return await call_next(request)

        token = auth_header.split(" ", 1)[1]

        # Look up user plan
        user_plan = await _get_user_plan(token)
        if user_plan is None:
            return await call_next(request)

        user_id = user_plan["user_id"]
        plan = user_plan["plan"]
        limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

        # Check rate
        entry = _get_rate_entry(user_id)
        entry["count"] += 1

        remaining = max(0, limit - entry["count"])
        reset_in = int(WINDOW_SECONDS - (time.time() - entry["window_start"]))

        response = await call_next(request) if entry["count"] <= limit else None

        if response is None:
            logger.warning(f"Rate limit exceeded for user {user_id} (plan: {plan}, limit: {limit}/min)")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "plan": plan,
                    "limit": f"{limit} requests per minute",
                    "retry_after": reset_in,
                    "upgrade_message": f"Upgrade your plan for higher limits. Current: {plan} ({limit}/min)",
                },
            )

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)
        response.headers["X-RateLimit-Plan"] = plan

        return response


# Cache for user plan lookups (avoid DB hit on every request)
_plan_cache = {}
_PLAN_CACHE_TTL = 300  # 5 min


async def _get_user_plan(token: str) -> Optional[dict]:
    """Get user's plan from JWT token, with caching."""
    import jwt
    import os

    try:
        secret = os.environ.get("SUPABASE_JWT_SECRET")
        if not secret:
            return None
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return None

        # Check cache
        cached = _plan_cache.get(user_id)
        if cached and (time.time() - cached["ts"]) < _PLAN_CACHE_TTL:
            return cached["data"]

        # Fetch from DB
        user = await db.profiles.find_one({"id": user_id}, {"_id": 0, "id": 1, "subscription_plan": 1, "role": 1})
        if not user:
            return None

        plan = user.get("subscription_plan", "free")
        if user.get("role") == "admin":
            plan = "admin"

        data = {"user_id": user_id, "plan": plan}
        _plan_cache[user_id] = {"data": data, "ts": time.time()}
        return data

    except Exception:
        return None
