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

radar_router = APIRouter(prefix="/api/radar")

@radar_router.get("/live-events")
async def get_live_radar_events(
    current_user: AuthenticatedUser = Depends(get_current_user),
    limit: int = 20,
):
    """
    Live signal feed: trend spikes, new ads, supplier demand jumps,
    competition drops. Designed to auto-refresh every 30s on the frontend.
    """
    events = []

    # 1. Trend spikes — products with high trend_velocity
    spike_cursor = db.products.find(
        {"trend_velocity": {"$gt": 15}, "launch_score": {"$exists": True}},
        {"_id": 0},
    ).sort("trend_velocity", -1).limit(8)
    spikes = await spike_cursor.to_list(8)
    for p in spikes:
        events.append({
            "type": "trend_spike",
            "icon": "trending-up",
            "title": f"Trend spike: {p.get('product_name', '')[:50]}",
            "detail": f"+{p.get('trend_velocity', 0):.0f}% trend velocity",
            "product_id": p.get("id"),
            "product_name": p.get("product_name", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "trend_stage": p.get("trend_stage", "Stable"),
            "timestamp": p.get("updated_at") or p.get("last_updated") or datetime.now(timezone.utc).isoformat(),
        })

    # 2. New ad activity — products with ad signals
    ad_cursor = db.products.find(
        {"ad_count": {"$gt": 5}, "launch_score": {"$exists": True}},
        {"_id": 0},
    ).sort("ad_count", -1).limit(6)
    ads = await ad_cursor.to_list(6)
    for p in ads:
        events.append({
            "type": "new_ads",
            "icon": "megaphone",
            "title": f"Ad activity: {p.get('product_name', '')[:50]}",
            "detail": f"{p.get('ad_count', 0)} ads detected across platforms",
            "product_id": p.get("id"),
            "product_name": p.get("product_name", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "trend_stage": p.get("trend_stage", "Stable"),
            "timestamp": p.get("updated_at") or p.get("last_updated") or datetime.now(timezone.utc).isoformat(),
        })

    # 3. Supplier demand jumps — high order velocity
    demand_cursor = db.products.find(
        {"supplier_order_velocity": {"$gt": 20}, "launch_score": {"$exists": True}},
        {"_id": 0},
    ).sort("supplier_order_velocity", -1).limit(6)
    demand = await demand_cursor.to_list(6)
    for p in demand:
        events.append({
            "type": "supplier_demand",
            "icon": "truck",
            "title": f"Supplier demand: {p.get('product_name', '')[:50]}",
            "detail": f"{p.get('supplier_order_velocity', 0)} orders/week velocity",
            "product_id": p.get("id"),
            "product_name": p.get("product_name", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "trend_stage": p.get("trend_stage", "Stable"),
            "timestamp": p.get("updated_at") or p.get("last_updated") or datetime.now(timezone.utc).isoformat(),
        })

    # 4. Competition drops — low competition products
    comp_cursor = db.products.find(
        {"competition_level": "low", "launch_score": {"$gte": 30}},
        {"_id": 0},
    ).sort("launch_score", -1).limit(6)
    low_comp = await comp_cursor.to_list(6)
    for p in low_comp:
        events.append({
            "type": "competition_drop",
            "icon": "shield",
            "title": f"Low competition: {p.get('product_name', '')[:50]}",
            "detail": f"Competition: low | Launch score: {p.get('launch_score', 0)}",
            "product_id": p.get("id"),
            "product_name": p.get("product_name", ""),
            "image_url": p.get("image_url", ""),
            "launch_score": p.get("launch_score", 0),
            "trend_stage": p.get("trend_stage", "Stable"),
            "timestamp": p.get("updated_at") or p.get("last_updated") or datetime.now(timezone.utc).isoformat(),
        })

    # Sort by timestamp desc and deduplicate by product_id
    seen = set()
    unique_events = []
    for e in sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True):
        pid = e.get("product_id")
        if pid not in seen:
            seen.add(pid)
            unique_events.append(e)

    return {
        "events": unique_events[:limit],
        "total": len(unique_events),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# Radar Watches — User-configurable alert conditions
# ═══════════════════════════════════════════════════════════════════


class CreateWatchRequest(BaseModel):
    name: str
    watch_type: str  # product_score, category_trend, competitor_new_products
    condition: Dict[str, Any]  # e.g. {"product_id": "...", "operator": "below", "value": 60}
    notify_email: bool = True
    notify_in_app: bool = True


@radar_router.post("/watches")
async def create_watch(
    req: CreateWatchRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Create a new radar watch (alert condition)."""
    watch = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.user_id,
        "name": req.name,
        "watch_type": req.watch_type,
        "condition": req.condition,
        "notify_email": req.notify_email,
        "notify_in_app": req.notify_in_app,
        "active": True,
        "triggered_count": 0,
        "last_triggered": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.radar_watches.insert_one(watch)
    watch.pop("_id", None)
    return {"watch": watch}


@radar_router.get("/watches")
async def get_watches(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get all radar watches for the current user."""
    watches = await db.radar_watches.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"watches": watches, "total": len(watches)}


@radar_router.put("/watches/{watch_id}")
async def update_watch(
    watch_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Toggle active status or update a watch."""
    body = await request.json()
    updates = {k: v for k, v in body.items() if k in ("name", "active", "condition", "notify_email", "notify_in_app")}
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    result = await db.radar_watches.update_one(
        {"id": watch_id, "user_id": current_user.user_id},
        {"$set": updates},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Watch not found")
    watch = await db.radar_watches.find_one({"id": watch_id}, {"_id": 0})
    return {"watch": watch}


@radar_router.delete("/watches/{watch_id}")
async def delete_watch(
    watch_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Delete a radar watch."""
    result = await db.radar_watches.delete_one(
        {"id": watch_id, "user_id": current_user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Watch not found")
    return {"deleted": True}


@radar_router.get("/alert-feed")
async def get_alert_feed(
    current_user: AuthenticatedUser = Depends(get_current_user),
    limit: int = 30,
):
    """
    Get recent alert feed — combines radar events + triggered watch alerts.
    """
    # Triggered watch alerts
    triggered = await db.watch_alerts.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("triggered_at", -1).limit(limit).to_list(limit)

    # Recent radar detections (from notification system)
    notifs = await db.notifications.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    return {
        "alerts": triggered,
        "notifications": notifs,
        "total_alerts": len(triggered),
        "total_notifications": len(notifs),
    }


routers = [radar_router]
