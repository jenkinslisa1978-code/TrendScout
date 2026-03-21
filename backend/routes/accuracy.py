"""
Prediction Accuracy Tracking System

Snapshots product scores at time of calculation, then compares
against real market data after 30 and 90 days to measure accuracy.

Collections:
  - prediction_snapshots: Original predictions with timestamps
  - prediction_reviews: 30/90 day comparisons with accuracy metrics
"""
from fastapi import APIRouter, Request
from datetime import datetime, timezone, timedelta
import logging
from common.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/accuracy", tags=["accuracy"])

routers = [router]


@router.get("/stats")
async def get_accuracy_stats():
    """
    Return live accuracy metrics based on tracked predictions.
    Only reports stats once we have enough data to be meaningful.
    """
    total_tracked = await db.prediction_snapshots.count_documents({})
    total_reviewed = await db.prediction_reviews.count_documents({})

    if total_reviewed < 5:
        # Not enough data yet — be honest about it
        return {
            "status": "ok",
            "total_tracked": total_tracked,
            "total_reviewed": total_reviewed,
            "has_enough_data": False,
            "margin_accuracy_pct": None,
            "trend_accuracy_pct": None,
            "last_updated": None,
        }

    # Calculate real accuracy from reviewed predictions
    pipeline = [
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "margin_accurate": {"$sum": {"$cond": [{"$eq": ["$margin_within_5pct", True]}, 1, 0]}},
            "trend_correct": {"$sum": {"$cond": [{"$eq": ["$trend_direction_correct", True]}, 1, 0]}},
            "last_reviewed": {"$max": "$reviewed_at"},
        }}
    ]

    result = await db.prediction_reviews.aggregate(pipeline).to_list(1)

    if not result:
        return {
            "status": "ok",
            "total_tracked": total_tracked,
            "total_reviewed": 0,
            "has_enough_data": False,
            "margin_accuracy_pct": None,
            "trend_accuracy_pct": None,
            "last_updated": None,
        }

    r = result[0]
    total = r["total"]

    return {
        "status": "ok",
        "total_tracked": total_tracked,
        "total_reviewed": total,
        "has_enough_data": total >= 5,
        "margin_accuracy_pct": round((r["margin_accurate"] / total) * 100) if total > 0 else 0,
        "trend_accuracy_pct": round((r["trend_correct"] / total) * 100) if total > 0 else 0,
        "last_updated": r.get("last_reviewed", ""),
    }


async def snapshot_prediction(db, product_id: str, product_data: dict):
    """
    Save a prediction snapshot when a product is first scored.
    Call this from the product scoring pipeline.
    """
    existing = await db.prediction_snapshots.find_one({"product_id": product_id})
    if existing:
        return  # Already snapshotted — don't overwrite

    snapshot = {
        "product_id": product_id,
        "product_name": product_data.get("name") or product_data.get("product_name", "Unknown"),
        "snapshot_date": datetime.now(timezone.utc).isoformat(),
        "predicted_score": product_data.get("launch_score") or product_data.get("viability_score", 0),
        "predicted_trend_direction": product_data.get("trend_stage", "unknown"),
        "predicted_margin_pct": product_data.get("estimated_margin_pct", 0),
        "predicted_competition": product_data.get("competition_level", "unknown"),
        "raw_signals": {
            "trend_score": product_data.get("trend_score", 0),
            "competition_score": product_data.get("competition_score", 0),
            "margin_score": product_data.get("margin_score", 0),
            "supplier_score": product_data.get("supplier_score", 0),
            "ad_score": product_data.get("ad_score", 0),
        },
        "reviewed_30d": False,
        "reviewed_90d": False,
    }

    await db.prediction_snapshots.insert_one(snapshot)
    logger.info(f"Prediction snapshot saved for product {product_id}")


async def review_prediction(db, snapshot: dict, current_data: dict, review_type: str = "30d"):
    """
    Compare a snapshot prediction against current market data.
    Creates a prediction_review document with accuracy metrics.
    """
    predicted_margin = snapshot.get("predicted_margin_pct", 0)
    actual_margin = current_data.get("estimated_margin_pct", 0)
    margin_diff = abs(predicted_margin - actual_margin)

    predicted_trend = snapshot.get("predicted_trend_direction", "unknown")
    actual_trend = current_data.get("trend_stage", "unknown")

    # Trend is "correct" if general direction matches
    rising_terms = {"emerging", "rising", "growing", "new"}
    stable_terms = {"stable", "mature", "steady"}
    declining_terms = {"declining", "saturated", "fading"}

    def trend_bucket(t):
        t_lower = t.lower()
        if any(x in t_lower for x in rising_terms):
            return "rising"
        if any(x in t_lower for x in declining_terms):
            return "declining"
        return "stable"

    trend_correct = trend_bucket(predicted_trend) == trend_bucket(actual_trend)

    review = {
        "product_id": snapshot["product_id"],
        "product_name": snapshot["product_name"],
        "review_type": review_type,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_date": snapshot["snapshot_date"],
        "predicted_score": snapshot["predicted_score"],
        "current_score": current_data.get("launch_score") or current_data.get("viability_score", 0),
        "score_diff": abs(snapshot["predicted_score"] - (current_data.get("launch_score") or 0)),
        "predicted_margin_pct": predicted_margin,
        "actual_margin_pct": actual_margin,
        "margin_diff_pct": margin_diff,
        "margin_within_5pct": margin_diff <= 5,
        "predicted_trend": predicted_trend,
        "actual_trend": actual_trend,
        "trend_direction_correct": trend_correct,
    }

    await db.prediction_reviews.insert_one(review)

    # Mark snapshot as reviewed
    update_field = f"reviewed_{review_type}"
    await db.prediction_snapshots.update_one(
        {"product_id": snapshot["product_id"]},
        {"$set": {update_field: True}}
    )

    logger.info(f"Prediction review ({review_type}) for {snapshot['product_name']}: margin_ok={margin_diff <= 5}, trend_ok={trend_correct}")
    return review
