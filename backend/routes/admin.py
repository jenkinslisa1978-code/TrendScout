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

image_review_router = APIRouter(prefix="/api/admin/image-review")
analytics_router = APIRouter(prefix="/api/analytics")

@image_review_router.get("/metrics")
async def image_review_metrics(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Get image QA metrics."""
    await require_admin(current_user)

    pipeline = [
        {"$group": {"_id": "$image_status", "count": {"$sum": 1}}},
    ]
    status_counts = {doc["_id"]: doc["count"] async for doc in db.products.aggregate(pipeline)}
    pinned = await db.products.count_documents({"image_pinned": True})
    total = await db.products.count_documents({})

    return {
        "total_products": total,
        "needs_review": status_counts.get("needs_review", 0),
        "pending": status_counts.get("pending", 0),
        "approved": status_counts.get("approved", 0),
        "rejected": status_counts.get("rejected", 0),
        "placeholder": status_counts.get("placeholder", 0),
        "pinned": pinned,
    }


@image_review_router.get("/products")
async def list_review_products(
    status: str = None,
    confidence_max: float = None,
    page: int = 1,
    limit: int = 20,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """List products for image review with filters."""
    await require_admin(current_user)

    query = {}
    if status:
        query["image_status"] = status
    if confidence_max is not None:
        query["image_confidence"] = {"$lte": confidence_max}

    skip = (page - 1) * limit
    total = await db.products.count_documents(query)

    products = await db.products.find(
        query,
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "image_url": 1,
         "image_status": 1, "image_confidence": 1, "image_pinned": 1,
         "image_mismatch_reason": 1, "image_detected_object": 1,
         "image_validated_at": 1, "image_review_note": 1, "image_candidates": 1,
         "launch_score": 1}
    ).sort("image_confidence", 1).skip(skip).limit(limit).to_list(limit)

    return {"products": products, "total": total, "page": page, "limit": limit}


@image_review_router.get("/products/{product_id}")
async def get_review_product(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get detailed image review data for a product."""
    await require_admin(current_user)

    product = await db.products.find_one(
        {"id": product_id},
        {"_id": 0}
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@image_review_router.put("/products/{product_id}/approve")
async def approve_image(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Approve the current image for a product."""
    await require_admin(current_user)

    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {
            "image_status": "approved",
            "image_confidence": 1.0,
            "image_validated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Image approved", "status": "approved"}


@image_review_router.put("/products/{product_id}/reject")
async def reject_image(
    product_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Reject image and set placeholder."""
    await require_admin(current_user)

    body = await request.json()
    reason = body.get("reason", "Manual rejection")

    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {
            "image_status": "placeholder",
            "image_url": "",
            "image_confidence": 0.0,
            "image_mismatch_reason": reason,
            "image_validated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Image rejected, placeholder set", "status": "placeholder"}


@image_review_router.put("/products/{product_id}/url")
async def set_image_url(
    product_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Set a custom image URL for a product."""
    await require_admin(current_user)

    body = await request.json()
    url = body.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="url required")

    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {
            "image_url": url,
            "image_status": "approved",
            "image_confidence": 1.0,
            "image_review_note": "Manual URL override",
            "image_validated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Image URL updated", "url": url}


@image_review_router.put("/products/{product_id}/pin")
async def pin_image(
    product_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Pin/unpin an image to prevent automatic updates."""
    await require_admin(current_user)

    body = await request.json()
    pinned = body.get("pinned", True)

    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {"image_pinned": pinned}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Image {'pinned' if pinned else 'unpinned'}", "pinned": pinned}


@image_review_router.put("/products/{product_id}/select-candidate")
async def select_candidate_image(
    product_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Select a candidate image from the candidates list."""
    await require_admin(current_user)

    body = await request.json()
    url = body.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="url required")

    result = await db.products.update_one(
        {"id": product_id},
        {"$set": {
            "image_url": url,
            "image_status": "approved",
            "image_confidence": 0.85,
            "image_review_note": "Admin selected from candidates",
            "image_validated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Candidate image selected", "url": url}


@image_review_router.post("/bulk")
async def bulk_image_action(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Perform bulk image review operations."""
    await require_admin(current_user)

    body = await request.json()
    action = body.get("action")
    product_ids = body.get("product_ids", [])

    if not action or not product_ids:
        raise HTTPException(status_code=400, detail="action and product_ids required")

    now = datetime.now(timezone.utc).isoformat()

    if action == "approve":
        result = await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": {"image_status": "approved", "image_confidence": 1.0, "image_validated_at": now}}
        )
    elif action == "reject":
        result = await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": {"image_status": "placeholder", "image_url": "", "image_confidence": 0.0, "image_validated_at": now}}
        )
    elif action == "mark_placeholder":
        result = await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": {"image_status": "placeholder", "image_url": "", "image_validated_at": now}}
        )
    elif action == "mark_needs_review":
        result = await db.products.update_many(
            {"id": {"$in": product_ids}},
            {"$set": {"image_status": "needs_review", "image_validated_at": now}}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")

    return {"message": f"Bulk {action} completed", "modified": result.modified_count}




# =====================
# ANALYTICS
# =====================

analytics_router = APIRouter(prefix="/api/analytics")


@analytics_router.post("/event")
async def track_event(request: Request):
    """Track an analytics event. No auth required for public page events."""
    body = await request.json()
    event_type = body.get("event")
    if not event_type:
        raise HTTPException(status_code=400, detail="event field required")

    # Extract user from token if present
    user_id = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            import jwt
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, os.environ.get('JWT_SECRET', ''), algorithms=["HS256"])
            user_id = payload.get("sub")
        except Exception:
            pass

    doc = {
        "event": event_type,
        "properties": body.get("properties", {}),
        "user_id": user_id,
        "session_id": body.get("session_id"),
        "page": body.get("page", ""),
        "referrer": body.get("referrer", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_agent": request.headers.get("User-Agent", "")[:200],
    }
    await db.analytics_events.insert_one(doc)
    return {"ok": True}


@analytics_router.post("/batch")
async def track_batch_events(request: Request):
    """Track multiple analytics events in a single request."""
    body = await request.json()
    events = body.get("events", [])
    if not events:
        raise HTTPException(status_code=400, detail="events array required")

    user_id = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            import jwt
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, os.environ.get('JWT_SECRET', ''), algorithms=["HS256"])
            user_id = payload.get("sub")
        except Exception:
            pass

    now = datetime.now(timezone.utc).isoformat()
    docs = []
    for evt in events[:50]:
        docs.append({
            "event": evt.get("event", "unknown"),
            "properties": evt.get("properties", {}),
            "user_id": user_id,
            "session_id": evt.get("session_id"),
            "page": evt.get("page", ""),
            "referrer": evt.get("referrer", ""),
            "timestamp": evt.get("timestamp", now),
            "user_agent": request.headers.get("User-Agent", "")[:200],
        })
    if docs:
        await db.analytics_events.insert_many(docs)
    return {"ok": True, "count": len(docs)}


@analytics_router.get("/dashboard")
async def get_analytics_dashboard(
    days: int = 7,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Admin-only analytics dashboard data."""
    profile = await db.profiles.find_one({"email": current_user.email})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    from_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    pipeline_events = [
        {"$match": {"timestamp": {"$gte": from_date}}},
        {"$group": {"_id": "$event", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    event_counts = {doc["_id"]: doc["count"] async for doc in db.analytics_events.aggregate(pipeline_events)}

    pipeline_daily = [
        {"$match": {"timestamp": {"$gte": from_date}}},
        {"$addFields": {"day": {"$substr": ["$timestamp", 0, 10]}}},
        {"$group": {"_id": {"day": "$day", "event": "$event"}, "count": {"$sum": 1}}},
        {"$sort": {"_id.day": 1}},
    ]
    daily_raw = await db.analytics_events.aggregate(pipeline_daily).to_list(500)
    daily = {}
    for d in daily_raw:
        day = d["_id"]["day"]
        if day not in daily:
            daily[day] = {}
        daily[day][d["_id"]["event"]] = d["count"]

    pipeline_pages = [
        {"$match": {"timestamp": {"$gte": from_date}, "event": "page_view"}},
        {"$group": {"_id": "$page", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
    top_pages = await db.analytics_events.aggregate(pipeline_pages).to_list(20)

    total_events = await db.analytics_events.count_documents({"timestamp": {"$gte": from_date}})
    unique_sessions = len(await db.analytics_events.distinct("session_id", {"timestamp": {"$gte": from_date}}))
    unique_users = len(await db.analytics_events.distinct("user_id", {"timestamp": {"$gte": from_date}, "user_id": {"$ne": None}}))

    return {
        "period_days": days,
        "total_events": total_events,
        "unique_sessions": unique_sessions,
        "unique_users": unique_users,
        "event_counts": event_counts,
        "daily_breakdown": daily,
        "top_pages": [{"page": p["_id"], "views": p["count"]} for p in top_pages],
    }


@analytics_router.get("/funnel")
async def get_conversion_funnel(
    days: int = 30,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Admin-only conversion funnel data."""
    profile = await db.profiles.find_one({"email": current_user.email})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    from_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    funnel_events = ["page_view", "signup_click", "signup_complete", "product_view", "upgrade_click", "checkout_start"]
    funnel = {}
    for evt in funnel_events:
        count = await db.analytics_events.count_documents({"event": evt, "timestamp": {"$gte": from_date}})
        funnel[evt] = count

    # Calculate conversion rates
    conversions = {}
    if funnel.get("page_view", 0) > 0:
        conversions["visit_to_signup_click"] = round(funnel.get("signup_click", 0) / funnel["page_view"] * 100, 1)
    if funnel.get("signup_click", 0) > 0:
        conversions["click_to_complete"] = round(funnel.get("signup_complete", 0) / funnel["signup_click"] * 100, 1)
    if funnel.get("signup_complete", 0) > 0:
        conversions["signup_to_product_view"] = round(funnel.get("product_view", 0) / funnel["signup_complete"] * 100, 1)
    if funnel.get("product_view", 0) > 0:
        conversions["view_to_upgrade_click"] = round(funnel.get("upgrade_click", 0) / funnel["product_view"] * 100, 1)

    return {
        "period_days": days,
        "funnel": funnel,
        "conversion_rates": conversions,
    }


# =====================
# GROWTH / REVENUE OVERVIEW
# =====================

@analytics_router.get("/growth")
async def get_growth_metrics(
    days: int = 30,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Admin-only growth & revenue metrics."""
    await require_admin(current_user)

    now = datetime.now(timezone.utc)
    from_date = (now - timedelta(days=days)).isoformat()
    prev_from = (now - timedelta(days=days * 2)).isoformat()

    # --- Revenue from subscriptions ---
    plan_prices = {"pro": 39, "elite": 79}
    active_subs = await db.subscriptions.find(
        {"status": "active"}, {"_id": 0, "plan_name": 1, "user_id": 1, "created_at": 1}
    ).to_list(500)
    mrr = sum(plan_prices.get(s.get("plan_name", "").lower(), 0) for s in active_subs)
    new_subs_period = [s for s in active_subs if s.get("created_at", "") >= from_date]
    new_revenue = sum(plan_prices.get(s.get("plan_name", "").lower(), 0) for s in new_subs_period)
    total_paid = len([s for s in active_subs if s.get("plan_name", "").lower() in plan_prices])

    # Previous period for comparison
    prev_subs = [s for s in active_subs if prev_from <= s.get("created_at", "") < from_date]
    prev_revenue = sum(plan_prices.get(s.get("plan_name", "").lower(), 0) for s in prev_subs)

    # --- Lead metrics ---
    total_leads = await db.leads.count_documents({})
    period_leads = await db.leads.count_documents({"created_at": {"$gte": from_date}})
    prev_leads = await db.leads.count_documents({"created_at": {"$gte": prev_from, "$lt": from_date}})

    # Lead sources breakdown
    source_pipeline = [
        {"$match": {"created_at": {"$gte": from_date}}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    lead_sources = {doc["_id"]: doc["count"] async for doc in db.leads.aggregate(source_pipeline)}

    # Top searched products from lead context
    search_pipeline = [
        {"$match": {"context": {"$exists": True, "$ne": ""}}},
        {"$project": {"term": {"$trim": {"input": {"$replaceAll": {"input": "$context", "find": "Searched: ", "replacement": ""}}}}}},
        {"$group": {"_id": {"$toLower": "$term"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    top_searches = [{"term": doc["_id"], "count": doc["count"]} async for doc in db.leads.aggregate(search_pipeline)]

    # --- Email drip metrics ---
    drip_pipeline = [
        {"$unwind": "$drip_emails_sent"},
        {"$group": {"_id": "$drip_emails_sent.type", "count": {"$sum": 1}}},
    ]
    drip_counts = {doc["_id"]: doc["count"] async for doc in db.leads.aggregate(drip_pipeline)}

    # --- Conversion funnel ---
    total_users = await db.auth_users.count_documents({})
    period_users = await db.auth_users.count_documents({"created_at": {"$gte": from_date}})
    trial_count = await db.trials.count_documents({})

    # Plan breakdown
    plan_pipeline = [
        {"$group": {"_id": "$plan", "count": {"$sum": 1}}},
    ]
    plan_dist = {doc["_id"] or "none": doc["count"] async for doc in db.profiles.aggregate(plan_pipeline)}

    return {
        "period_days": days,
        "revenue": {
            "mrr": mrr,
            "new_revenue_period": new_revenue,
            "prev_revenue_period": prev_revenue,
            "total_paid_subscribers": total_paid,
            "new_subscribers_period": len(new_subs_period),
        },
        "leads": {
            "total": total_leads,
            "period": period_leads,
            "prev_period": prev_leads,
            "sources": lead_sources,
            "top_searches": top_searches,
        },
        "email_drip": {
            "viability_result_sent": drip_counts.get("viability_result", 0),
            "trending_products_sent": drip_counts.get("trending_products", 0),
            "trial_prompt_sent": drip_counts.get("trial_prompt", 0),
        },
        "users": {
            "total": total_users,
            "period_signups": period_users,
            "trials": trial_count,
            "plan_distribution": plan_dist,
        },
    }



admin_tools_router = APIRouter(prefix="/api/admin")


@admin_tools_router.post("/reseed-products")
async def reseed_products(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Admin-only: Reseed the products database."""
    await require_admin(current_user)
    try:
        from seed_database import seed_database
        result = await seed_database()
        count = result.get("products_processed", 0) if isinstance(result, dict) else 0
        return {"success": True, "products_processed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


routers = [image_review_router, analytics_router, admin_tools_router]
