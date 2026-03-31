"""
TikTok Viral Predictor API.

Uses AI to analyse products and predict which ones are likely to go viral
on TikTok in the next 48-72 hours. Predictions are generated periodically
and cached in MongoDB.
"""

import asyncio
import os
import re
import json
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query

from common.database import db
from auth import get_current_user, AuthenticatedUser

logger = logging.getLogger(__name__)

public_router = APIRouter(prefix="/api/public")
premium_router = APIRouter(prefix="/api/viral-predictions")


async def _generate_predictions():
    """
    Core prediction generator. Analyses top products in the DB and uses
    GPT-5.2 to predict viral potential on TikTok.
    """
    # Fetch products with decent scores to analyse
    products = await db.products.find(
        {"launch_score": {"$gte": 1}},
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "image_url": 1,
         "launch_score": 1, "trend_score": 1, "estimated_retail_price": 1,
         "supplier_cost": 1, "estimated_margin": 1, "tiktok_views": 1,
         "competition_level": 1, "ad_activity_score": 1, "data_source": 1,
         "created_at": 1},
    ).sort("launch_score", -1).limit(80).to_list(80)

    if not products:
        # Fallback: grab any products regardless of score
        products = await db.products.find(
            {},
            {"_id": 0, "id": 1, "product_name": 1, "category": 1, "image_url": 1,
             "launch_score": 1, "trend_score": 1, "estimated_retail_price": 1,
             "supplier_cost": 1, "estimated_margin": 1, "tiktok_views": 1,
             "competition_level": 1, "ad_activity_score": 1, "data_source": 1,
             "created_at": 1},
        ).limit(40).to_list(40)

    if not products:
        logger.warning("No products in DB to generate viral predictions from")
        return []

    # Build summary for AI
    product_summaries = []
    for p in products[:40]:
        cost = p.get("supplier_cost", 0) or 0
        retail = p.get("estimated_retail_price", 0) or 0
        margin = p.get("estimated_margin", 0) or 0
        product_summaries.append(
            f"- {p.get('product_name', '?')} | Cat: {p.get('category', '?')} | "
            f"Score: {p.get('launch_score', 0)} | Price: ${retail:.0f} | "
            f"Margin: {margin:.0f}% | TikTok views: {p.get('tiktok_views', 0)} | "
            f"Competition: {p.get('competition_level', '?')}"
        )

    llm_key = os.environ.get("EMERGENT_LLM_KEY")
    if not llm_key:
        logger.warning("No LLM key for viral predictions")
        return []

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        chat = LlmChat(
            api_key=llm_key,
            session_id=f"viral-pred-{uuid.uuid4().hex[:8]}",
            system_message=(
                "You are a TikTok trend analyst specialising in UK ecommerce. "
                "You predict which products will go viral on TikTok in the next 48-72 hours. "
                "Return ONLY valid JSON array, no markdown."
            ),
        ).with_model("openai", "gpt-5.2")

        prompt = (
            "Analyse these products and predict the TOP 12 most likely to go viral on TikTok "
            "in the next 48-72 hours. Consider: visual appeal, demo-ability, price impulse-buy threshold, "
            "trending TikTok formats (GRWM, hauls, satisfying, life hacks, before/after), "
            "UK audience preferences, and seasonality.\n\n"
            "Products:\n" + "\n".join(product_summaries) + "\n\n"
            "Return a JSON ARRAY of objects, ranked by viral probability:\n"
            '[{"product_name": "exact name from list",'
            '"viral_score": 85,'
            '"confidence": "high",'
            '"predicted_window": "48-72 hours",'
            '"reasoning": "why this will go viral",'
            '"tiktok_format": "best TikTok format for this product",'
            '"hook_idea": "specific 3-second hook idea",'
            '"hashtags": ["#tag1", "#tag2", "#tag3"],'
            '"target_demographic": "specific UK demographic",'
            '"estimated_views": "500K-2M",'
            '"ad_budget_suggestion": "£50-100 for initial test",'
            '"urgency": "high/medium/low"}]'
        )

        response = await chat.send_message(UserMessage(text=prompt))

        # Parse JSON array
        predictions = []
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                predictions = json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            logger.error("Failed to parse viral predictions JSON")
            return []

        # Enrich with product data
        enriched = []
        for pred in predictions[:12]:
            pred_name = pred.get("product_name", "").lower()
            matched = None
            for p in products:
                if p.get("product_name", "").lower() == pred_name:
                    matched = p
                    break
            if not matched:
                # fuzzy match
                for p in products:
                    if pred_name[:20] in p.get("product_name", "").lower():
                        matched = p
                        break

            enriched.append({
                "id": str(uuid.uuid4()),
                "product_id": matched.get("id", "") if matched else "",
                "product_name": pred.get("product_name", ""),
                "category": matched.get("category", "") if matched else "",
                "image_url": matched.get("image_url", "") if matched else "",
                "launch_score": matched.get("launch_score", 0) if matched else 0,
                "supplier_cost": matched.get("supplier_cost", 0) if matched else 0,
                "retail_price": matched.get("estimated_retail_price", 0) if matched else 0,
                "viral_score": pred.get("viral_score", 50),
                "confidence": pred.get("confidence", "medium"),
                "predicted_window": pred.get("predicted_window", "48-72 hours"),
                "reasoning": pred.get("reasoning", ""),
                "tiktok_format": pred.get("tiktok_format", ""),
                "hook_idea": pred.get("hook_idea", ""),
                "hashtags": pred.get("hashtags", []),
                "target_demographic": pred.get("target_demographic", ""),
                "estimated_views": pred.get("estimated_views", ""),
                "ad_budget_suggestion": pred.get("ad_budget_suggestion", ""),
                "urgency": pred.get("urgency", "medium"),
            })

        # Save to DB
        if enriched:
            batch = {
                "id": str(uuid.uuid4()),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "predictions": enriched,
                "product_count_analysed": len(products),
            }
            await db.viral_predictions.insert_one(batch)
            batch.pop("_id", None)

        logger.info(f"Generated {len(enriched)} viral predictions")
        return enriched

    except Exception as e:
        logger.error(f"Viral prediction generation error: {e}")
        return []


