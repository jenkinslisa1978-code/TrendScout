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

workspace_router = APIRouter(prefix="/api/workspace")

@workspace_router.get("/products")
async def list_workspace_products(
    status: str = None,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """List user's saved workspace products."""
    query = {"user_id": current_user.user_id}
    if status:
        query["launch_status"] = status

    items = await db.workspace_products.find(
        query, {"_id": 0}
    ).sort("saved_at", -1).to_list(200)

    # Enrich with latest product data
    product_ids = [item["product_id"] for item in items]
    products = {}
    if product_ids:
        prods = await db.products.find(
            {"id": {"$in": product_ids}},
            {"_id": 0, "id": 1, "product_name": 1, "image_url": 1, "category": 1,
             "launch_score": 1, "estimated_margin": 1, "estimated_retail_price": 1,
             "tiktok_views": 1, "trend_stage": 1, "opportunity_rating": 1,
             "early_trend_label": 1}
        ).to_list(200)
        products = {p["id"]: p for p in prods}

    result = []
    for item in items:
        product = products.get(item["product_id"], {})
        result.append({**item, "product": product})

    return {"items": result, "count": len(result)}


@workspace_router.post("/products")
async def save_workspace_product(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Save a product to workspace."""
    body = await request.json()
    product_id = body.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id required")

    existing = await db.workspace_products.find_one(
        {"user_id": current_user.user_id, "product_id": product_id}
    )
    if existing:
        return {"message": "Already saved", "id": existing.get("id")}

    doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.user_id,
        "product_id": product_id,
        "note": body.get("note", ""),
        "launch_status": body.get("launch_status", "researching"),
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.workspace_products.insert_one(doc)
    doc.pop("_id", None)
    return doc


@workspace_router.delete("/products/{product_id}")
async def remove_workspace_product(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Remove a product from workspace."""
    result = await db.workspace_products.delete_one(
        {"user_id": current_user.user_id, "product_id": product_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in workspace")
    return {"message": "Removed"}


@workspace_router.put("/products/{product_id}/note")
async def update_workspace_note(
    product_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update note for a workspace product."""
    body = await request.json()
    note = body.get("note", "")
    result = await db.workspace_products.update_one(
        {"user_id": current_user.user_id, "product_id": product_id},
        {"$set": {"note": note, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in workspace")
    return {"message": "Note updated"}


@workspace_router.put("/products/{product_id}/status")
async def update_workspace_status(
    product_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update launch status for a workspace product."""
    body = await request.json()
    status = body.get("launch_status", "researching")
    valid_statuses = ["researching", "testing", "launched", "dropped"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(valid_statuses)}")

    result = await db.workspace_products.update_one(
        {"user_id": current_user.user_id, "product_id": product_id},
        {"$set": {"launch_status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in workspace")
    return {"message": "Status updated", "launch_status": status}


@workspace_router.get("/products/{product_id}/check")
async def check_workspace_product(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Check if a product is saved in workspace."""
    item = await db.workspace_products.find_one(
        {"user_id": current_user.user_id, "product_id": product_id},
        {"_id": 0, "id": 1, "launch_status": 1, "note": 1}
    )
    return {"saved": item is not None, "item": item}




# =====================
# BLOG SYSTEM
# =====================

blog_router = APIRouter(prefix="/api/blog")




routers = [workspace_router]
