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

from services.intelligence import ProductValidationEngine, TrendAnalyzer, SuccessPredictionModel

product_validator = ProductValidationEngine(db)
trend_analyzer = TrendAnalyzer(db)
success_predictor = SuccessPredictionModel(db)

dashboard_router = APIRouter(prefix="/api/dashboard")

@dashboard_router.get("/daily-winners")
async def get_daily_winning_products(limit: int = 10):
    """
    Get today's top winning products - answers "What should I launch today?"
    
    Ranked primarily by launch_score (the primary decision metric).
    """
    # Get products with launch_score, sorted by launch_score
    products = await db.products.find(
        {"launch_score": {"$gte": 40}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(limit * 3).to_list(limit * 3)
    
    if not products:
        # Fallback to products with win_score
        products = await db.products.find(
            {"win_score": {"$gte": 50}},
            {"_id": 0}
        ).sort("win_score", -1).limit(limit * 2).to_list(limit * 2)
    
    if not products:
        # Final fallback to all products sorted by trend_score
        products = await db.products.find(
            {},
            {"_id": 0}
        ).sort("trend_score", -1).limit(limit * 2).to_list(limit * 2)
    
    # Build response with launch_score as primary metric
    ranked_products = []
    for product in products:
        # Get validation and prediction for additional context
        validation = product_validator.validate_product(product)
        prediction = success_predictor.predict_success(product)
        trend = trend_analyzer.analyze_trend(product)
        
        # Use launch_score as the primary ranking metric
        launch_score = product.get("launch_score", 0)
        launch_label = product.get("launch_score_label", "risky")
        launch_reasoning = product.get("launch_score_reasoning", "")
        
        # Only include products with reasonable scores
        if launch_score >= 40 or validation.overall_score >= 40:
            ranked_products.append({
                "product_id": product.get("id"),
                "product_name": product.get("product_name"),
                "category": product.get("category"),
                "image_url": product.get("image_url"),
                # Launch Score - PRIMARY METRIC
                "launch_score": launch_score,
                "launch_score_label": launch_label,
                "launch_score_reasoning": launch_reasoning,
                # Supporting metrics
                "trend_stage": product.get("trend_stage"),
                "trend_velocity": trend.velocity_percent,
                "estimated_margin": f"£{(product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)):.2f}",
                "margin_percent": round(((product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)) / product.get('estimated_retail_price', 1)) * 100) if product.get('estimated_retail_price', 0) > 0 else 0,
                "competition_level": product.get("competition_level"),
                "success_probability": round(prediction.success_probability, 1),
                "validation_result": validation.recommendation.value,
                "validation_label": validation.recommendation_label,
                "confidence_score": validation.confidence_score,
                "ranking_score": launch_score,  # Use launch_score for ranking
                "strengths": validation.strengths[:2],
                "is_early_opportunity": trend.is_early_opportunity,
                "is_simulated": product.get("data_source") == "simulated",
            })
    
    # Sort by launch_score (primary decision metric)
    ranked_products.sort(key=lambda x: x["launch_score"], reverse=True)
    
    return {
        "daily_winners": ranked_products[:limit],
        "count": len(ranked_products[:limit]),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# =====================================================
# LIVE OPPORTUNITY FEED ENDPOINTS
# =====================================================

@dashboard_router.get("/opportunity-feed")
async def get_opportunity_feed(
    limit: int = 20,
    hours: int = 24,
    event_types: Optional[str] = None
):
    """
    Get live opportunity feed with recent product signal changes.
    
    Returns events sorted by priority and recency:
    1. entered_strong_launch (highest priority)
    2. new_high_score
    3. trend_spike
    4. competition_increase
    5. approaching_saturation
    
    Args:
        limit: Maximum events to return (default 20)
        hours: Only get events from last N hours (default 24)
        event_types: Comma-separated list of event types to filter
    """
    from services.opportunity_feed_service import create_feed_service
    
    feed_service = create_feed_service(db)
    
    # Parse event types if provided
    types_list = None
    if event_types:
        types_list = [t.strip() for t in event_types.split(",")]
    
    events = await feed_service.get_feed(
        limit=limit,
        event_types=types_list,
        hours=hours
    )
    
    return {
        "events": events,
        "count": len(events),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@dashboard_router.get("/opportunity-feed/stats")
async def get_feed_stats():
    """Get statistics about the opportunity feed"""
    from services.opportunity_feed_service import create_feed_service
    
    feed_service = create_feed_service(db)
    stats = await feed_service.get_feed_stats()
    
    return stats


@dashboard_router.post("/opportunity-feed/generate-sample")
async def generate_sample_feed_events(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Generate sample feed events from current products (admin only).
    Useful for testing and demo purposes.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.opportunity_feed_service import create_feed_service, FeedEventType
    
    feed_service = create_feed_service(db)
    
    # Get products with high launch scores
    high_score_products = await db.products.find(
        {"launch_score": {"$gte": 75}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(10).to_list(10)
    
    events_created = []
    
    for product in high_score_products[:5]:
        launch_score = product.get("launch_score", 0)
        
        # Determine event type based on score
        if launch_score >= 80:
            event = await feed_service.create_event(
                FeedEventType.ENTERED_STRONG_LAUNCH,
                product,
                reason=f"Launch Score of {launch_score} qualifies for Strong Launch category",
                change_data={"launch_score": launch_score},
                confidence=0.9
            )
        else:
            event = await feed_service.create_event(
                FeedEventType.NEW_HIGH_SCORE,
                product,
                reason=f"High potential product detected with score {launch_score}",
                change_data={"launch_score": launch_score},
                confidence=0.85
            )
        
        if event:
            events_created.append(event)
    
    # Add a trend spike event
    trending_products = await db.products.find(
        {"trend_score": {"$gte": 70}},
        {"_id": 0}
    ).sort("trend_score", -1).limit(3).to_list(3)
    
    for product in trending_products[:2]:
        event = await feed_service.create_event(
            FeedEventType.TREND_SPIKE,
            product,
            reason=f"Strong trend momentum detected - score increased to {product.get('trend_score', 0)}",
            change_data={"trend_score": product.get("trend_score", 0), "change_percent": 25},
            confidence=0.8
        )
        if event:
            events_created.append(event)
    
    return {
        "success": True,
        "events_created": len(events_created),
        "events": events_created
    }


@dashboard_router.post("/opportunity-feed/mark-read")
async def mark_feed_events_read(
    event_ids: List[str],
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Mark specific feed events as read"""
    from services.opportunity_feed_service import create_feed_service
    
    feed_service = create_feed_service(db)
    await feed_service.mark_as_read(event_ids, current_user.user_id)
    
    return {"success": True, "marked_count": len(event_ids)}


@dashboard_router.get("/watchlist")
async def get_user_watchlist(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get user's product watchlist with updated metrics and change indicators"""
    user_id = current_user.user_id
    
    # Get watchlist items
    watchlist = await db.watchlist.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("added_at", -1).to_list(100)
    
    # Enrich with current product data and changes
    enriched_items = []
    for item in watchlist:
        product = await db.products.find_one({"id": item["product_id"]}, {"_id": 0})
        if not product:
            continue
        
        # Get current analysis
        validation = product_validator.validate_product(product)
        prediction = success_predictor.predict_success(product)
        trend = trend_analyzer.analyze_trend(product)
        
        # Calculate changes from initial snapshot
        initial_success = item.get("initial_success_probability", prediction.success_probability)
        initial_velocity = item.get("initial_trend_velocity", trend.velocity_percent)
        initial_competition = item.get("initial_competition_level", product.get("competition_level"))
        initial_margin = item.get("initial_margin_score", product.get("margin_score", 50))
        
        success_change = prediction.success_probability - initial_success
        velocity_change = trend.velocity_percent - initial_velocity
        margin_change = product.get("margin_score", 50) - initial_margin
        
        # Determine competition change
        competition_levels = {"low": 1, "medium": 2, "high": 3}
        current_comp_num = competition_levels.get(product.get("competition_level"), 2)
        initial_comp_num = competition_levels.get(initial_competition, 2)
        competition_change = current_comp_num - initial_comp_num  # Positive = worse
        
        enriched_items.append({
            "watchlist_id": item.get("id"),
            "product_id": product.get("id"),
            "product_name": product.get("product_name"),
            "category": product.get("category"),
            "image_url": product.get("image_url"),
            "added_at": item.get("added_at"),
            "notes": item.get("notes"),
            
            # Current metrics
            "trend_stage": product.get("trend_stage"),
            "trend_velocity": trend.velocity_percent,
            "success_probability": round(prediction.success_probability, 1),
            "competition_level": product.get("competition_level"),
            "margin_score": product.get("margin_score", 50),
            "validation_result": validation.recommendation.value,
            "validation_label": validation.recommendation_label,
            
            # Change indicators
            "changes": {
                "success_change": round(success_change, 1),
                "velocity_change": round(velocity_change, 1),
                "margin_change": margin_change,
                "competition_change": competition_change,  # Positive = got worse
            },
            
            # Signal directions
            "signals": {
                "trend": "improving" if velocity_change > 5 else ("declining" if velocity_change < -5 else "stable"),
                "success": "improving" if success_change > 3 else ("declining" if success_change < -3 else "stable"),
                "competition": "improving" if competition_change < 0 else ("worsening" if competition_change > 0 else "stable"),
                "margin": "improving" if margin_change > 3 else ("declining" if margin_change < -3 else "stable"),
            },
            
            "is_simulated": product.get("data_source") == "simulated",
        })
    
    return {
        "watchlist": enriched_items,
        "count": len(enriched_items),
    }


@dashboard_router.post("/watchlist")
async def add_to_watchlist(
    request: WatchlistItemCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Add a product to user's watchlist"""
    user_id = current_user.user_id
    
    # Check if already in watchlist
    existing = await db.watchlist.find_one({
        "user_id": user_id,
        "product_id": request.product_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Product already in watchlist")
    
    # Get product for initial snapshot
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get current metrics for snapshot
    prediction = success_predictor.predict_success(product)
    trend = trend_analyzer.analyze_trend(product)
    
    # Create watchlist item
    watchlist_item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "product_id": request.product_id,
        "added_at": datetime.now(timezone.utc).isoformat(),
        "notes": request.notes,
        "initial_success_probability": prediction.success_probability,
        "initial_trend_velocity": trend.velocity_percent,
        "initial_competition_level": product.get("competition_level"),
        "initial_margin_score": product.get("margin_score", 50),
    }
    
    await db.watchlist.insert_one(watchlist_item)
    
    return {
        "success": True,
        "watchlist_item": {k: v for k, v in watchlist_item.items() if k != "_id"},
        "message": f"Added {product.get('product_name')} to watchlist"
    }


@dashboard_router.delete("/watchlist/{product_id}")
async def remove_from_watchlist(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Remove a product from user's watchlist"""
    user_id = current_user.user_id
    
    result = await db.watchlist.delete_one({
        "user_id": user_id,
        "product_id": product_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not in watchlist")
    
    return {"success": True, "message": "Removed from watchlist"}


@dashboard_router.get("/watchlist/check/{product_id}")
async def check_watchlist_status(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Check if a product is in user's watchlist"""
    user_id = current_user.user_id
    
    item = await db.watchlist.find_one({
        "user_id": user_id,
        "product_id": product_id
    }, {"_id": 0})
    
    return {
        "in_watchlist": item is not None,
        "watchlist_item": item
    }


@dashboard_router.get("/alerts")
async def get_user_alerts(
    unread_only: bool = False,
    limit: int = 50,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get user's opportunity alerts"""
    user_id = current_user.user_id
    
    query = {"user_id": user_id}
    if unread_only:
        query["is_read"] = False
    
    alerts = await db.alerts.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Count unread
    unread_count = await db.alerts.count_documents({
        "user_id": user_id,
        "is_read": False
    })
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "unread_count": unread_count,
    }


@dashboard_router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Mark an alert as read"""
    user_id = current_user.user_id
    
    result = await db.alerts.update_one(
        {"id": alert_id, "user_id": user_id},
        {"$set": {"is_read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"success": True}


@dashboard_router.post("/alerts/read-all")
async def mark_all_alerts_read(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Mark all alerts as read"""
    user_id = current_user.user_id
    
    result = await db.alerts.update_many(
        {"user_id": user_id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    
    return {"success": True, "updated_count": result.modified_count}


@dashboard_router.get("/market-radar")
async def get_market_opportunity_radar(limit: int = 10):
    """
    Get market opportunity clusters - groups of related products showing trends.
    
    Identifies emerging opportunity clusters rather than individual products.
    """
    # Get all products (use trend_score as fallback if win_score is 0)
    products = await db.products.find(
        {},
        {"_id": 0}
    ).to_list(500)
    
    # Filter to products with some score
    products = [p for p in products if p.get("trend_score", 0) > 0 or p.get("win_score", 0) > 0]
    
    if not products:
        # Get any products if no scored ones
        products = await db.products.find({}, {"_id": 0}).limit(100).to_list(100)
    
    # Group by category and analyze
    category_clusters = {}
    
    for product in products:
        category = product.get("category", "Other")
        
        if category not in category_clusters:
            category_clusters[category] = {
                "products": [],
                "total_velocity": 0,
                "total_success": 0,
                "competition_levels": [],
            }
        
        trend = trend_analyzer.analyze_trend(product)
        prediction = success_predictor.predict_success(product)
        
        category_clusters[category]["products"].append(product)
        category_clusters[category]["total_velocity"] += trend.velocity_percent
        category_clusters[category]["total_success"] += prediction.success_probability
        category_clusters[category]["competition_levels"].append(product.get("competition_level", "medium"))
    
    # Calculate cluster metrics
    clusters = []
    for category, data in category_clusters.items():
        product_count = len(data["products"])
        if product_count < 2:
            continue  # Skip single-product clusters
        
        avg_velocity = data["total_velocity"] / product_count
        avg_success = data["total_success"] / product_count
        
        # Calculate dominant competition level
        comp_counts = {"low": 0, "medium": 0, "high": 0}
        for level in data["competition_levels"]:
            comp_counts[level] = comp_counts.get(level, 0) + 1
        dominant_competition = max(comp_counts, key=comp_counts.get)
        
        # Determine trend stage for cluster
        if avg_velocity > 50:
            cluster_trend = "exploding"
        elif avg_velocity > 20:
            cluster_trend = "rising"
        elif avg_velocity > 5:
            cluster_trend = "early_trend"
        elif avg_velocity >= -5:
            cluster_trend = "stable"
        else:
            cluster_trend = "declining"
        
        # Calculate cluster opportunity score
        cluster_score = (
            avg_success * 0.4 +
            (avg_velocity if avg_velocity > 0 else 0) * 0.3 +
            (100 if dominant_competition == "low" else 60 if dominant_competition == "medium" else 30) * 0.3
        )
        
        clusters.append({
            "cluster_name": category,
            "trend_stage": cluster_trend,
            "avg_success_probability": round(avg_success, 1),
            "avg_trend_velocity": round(avg_velocity, 1),
            "product_count": product_count,
            "competition_level": dominant_competition,
            "opportunity_score": round(cluster_score, 1),
            "top_products": [
                {
                    "id": p.get("id"),
                    "name": p.get("product_name"),
                    "success_probability": round(success_predictor.predict_success(p).success_probability, 1),
                }
                for p in sorted(data["products"], key=lambda x: x.get("win_score", 0), reverse=True)[:3]
            ],
        })
    
    # Sort by opportunity score
    clusters.sort(key=lambda x: x["opportunity_score"], reverse=True)
    
    return {
        "market_radar": clusters[:limit],
        "count": len(clusters[:limit]),
        "total_clusters": len(clusters),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@dashboard_router.get("/market-radar/{cluster_name}")
async def get_cluster_products(cluster_name: str, limit: int = 20):
    """Get all products in a market cluster/category"""
    products = await db.products.find(
        {"category": cluster_name},
        {"_id": 0}
    ).sort("win_score", -1).limit(limit).to_list(limit)
    
    enriched = []
    for product in products:
        validation = product_validator.validate_product(product)
        prediction = success_predictor.predict_success(product)
        
        enriched.append({
            "product_id": product.get("id"),
            "product_name": product.get("product_name"),
            "trend_stage": product.get("trend_stage"),
            "success_probability": round(prediction.success_probability, 1),
            "competition_level": product.get("competition_level"),
            "validation_result": validation.recommendation.value,
            "margin_score": product.get("margin_score", 50),
            "is_simulated": product.get("data_source") == "simulated",
        })
    
    return {
        "cluster_name": cluster_name,
        "products": enriched,
        "count": len(enriched),
    }


@dashboard_router.get("/summary")
async def get_dashboard_summary(
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """
    Get complete dashboard summary for the home view.
    Combines daily winners, watchlist preview, alerts, and market radar.
    """
    user_id = current_user.user_id if current_user else None
    
    # Get daily winners (top 5)
    daily_winners_response = await get_daily_winning_products(limit=5)
    
    # Get market radar (top 5 clusters)
    market_radar_response = await get_market_opportunity_radar(limit=5)
    
    # Get watchlist and alerts if authenticated
    watchlist_preview = []
    unread_alerts = 0
    
    if user_id:
        # Get watchlist preview
        watchlist_items = await db.watchlist.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("added_at", -1).limit(3).to_list(3)
        
        for item in watchlist_items:
            product = await db.products.find_one({"id": item["product_id"]}, {"_id": 0, "product_name": 1, "id": 1})
            if product:
                watchlist_preview.append({
                    "product_id": product.get("id"),
                    "product_name": product.get("product_name"),
                })
        
        # Count unread alerts
        unread_alerts = await db.alerts.count_documents({
            "user_id": user_id,
            "is_read": False
        })
    
    # Get platform stats
    total_products = await db.products.count_documents({})
    launch_opportunities = len([p for p in daily_winners_response.get("daily_winners", []) if p.get("validation_result") == "launch_opportunity"])
    
    return {
        "daily_winners": daily_winners_response.get("daily_winners", [])[:5],
        "market_radar": market_radar_response.get("market_radar", [])[:5],
        "watchlist_preview": watchlist_preview,
        "unread_alerts": unread_alerts,
        "stats": {
            "total_products": total_products,
            "launch_opportunities": launch_opportunities,
            "trending_clusters": market_radar_response.get("count", 0),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# =====================
# ROUTES - Market Intelligence Reports
# =====================

from services.reports import WeeklyWinningProductsReport, MonthlyMarketTrendsReport
from services.reports.report_generator import ReportType, ReportAccessLevel


def check_report_access(user_plan: str, required_level: str) -> bool:
    """Check if user's plan allows access to a report section"""
    plan_levels = {
        "free": 0,
        "pro": 1,
        "elite": 2
    }
    access_levels = {
        "public": -1,
        "free": 0,
        "pro": 1, 
        "elite": 2
    }
    
    user_level = plan_levels.get(user_plan, 0)
    required = access_levels.get(required_level, 0)
    
    return user_level >= required


def filter_report_by_access(report: dict, user_plan: str) -> dict:
    """Filter report sections based on user's subscription plan"""
    filtered_sections = []
    
    for section in report.get("sections", []):
        section_access = section.get("access_level", "free")
        if check_report_access(user_plan, section_access):
            filtered_sections.append(section)
        else:
            # Include section metadata but mark as locked
            filtered_sections.append({
                "title": section.get("title"),
                "description": section.get("description"),
                "access_level": section_access,
                "locked": True,
                "unlock_message": f"Upgrade to {section_access.title()} to access this section"
            })
    
    return {
        **report,
        "sections": filtered_sections
    }




@dashboard_router.get("/next-steps")
async def get_next_steps(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Product Decision Panel — personalised "What should I do next?" recommendations.
    Analyses saved products, stores, activity and returns prioritised actions.
    """
    user_id = current_user.user_id
    profile = await db.profiles.find_one({"id": user_id}, {"_id": 0})
    plan = profile.get("plan", "free") if profile else "free"

    saved_count = await db.saved_products.count_documents({"user_id": user_id})
    store_count = await db.stores.count_documents({"user_id": user_id})
    watchlist_count = await db.watchlist.count_documents({"user_id": user_id})
    unread_alerts = await db.alerts.count_documents({"user_id": user_id, "is_read": False})

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    usage_doc = await db.daily_usage.find_one(
        {"user_id": user_id, "date": today}, {"_id": 0}
    )
    insights_used = usage_doc.get("insights_used", 0) if usage_doc else 0

    # Top product candidate
    top_product = await db.products.find_one(
        {"launch_score": {"$gte": 70}},
        {"_id": 0, "id": 1, "product_name": 1, "launch_score": 1, "category": 1, "image_url": 1}
    )

    steps = []
    # Priority 1: Unread alerts
    if unread_alerts > 0:
        steps.append({
            "id": "check-alerts",
            "priority": 1,
            "title": f"Review {unread_alerts} unread alert{'s' if unread_alerts != 1 else ''}",
            "description": "New trend alerts may contain time-sensitive opportunities.",
            "action": {"label": "View Alerts", "href": "/dashboard?tab=alerts"},
            "icon": "bell",
        })

    # Priority 2: No saved products yet
    if saved_count == 0:
        steps.append({
            "id": "save-first-product",
            "priority": 2,
            "title": "Save your first product",
            "description": "Browse trending products and save ones you want to research further.",
            "action": {"label": "Discover Products", "href": "/discover"},
            "icon": "bookmark",
        })

    # Priority 3: Has saved products but no store
    if saved_count > 0 and store_count == 0:
        steps.append({
            "id": "create-store",
            "priority": 3,
            "title": "Create your first store",
            "description": f"You have {saved_count} saved product{'s' if saved_count != 1 else ''}. Build a store around your best pick.",
            "action": {"label": "Build Store", "href": "/discover"},
            "icon": "store",
        })

    # Priority 4: High-scoring product to launch
    if top_product:
        steps.append({
            "id": "launch-top-product",
            "priority": 4,
            "title": f"Launch \"{top_product.get('product_name', 'Top Product')}\"",
            "description": f"This product scored {top_product.get('launch_score', 0)}/100 — a strong launch candidate.",
            "action": {"label": "Start Launch Wizard", "href": f"/launch/{top_product['id']}"},
            "icon": "rocket",
            "product": {
                "id": top_product.get("id"),
                "name": top_product.get("product_name"),
                "score": top_product.get("launch_score", 0),
                "category": top_product.get("category"),
                "image_url": top_product.get("image_url"),
            },
        })

    # Priority 5: Empty watchlist
    if watchlist_count == 0:
        steps.append({
            "id": "start-watchlist",
            "priority": 5,
            "title": "Start your watchlist",
            "description": "Add products to your watchlist to track price and trend changes over time.",
            "action": {"label": "Browse Products", "href": "/discover"},
            "icon": "eye",
        })

    # Priority 6: Upgrade nudge for free users
    if plan == "free" and insights_used >= 2:
        steps.append({
            "id": "upgrade-plan",
            "priority": 6,
            "title": "Unlock unlimited insights",
            "description": "You've used your free daily insights. Upgrade to keep discovering.",
            "action": {"label": "See Plans", "href": "/pricing"},
            "icon": "zap",
        })

    # Priority 7: Explore ads (for pro/elite)
    if plan in ("pro", "elite") and store_count > 0:
        steps.append({
            "id": "generate-ads",
            "priority": 7,
            "title": "Generate ad creatives",
            "description": "Use the AI ad generator to create high-converting creatives for your store.",
            "action": {"label": "Ad Generator", "href": "/optimization"},
            "icon": "sparkles",
        })

    # Always: daily discovery nudge
    if not any(s["id"] == "save-first-product" for s in steps):
        steps.append({
            "id": "daily-discovery",
            "priority": 8,
            "title": "Explore today's trending products",
            "description": "New products are scored daily. See what's trending now.",
            "action": {"label": "Discover", "href": "/discover"},
            "icon": "trending-up",
        })

    steps.sort(key=lambda s: s["priority"])

    return {
        "steps": steps[:5],
        "stats": {
            "saved_products": saved_count,
            "stores": store_count,
            "watchlist": watchlist_count,
            "insights_used_today": insights_used,
        },
    }


routers = [dashboard_router]
