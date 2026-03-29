"""
Product Alert Subscriptions — Instant email alerts for high-scoring products.

Paid users only (starter+). Users subscribe to categories with a minimum score
threshold (default 50). When new products matching those criteria appear,
an instant email is sent via Resend.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid
import logging

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.helpers import get_user_plan

logger = logging.getLogger(__name__)

product_alerts_router = APIRouter(prefix="/api/product-alerts")

VALID_PLANS = {"starter", "pro", "elite"}


async def _require_paid(user: AuthenticatedUser):
    plan = await get_user_plan(user.user_id)
    if plan not in VALID_PLANS:
        raise HTTPException(
            status_code=403,
            detail="Product alerts require a paid plan (Starter or above). Upgrade to get instant alerts.",
        )
    return plan


# ── Pydantic models ──────────────────────────────────────────────────

class AlertSubscriptionCreate(BaseModel):
    categories: List[str] = Field(..., min_length=1, description="Categories to watch")
    min_score: int = Field(50, ge=1, le=100, description="Minimum demand/launch score")
    label: Optional[str] = Field(None, description="Optional friendly label")


class AlertSubscriptionUpdate(BaseModel):
    categories: Optional[List[str]] = None
    min_score: Optional[int] = Field(None, ge=1, le=100)
    label: Optional[str] = None
    active: Optional[bool] = None


# ── CRUD endpoints ───────────────────────────────────────────────────

@product_alerts_router.get("/subscriptions")
async def list_subscriptions(current_user: AuthenticatedUser = Depends(get_current_user)):
    """List all alert subscriptions for the current user."""
    await _require_paid(current_user)
    subs = await db.product_alert_subscriptions.find(
        {"user_id": current_user.user_id},
        {"_id": 0},
    ).sort("created_at", -1).to_list(50)
    return {"subscriptions": subs}


@product_alerts_router.post("/subscriptions")
async def create_subscription(
    body: AlertSubscriptionCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Create a new alert subscription."""
    await _require_paid(current_user)

    # Cap at 10 subscriptions per user
    count = await db.product_alert_subscriptions.count_documents({"user_id": current_user.user_id})
    if count >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 alert subscriptions per account.")

    doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.user_id,
        "user_email": current_user.email,
        "categories": [c.strip() for c in body.categories if c.strip()],
        "min_score": body.min_score,
        "label": body.label or ", ".join(body.categories[:3]),
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.product_alert_subscriptions.insert_one(doc)
    doc.pop("_id", None)
    return {"subscription": doc}


@product_alerts_router.put("/subscriptions/{sub_id}")
async def update_subscription(
    sub_id: str,
    body: AlertSubscriptionUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Update an existing alert subscription."""
    await _require_paid(current_user)
    existing = await db.product_alert_subscriptions.find_one(
        {"id": sub_id, "user_id": current_user.user_id}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Subscription not found.")

    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if body.categories is not None:
        updates["categories"] = [c.strip() for c in body.categories if c.strip()]
    if body.min_score is not None:
        updates["min_score"] = body.min_score
    if body.label is not None:
        updates["label"] = body.label
    if body.active is not None:
        updates["active"] = body.active

    await db.product_alert_subscriptions.update_one({"id": sub_id}, {"$set": updates})
    updated = await db.product_alert_subscriptions.find_one({"id": sub_id}, {"_id": 0})
    return {"subscription": updated}


@product_alerts_router.put("/subscriptions/{sub_id}/toggle")
async def toggle_subscription(
    sub_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Toggle active/inactive for a subscription."""
    await _require_paid(current_user)
    existing = await db.product_alert_subscriptions.find_one(
        {"id": sub_id, "user_id": current_user.user_id}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Subscription not found.")
    new_active = not existing.get("active", True)
    await db.product_alert_subscriptions.update_one(
        {"id": sub_id}, {"$set": {"active": new_active, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"active": new_active}


@product_alerts_router.delete("/subscriptions/{sub_id}")
async def delete_subscription(
    sub_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Delete an alert subscription."""
    await _require_paid(current_user)
    result = await db.product_alert_subscriptions.delete_one(
        {"id": sub_id, "user_id": current_user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found.")
    return {"deleted": True}


# ── Alert history ────────────────────────────────────────────────────

@product_alerts_router.get("/history")
async def get_alert_history(
    limit: int = 30,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get history of alerts sent to this user."""
    await _require_paid(current_user)
    history = await db.product_alert_history.find(
        {"user_id": current_user.user_id},
        {"_id": 0},
    ).sort("sent_at", -1).limit(limit).to_list(limit)
    return {"alerts": history}


# ── Available categories (public, for the UI dropdown) ───────────────

@product_alerts_router.get("/categories")
async def get_available_categories(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get distinct product categories available for alerting."""
    categories = await db.products.distinct("category")
    return {"categories": sorted([c for c in categories if c])}


# ── Trigger: check new products against subscriptions ────────────────

async def check_and_send_alerts(product: dict):
    """
    Called when a product is created/updated with score >= 50.
    Checks all active subscriptions and sends instant email alerts.
    """
    from services.email_service import email_service

    score = product.get("launch_score") or product.get("market_score") or 0
    category = product.get("category", "")
    product_id = product.get("id", "")
    product_name = product.get("product_name", "Unknown")

    if score < 50 or not category:
        return

    # Find matching active subscriptions
    subs = await db.product_alert_subscriptions.find({
        "active": True,
        "min_score": {"$lte": score},
        "categories": {"$in": [category]},
    }).to_list(None)

    if not subs:
        return

    for sub in subs:
        user_id = sub.get("user_id")
        user_email = sub.get("user_email")
        sub_id = sub.get("id")

        if not user_email:
            continue

        # Dedupe: don't send same product+user combo twice
        already_sent = await db.product_alert_history.find_one({
            "user_id": user_id,
            "product_id": product_id,
        })
        if already_sent:
            continue

        # Verify user still has a paid plan
        plan = await get_user_plan(user_id)
        if plan not in VALID_PLANS:
            continue

        # Send the email
        try:
            result = await email_service.send_instant_product_alert(
                to_email=user_email,
                product_name=product_name,
                category=category,
                score=score,
                product_id=product_id,
                trend_label=product.get("trend_stage") or product.get("early_trend_label") or "Emerging",
            )
            status = result.get("status", "error")
        except Exception as e:
            logger.error(f"Alert email failed for {user_email}: {e}")
            status = "error"

        # Record in history
        await db.product_alert_history.insert_one({
            "id": str(uuid.uuid4()),
            "subscription_id": sub_id,
            "user_id": user_id,
            "user_email": user_email,
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "score": score,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "email_status": status,
        })

    logger.info(f"Processed {len(subs)} alert subscriptions for product '{product_name}' (score={score})")


routers = [product_alerts_router]
