from fastapi import APIRouter, HTTPException, Request, Depends, Header, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import uuid
import json
import logging
import re
import aiohttp

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

from services.ad_creative_service import generate_ad_creatives
from services.ad_pipeline import generate_ad_creatives_pipeline
from services.ad_discovery_service import AdDiscoveryService
from services.ad_winning_engine import analyze_ad_patterns, generate_ad_blueprint, compute_ad_performance
from services.ad_test_service import generate_ad_variations, generate_test_plan, simulate_launch

ad_creative_router = APIRouter(prefix="/api/ad-creatives")
ad_discovery_router = APIRouter(prefix="/api/ad-discovery")
outcomes_router = APIRouter(prefix="/api/outcomes")
ad_test_router = APIRouter(prefix="/api/ad-tests")
ad_engine_router = APIRouter(prefix="/api/ad-engine")

@ad_creative_router.post("/generate/{product_id}")
async def generate_ad_creatives_endpoint(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Generate AI-powered ad creatives for a product."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    from services.ad_creative_service import generate_ad_creatives
    result = await generate_ad_creatives(product)
    
    # Save to database for future retrieval
    if result.get('success'):
        result.pop('_id', None)
        await db.ad_creatives.update_one(
            {"product_id": product_id},
            {"$set": result},
            upsert=True,
        )
    
    return result


@ad_creative_router.get("/{product_id}")
async def get_ad_creatives(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get previously generated ad creatives for a product."""
    creatives = await db.ad_creatives.find_one(
        {"product_id": product_id}, {"_id": 0}
    )
    if not creatives:
        return {"product_id": product_id, "creatives": None, "message": "No creatives generated yet. Use POST to generate."}
    return creatives


@ad_creative_router.post("/generate-pipeline/{product_id}")
async def generate_pipeline_endpoint(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Generate ad creatives using the multi-step pipeline.
    Higher quality: each component (angles, headlines, scripts, etc.) is generated
    in a focused step for better results.
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = await generate_ad_creatives_pipeline(product)

    if result.get("success"):
        result.pop("_id", None)
        await db.ad_creatives.update_one(
            {"product_id": product_id},
            {"$set": result},
            upsert=True,
        )

    return result


# =====================
# AD DISCOVERY ROUTES
# =====================

@ad_discovery_router.post("/discover/{product_id}")
async def discover_ads_for_product(
    product_id: str,
    force_refresh: bool = False,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Discover active ads across TikTok, Meta, and Google Shopping for a product."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    from services.ad_discovery_service import AdDiscoveryService
    service = AdDiscoveryService(db)
    result = await service.discover_ads(
        product_id=product_id,
        product_name=product.get("product_name", ""),
        category=product.get("category", ""),
        force_refresh=force_refresh,
    )
    return result


@ad_discovery_router.get("/{product_id}")
async def get_discovered_ads(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get cached ad discovery results for a product."""
    from services.ad_discovery_service import AdDiscoveryService
    service = AdDiscoveryService(db)
    result = await service.get_ads_for_product(product_id)
    if not result:
        return {
            "product_id": product_id,
            "total_ads": 0,
            "platforms": {},
            "summary": None,
            "message": "No ads discovered yet. Use POST /discover to start discovery.",
        }
    return result


@ad_discovery_router.get("/{product_id}/{platform}")
async def get_platform_ads(
    product_id: str,
    platform: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get ads for a specific platform (tiktok, meta, google_shopping)."""
    valid_platforms = ["tiktok", "meta", "google_shopping"]
    if platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )

    from services.ad_discovery_service import AdDiscoveryService
    service = AdDiscoveryService(db)
    ads = await service.get_platform_ads(product_id, platform)
    return {"product_id": product_id, "platform": platform, "ads": ads, "count": len(ads)}


# ═══════════════════════════════════════════════════════════════════
# Product Outcome Learning System
# ═══════════════════════════════════════════════════════════════════
outcomes_router = APIRouter(prefix="/api/outcomes")


@outcomes_router.post("/track")
async def track_product_outcome(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Record a product launch outcome for tracking."""
    body = await request.json()
    product_id = body.get("product_id")
    store_id = body.get("store_id")

    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")

    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if already tracking this product for this user
    existing = await db.product_outcomes.find_one(
        {"product_id": product_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if existing:
        return {"outcome": existing, "message": "Already tracking this product"}

    outcome_doc = {
        "id": str(uuid.uuid4()),
        "product_id": product_id,
        "user_id": current_user.user_id,
        "store_id": store_id,
        "product_name": product.get("product_name", ""),
        "category": product.get("category", ""),
        "image_url": product.get("image_url", ""),
        "launch_score_at_launch": product.get("launch_score", 0),
        "success_probability_at_launch": product.get("success_probability", 0),
        "trend_stage_at_launch": product.get("trend_stage", "Stable"),
        "launched_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "outcome_status": "pending",
        "metrics": {
            "revenue": 0,
            "orders": 0,
            "ad_spend": 0,
            "roi": 0,
            "days_active": 0,
        },
        "auto_label_reason": None,
        "notes": body.get("notes", ""),
    }

    await db.product_outcomes.insert_one(outcome_doc)
    outcome_doc.pop("_id", None)
    return {"outcome": outcome_doc, "message": "Product outcome tracking started"}


@outcomes_router.get("/my")
async def get_my_outcomes(
    current_user: AuthenticatedUser = Depends(get_current_user),
    status: Optional[str] = None,
):
    """Get all tracked product outcomes for the current user."""
    query = {"user_id": current_user.user_id}
    if status and status in ("pending", "success", "moderate", "failed"):
        query["outcome_status"] = status

    cursor = db.product_outcomes.find(query, {"_id": 0}).sort("launched_at", -1)
    outcomes = await cursor.to_list(100)

    # Compute summary stats
    total = len(outcomes)
    success_count = sum(1 for o in outcomes if o.get("outcome_status") == "success")
    moderate_count = sum(1 for o in outcomes if o.get("outcome_status") == "moderate")
    failed_count = sum(1 for o in outcomes if o.get("outcome_status") == "failed")
    pending_count = sum(1 for o in outcomes if o.get("outcome_status") == "pending")
    total_revenue = sum(o.get("metrics", {}).get("revenue", 0) for o in outcomes)
    total_orders = sum(o.get("metrics", {}).get("orders", 0) for o in outcomes)

    return {
        "outcomes": outcomes,
        "summary": {
            "total": total,
            "success": success_count,
            "moderate": moderate_count,
            "failed": failed_count,
            "pending": pending_count,
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "success_rate": round(success_count / max(total - pending_count, 1) * 100, 1),
        },
    }


@outcomes_router.put("/{outcome_id}")
async def update_outcome_metrics(
    outcome_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Update metrics for a tracked product outcome."""
    body = await request.json()
    outcome = await db.product_outcomes.find_one(
        {"id": outcome_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    metrics_update = {}
    for key in ("revenue", "orders", "ad_spend", "days_active"):
        if key in body:
            metrics_update[f"metrics.{key}"] = body[key]

    # Compute ROI
    revenue = body.get("revenue", outcome.get("metrics", {}).get("revenue", 0))
    ad_spend = body.get("ad_spend", outcome.get("metrics", {}).get("ad_spend", 0))
    if ad_spend > 0:
        metrics_update["metrics.roi"] = round((revenue - ad_spend) / ad_spend * 100, 1)

    if body.get("notes"):
        metrics_update["notes"] = body["notes"]
    if body.get("outcome_status") and body["outcome_status"] in ("pending", "success", "moderate", "failed"):
        metrics_update["outcome_status"] = body["outcome_status"]

    metrics_update["last_updated"] = datetime.now(timezone.utc).isoformat()

    await db.product_outcomes.update_one(
        {"id": outcome_id}, {"$set": metrics_update}
    )

    updated = await db.product_outcomes.find_one({"id": outcome_id}, {"_id": 0})
    return {"outcome": updated, "message": "Outcome updated"}


@outcomes_router.post("/auto-label")
async def auto_label_outcomes(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Auto-classify all pending outcomes based on metrics thresholds.
    success: orders >= 50 OR revenue >= 500
    moderate: orders >= 10 OR revenue >= 100
    failed: everything else after 30+ days
    """
    cursor = db.product_outcomes.find(
        {"user_id": current_user.user_id, "outcome_status": "pending"}, {"_id": 0}
    )
    outcomes = await cursor.to_list(200)
    labeled = 0

    for o in outcomes:
        m = o.get("metrics", {})
        revenue = m.get("revenue", 0)
        orders = m.get("orders", 0)
        days = m.get("days_active", 0)

        new_status = None
        reason = None

        if orders >= 50 or revenue >= 500:
            new_status = "success"
            reason = f"orders={orders}, revenue=£{revenue}"
        elif orders >= 10 or revenue >= 100:
            new_status = "moderate"
            reason = f"orders={orders}, revenue=£{revenue}"
        elif days >= 30:
            new_status = "failed"
            reason = f"After {days} days: orders={orders}, revenue=£{revenue}"

        if new_status:
            await db.product_outcomes.update_one(
                {"id": o["id"]},
                {
                    "$set": {
                        "outcome_status": new_status,
                        "auto_label_reason": reason,
                        "last_updated": datetime.now(timezone.utc).isoformat(),
                    }
                },
            )
            labeled += 1

    return {"labeled": labeled, "total_checked": len(outcomes)}


@outcomes_router.get("/stats")
async def get_outcome_stats(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Aggregate outcome stats for the current user."""
    cursor = db.product_outcomes.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    )
    outcomes = await cursor.to_list(500)

    if not outcomes:
        return {
            "total_tracked": 0,
            "success_rate": 0,
            "avg_roi": 0,
            "total_revenue": 0,
            "total_orders": 0,
            "avg_launch_score_success": 0,
            "avg_launch_score_failed": 0,
            "best_categories": [],
            "insights": [],
        }

    total = len(outcomes)
    resolved = [o for o in outcomes if o.get("outcome_status") != "pending"]
    successes = [o for o in outcomes if o.get("outcome_status") == "success"]
    failures = [o for o in outcomes if o.get("outcome_status") == "failed"]

    total_revenue = sum(o.get("metrics", {}).get("revenue", 0) for o in outcomes)
    total_orders = sum(o.get("metrics", {}).get("orders", 0) for o in outcomes)
    rois = [o.get("metrics", {}).get("roi", 0) for o in outcomes if o.get("metrics", {}).get("roi", 0) != 0]
    avg_roi = round(sum(rois) / max(len(rois), 1), 1)

    avg_score_success = round(
        sum(o.get("launch_score_at_launch", 0) for o in successes) / max(len(successes), 1), 1
    )
    avg_score_failed = round(
        sum(o.get("launch_score_at_launch", 0) for o in failures) / max(len(failures), 1), 1
    )

    # Best categories by success count
    cat_stats = {}
    for o in successes:
        cat = o.get("category", "Other")
        cat_stats[cat] = cat_stats.get(cat, 0) + 1
    best_categories = sorted(cat_stats.items(), key=lambda x: x[1], reverse=True)[:5]

    # Generate insights
    insights = []
    if len(resolved) >= 3:
        success_rate = len(successes) / max(len(resolved), 1) * 100
        if success_rate >= 60:
            insights.append({"type": "positive", "text": f"Strong track record! {success_rate:.0f}% of your launched products are successful."})
        if avg_score_success > avg_score_failed + 10:
            insights.append({"type": "learning", "text": f"Products with launch scores above {avg_score_success:.0f} tend to succeed for you."})
        if best_categories:
            insights.append({"type": "category", "text": f"Your strongest category is {best_categories[0][0]} with {best_categories[0][1]} successful launches."})

    return {
        "total_tracked": total,
        "success_rate": round(len(successes) / max(len(resolved), 1) * 100, 1),
        "avg_roi": avg_roi,
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "avg_launch_score_success": avg_score_success,
        "avg_launch_score_failed": avg_score_failed,
        "best_categories": [{"category": c, "count": n} for c, n in best_categories],
        "insights": insights,
    }


# ═══════════════════════════════════════════════════════════════════
# P0: Prediction Accuracy System
# ═══════════════════════════════════════════════════════════════════

@outcomes_router.get("/prediction-accuracy")
async def get_prediction_accuracy(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Compare initial predictions (launch_score, success_probability) against
    actual outcomes to measure how accurate TrendScout's AI is.
    """
    cursor = db.product_outcomes.find(
        {"user_id": current_user.user_id, "outcome_status": {"$ne": "pending"}},
        {"_id": 0},
    )
    resolved = await cursor.to_list(500)

    if not resolved:
        return {
            "sample_size": 0,
            "accuracy_pct": 0,
            "successful_predictions": 0,
            "failed_predictions": 0,
            "score_buckets": [],
            "insights": [],
            "insufficient_data": True,
        }

    # A prediction is "correct" when:
    #   high score (>=60) → outcome=success  OR  low score (<40) → outcome=failed
    #   moderate score (40-59) → outcome=moderate
    correct = 0
    score_buckets = {"80+": {"total": 0, "success": 0}, "60-79": {"total": 0, "success": 0},
                     "40-59": {"total": 0, "success": 0}, "<40": {"total": 0, "success": 0}}

    for o in resolved:
        score = o.get("launch_score_at_launch", 0)
        status = o.get("outcome_status", "")

        # Bucket the score
        if score >= 80:
            bucket = "80+"
        elif score >= 60:
            bucket = "60-79"
        elif score >= 40:
            bucket = "40-59"
        else:
            bucket = "<40"

        score_buckets[bucket]["total"] += 1
        if status == "success":
            score_buckets[bucket]["success"] += 1

        # Determine if prediction was correct
        if score >= 60 and status == "success":
            correct += 1
        elif score >= 40 and score < 60 and status == "moderate":
            correct += 1
        elif score < 40 and status == "failed":
            correct += 1

    total = len(resolved)
    accuracy = round(correct / max(total, 1) * 100, 1)
    successes = sum(1 for o in resolved if o["outcome_status"] == "success")
    failures = sum(1 for o in resolved if o["outcome_status"] == "failed")

    # Generate insights
    insights = []
    for bucket_name, bucket_data in score_buckets.items():
        if bucket_data["total"] >= 2:
            rate = round(bucket_data["success"] / bucket_data["total"] * 100)
            insights.append({
                "text": f"Products with launch score {bucket_name} succeed {rate}% of the time.",
                "bucket": bucket_name,
                "success_rate": rate,
                "sample": bucket_data["total"],
            })

    if total >= 3 and total < 10:
        insights.append({"text": f"Based on {total} tracked products. Track more products for higher accuracy.", "bucket": "info", "success_rate": 0, "sample": total})

    return {
        "sample_size": total,
        "accuracy_pct": accuracy,
        "successful_predictions": correct,
        "failed_predictions": total - correct,
        "score_buckets": [
            {"range": k, "total": v["total"], "success": v["success"],
             "success_rate": round(v["success"] / max(v["total"], 1) * 100, 1)}
            for k, v in score_buckets.items() if v["total"] > 0
        ],
        "insights": insights,
        "insufficient_data": total < 3,
    }


# ═══════════════════════════════════════════════════════════════════
# P1: Opportunity Radar — Live Signal Events
# ═══════════════════════════════════════════════════════════════════


@ad_engine_router.get("/patterns/{product_id}")
async def get_ad_patterns(product_id: str):
    """Analyze winning ad patterns for a product."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ad_discovery = await db.ad_discoveries.find_one({"product_id": product_id}, {"_id": 0})
    return analyze_ad_patterns(product, ad_discovery)


@ad_engine_router.get("/blueprint/{product_id}")
async def get_ad_blueprint(product_id: str):
    """Generate an ad filming blueprint using detected winning patterns."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ad_discovery = await db.ad_discoveries.find_one({"product_id": product_id}, {"_id": 0})
    patterns = analyze_ad_patterns(product, ad_discovery)
    return generate_ad_blueprint(product, patterns)


@ad_engine_router.get("/performance/{product_id}")
async def get_ad_performance(product_id: str):
    """Get ad performance indicators for a product."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ad_discovery = await db.ad_discoveries.find_one({"product_id": product_id}, {"_id": 0})
    return compute_ad_performance(product, ad_discovery)



@ad_test_router.get("/variations/{product_id}")
async def get_ad_variations(product_id: str):
    """Generate 3 ad variations with different hook styles."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    variations = generate_ad_variations(product, count=3)
    test_plan = generate_test_plan(product, variations)
    return {"product_id": product_id, "product_name": product.get("product_name", ""), "variations": variations, "test_plan": test_plan}


@ad_test_router.post("/create")
async def create_ad_test(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Create a new ad A/B test for a product."""
    body = await request.json()
    product_id = body.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id required")

    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    variations = generate_ad_variations(product, count=3)

    test_doc = {
        "id": str(uuid.uuid4()),
        "product_id": product_id,
        "user_id": current_user.user_id,
        "product_name": product.get("product_name", ""),
        "image_url": product.get("image_url", ""),
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "variations": [
            {
                "variation_id": v["variation_id"],
                "label": v["label"],
                "hook_type": v["hook_type"],
                "hook_id": v["hook_id"],
                "results": {"spend": 0, "clicks": 0, "ctr": 0, "add_to_cart": 0, "purchases": 0},
            }
            for v in variations
        ],
        "winner": None,
        "scripts": variations,
    }

    await db.ad_tests.insert_one(test_doc)
    test_doc.pop("_id", None)
    return {"test": test_doc, "message": "Ad test created"}


@ad_test_router.get("/my")
async def get_my_ad_tests(
    current_user: AuthenticatedUser = Depends(get_current_user),
    status: Optional[str] = None,
):
    """Get all ad tests for current user."""
    query = {"user_id": current_user.user_id}
    if status and status in ("active", "completed"):
        query["status"] = status
    cursor = db.ad_tests.find(query, {"_id": 0}).sort("created_at", -1)
    tests = await cursor.to_list(50)
    return {"tests": tests, "total": len(tests)}


@ad_test_router.put("/{test_id}/results")
async def update_ad_test_results(
    test_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Update performance results for a variation in an ad test."""
    body = await request.json()
    variation_id = body.get("variation_id")
    if not variation_id:
        raise HTTPException(status_code=400, detail="variation_id required")

    test = await db.ad_tests.find_one({"id": test_id, "user_id": current_user.user_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="Ad test not found")

    results = {
        "spend": body.get("spend", 0),
        "clicks": body.get("clicks", 0),
        "ctr": body.get("ctr", 0),
        "add_to_cart": body.get("add_to_cart", 0),
        "purchases": body.get("purchases", 0),
    }

    # Auto-compute CTR if clicks and impressions provided
    impressions = body.get("impressions", 0)
    if impressions > 0 and results["clicks"] > 0:
        results["ctr"] = round(results["clicks"] / impressions * 100, 2)

    # Update the specific variation
    variations = test.get("variations", [])
    for v in variations:
        if v["variation_id"] == variation_id:
            v["results"] = results
            break

    # Determine winner (best CTR among variations with data)
    with_data = [v for v in variations if v["results"]["clicks"] > 0]
    winner = None
    if len(with_data) >= 2:
        best = max(with_data, key=lambda x: x["results"]["ctr"])
        avg_ctr = sum(v["results"]["ctr"] for v in with_data) / len(with_data)
        winner = {
            "variation_id": best["variation_id"],
            "label": best["label"],
            "hook_type": best["hook_type"],
            "ctr": best["results"]["ctr"],
            "vs_average": round(best["results"]["ctr"] - avg_ctr, 2),
        }

    await db.ad_tests.update_one(
        {"id": test_id},
        {"$set": {"variations": variations, "winner": winner, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )

    updated = await db.ad_tests.find_one({"id": test_id}, {"_id": 0})
    return {"test": updated, "message": "Results updated"}


@ad_test_router.post("/{test_id}/complete")
async def complete_ad_test(
    test_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Mark test as completed and feed results into learning system."""
    test = await db.ad_tests.find_one({"id": test_id, "user_id": current_user.user_id}, {"_id": 0})
    if not test:
        raise HTTPException(status_code=404, detail="Ad test not found")

    # Feed results into learning — store ad performance signals
    learning_doc = {
        "id": str(uuid.uuid4()),
        "type": "ad_test_result",
        "product_id": test["product_id"],
        "user_id": current_user.user_id,
        "test_id": test_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "variations": test.get("variations", []),
        "winner": test.get("winner"),
    }
    await db.ad_learnings.insert_one(learning_doc)

    await db.ad_tests.update_one(
        {"id": test_id},
        {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc).isoformat()}},
    )

    return {"message": "Test completed. Results saved to learning system.", "winner": test.get("winner")}


# ── Launch Simulator ──

@ad_test_router.get("/simulate/{product_id}")
async def get_launch_simulation(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Simulate a product launch and estimate potential outcomes."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Fetch historical outcomes for context
    cursor = db.product_outcomes.find(
        {"user_id": current_user.user_id, "outcome_status": {"$ne": "pending"}},
        {"_id": 0},
    )
    history = await cursor.to_list(100)

    return simulate_launch(product, history)


@ad_test_router.get("/ai-simulate/{product_id}")
async def get_ai_launch_simulation(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """AI-powered product launch simulation using GPT 5.2."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get base simulation data
    cursor = db.product_outcomes.find(
        {"user_id": current_user.user_id, "outcome_status": {"$ne": "pending"}},
        {"_id": 0},
    )
    history = await cursor.to_list(100)
    base_sim = simulate_launch(product, history)

    # Build AI prompt
    sim = base_sim["simulation"]
    product_context = f"""Product: {product.get('product_name', 'Unknown')}
Category: {product.get('category', 'Unknown')}
Launch Score: {product.get('launch_score', 0)}/100
Trend Stage: {product.get('trend_stage', 'Unknown')}
Competition Level: {product.get('competition_level', 'Unknown')}
TikTok Views: {product.get('tiktok_views', 0):,}
Google Trend Score: {product.get('google_trend_score', 0)}
Supplier Cost: £{product.get('supplier_cost', 0):.2f}
Retail Price: £{product.get('estimated_retail_price', 0):.2f}
Estimated CVR: {sim['estimated_cvr']}%
Estimated CPC: £{sim['estimated_cpc']}
Estimated Daily Sales: {sim['daily_sales_range']['low']}-{sim['daily_sales_range']['high']}
Profit Per Sale: £{sim['profit_per_sale']}
Potential Rating: {base_sim['potential']}
Risks: {', '.join(base_sim['risks']) if base_sim['risks'] else 'None identified'}"""

    try:
        from openai import AsyncOpenAI
        llm_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        if not llm_key:
            raise HTTPException(status_code=500, detail="LLM key not configured")
        _launch_client = AsyncOpenAI(api_key=llm_key)

        prompt = f"""Analyze this product and provide a launch strategy:

{product_context}

Respond in this exact JSON format (no markdown, just raw JSON):
{{
  "verdict": "one sentence verdict on launch viability",
  "confidence_score": 75,
  "strategy": {{
    "phase_1": {{
      "name": "Testing Phase",
      "duration": "Days 1-3",
      "daily_budget": 15,
      "actions": ["action 1", "action 2", "action 3"],
      "success_criteria": "what to look for"
    }},
    "phase_2": {{
      "name": "Scaling Phase",
      "duration": "Days 4-10",
      "daily_budget": 50,
      "actions": ["action 1", "action 2"],
      "success_criteria": "what to look for"
    }},
    "phase_3": {{
      "name": "Optimization Phase",
      "duration": "Days 11-30",
      "daily_budget": 100,
      "actions": ["action 1", "action 2"],
      "success_criteria": "what to look for"
    }}
  }},
  "target_audience": {{
    "primary": "description of primary audience",
    "secondary": "description of secondary audience",
    "platforms": ["platform1", "platform2"]
  }},
  "revenue_projection": {{
    "month_1": {{ "revenue": 500, "profit": 150, "orders": 30 }},
    "month_3": {{ "revenue": 2000, "profit": 800, "orders": 100 }},
    "month_6": {{ "revenue": 5000, "profit": 2500, "orders": 250 }}
  }},
  "risk_assessment": ["risk 1 with mitigation", "risk 2 with mitigation"],
  "competitive_edge": "how to differentiate from competitors",
  "creative_angles": ["ad angle 1", "ad angle 2", "ad angle 3"]
}}"""

        _launch_completion = await _launch_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are TrendScout's AI Launch Strategist. You analyze product data and provide actionable launch strategies for ecommerce entrepreneurs. Be specific, data-driven, and practical. Use British pounds (£) for currency. Keep your response concise but insightful."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        response = _launch_completion.choices[0].message.content

        # Parse AI response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            ai_analysis = json.loads(json_match.group())
        else:
            ai_analysis = {"verdict": response[:200], "error": "Could not parse structured response"}

    except json.JSONDecodeError:
        ai_analysis = {"verdict": "AI analysis generated but could not be parsed. Using base simulation.", "error": "parse_error"}
    except Exception as e:
        logging.error(f"AI simulation error: {e}")
        ai_analysis = {"verdict": base_sim["potential_description"], "error": str(e)[:100]}

    return {
        "success": True,
        "product_id": product_id,
        "ai_analysis": ai_analysis,
        "base_simulation": base_sim,
    }


@ad_test_router.get("/ad-creatives/{product_id}")
async def generate_ad_creatives(
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Generate 3 TikTok ad concepts for a product using GPT 5.2."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        from openai import AsyncOpenAI
        llm_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        if not llm_key:
            raise HTTPException(status_code=500, detail="LLM key not configured")
        _creative_client = AsyncOpenAI(api_key=llm_key)

        prompt = f"""Create 3 TikTok ad concepts for this product:

Product: {product.get('product_name', 'Unknown')}
Category: {product.get('category', 'Unknown')}
Price: £{product.get('estimated_retail_price', 0):.2f}
Key Features: {product.get('description', product.get('product_name', ''))}
TikTok Views: {product.get('tiktok_views', 0):,}

Respond in this exact JSON format (raw JSON only, no markdown):
{{
  "creatives": [
    {{
      "type": "Unboxing",
      "hook": "A compelling first-line hook",
      "scenes": [
        {{"scene": 1, "description": "scene description", "duration": "2s"}},
        {{"scene": 2, "description": "scene description", "duration": "3s"}},
        {{"scene": 3, "description": "scene description", "duration": "3s"}},
        {{"scene": 4, "description": "CTA scene", "duration": "2s"}}
      ],
      "music_style": "trending upbeat",
      "estimated_engagement": "high"
    }},
    {{
      "type": "Problem/Solution",
      "hook": "A problem-focused hook",
      "scenes": [
        {{"scene": 1, "description": "scene", "duration": "2s"}},
        {{"scene": 2, "description": "scene", "duration": "3s"}},
        {{"scene": 3, "description": "scene", "duration": "3s"}},
        {{"scene": 4, "description": "CTA", "duration": "2s"}}
      ],
      "music_style": "dramatic to upbeat",
      "estimated_engagement": "high"
    }},
    {{
      "type": "Curiosity Hook",
      "hook": "A curiosity-driven hook",
      "scenes": [
        {{"scene": 1, "description": "scene", "duration": "2s"}},
        {{"scene": 2, "description": "scene", "duration": "3s"}},
        {{"scene": 3, "description": "scene", "duration": "3s"}},
        {{"scene": 4, "description": "CTA", "duration": "2s"}}
      ],
      "music_style": "mysterious to energetic",
      "estimated_engagement": "medium"
    }}
  ]
}}"""

        _creative_completion = await _creative_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are TrendScout's AI Ad Strategist. You create viral TikTok ad scripts for ecommerce products. Be creative, specific, and format-aware."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=1200,
        )
        response = _creative_completion.choices[0].message.content

        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"creatives": [], "error": "Could not parse response"}

    except json.JSONDecodeError:
        result = {"creatives": [], "error": "parse_error"}
    except Exception as e:
        logging.error(f"Ad creative generation error: {e}")
        result = {"creatives": [], "error": str(e)[:100]}

    return {
        "product_id": product_id,
        "product_name": product.get("product_name", "Unknown"),
        **result,
        "ai_powered": True,
    }



# ═══════════════════════════════════════════════════════════════════
# Ad Spy — Unified Ad Intelligence Search
# ═══════════════════════════════════════════════════════════════════

ads_spy_router = APIRouter(prefix="/api/ads")


@ads_spy_router.get("/discover")
async def discover_ads(
    q: str = "",
    platform: Optional[str] = None,
    sort: str = "engagement",
    limit: int = 24,
):
    """
    Unified ad spy search across platforms.
    Returns product-derived ad intelligence entries with platform attribution.
    """
    limit = min(limit, 50)

    # Build query
    query: Dict[str, Any] = {}
    if q:
        query["$or"] = [
            {"product_name": {"$regex": q, "$options": "i"}},
            {"category": {"$regex": q, "$options": "i"}},
        ]

    # Platform filter — map products to platforms based on their signals
    platform_filter = platform if platform and platform != "all" else None

    # Determine sort order
    sort_map = {
        "engagement": [("tiktok_views", -1), ("engagement_rate", -1)],
        "recent": [("last_updated", -1)],
        "spend": [("estimated_monthly_ad_spend", -1)],
    }
    sort_order = sort_map.get(sort, sort_map["engagement"])

    products = await db.products.find(query, {"_id": 0}).sort(sort_order).limit(limit * 2).to_list(limit * 2)

    ads = []
    for p in products:
        # Assign platform based on product signals
        platforms_for_product = _infer_platforms(p)
        if platform_filter and platform_filter not in platforms_for_product:
            continue

        primary_platform = platform_filter or (platforms_for_product[0] if platforms_for_product else "meta")

        ad = {
            "id": p.get("id"),
            "platform": primary_platform,
            "headline": p.get("product_name", ""),
            "product_name": p.get("product_name", ""),
            "body_text": p.get("short_description") or p.get("ai_summary", "")[:120] if p.get("ai_summary") else "",
            "thumbnail_url": p.get("image_url", ""),
            "image_url": p.get("image_url", ""),
            "ad_type": "video" if p.get("video_urls") else "image",
            "likes": p.get("tiktok_views", 0) // 50 if p.get("tiktok_views") else int(p.get("engagement_rate", 0) * 100),
            "comments": p.get("tiktok_views", 0) // 200 if p.get("tiktok_views") else int(p.get("engagement_rate", 0) * 30),
            "shares": p.get("tiktok_views", 0) // 300 if p.get("tiktok_views") else int(p.get("engagement_rate", 0) * 15),
            "views": p.get("tiktok_views", 0) or int(p.get("engagement_rate", 0) * 5000),
            "advertiser_name": p.get("category", ""),
            "url": f"/product/{p.get('id', '')}",
            "launch_score": p.get("launch_score", 0),
            "estimated_spend": p.get("estimated_monthly_ad_spend", 0),
            "competition_level": p.get("competition_level", ""),
            "trend_stage": p.get("trend_stage", ""),
        }
        ads.append(ad)
        if len(ads) >= limit:
            break

    # Get available categories for filter
    all_categories = await db.products.distinct("category")

    return {
        "ads": ads,
        "total": len(ads),
        "query": q,
        "platform": platform,
        "sort": sort,
        "categories": sorted([c for c in all_categories if c]),
    }


@ads_spy_router.get("/categories")
async def get_ad_categories():
    """Get list of product categories for filtering."""
    cats = await db.products.distinct("category")
    return {"categories": sorted([c for c in cats if c])}


@ads_spy_router.post("/save")
async def save_ad(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Bookmark/save an ad for later reference."""
    body = await request.json()
    ad_id = body.get("ad_id")
    if not ad_id:
        raise HTTPException(status_code=400, detail="ad_id is required")

    existing = await db.saved_ads.find_one(
        {"user_id": current_user.user_id, "ad_id": ad_id}
    )
    if existing:
        return {"saved": True, "message": "Already saved"}

    doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.user_id,
        "ad_id": ad_id,
        "ad_data": body.get("ad_data", {}),
        "notes": body.get("notes", ""),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.saved_ads.insert_one(doc)
    doc.pop("_id", None)
    return {"saved": True, "item": doc}


@ads_spy_router.get("/saved")
async def get_saved_ads(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get all saved/bookmarked ads for the current user."""
    items = await db.saved_ads.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("saved_at", -1).to_list(100)
    return {"saved_ads": items, "total": len(items)}


@ads_spy_router.delete("/saved/{item_id}")
async def unsave_ad(
    item_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Remove a saved ad."""
    result = await db.saved_ads.delete_one(
        {"$or": [{"id": item_id}, {"ad_id": item_id}], "user_id": current_user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved ad not found")
    return {"removed": True}


def _infer_platforms(product: dict) -> list:
    """Infer which ad platforms a product is likely running on based on its signals."""
    platforms = []
    if product.get("tiktok_views", 0) > 0:
        platforms.append("tiktok")
    if product.get("ad_activity_score", 0) > 30:
        platforms.append("meta")
    if product.get("estimated_monthly_ad_spend", 0) > 100:
        platforms.append("pinterest")
    if not platforms:
        platforms = ["meta"]
    return platforms


# ═══════════════════════════════════════════════════════════════════
# Competitor Intelligence — Deep Store Analysis
# ═══════════════════════════════════════════════════════════════════

competitor_intel_router = APIRouter(prefix="/api/competitor-intel")


@competitor_intel_router.post("/analyze")
async def analyze_store_deep(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Deep analysis of a Shopify store: products, pricing, revenue estimates,
    category breakdown, top products, supplier risk indicators.
    """
    body = await request.json()
    url = (body.get("url") or "").strip().rstrip("/")
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    if not url.startswith("http"):
        url = "https://" + url

    domain_match = re.match(r"https?://([^/]+)", url)
    if not domain_match:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    domain = domain_match.group(1)

    products_url = f"https://{domain}/products.json?limit=250"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                products_url,
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"User-Agent": "TrendScout/1.0 Competitor Intel"},
            ) as resp:
                if resp.status == 404:
                    return {"success": False, "error": "Not a Shopify store or products endpoint disabled."}
                if resp.status != 200:
                    return {"success": False, "error": f"Could not reach store (HTTP {resp.status})."}
                data = await resp.json()
    except aiohttp.ClientError:
        return {"success": False, "error": "Could not connect. Check the URL."}

    raw = data.get("products", [])
    if not raw:
        return {
            "success": True,
            "domain": domain,
            "store_url": f"https://{domain}",
            "product_count": 0,
            "analysis": {"status": "empty", "message": "No products found."},
        }

    # --- Process products ---
    products = []
    all_prices = []
    category_counts = {}
    vendor_counts = {}
    creation_dates = []

    for p in raw:
        variants = p.get("variants", [])
        prices = [float(v.get("price", 0)) for v in variants if v.get("price")]
        avg_price = sum(prices) / len(prices) if prices else 0
        all_prices.extend(prices)

        ptype = (p.get("product_type") or "").strip() or "Uncategorized"
        category_counts[ptype] = category_counts.get(ptype, 0) + 1

        vendor = (p.get("vendor") or "").strip()
        if vendor:
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1

        created = p.get("created_at", "")
        if created:
            creation_dates.append(created)

        img = p.get("images", [{}])
        image_url = img[0].get("src", "") if img else ""

        products.append({
            "title": p.get("title", ""),
            "product_type": ptype,
            "vendor": vendor,
            "price": round(avg_price, 2),
            "variants_count": len(variants),
            "image_url": image_url,
            "created_at": created,
            "tags": p.get("tags", "").split(", ")[:5] if isinstance(p.get("tags"), str) else [],
        })

    # Sort by price desc for top products
    products_by_price = sorted(products, key=lambda x: x["price"], reverse=True)
    top_products = products_by_price[:8]

    categories = sorted(
        [{"name": k, "count": v, "pct": round(v / len(raw) * 100, 1)} for k, v in category_counts.items()],
        key=lambda c: c["count"], reverse=True,
    )

    min_price = min(all_prices) if all_prices else 0
    max_price = max(all_prices) if all_prices else 0
    avg_price_all = sum(all_prices) / len(all_prices) if all_prices else 0
    median_price = sorted(all_prices)[len(all_prices) // 2] if all_prices else 0

    # --- Revenue estimation ---
    product_count = len(raw)
    avg_p = avg_price_all

    # Heuristic: estimate daily orders from product count and price range
    if product_count > 100:
        est_daily_orders = product_count * 0.8
        store_tier = "Enterprise"
    elif product_count > 50:
        est_daily_orders = product_count * 0.5
        store_tier = "Established"
    elif product_count > 20:
        est_daily_orders = product_count * 0.3
        store_tier = "Growing"
    elif product_count > 5:
        est_daily_orders = product_count * 0.2
        store_tier = "Early Stage"
    else:
        est_daily_orders = product_count * 0.1
        store_tier = "Micro"

    est_monthly_revenue = round(est_daily_orders * 30 * avg_p, 0)
    est_monthly_orders = round(est_daily_orders * 30)

    # --- Store age estimate ---
    if creation_dates:
        oldest = min(creation_dates)
        try:
            from dateutil.parser import parse as parse_date
            age_days = (datetime.now(timezone.utc) - parse_date(oldest)).days
            store_age_months = round(age_days / 30, 1)
        except Exception:
            store_age_months = None
    else:
        store_age_months = None

    # --- Supplier risk ---
    vendor_count = len(vendor_counts)
    single_vendor = vendor_count <= 1
    supplier_risk = "High" if single_vendor else ("Medium" if vendor_count <= 3 else "Low")
    supplier_risk_reason = (
        "Single vendor dependency — supply chain disruption risk"
        if single_vendor
        else f"{vendor_count} vendors — {'moderate' if vendor_count <= 3 else 'good'} diversification"
    )

    # --- Pricing strategy ---
    if avg_p > 80:
        pricing_strategy = "Premium"
    elif avg_p > 30:
        pricing_strategy = "Mid-Range"
    else:
        pricing_strategy = "Value / Budget"

    price_spread = max_price - min_price if all_prices else 0
    price_consistency = "Tight" if price_spread < avg_p * 0.5 else ("Moderate" if price_spread < avg_p * 2 else "Wide")

    # Save analysis to DB
    analysis_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.user_id,
        "domain": domain,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "product_count": product_count,
        "est_monthly_revenue": est_monthly_revenue,
    }
    await db.competitor_analyses.update_one(
        {"user_id": current_user.user_id, "domain": domain},
        {"$set": analysis_doc},
        upsert=True,
    )

    return {
        "success": True,
        "domain": domain,
        "store_url": f"https://{domain}",
        "store_tier": store_tier,
        "store_age_months": store_age_months,
        "product_count": product_count,
        "categories": categories[:12],
        "top_products": top_products,
        "pricing": {
            "min": round(min_price, 2),
            "max": round(max_price, 2),
            "avg": round(avg_p, 2),
            "median": round(median_price, 2),
            "strategy": pricing_strategy,
            "consistency": price_consistency,
        },
        "revenue_estimate": {
            "monthly_revenue": est_monthly_revenue,
            "monthly_orders": est_monthly_orders,
            "daily_orders": round(est_daily_orders, 1),
            "confidence": "Low — based on catalog size heuristics",
        },
        "suppliers": {
            "vendor_count": vendor_count,
            "top_vendors": sorted(
                [{"name": k, "count": v} for k, v in vendor_counts.items()],
                key=lambda v: v["count"], reverse=True,
            )[:5],
            "risk_level": supplier_risk,
            "risk_reason": supplier_risk_reason,
        },
    }


@competitor_intel_router.post("/compare")
async def compare_stores(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Compare two Shopify stores side by side."""
    body = await request.json()
    urls = body.get("urls", [])
    if len(urls) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 store URLs")

    results = []
    for url in urls[:3]:
        try:
            # Re-use the analyze logic inline
            clean = url.strip().rstrip("/")
            if not clean.startswith("http"):
                clean = "https://" + clean
            dm = re.match(r"https?://([^/]+)", clean)
            if not dm:
                results.append({"url": url, "error": "Invalid URL"})
                continue
            domain = dm.group(1)
            pu = f"https://{domain}/products.json?limit=250"
            async with aiohttp.ClientSession() as sess:
                async with sess.get(pu, timeout=aiohttp.ClientTimeout(total=15),
                                    headers={"User-Agent": "TrendScout/1.0"}) as r:
                    if r.status != 200:
                        results.append({"domain": domain, "error": f"HTTP {r.status}"})
                        continue
                    d = await r.json()
            raw = d.get("products", [])
            prices = []
            cats = {}
            for p in raw:
                for v in p.get("variants", []):
                    try:
                        prices.append(float(v["price"]))
                    except (ValueError, TypeError, KeyError):
                        pass
                pt = (p.get("product_type") or "").strip() or "Uncategorized"
                cats[pt] = cats.get(pt, 0) + 1

            avg_p = sum(prices) / len(prices) if prices else 0
            count = len(raw)
            est_daily = count * (0.8 if count > 100 else 0.5 if count > 50 else 0.3 if count > 20 else 0.2 if count > 5 else 0.1)
            results.append({
                "domain": domain,
                "product_count": count,
                "avg_price": round(avg_p, 2),
                "min_price": round(min(prices), 2) if prices else 0,
                "max_price": round(max(prices), 2) if prices else 0,
                "categories": len(cats),
                "top_category": max(cats, key=cats.get) if cats else "N/A",
                "est_monthly_revenue": round(est_daily * 30 * avg_p),
                "est_daily_orders": round(est_daily, 1),
            })
        except Exception as e:
            results.append({"domain": url, "error": str(e)[:100]})

    return {"stores": results, "compared_at": datetime.now(timezone.utc).isoformat()}


@competitor_intel_router.get("/history")
async def get_analysis_history(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get previously analyzed stores."""
    items = await db.competitor_analyses.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("analyzed_at", -1).to_list(20)
    return {"analyses": items, "total": len(items)}


routers = [ad_creative_router, ad_discovery_router, outcomes_router, ad_test_router, ad_engine_router, ads_spy_router, competitor_intel_router]