async def _get_latest_predictions():
    """Get the most recent prediction batch from DB."""
    latest = await db.viral_predictions.find_one(
        {}, {"_id": 0}, sort=[("generated_at", -1)]
    )
    return latest


@public_router.get("/viral-predictions")
async def get_public_viral_predictions():
    """
    Public endpoint — returns top 3 viral predictions as a teaser.
    If no cached predictions exist, fires generation in the background
    and returns an empty list immediately (avoids HTTP timeout on LLM call).
    """
    latest = await _get_latest_predictions()
    if not latest or not latest.get("predictions"):
        # Fire generation in background — don't block the HTTP request
        asyncio.create_task(_generate_predictions())
        return {
            "success": True,
            "predictions": [],
            "total_available": 0,
            "generating": True,
            "message": "AI is generating predictions — check back in 60 seconds",
        }

    all_preds = latest.get("predictions", [])
    return {
        "success": True,
        "predictions": all_preds[:3],
        "total_available": len(all_preds),
        "generated_at": latest.get("generated_at", ""),
        "upgrade_cta": "Sign up to see all predictions, get alerts, and access TikTok ad scripts",
    }


@premium_router.get("")
async def get_full_viral_predictions(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Premium endpoint — returns all viral predictions with full details.
    """
    latest = await _get_latest_predictions()
    if not latest or not latest.get("predictions"):
        predictions = await _generate_predictions()
        return {
            "success": True,
            "predictions": predictions,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "success": True,
        "predictions": latest.get("predictions", []),
        "generated_at": latest.get("generated_at", ""),
        "product_count_analysed": latest.get("product_count_analysed", 0),
    }


@premium_router.post("/refresh")
async def refresh_viral_predictions(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Manually trigger a fresh batch of viral predictions.
    """
    predictions = await _generate_predictions()
    return {
        "success": True,
        "predictions": predictions,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(predictions),
    }


@premium_router.get("/history")
async def viral_prediction_history(
    limit: int = Query(5, ge=1, le=20),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get previous prediction batches."""
    cursor = db.viral_predictions.find(
        {}, {"_id": 0}
    ).sort("generated_at", -1).limit(limit)
    batches = await cursor.to_list(limit)
    return {"success": True, "history": batches}


routers = [public_router, premium_router]
