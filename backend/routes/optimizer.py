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

from services.budget_optimizer import recommend_for_test, recommend_for_variation, generate_dashboard_summary, RULE_PRESETS, get_presets
from services.notification_service import create_notification_service, NotificationType

optimizer_router = APIRouter(prefix="/api/optimization")

@optimizer_router.get("/presets")
async def get_rule_presets(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get available optimizer rule presets."""
    return {"presets": get_presets()}


@optimizer_router.post("/set-preset")
async def set_user_preset(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Set the user's preferred optimization preset."""
    body = await request.json()
    preset = body.get("preset", "balanced")
    if preset not in RULE_PRESETS:
        raise HTTPException(status_code=400, detail=f"Invalid preset: {preset}")

    await db.profiles.update_one(
        {"id": current_user.user_id},
        {"$set": {"optimizer_preset": preset}},
        upsert=True
    )
    return {"status": "success", "preset": preset}


@optimizer_router.post("/toggle-auto-recommend")
async def toggle_auto_recommend(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Toggle auto-recommend mode for the user."""
    body = await request.json()
    enabled = body.get("enabled", False)

    await db.profiles.update_one(
        {"id": current_user.user_id},
        {"$set": {"auto_recommend_enabled": enabled}},
        upsert=True
    )
    return {"status": "success", "auto_recommend_enabled": enabled}


@optimizer_router.get("/settings")
async def get_optimizer_settings(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get user's optimizer settings (preset + auto-recommend)."""
    profile = await db.profiles.find_one(
        {"id": current_user.user_id},
        {"_id": 0, "optimizer_preset": 1, "auto_recommend_enabled": 1}
    )
    return {
        "preset": (profile or {}).get("optimizer_preset", "balanced"),
        "auto_recommend_enabled": (profile or {}).get("auto_recommend_enabled", False),
    }


@optimizer_router.post("/recommend/{test_id}")
async def get_recommendations(
    test_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get budget optimization recommendations for an ad test."""
    test = await db.ad_tests.find_one({"id": test_id, "user_id": current_user.user_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="Ad test not found")

    body = {}
    try:
        body = await request.json()
    except Exception:
        pass

    # Get user's preset
    profile = await db.profiles.find_one(
        {"id": current_user.user_id},
        {"_id": 0, "optimizer_preset": 1}
    )
    preset = body.get("preset", (profile or {}).get("optimizer_preset", "balanced"))
    target_cpa = body.get("target_cpa")
    result = recommend_for_test(test, target_cpa, preset=preset)

    # Log optimization events and generate alerts for actionable items
    from services.notification_service import create_notification_service, NotificationType
    notification_service = create_notification_service(db)

    for rec in result["recommendations"]:
        event_doc = {
            "id": str(uuid.uuid4()),
            "test_id": test_id,
            "variation_id": rec["variation_id"],
            "user_id": current_user.user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_snapshot": rec["metrics"],
            "recommendation_action": rec["action"],
            "recommended_budget": rec["recommended_budget"],
            "confidence": rec["confidence"],
            "reason_codes": rec["reasoning"],
            "preset": preset,
            "user_applied_action": None,
            "outcome_after_24h": None,
            "outcome_after_72h": None,
        }
        await db.optimization_events.insert_one(event_doc)

        # Generate optimizer alert for pause/kill/scale actions
        if rec["action"] in ("pause", "kill", "increase_budget") and rec["confidence"] >= 0.5:
            alert_type_map = {
                "pause": "should_pause",
                "kill": "should_pause",
                "increase_budget": "should_scale",
            }
            alert_doc = {
                "id": str(uuid.uuid4()),
                "user_id": current_user.user_id,
                "test_id": test_id,
                "variation_id": rec["variation_id"],
                "alert_type": alert_type_map[rec["action"]],
                "action": rec["action"],
                "label": rec["label"],
                "confidence": rec["confidence"],
                "reasoning": rec["reasoning"],
                "metrics": rec["metrics"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "read": False,
            }
            await db.optimizer_alerts.insert_one(alert_doc)

            # Also create in-app notification
            try:
                fake_product = {
                    "id": test_id,
                    "product_name": f"{test.get('product_name', 'Ad')} — {rec['label']}",
                    "launch_score": int(rec["confidence"] * 100),
                }
                await notification_service.create_notification(
                    user_id=current_user.user_id,
                    notification_type=NotificationType.SCORE_MILESTONE,
                    product=fake_product,
                )
            except Exception:
                pass

    return result


@optimizer_router.get("/timeline/{test_id}")
async def get_optimization_timeline(
    test_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get optimization event timeline for a test."""
    cursor = db.optimization_events.find(
        {"test_id": test_id, "user_id": current_user.user_id},
        {"_id": 0},
    ).sort("timestamp", -1)
    events = await cursor.to_list(100)
    return {"events": events, "total": len(events)}


@optimizer_router.get("/dashboard-summary")
async def get_optimizer_dashboard_summary(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get optimization summary across all active ad tests."""
    profile = await db.profiles.find_one(
        {"id": current_user.user_id},
        {"_id": 0, "optimizer_preset": 1}
    )
    preset = (profile or {}).get("optimizer_preset", "balanced")
    cursor = db.ad_tests.find(
        {"user_id": current_user.user_id, "status": "active"},
        {"_id": 0},
    )
    active_tests = await cursor.to_list(50)
    return generate_dashboard_summary(active_tests, preset=preset)


@optimizer_router.get("/alerts")
async def get_optimizer_alerts(
    limit: int = 20,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get optimizer alerts for the current user."""
    cursor = db.optimizer_alerts.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    alerts = await cursor.to_list(limit)
    unread = sum(1 for a in alerts if not a.get("read"))
    return {"alerts": alerts, "total": len(alerts), "unread": unread}


@optimizer_router.post("/alerts/mark-read")
async def mark_optimizer_alerts_read(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Mark all optimizer alerts as read."""
    result = await db.optimizer_alerts.update_many(
        {"user_id": current_user.user_id, "read": False},
        {"$set": {"read": True}}
    )
    return {"marked_read": result.modified_count}




routers = [optimizer_router]
