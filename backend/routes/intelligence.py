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

from services.data_integrity import DataIntegrityService
from services.intelligence import ProductValidationEngine, TrendAnalyzer, SuccessPredictionModel

data_integrity_service = DataIntegrityService(db)
product_validator = ProductValidationEngine(db)
trend_analyzer = TrendAnalyzer(db)
success_predictor = SuccessPredictionModel(db)

intelligence_router = APIRouter(prefix="/api/intelligence")

@intelligence_router.get("/validate/{product_id}")
async def validate_product_for_launch(product_id: str):
    """
    Validate if a product is viable to launch.
    
    Returns:
    - recommendation: LAUNCH_OPPORTUNITY | PROMISING_MONITOR | HIGH_RISK | INSUFFICIENT_DATA
    - overall_score: 0-100 viability score
    - signals: Detailed breakdown of each factor
    - strengths/weaknesses: Key insights
    - action_items: Recommended next steps
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    validation = product_validator.validate_product(product)
    
    return {
        "product_id": product_id,
        "product_name": product.get("product_name"),
        "validation": validation.to_dict(),
    }


@intelligence_router.get("/trend-analysis/{product_id}")
async def get_product_trend_analysis(product_id: str):
    """
    Get detailed trend analysis for a product.
    
    Returns:
    - trend_stage: exploding | rising | early_trend | stable | declining
    - trend_velocity: Rate of growth
    - is_early_opportunity: Boolean flag
    - days_until_saturation: Estimated timeline
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    analysis = trend_analyzer.analyze_trend(product)
    
    return {
        "product_id": product_id,
        "product_name": product.get("product_name"),
        "trend_analysis": analysis.to_dict(),
    }


@intelligence_router.get("/success-prediction/{product_id}")
async def predict_product_success(product_id: str):
    """
    Predict success probability for a product launch.
    
    Returns:
    - success_probability: 0-100 score
    - outcome: HIGH_SUCCESS | MODERATE_SUCCESS | UNCERTAIN | LIKELY_FAILURE
    - factors: Contributing factors with explanations
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    prediction = success_predictor.predict_success(product)
    
    return {
        "product_id": product_id,
        "product_name": product.get("product_name"),
        "prediction": prediction.to_dict(),
    }


@intelligence_router.get("/complete-analysis/{product_id}")
async def get_complete_product_analysis(product_id: str):
    """
    Get complete intelligence analysis including validation, trends, and prediction.
    
    This is the primary endpoint for the "Should I launch this?" question.
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Run all analyses
    validation = product_validator.validate_product(product)
    trend_analysis = trend_analyzer.analyze_trend(product)
    prediction = success_predictor.predict_success(product)
    
    # Get data integrity info
    integrity_data = data_integrity_service.format_for_ui(product)
    
    return {
        "product_id": product_id,
        "product_name": product.get("product_name"),
        "category": product.get("category"),
        
        # Primary recommendation
        "recommendation": validation.recommendation.value,
        "recommendation_label": validation.recommendation_label,
        "overall_score": validation.overall_score,
        "risk_level": validation.risk_level.value,
        
        # Success prediction
        "success_probability": prediction.success_probability,
        "success_outcome": prediction.outcome.value,
        
        # Trend info
        "trend_stage": trend_analysis.trend_stage.value,
        "trend_velocity": trend_analysis.velocity_percent,
        "is_early_opportunity": trend_analysis.is_early_opportunity,
        
        # Key insights
        "strengths": validation.strengths,
        "weaknesses": validation.weaknesses,
        "action_items": validation.action_items,
        
        # Summaries
        "validation_summary": validation.summary,
        "prediction_summary": prediction.prediction_explanation,
        
        # Confidence
        "confidence": min(validation.confidence_score, prediction.confidence),
        
        # Data quality
        "data_integrity": integrity_data.get("data_integrity"),
        "warnings": integrity_data.get("warnings", []),
        
        # Full details (expandable)
        "details": {
            "validation": validation.to_dict(),
            "trend_analysis": trend_analysis.to_dict(),
            "prediction": prediction.to_dict(),
        }
    }


@intelligence_router.get("/opportunities")
async def get_launch_opportunities(
    min_score: int = 70,
    limit: int = 20,
    sort_by: str = "score"
):
    """
    Get products that are identified as launch opportunities.
    
    Returns products with LAUNCH_OPPORTUNITY recommendation.
    """
    # Get high-scoring products
    products = await db.products.find(
        {"win_score": {"$gte": min_score}},
        {"_id": 0}
    ).sort("win_score", -1).limit(limit * 2).to_list(limit * 2)
    
    # Validate each and filter
    opportunities = []
    for product in products:
        validation = product_validator.validate_product(product)
        
        if validation.recommendation.value in ["launch_opportunity", "promising_monitor"]:
            opportunities.append({
                "product_id": product.get("id"),
                "product_name": product.get("product_name"),
                "category": product.get("category"),
                "recommendation": validation.recommendation.value,
                "recommendation_label": validation.recommendation_label,
                "overall_score": validation.overall_score,
                "success_probability": success_predictor.predict_success(product).success_probability,
                "risk_level": validation.risk_level.value,
                "summary": validation.summary,
                "strengths": validation.strengths[:2],
                "is_simulated": product.get("data_source") == "simulated",
            })
        
        if len(opportunities) >= limit:
            break
    
    return {
        "opportunities": opportunities,
        "count": len(opportunities),
        "filters": {
            "min_score": min_score,
            "limit": limit,
        }
    }


@intelligence_router.get("/early-opportunities")
async def get_early_trend_opportunities(
    limit: int = 20,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Get products showing early trend signals - best first-mover opportunities.
    Elite plan only.
    """
    await require_plan(current_user, "elite", "early trend detection")
    # Get products with early trend indicators
    products = await db.products.find(
        {
            "$or": [
                {"early_trend_score": {"$gte": 70}},
                {"trend_stage": "early"},
                {"competition_level": "low"}
            ]
        },
        {"_id": 0}
    ).sort("early_trend_score", -1).limit(limit * 2).to_list(limit * 2)
    
    # Analyze trends and filter
    early_opportunities = []
    for product in products:
        trend = trend_analyzer.analyze_trend(product)
        
        if trend.is_early_opportunity:
            validation = product_validator.validate_product(product)
            
            early_opportunities.append({
                "product_id": product.get("id"),
                "product_name": product.get("product_name"),
                "category": product.get("category"),
                "trend_stage": trend.trend_stage.value,
                "velocity_percent": trend.velocity_percent,
                "days_until_saturation": trend.days_until_saturation,
                "momentum_score": trend.momentum_score,
                "validation_score": validation.overall_score,
                "reasoning": trend.reasoning[:2],
                "is_simulated": product.get("data_source") == "simulated",
            })
        
        if len(early_opportunities) >= limit:
            break
    
    return {
        "early_opportunities": early_opportunities,
        "count": len(early_opportunities),
    }


# =====================
# ROUTES - Dashboard Intelligence
# =====================



routers = [intelligence_router]
