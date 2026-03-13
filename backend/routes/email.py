from fastapi import APIRouter, HTTPException, Request, Depends, Header, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import uuid
import json
import logging
import re

from auth import get_current_user, get_optional_user, AuthenticatedUser
from common.database import db
from common.cache import get_cached, set_cached, slugify, get_margin_range
from common.helpers import (
    get_user_plan, require_plan, require_admin, build_winning_reasons,
    track_product_store_created, track_product_exported, run_automation_on_products,
)
from common.scoring import (
    calculate_trend_score, calculate_trend_stage, calculate_opportunity_rating,
    generate_ai_summary, calculate_early_trend_score, calculate_market_score,
    calculate_launch_score, generate_mock_competitor_data, calculate_success_probability,
    should_generate_alert, generate_alert, run_full_automation, generate_early_trend_alert,
    should_generate_early_trend_alert,
)
from common.models import *

email_router = APIRouter(prefix="/api/email")
api_router = APIRouter(prefix="/api")

@email_router.post("/send-test")
async def send_test_email(
    to_email: str,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send a test email to verify Resend integration (admin only).
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.email_service import email_service
    
    html_content = """
    <html>
    <body style="font-family: sans-serif; padding: 20px;">
        <h1 style="color: #4f46e5;">TrendScout Test Email</h1>
        <p>This is a test email from TrendScout to verify the email integration is working correctly.</p>
        <p style="color: #6b7280; font-size: 12px;">Sent via Resend API</p>
    </body>
    </html>
    """
    
    result = await email_service.send_email(
        to_email=to_email,
        subject="TrendScout - Test Email",
        html_content=html_content
    )
    
    return result


@email_router.post("/send-weekly-digest")
async def send_weekly_digest_to_user(
    to_email: str,
    user_name: Optional[str] = None,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send weekly digest email to a specific user (admin only).
    Uses latest weekly report data.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.email_service import email_service
    
    # Get latest weekly report
    report = await db.reports.find_one(
        {
            "metadata.report_type": "weekly_winning_products",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0}
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="No weekly report available")
    
    result = await email_service.send_weekly_digest(
        to_email=to_email,
        user_name=user_name or "there",
        report_data=report
    )
    
    return result


@email_router.post("/send-weekly-digest-all")
async def send_weekly_digest_to_all_subscribers(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send weekly digest email to all subscribed users (admin only).
    This is called by the scheduled job.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.email_service import email_service
    
    # Get latest weekly report
    report = await db.reports.find_one(
        {
            "metadata.report_type": "weekly_winning_products",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0}
    )
    
    if not report:
        return {"status": "skipped", "reason": "No weekly report available", "sent": 0}
    
    # Get all users subscribed to weekly digest
    subscribed_users = await db.profiles.find(
        {"email_preferences.weekly_digest": True},
        {"_id": 0, "email": 1, "name": 1}
    ).to_list(None)
    
    # If no explicit subscribers, check for users with email
    if not subscribed_users:
        subscribed_users = await db.profiles.find(
            {"email": {"$exists": True, "$ne": None}},
            {"_id": 0, "email": 1, "name": 1}
        ).to_list(50)  # Limit to 50 for safety
    
    results = {
        "status": "completed",
        "total_subscribers": len(subscribed_users),
        "sent": 0,
        "failed": 0,
        "errors": []
    }
    
    for user in subscribed_users:
        try:
            result = await email_service.send_weekly_digest(
                to_email=user.get('email'),
                user_name=user.get('name', user.get('email', '').split('@')[0]),
                report_data=report
            )
            if result.get('status') == 'success':
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'email': user.get('email'),
                    'error': result.get('error')
                })
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'email': user.get('email'),
                'error': str(e)
            })
    
    return results


