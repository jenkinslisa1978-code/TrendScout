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

from services.notification_service import create_notification_service, NotificationType

notifications_router = APIRouter(prefix="/api/notifications")

@notifications_router.get("/")
async def get_notifications(
    current_user: AuthenticatedUser = Depends(get_current_user),
    limit: int = 50,
    unread_only: bool = False,
    types: Optional[str] = None
):
    """
    Get user's notifications.
    
    Args:
        limit: Max notifications to return (default 50)
        unread_only: Only return unread notifications
        types: Comma-separated list of notification types to filter
    """
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    
    # Parse types if provided
    type_list = None
    if types:
        type_list = [t.strip() for t in types.split(",")]
    
    notifications = await notification_service.get_notifications(
        user_id=current_user.user_id,
        limit=limit,
        unread_only=unread_only,
        notification_types=type_list
    )
    
    unread_count = await notification_service.get_unread_count(current_user.user_id)
    
    return {
        "notifications": notifications,
        "count": len(notifications),
        "unread_count": unread_count
    }


@notifications_router.get("/unread-count")
async def get_unread_count(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get count of unread notifications"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    count = await notification_service.get_unread_count(current_user.user_id)
    
    return {"unread_count": count}


@notifications_router.post("/mark-read")
async def mark_notifications_read(
    notification_ids: List[str],
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Mark specific notifications as read"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    modified = await notification_service.mark_as_read(
        user_id=current_user.user_id,
        notification_ids=notification_ids
    )
    
    return {"status": "success", "modified_count": modified}


@notifications_router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Mark all notifications as read"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    modified = await notification_service.mark_all_as_read(current_user.user_id)
    
    return {"status": "success", "modified_count": modified}


@notifications_router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Delete a specific notification"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    deleted = await notification_service.delete_notification(
        user_id=current_user.user_id,
        notification_id=notification_id
    )
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"status": "deleted"}


