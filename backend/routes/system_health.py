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

from services.system_health import get_full_system_health
from services.data_integration import DataIntegrationService

health_router = APIRouter(prefix="/api/system-health")
integration_router = APIRouter(prefix="/api/data-integration")

@health_router.get("")
async def system_health_check(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get full system health report (admin only)."""
    profile = await db.profiles.find_one(
        {"id": current_user.user_id}, {"_id": 0, "is_admin": 1}
    )
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    scheduler_mgr = None
    try:
        from services.jobs.scheduler import SchedulerManager
        scheduler_mgr = SchedulerManager.get_instance().scheduler
    except Exception:
        pass

    return await get_full_system_health(db, scheduler_mgr)



# ── Data Integration endpoints (admin only) ──
from services.data_integration import DataIntegrationService

integration_router = APIRouter(prefix="/api/data-integration")


@integration_router.post("/enrich/{product_id}")
async def enrich_product(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Enrich a single product with all real data sources."""
    svc = DataIntegrationService(db)
    return await svc.enrich_product(product_id)


@integration_router.post("/run-ingestion")
async def run_full_ingestion(
    limit: int = 20,
    background_tasks: BackgroundTasks = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Run full data ingestion across all sources (admin only). Runs async in background."""
    profile = await db.profiles.find_one(
        {"id": current_user.user_id}, {"_id": 0, "is_admin": 1}
    )
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    # Start in background to avoid gateway timeout
    import asyncio

    async def _run():
        svc = DataIntegrationService(db)
        await svc.run_full_ingestion(limit=limit)

    asyncio.ensure_future(_run())
    return {
        "status": "started",
        "message": f"Data ingestion started for up to {limit} products. Check /api/data-integration/source-health for progress.",
    }


@integration_router.get("/source-health")
async def get_source_health(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get health status of all data sources from pull logs."""
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": {"source": "$source", "method": "$method"},
            "last_success": {"$first": {"$cond": [{"$eq": ["$success", True]}, "$timestamp", None]}},
            "last_error": {"$first": {"$cond": [{"$eq": ["$success", False]}, "$error", None]}},
            "total": {"$sum": 1},
            "successes": {"$sum": {"$cond": ["$success", 1, 0]}},
            "avg_latency": {"$avg": "$latency_ms"},
        }},
    ]
    results = await db.source_pull_log.aggregate(pipeline).to_list(100)

    # Also get latest ingestion log
    latest_ingestion = await db.ingestion_log.find_one(
        {}, {"_id": 0}, sort=[("timestamp", -1)]
    )

    return {
        "sources": [
            {
                "source": r["_id"]["source"],
                "method": r["_id"]["method"],
                "success_rate": round(r["successes"] / max(r["total"], 1) * 100),
                "total_pulls": r["total"],
                "last_success": r["last_success"],
                "last_error": r["last_error"],
                "avg_latency_ms": round(r["avg_latency"] or 0, 1),
            }
            for r in results
        ],
        "latest_ingestion": latest_ingestion,
    }


@integration_router.get("/integration-health")
async def get_integration_health(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get health status of all official API integrations."""
    profile = await db.profiles.find_one(
        {"id": current_user.user_id}, {"_id": 0, "is_admin": 1}
    )
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    svc = DataIntegrationService(db)
    return await svc.get_integration_health()


@integration_router.get("/ingestion-status")
async def get_ingestion_status(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get latest ingestion run status."""
    latest = await db.ingestion_log.find_one(
        {}, {"_id": 0}, sort=[("timestamp", -1)]
    )
    # Count enriched products
    enriched_count = await db.products.count_documents({"data_confidence": {"$exists": True}})
    total_count = await db.products.count_documents({})

    confidence_breakdown = {}
    for conf in ["live", "estimated", "fallback"]:
        confidence_breakdown[conf] = await db.products.count_documents({"data_confidence": conf})

    return {
        "latest_ingestion": latest,
        "enriched_count": enriched_count,
        "total_products": total_count,
        "confidence_breakdown": confidence_breakdown,
    }



routers = [health_router, integration_router]