@email_router.get("/subscription-status")
async def get_email_subscription_status(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Get current user's email subscription status.
    """
    user = await db.profiles.find_one(
        {"email": current_user.email},
        {"_id": 0, "email_preferences": 1}
    )
    
    default_prefs = {
        "weekly_digest": True,
        "product_alerts": True,
        "marketing": False
    }
    
    return {
        "email": current_user.email,
        "preferences": user.get("email_preferences", default_prefs) if user else default_prefs
    }


@email_router.post("/subscription-status")
async def update_email_subscription_status(
    weekly_digest: Optional[bool] = True,
    product_alerts: Optional[bool] = True,
    marketing: Optional[bool] = False,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Update current user's email subscription preferences.
    """
    preferences = {
        "weekly_digest": weekly_digest,
        "product_alerts": product_alerts,
        "marketing": marketing
    }
    
    await db.profiles.update_one(
        {"email": current_user.email},
        {
            "$set": {"email_preferences": preferences}
        }
    )
    
    return {
        "status": "updated",
        "email": current_user.email,
        "preferences": preferences
    }


@email_router.get("/product-of-the-week")
async def get_product_of_the_week():
    """
    Get the Product of the Week - the highest launch score product.
    Public endpoint for display on landing/trending pages.
    """
    cursor = db.products.find(
        {"launch_score": {"$gte": 60}},
        {"_id": 0}
    ).sort([("launch_score", -1), ("market_score", -1)]).limit(4)
    
    products = await cursor.to_list(4)
    
    if not products:
        # Fallback to any top product
        cursor = db.products.find({}, {"_id": 0}).sort([("market_score", -1)]).limit(4)
        products = await cursor.to_list(4)
    
    if not products:
        raise HTTPException(status_code=404, detail="No products available")
    
    featured = products[0]
    runners_up = products[1:4] if len(products) > 1 else []
    
    return {
        "product": {
            "id": featured["id"],
            "product_name": featured.get("product_name"),
            "category": featured.get("category"),
            "image_url": featured.get("image_url"),
            "launch_score": featured.get("launch_score", 0),
            "launch_score_label": featured.get("launch_score_label", "risky"),
            "trend_stage": featured.get("trend_stage"),
            "trend_score": featured.get("trend_score"),
            "market_score": featured.get("market_score"),
            "early_trend_label": featured.get("early_trend_label"),
            "margin_range": get_margin_range(featured.get("estimated_margin", 0)),
        },
        "runners_up": [
            {
                "id": p["id"],
                "product_name": p.get("product_name"),
                "category": p.get("category"),
                "launch_score": p.get("launch_score", 0),
            }
            for p in runners_up
        ],
        "week_of": datetime.now(timezone.utc).strftime("%B %d, %Y"),
    }


@email_router.post("/send-product-of-the-week")
async def send_product_of_the_week_email(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send Product of the Week email to all subscribed users.
    Includes personalized referral links for viral loop.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.email_service import email_service
    
    # Get top product
    cursor = db.products.find(
        {"launch_score": {"$gte": 60}},
        {"_id": 0}
    ).sort([("launch_score", -1), ("market_score", -1)]).limit(4)
    products = await cursor.to_list(4)
    
    if not products:
        return {"status": "skipped", "reason": "No qualifying products", "sent": 0}
    
    featured = products[0]
    runners_up = products[1:4] if len(products) > 1 else []
    
    # Build product data with runners_up for the email template
    product_data = {
        "id": featured["id"],
        "product_name": featured.get("product_name"),
        "category": featured.get("category"),
        "launch_score": featured.get("launch_score", 0),
        "trend_stage": featured.get("trend_stage"),
        "margin_range": get_margin_range(featured.get("estimated_margin", 0)),
        "_runners_up": [
            {
                "product_name": p.get("product_name"),
                "category": p.get("category"),
                "launch_score": p.get("launch_score", 0),
            }
            for p in runners_up
        ],
    }
    
    # Get subscribed users
    subscribed_users = await db.profiles.find(
        {"email": {"$exists": True, "$ne": None}},
        {"_id": 0, "id": 1, "email": 1, "name": 1}
    ).to_list(100)
    
    results = {"status": "completed", "total": len(subscribed_users), "sent": 0, "failed": 0, "product": featured.get("product_name")}
    
    for user in subscribed_users:
        # Get user's referral code for viral loop
        referral = await db.user_referrals.find_one({"user_id": user.get("id")}, {"_id": 0, "referral_code": 1})
        referral_code = referral.get("referral_code") if referral else None
        
        try:
            result = await email_service.send_product_of_the_week(
                to_email=user.get("email"),
                user_name=user.get("name", user.get("email", "").split("@")[0]),
                product=product_data,
                referral_code=referral_code,
            )
            if result.get("status") == "success":
                results["sent"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["failed"] += 1
            logger.error(f"POTW email error for {user.get('email')}: {e}")
    
    return results


@api_router.post("/newsletter/subscribe")
async def subscribe_newsletter(request: Request):
    """
    Subscribe an email to the Product of the Week newsletter.
    Public endpoint - no auth required.
    """
    body = await request.json()
    email = body.get("email", "").strip().lower()

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")

    # Check if already subscribed
    existing = await db.newsletter_subscribers.find_one({"email": email})
    if existing:
        if existing.get("status") == "active":
            return {"status": "already_subscribed", "email": email}
        # Reactivate
        await db.newsletter_subscribers.update_one(
            {"email": email},
            {"$set": {"status": "active", "resubscribed_at": datetime.now(timezone.utc).isoformat()}}
        )
        return {"status": "resubscribed", "email": email}

    await db.newsletter_subscribers.insert_one({
        "email": email,
        "status": "active",
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
        "source": "landing_page",
    })

    return {"status": "subscribed", "email": email}


@api_router.post("/newsletter/unsubscribe")
async def unsubscribe_newsletter(request: Request):
    """Unsubscribe from the newsletter."""
    body = await request.json()
    email = body.get("email", "").strip().lower()

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    result = await db.newsletter_subscribers.update_one(
        {"email": email},
        {"$set": {"status": "unsubscribed", "unsubscribed_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {"status": "unsubscribed", "email": email}



routers = [email_router, api_router]