@notifications_router.get("/preferences")
async def get_notification_preferences(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get user's notification preferences"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    prefs = await notification_service.get_user_preferences(current_user.user_id)
    
    return prefs


class NotificationPreferencesUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    alert_threshold: Optional[int] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    watchlist_priority_enabled: Optional[bool] = None
    notification_types: Optional[Dict[str, bool]] = None


@notifications_router.put("/preferences")
async def update_notification_preferences(
    updates: NotificationPreferencesUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update user's notification preferences"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    
    # Convert to dict, excluding None values
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    
    prefs = await notification_service.update_user_preferences(
        user_id=current_user.user_id,
        updates=update_dict
    )
    
    return prefs


@notifications_router.post("/test-alert")
async def send_test_notification(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Send a test notification to the current user (for testing)"""
    from services.notification_service import create_notification_service, NotificationType
    
    notification_service = create_notification_service(db)
    
    # Get a sample product
    product = await db.products.find_one(
        {"launch_score": {"$gte": 75}},
        {"_id": 0}
    )
    
    if not product:
        raise HTTPException(status_code=404, detail="No products with high launch score found")
    
    notification = await notification_service.create_notification(
        user_id=current_user.user_id,
        notification_type=NotificationType.STRONG_LAUNCH,
        product=product,
        force=True  # Skip dedup for test
    )
    
    if notification:
        return {
            "status": "success",
            "message": "Test notification sent",
            "notification": notification
        }
    else:
        return {
            "status": "skipped",
            "message": "Notification was skipped (check preferences)"
        }


@notifications_router.post("/radar-scan")
async def run_radar_scan(
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Scan products for radar threshold crossings and generate notifications for all users."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    async def _run_scan():
        from services.notification_service import create_notification_service, NotificationType
        notification_service = create_notification_service(db)

        # Radar thresholds
        LAUNCH_SCORE_THRESHOLD = 70
        MARGIN_THRESHOLD = 0.5  # 50% margin

        # Find products that crossed radar thresholds
        radar_products = await db.products.find(
            {"$or": [
                {"launch_score": {"$gte": LAUNCH_SCORE_THRESHOLD}},
                {"early_trend_label": {"$in": ["exploding", "rising"]}},
            ]},
            {"_id": 0}
        ).sort("launch_score", -1).limit(20).to_list(20)

        if not radar_products:
            return

        # Mark products as radar detected
        product_ids = [p["id"] for p in radar_products]
        await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": {"radar_detected": True, "radar_detected_at": datetime.now(timezone.utc).isoformat()}}
        )

        # Get all users to notify
        users = await db.profiles.find(
            {"id": {"$exists": True}},
            {"_id": 0, "id": 1}
        ).to_list(100)

        notifications_created = 0
        for user in users:
            for product in radar_products[:5]:  # Top 5 per user
                try:
                    notif = await notification_service.create_notification(
                        user_id=user["id"],
                        notification_type=NotificationType.RADAR_DETECTED,
                        product=product,
                    )
                    if notif:
                        notifications_created += 1
                except Exception:
                    pass

        logging.info(f"Radar scan complete: {len(radar_products)} products detected, {notifications_created} notifications")

    background_tasks.add_task(_run_scan)
    return {"status": "started", "message": "Radar scan initiated in background"}


@notifications_router.get("/radar-detections")
async def get_radar_detections(
    limit: int = 10,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get recently radar-detected products."""
    products = await db.products.find(
        {"radar_detected": True},
        {"_id": 0}
    ).sort("radar_detected_at", -1).limit(limit).to_list(limit)

    return {"products": products, "count": len(products)}


@notifications_router.post("/radar-digest")
async def send_radar_digest_email(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Send a radar digest email to the current user with recent detections."""
    from services.email_service import EmailService

    # Get recent radar detections
    products = await db.products.find(
        {"radar_detected": True},
        {"_id": 0}
    ).sort("radar_detected_at", -1).limit(5).to_list(5)

    if not products:
        return {"status": "skipped", "message": "No radar detections to send"}

    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    user = await db.auth_users.find_one({"id": current_user.user_id}, {"_id": 0, "email": 1})
    email = user.get("email") if user else (profile.get("email") if profile else None)
    user_name = profile.get("full_name", "there") if profile else "there"

    if not email:
        raise HTTPException(status_code=400, detail="No email found for user")

    # Build digest HTML
    product_rows = ""
    for p in products:
        margin = p.get("estimated_margin", 0)
        margin_pct = int((margin / p.get("estimated_retail_price", 1)) * 100) if p.get("estimated_retail_price") else 0
        product_rows += f"""
        <tr style="border-bottom:1px solid #f1f5f9;">
            <td style="padding:12px 8px;font-weight:600;color:#1e293b;">{p.get('product_name','Unknown')}</td>
            <td style="padding:12px 8px;text-align:center;"><span style="background:#eef2ff;color:#4f46e5;padding:4px 10px;border-radius:12px;font-weight:700;">{p.get('launch_score',0)}</span></td>
            <td style="padding:12px 8px;text-align:center;color:#059669;font-weight:600;">{margin_pct}%</td>
            <td style="padding:12px 8px;text-align:center;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:8px;font-size:12px;">{p.get('early_trend_label','—')}</span></td>
        </tr>"""

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#ffffff;">
        <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:32px;text-align:center;">
            <h1 style="color:white;margin:0;font-size:24px;">TrendScout Radar Digest</h1>
            <p style="color:#c7d2fe;margin:8px 0 0;">Your daily winning product detections</p>
        </div>
        <div style="padding:24px;">
            <p style="color:#475569;">Hi {user_name},</p>
            <p style="color:#475569;">TrendScout Radar detected <strong>{len(products)} winning products</strong> for you today:</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;">
                <thead>
                    <tr style="border-bottom:2px solid #e2e8f0;">
                        <th style="padding:8px;text-align:left;color:#64748b;font-size:12px;">PRODUCT</th>
                        <th style="padding:8px;text-align:center;color:#64748b;font-size:12px;">SCORE</th>
                        <th style="padding:8px;text-align:center;color:#64748b;font-size:12px;">MARGIN</th>
                        <th style="padding:8px;text-align:center;color:#64748b;font-size:12px;">STAGE</th>
                    </tr>
                </thead>
                <tbody>{product_rows}</tbody>
            </table>
            <div style="text-align:center;margin:24px 0;">
                <a href="{os.environ.get('FRONTEND_URL', 'https://trendscout.click')}/dashboard" style="background:#4f46e5;color:white;padding:12px 32px;border-radius:8px;text-decoration:none;font-weight:600;">View Full Dashboard</a>
            </div>
            <p style="color:#94a3b8;font-size:12px;text-align:center;">You're receiving this because you have radar alerts enabled.</p>
        </div>
    </div>"""

    email_service = EmailService()
    result = await email_service.send_email(
        to_email=email,
        subject=f"TrendScout Radar: {len(products)} winning products detected",
        html_content=html
    )

    return {"status": "sent" if result.get("success") else "failed", "products_included": len(products)}


@notifications_router.get("/threshold-subscription")
async def get_threshold_subscription(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get user's threshold alert subscription settings."""
    sub = await db.threshold_subscriptions.find_one(
        {"user_id": current_user.user_id},
        {"_id": 0}
    )
    if not sub:
        sub = {
            "user_id": current_user.user_id,
            "enabled": False,
            "score_threshold": 75,
            "categories": [],
            "email_alerts": True,
            "in_app_alerts": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    return sub


class ThresholdSubscriptionUpdate(BaseModel):
    enabled: Optional[bool] = None
    score_threshold: Optional[int] = None
    categories: Optional[List[str]] = None
    email_alerts: Optional[bool] = None
    in_app_alerts: Optional[bool] = None


@notifications_router.put("/threshold-subscription")
async def update_threshold_subscription(
    updates: ThresholdSubscriptionUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update user's threshold alert subscription."""
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.threshold_subscriptions.update_one(
        {"user_id": current_user.user_id},
        {"$set": update_dict, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return await db.threshold_subscriptions.find_one(
        {"user_id": current_user.user_id},
        {"_id": 0}
    )


@notifications_router.post("/scan-thresholds")
async def scan_thresholds_for_alerts(
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Admin: Scan products against all user threshold subscriptions and send alerts."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    async def _scan():
        from services.notification_service import create_notification_service, NotificationType
        ns = create_notification_service(db)

        subs = await db.threshold_subscriptions.find(
            {"enabled": True},
            {"_id": 0}
        ).to_list(500)

        if not subs:
            return

        all_products = await db.products.find(
            {"launch_score": {"$gte": 40}},
            {"_id": 0}
        ).sort("launch_score", -1).limit(50).to_list(50)

        total = 0
        for sub in subs:
            threshold = sub.get("score_threshold", 75)
            cats = sub.get("categories", [])
            user_id = sub["user_id"]

            matching = [
                p for p in all_products
                if p.get("launch_score", 0) >= threshold
                and (not cats or p.get("category") in cats)
            ]

            for product in matching[:5]:
                try:
                    notif = await ns.create_notification(
                        user_id=user_id,
                        notification_type=NotificationType.SCORE_MILESTONE,
                        product=product,
                    )
                    if notif:
                        total += 1
                except Exception:
                    pass

        logging.info(f"Threshold scan: {total} notifications created for {len(subs)} subscriptions")

    background_tasks.add_task(_scan)
    return {"status": "started", "message": "Threshold scan initiated"}




# =====================
# ROUTES - User / Onboarding
# =====================



routers = [notifications_router]
