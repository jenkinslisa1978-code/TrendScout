"""
Shared helper functions used across multiple route modules.
"""
import os
import jwt
import time
from datetime import datetime, timezone
from fastapi import HTTPException, Depends

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.scoring import calculate_success_probability


async def get_user_plan(user_id: str) -> str:
    """Get user's current plan from profile. Admins always get 'elite'."""
    profile = await db.profiles.find_one({"id": user_id}, {"_id": 0, "plan": 1, "is_admin": 1})
    if not profile:
        return "free"
    if profile.get("is_admin"):
        return "elite"
    return profile.get("plan", "free").lower()


async def require_plan(user: AuthenticatedUser, minimum_plan: str, feature_name: str = "this feature"):
    """Raise 403 if user's plan is below the required minimum."""
    from services.subscription_service import FeatureGate
    plan = await get_user_plan(user.user_id)
    if not FeatureGate.requires_at_least(plan, minimum_plan):
        raise HTTPException(
            status_code=403,
            detail=f"Upgrade to {minimum_plan.title()} to access {feature_name}. Your current plan: {plan}."
        )


async def require_admin(current_user: AuthenticatedUser):
    """Raise 403 if user is not an admin."""
    profile = await db.profiles.find_one(
        {"id": current_user.user_id}, {"_id": 0, "is_admin": 1}
    )
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")


def generate_auth_token(user_id: str, email: str, ttl_seconds: int = 900) -> str:
    """Generate a short-lived JWT access token (default 15 min)."""
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "type": "access",
        "iat": int(time.time()),
        "exp": int(time.time()) + ttl_seconds,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def generate_refresh_token(user_id: str, email: str) -> str:
    """Generate a long-lived refresh token (7 days)."""
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    payload = {
        "sub": user_id,
        "email": email,
        "type": "refresh",
        "iat": int(time.time()),
        "exp": int(time.time()) + 60 * 60 * 24 * 7,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_refresh_token(token: str) -> dict:
    """Verify and decode a refresh token. Returns payload or raises."""
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    payload = jwt.decode(token, secret, algorithms=["HS256"], options={"require": ["sub", "exp"]})
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token")
    return payload


def set_auth_cookies(response, user_id: str, email: str):
    """Set __Host-refresh and __Host-csrf cookies on a response."""
    from middleware.csrf import generate_csrf_token
    refresh = generate_refresh_token(user_id, email)
    response.set_cookie(
        key="__Host-refresh",
        value=refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 7,
    )
    response.set_cookie(
        key="__Host-csrf",
        value=generate_csrf_token(),
        httponly=False,
        secure=True,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 7,
    )
    return response


def build_winning_reasons(product: dict) -> list:
    """Build human-readable reasons for why this product was selected."""
    reasons = []
    score = product.get("launch_score", 0)
    if score >= 80:
        reasons.append(f"Exceptional launch score of {score}/100")
    elif score >= 60:
        reasons.append(f"Strong launch score of {score}/100")
    prob = product.get("success_probability", 0)
    if prob >= 70:
        reasons.append(f"{prob}% predicted success probability")
    stage = product.get("trend_stage", "")
    if stage in ["Emerging", "Exploding"]:
        reasons.append(f"Product is in '{stage}' trend stage - early mover advantage")
    margin = product.get("estimated_margin", 0)
    if margin and margin > 10:
        reasons.append(f"Healthy profit margin (est. {margin:.0f}%+)")
    reviews = product.get("amazon_reviews", 0)
    rating = product.get("amazon_rating", 0)
    if rating and rating >= 4.5:
        reasons.append(f"High customer satisfaction ({rating} stars, {reviews:,} reviews)")
    if not reasons:
        reasons.append("Best available product based on current market data")
    return reasons


async def track_product_store_created(product_id: str):
    """Track when a store is created for a product."""
    await db.products.update_one(
        {"id": product_id},
        {
            "$inc": {"stores_created": 1, "success_signals": 1},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    await recalculate_product_success(product_id)


async def track_product_exported(product_id: str):
    """Track when a product is exported."""
    await db.products.update_one(
        {"id": product_id},
        {
            "$inc": {"exports_count": 1, "success_signals": 2},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    await recalculate_product_success(product_id)


async def recalculate_product_success(product_id: str):
    """Recalculate success probability for a product."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        return
    success_probability, proven_winner, user_engagement_score = calculate_success_probability(product)
    await db.products.update_one(
        {"id": product_id},
        {
            "$set": {
                "success_probability": success_probability,
                "proven_winner": proven_winner,
                "user_engagement_score": user_engagement_score,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )


async def run_automation_on_products(products: list) -> dict:
    """Helper to run full automation pipeline on a list of products."""
    from common.scoring import run_full_automation
    alerts_generated = 0
    for product in products:
        product.pop('_id', None)
        result = run_full_automation(product)
        processed = result['product']
        await db.products.update_one(
            {"id": processed['id']},
            {"$set": processed},
            upsert=True
        )
        if result['alert']:
            await db.trend_alerts.insert_one(result['alert'])
            alerts_generated += 1
        if result.get('early_alert'):
            await db.trend_alerts.insert_one(result['early_alert'])
            alerts_generated += 1
    return {"products_processed": len(products), "alerts_generated": alerts_generated}
