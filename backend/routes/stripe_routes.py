"""Stripe billing routes: checkout, portal, webhook, subscription, plans."""
from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone, timedelta
import os
import logging

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.models import CheckoutSessionRequest, PortalSessionRequest
from common.helpers import get_user_plan

stripe_router = APIRouter(prefix="/api/stripe")


@stripe_router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    from services.subscription_service import create_subscription_service
    subscription_service = create_subscription_service(db)
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    user_email = profile.get("email") if profile else current_user.email
    result = await subscription_service.create_checkout_session(
        user_id=current_user.user_id,
        user_email=user_email,
        plan=request.plan,
        success_url=request.success_url,
        cancel_url=request.cancel_url
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Checkout failed"))
    return result


@stripe_router.post("/create-portal-session")
async def create_portal_session(
    request: PortalSessionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    from services.subscription_service import create_subscription_service
    subscription_service = create_subscription_service(db)
    result = await subscription_service.create_portal_session(
        user_id=current_user.user_id,
        return_url=request.return_url
    )
    if not result.get("success"):
        if result.get("demo_mode"):
            return {"url": request.return_url, "demo_mode": True}
        raise HTTPException(status_code=400, detail=result.get("error", "Portal session failed"))
    return result


@stripe_router.post("/webhook")
async def stripe_webhook(request: Request):
    from services.subscription_service import create_subscription_service
    import stripe as stripe_module
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    if not stripe_key:
        return {"received": True, "demo_mode": True}
    try:
        stripe_module.api_key = stripe_key
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')

        # Always verify signature if webhook secret is set
        if not webhook_secret:
            raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")

        event = stripe_module.Webhook.construct_event(payload, sig_header, webhook_secret)

        subscription_service = create_subscription_service(db)
        result = await subscription_service.handle_webhook_event(event)
        return {"received": True, **result}
    except stripe_module.error.SignatureVerificationError as e:
        logging.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@stripe_router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    from services.subscription_service import create_subscription_service
    subscription_service = create_subscription_service(db)
    result = await subscription_service.downgrade_to_free(current_user.user_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Cancellation failed"))
    return result


@stripe_router.get("/plans")
async def get_subscription_plans():
    from services.subscription_service import get_all_plans
    return {"plans": get_all_plans(), "currency": "gbp", "currency_symbol": "\u00a3"}


@stripe_router.get("/subscription")
async def get_user_subscription(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    from services.subscription_service import create_subscription_service
    subscription_service = create_subscription_service(db)
    return await subscription_service.get_user_subscription(current_user.user_id)


@stripe_router.get("/feature-access")
async def get_feature_access(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    from services.subscription_service import FeatureGate
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    is_admin = profile.get("is_admin", False) if profile else False
    if not is_admin and current_user.email:
        admin_by_email = await db.profiles.find_one(
            {"email": current_user.email, "is_admin": True}, {"_id": 0}
        )
        if admin_by_email:
            is_admin = True
            await db.profiles.update_one(
                {"id": current_user.user_id},
                {"$set": {"is_admin": True, "plan": "elite"}},
                upsert=True
            )
    if is_admin:
        plan = "elite"
    else:
        plan = profile.get("plan", "free") if profile else "free"
    store_count = await db.stores.count_documents({"user_id": current_user.user_id})
    features = FeatureGate.get_plan_features(plan)
    daily_limit = features.get("max_analyses_daily", 2)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    usage_doc = await db.daily_usage.find_one(
        {"user_id": current_user.user_id, "date": today}, {"_id": 0}
    )
    insights_used = usage_doc.get("insights_used", 0) if usage_doc else 0

    # Check for active trial
    trial_data = None
    trial_unlocks = []
    if plan == "free":
        from routes.trial import TRIAL_FEATURES
        trial = await db.trials.find_one({"user_id": current_user.user_id}, {"_id": 0})
        if trial:
            activated_at = datetime.fromisoformat(trial["activated_at"])
            expires_at = activated_at + timedelta(hours=24)
            now = datetime.now(timezone.utc)
            if now < expires_at:
                feature_info = TRIAL_FEATURES.get(trial["feature"], {})
                trial_unlocks = feature_info.get("unlocks", [])
                trial_data = {
                    "active": True,
                    "feature": trial["feature"],
                    "feature_label": feature_info.get("label", ""),
                    "unlocks": trial_unlocks,
                    "remaining_seconds": int((expires_at - now).total_seconds()),
                    "expires_at": expires_at.isoformat(),
                }
            else:
                trial_data = {"active": False, "expired": True}

    return {
        "plan": plan,
        "is_admin": is_admin,
        "admin_bypass": is_admin,
        "trial": trial_data,
        "trial_unlocks": trial_unlocks,
        "features": {
            "full_reports": FeatureGate.can_access_full_reports(plan),
            "full_insights": FeatureGate.can_access_full_insights(plan),
            "pdf_export": FeatureGate.can_export_pdf(plan),
            "watchlist": FeatureGate.can_access_watchlist(plan),
            "alerts": FeatureGate.can_access_alerts(plan),
            "early_trends": FeatureGate.can_access_early_trends(plan),
            "automation_insights": FeatureGate.can_access_automation_insights(plan),
            "advanced_opportunities": FeatureGate.can_access_advanced_opportunities(plan),
            "direct_publish": FeatureGate.can_direct_publish(plan),
            "automated_reports": FeatureGate.can_access_automated_reports(plan),
            "priority_alerts": FeatureGate.can_access_priority_alerts(plan),
            "max_stores": FeatureGate.get_max_stores(plan),
            "can_create_store": FeatureGate.can_create_store(plan, store_count),
            "current_store_count": store_count,
            "max_analyses_daily": daily_limit,
            "insights_used_today": insights_used,
        }
    }


routers = [stripe_router]
