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

from services.data_integrity import DataIntegrityService, ConfidenceLevel, SignalOrigin, DataFreshness
from services.source_health import SourceHealthMonitor, SourceStatus

data_integrity_service = DataIntegrityService(db)
source_health_monitor = SourceHealthMonitor(db)

data_integrity_router = APIRouter(prefix="/api/data-integrity")

@data_integrity_router.get("/product/{product_id}")
async def get_product_data_integrity(product_id: str):
    """
    Get complete data integrity information for a product.
    Shows confidence scores, signal origins, and data freshness.
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    integrity_data = data_integrity_service.format_for_ui(product)
    
    return {
        "product_id": product_id,
        "product_name": product.get("product_name"),
        "data_integrity": integrity_data.get("data_integrity"),
        "warnings": integrity_data.get("warnings", []),
        "display_hints": integrity_data.get("display_hints", {}),
    }


@data_integrity_router.get("/products/confidence")
async def get_products_with_confidence(
    min_confidence: int = 0,
    max_confidence: int = 100,
    limit: int = 50
):
    """Get products filtered by confidence score"""
    cursor = db.products.find(
        {
            "confidence_score": {"$gte": min_confidence, "$lte": max_confidence}
        },
        {"_id": 0}
    ).sort("confidence_score", -1).limit(limit)
    
    products = await cursor.to_list(limit)
    
    # Add integrity metadata to each product
    products_with_integrity = []
    for product in products:
        integrity_data = data_integrity_service.format_for_ui(product)
        products_with_integrity.append({
            **product,
            "data_integrity": integrity_data.get("data_integrity"),
            "warnings": integrity_data.get("warnings", []),
        })
    
    # Calculate stats
    avg_confidence = sum(p.get("confidence_score", 0) for p in products) / len(products) if products else 0
    simulated_count = len([p for p in products if p.get("data_source") == "simulated"])
    
    return {
        "data": products_with_integrity,
        "stats": {
            "count": len(products),
            "avg_confidence": round(avg_confidence, 1),
            "simulated_count": simulated_count,
            "live_data_count": len(products) - simulated_count,
        }
    }


@data_integrity_router.get("/source-health")
async def get_source_health_status():
    """
    Get health status of all data sources.
    Shows which sources are live, simulated, or unavailable.
    """
    return await source_health_monitor.get_source_status_for_ui()


@data_integrity_router.get("/source-health/{source_name}")
async def get_single_source_health(source_name: str):
    """Get health status for a specific data source"""
    health = await source_health_monitor.get_source_health(source_name)
    return health.to_dict()


@data_integrity_router.get("/platform-health")
async def get_platform_health():
    """
    Get overall platform data health summary.
    Shows aggregate metrics across all data sources.
    """
    health = await source_health_monitor.get_platform_health()
    return health.to_dict()


@data_integrity_router.get("/data-freshness")
async def get_data_freshness_report():
    """Get data freshness report across all products"""
    # Count products by data freshness
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    
    # Get freshness stats
    fresh_count = await db.products.count_documents({
        "last_updated": {"$gte": (now - timedelta(hours=1)).isoformat()}
    })
    
    recent_count = await db.products.count_documents({
        "last_updated": {
            "$gte": (now - timedelta(hours=24)).isoformat(),
            "$lt": (now - timedelta(hours=1)).isoformat()
        }
    })
    
    stale_count = await db.products.count_documents({
        "$or": [
            {"last_updated": {"$lt": (now - timedelta(hours=24)).isoformat()}},
            {"last_updated": None}
        ]
    })
    
    total = fresh_count + recent_count + stale_count
    
    # Get oldest and newest data
    oldest = await db.products.find_one(
        {"last_updated": {"$ne": None}},
        {"_id": 0, "product_name": 1, "last_updated": 1},
        sort=[("last_updated", 1)]
    )
    newest = await db.products.find_one(
        {"last_updated": {"$ne": None}},
        {"_id": 0, "product_name": 1, "last_updated": 1},
        sort=[("last_updated", -1)]
    )
    
    return {
        "freshness_breakdown": {
            "fresh": {"count": fresh_count, "label": "< 1 hour old"},
            "recent": {"count": recent_count, "label": "1-24 hours old"},
            "stale": {"count": stale_count, "label": "> 24 hours old"},
        },
        "total_products": total,
        "freshness_score": round((fresh_count + recent_count * 0.5) / total * 100, 1) if total > 0 else 0,
        "oldest_data": oldest,
        "newest_data": newest,
        "last_checked": now.isoformat(),
    }


@data_integrity_router.get("/simulated-data-report")
async def get_simulated_data_report():
    """
    Get report on simulated vs real data in the platform.
    CRITICAL: This endpoint reveals which data is NOT real.
    """
    # Count by data source type
    pipeline = [
        {
            "$group": {
                "_id": "$data_source",
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$confidence_score"},
            }
        }
    ]
    
    source_stats = await db.products.aggregate(pipeline).to_list(100)
    
    simulated_count = 0
    live_count = 0
    unknown_count = 0
    
    source_breakdown = []
    for stat in source_stats:
        source_name = stat["_id"] or "unknown"
        is_simulated = source_name in ["simulated", "manual"]
        
        if is_simulated:
            simulated_count += stat["count"]
        elif source_name == "unknown":
            unknown_count += stat["count"]
        else:
            live_count += stat["count"]
        
        source_breakdown.append({
            "source": source_name,
            "count": stat["count"],
            "avg_confidence": round(stat["avg_confidence"] or 0, 1),
            "is_simulated": is_simulated,
            "is_live": not is_simulated and source_name != "unknown",
        })
    
    total = simulated_count + live_count + unknown_count
    
    return {
        "summary": {
            "total_products": total,
            "simulated_products": simulated_count,
            "live_data_products": live_count,
            "unknown_source_products": unknown_count,
            "simulated_percentage": round(simulated_count / total * 100, 1) if total > 0 else 0,
            "live_percentage": round(live_count / total * 100, 1) if total > 0 else 0,
        },
        "source_breakdown": sorted(source_breakdown, key=lambda x: x["count"], reverse=True),
        "warnings": [
            "IMPORTANT: Simulated data should not be presented as real insights.",
            f"{simulated_count} products are using simulated data.",
            "Configure API keys to enable live data ingestion.",
        ] if simulated_count > 0 else [],
    }


# =====================
# ROUTES - Intelligence (Product Validation, Predictions)
# =====================

from services.intelligence import (
    ProductValidationEngine,
    TrendAnalyzer,
    SuccessPredictionModel,
)

# Initialize intelligence services
product_validator = ProductValidationEngine(db)
trend_analyzer = TrendAnalyzer(db)
success_predictor = SuccessPredictionModel(db)




routers = [data_integrity_router]
