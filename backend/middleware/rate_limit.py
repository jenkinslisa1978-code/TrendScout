"""
API Rate Limiting Middleware — per-user, per-plan enforcement.
Uses Redis for distributed rate limiting with in-memory fallback.
"""
import time
import logging
import os
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from common.database import db
from common.redis_cache import cache_incr, cache_get_ttl

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
    "/api/scoring/methodology",
}

# Auth routes with stricter IP-based limits (per-IP, not per-user)
AUTH_RATE_PATHS = {
    "/api/auth/login": 10,       # 10 per minute
    "/api/auth/register": 5,     # 5 per minute
    "/api/auth/refresh": 10,     # 10 per minute
    "/api/auth/login-submit": 10,
    "/api/auth/signup-submit": 5,
    "/api/auth/forgot-password": 5,
    "/api/auth/reset-password": 5,
}

WINDOW_SECONDS = 60

# Cache for user plan lookups
_plan_cache = {}
_PLAN_CACHE_TTL = 300


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if not path.startswith("/api") or path in EXEMPT_PATHS:
            return await call_next(request)

        # --- Auth route IP-based rate limiting ---
        if path in AUTH_RATE_PATHS:
            client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
            auth_limit = AUTH_RATE_PATHS[path]
            auth_key = f"auth_rate:{client_ip}:{path}"
            count = cache_incr(auth_key, WINDOW_SECONDS)
            reset_in = cache_get_ttl(auth_key) or WINDOW_SECONDS

            if count > auth_limit:
                logger.warning(f"Auth rate limit exceeded for {client_ip} on {path}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many requests. Please try again later.",
                            "retry_after": reset_in,
                        },
                    },
                    headers={"Retry-After": str(reset_in)},
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(auth_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, auth_limit - count))
            response.headers["X-RateLimit-Reset"] = str(reset_in)
            return response

        # --- Per-user, per-plan rate limiting ---
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return await call_next(request)

        token = auth_header.split(" ", 1)[1]
        user_plan = await _get_user_plan(token)
        if user_plan is None:
            return await call_next(request)

        user_id = user_plan["user_id"]
        plan = user_plan["plan"]
        limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

        # Atomic increment via Redis (or fallback)
        count = cache_incr(f"rate:{user_id}", WINDOW_SECONDS)
        reset_in = cache_get_ttl(f"rate:{user_id}") or WINDOW_SECONDS
        remaining = max(0, limit - count)

        if count > limit:
            logger.warning(f"Rate limit exceeded for user {user_id} (plan: {plan}, limit: {limit}/min)")
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": f"Rate limit exceeded. Upgrade your plan for higher limits. Current: {plan} ({limit}/min)",
                        "retry_after": reset_in,
                    },
                },
                headers={"Retry-After": str(reset_in)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)
        response.headers["X-RateLimit-Plan"] = plan
        return response


async def _get_user_plan(token: str) -> Optional[dict]:
    """Get user's plan from JWT token, with caching."""
    import jwt

    try:
        secret = os.environ.get("SUPABASE_JWT_SECRET")
        if not secret:
            return None
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return None

        cached = _plan_cache.get(user_id)
        if cached and (time.time() - cached["ts"]) < _PLAN_CACHE_TTL:
            return cached["data"]

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
