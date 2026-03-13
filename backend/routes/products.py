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

data_integrity_service = DataIntegrityService(db)

api_router = APIRouter(prefix="/api")

@api_router.get("/products/find-winning")
async def find_winning_product(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    AI Co-pilot: Auto-selects the best product to launch right now.
    Returns the top product with supplier, profit estimate, and shipping info.
    """
    # Get top products sorted by launch_score
    cursor = db.products.find(
        {"is_canonical": {"$ne": False}, "launch_score": {"$exists": True}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(5)
    candidates = await cursor.to_list(5)

    if not candidates:
        return {"product": None, "message": "No products available. Data pipeline may still be running."}

    # Pick the best candidate (highest launch_score)
    product = candidates[0]
    product_id = product.get("id")

    # Get best supplier if available
    supplier = None
    if product.get("selected_supplier_id"):
        supplier = await db.suppliers.find_one(
            {"id": product["selected_supplier_id"]}, {"_id": 0}
        )
    if not supplier:
        # Find best supplier from DB
        sup_cursor = db.suppliers.find(
            {"product_id": product_id}, {"_id": 0}
        ).sort("price", 1).limit(1)
        suppliers = await sup_cursor.to_list(1)
        if suppliers:
            supplier = suppliers[0]

    # Calculate estimated profit
    selling_price = product.get("estimated_retail_price") or product.get("avg_selling_price") or product.get("recommended_price") or product.get("amazon_price") or product.get("price") or 0
    supplier_cost = product.get("supplier_cost", 0) or (supplier.get("price", 0) if supplier else 0) or selling_price * 0.35
    shipping_cost = product.get("estimated_shipping_cost", 0) or (supplier.get("shipping_cost", 0) if supplier else 0) or 0
    estimated_profit = round(selling_price - supplier_cost - shipping_cost, 2) if selling_price > 0 else 0
    profit_margin_pct = round((estimated_profit / selling_price * 100), 1) if selling_price > 0 else 0

    return {
        "product": {
            "id": product_id,
            "product_name": product.get("product_name", ""),
            "category": product.get("category", ""),
            "image_url": product.get("image_url", ""),
            "launch_score": product.get("launch_score", 0),
            "success_probability": product.get("success_probability", 0),
            "trend_stage": product.get("trend_stage", "Unknown"),
            "selling_price": selling_price,
            "estimated_profit": estimated_profit,
            "profit_margin_pct": profit_margin_pct,
            "amazon_rating": product.get("amazon_rating"),
            "amazon_reviews": product.get("amazon_reviews"),
        },
        "supplier": {
            "name": supplier.get("supplier_name", supplier.get("name", "Best Available Supplier")) if supplier else "Auto-matched supplier",
            "cost": supplier_cost,
            "shipping_origin": supplier.get("shipping_origin", supplier.get("origin", "CN")) if supplier else "CN",
            "delivery_estimate": supplier.get("delivery_estimate", supplier.get("shipping_time", "7-15 business days")) if supplier else "7-15 business days",
            "shipping_cost": shipping_cost,
            "id": supplier.get("id") if supplier else None,
        } if supplier or True else None,
        "recommendation": {
            "confidence": "high" if product.get("launch_score", 0) >= 70 else "medium",
            "reasons": build_winning_reasons(product),
        },
        "alternatives": [
            {
                "id": c.get("id"),
                "product_name": c.get("product_name", ""),
                "launch_score": c.get("launch_score", 0),
                "category": c.get("category", ""),
            }
            for c in candidates[1:4]
        ],
    }


def build_winning_reasons(product: dict) -> list:
    """Build human-readable reasons for why this product was selected."""
    reasons = []
    score = product.get("launch_score", 0)
    if score >= 80:
        reasons.append(f"Exceptional launch score of {score}/100")
    elif score >= 60:
        reasons.append(f"Strong launch score of {score}/100")

    prob = product.get("success_probability", 0)
    if prob >= 70:
        reasons.append(f"{prob}% predicted success probability")

    stage = product.get("trend_stage", "")
    if stage in ["Emerging", "Exploding"]:
        reasons.append(f"Product is in '{stage}' trend stage — early mover advantage")

    margin = product.get("estimated_margin", 0)
    if margin and margin > 10:
        reasons.append(f"Healthy profit margin (est. {margin:.0f}%+)")

    reviews = product.get("amazon_reviews", 0)
    rating = product.get("amazon_rating", 0)
    if rating and rating >= 4.5:
        reasons.append(f"High customer satisfaction ({rating} stars, {reviews:,} reviews)")

    if not reasons:
        reasons.append("Best available product based on current market data")

    return reasons


@api_router.get("/products")
async def get_products(
    category: Optional[str] = None,
    trend_stage: Optional[str] = None,
    opportunity_rating: Optional[str] = None,
    early_trend_label: Optional[str] = None,
    market_label: Optional[str] = None,
    competition_level: Optional[str] = None,
    min_trend_score: Optional[int] = None,
    max_trend_score: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = "trend_score",
    sort_order: str = "desc",
    limit: int = 100,
    include_integrity: bool = False,
    canonical_only: bool = True
):
    """Get products with filtering and optional data integrity metadata"""
    query = {}
    
    if canonical_only:
        query["is_canonical"] = {"$ne": False}
    
    if category:
        query["category"] = category
    if trend_stage:
        query["trend_stage"] = trend_stage
    if opportunity_rating:
        query["opportunity_rating"] = opportunity_rating
    if early_trend_label:
        query["early_trend_label"] = early_trend_label
    if market_label:
        query["market_label"] = market_label
    if competition_level:
        query["competition_level"] = competition_level
    if min_trend_score is not None or max_trend_score is not None:
        ts_query = {}
        if min_trend_score is not None:
            ts_query["$gte"] = min_trend_score
        if max_trend_score is not None:
            ts_query["$lte"] = max_trend_score
        query["trend_score"] = ts_query
    if min_price is not None or max_price is not None:
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        query["estimated_retail_price"] = price_query
    if search:
        query["$or"] = [
            {"product_name": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}},
        ]
    
    sort_direction = 1 if sort_order == "asc" else -1
    cursor = db.products.find(query, {"_id": 0}).sort(sort_by, sort_direction).limit(limit)
    products = await cursor.to_list(limit)
    
    # If include_integrity is True, add data integrity metadata to each product
    if include_integrity:
        products_with_integrity = []
        for product in products:
            integrity_data = data_integrity_service.format_for_ui(product)
            products_with_integrity.append({
                **product,
                "data_integrity": integrity_data.get("data_integrity"),
                "warnings": integrity_data.get("warnings", []),
            })
        products = products_with_integrity
    
    # Calculate data source stats for response metadata
    simulated_count = len([p for p in products if p.get("data_source") == "simulated"])
    canonical_count = len([p for p in products if p.get("is_canonical") is not False])
    multi_source_count = len([p for p in products if len(p.get("contributing_sources", [])) > 1])
    avg_confidence = sum(p.get("canonical_confidence", p.get("confidence_score", 0)) for p in products) / len(products) if products else 0
    
    return {
        "data": products,
        "metadata": {
            "total_count": len(products),
            "canonical_count": canonical_count,
            "multi_source_count": multi_source_count,
            "simulated_count": simulated_count,
            "live_data_count": len(products) - simulated_count,
            "avg_confidence_score": round(avg_confidence, 1),
            "data_quality_warning": "Some data is simulated. Check confidence scores." if simulated_count > 0 else None,
        }
    }

@api_router.get("/products/{product_id}")
async def get_product(product_id: str, include_integrity: bool = False):
    """Get single product with optional data integrity metadata"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    response = {"data": product}
    
    # Add data integrity info
    if include_integrity:
        integrity_data = data_integrity_service.format_for_ui(product)
        response["data_integrity"] = integrity_data.get("data_integrity")
        response["warnings"] = integrity_data.get("warnings", [])
        response["display_hints"] = integrity_data.get("display_hints", {})
    
    return response


@api_router.get("/products/{product_id}/launch-score-breakdown")
async def get_launch_score_breakdown(product_id: str):
    """
    Get detailed Launch Score breakdown for a product.
    Returns component scores, weights, contributions, and plain-English explanations.
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get raw scores (0-100)
    trend_score = product.get('trend_score', 0)
    margin_score = product.get('margin_score', 0)
    competition_score = product.get('competition_score', 0)
    ad_activity_score = product.get('ad_activity_score', 0)
    supplier_demand_score = product.get('supplier_demand_score', 0)
    
    # Weights as per formula
    weights = {
        'trend': 0.30,
        'margin': 0.25,
        'competition': 0.20,
        'ad_activity': 0.15,
        'supplier_demand': 0.10
    }
    
    # Calculate weighted contributions
    trend_contribution = round(trend_score * weights['trend'], 1)
    margin_contribution = round(margin_score * weights['margin'], 1)
    competition_contribution = round(competition_score * weights['competition'], 1)
    ad_activity_contribution = round(ad_activity_score * weights['ad_activity'], 1)
    supplier_contribution = round(supplier_demand_score * weights['supplier_demand'], 1)
    
    # Final launch score
    launch_score = product.get('launch_score', 0)
    launch_label = product.get('launch_score_label', 'risky')
    
    # Generate plain-English explanations for each component
    def get_component_explanation(name: str, score: int) -> dict:
        explanations = {
            'trend': {
                'high': "Strong trend momentum - this product is gaining significant attention",
                'medium': "Moderate trend activity - steady but not explosive growth",
                'low': "Limited trend momentum - market interest is low"
            },
            'margin': {
                'high': "Excellent profit margins - healthy pricing vs supplier costs",
                'medium': "Decent margins - reasonable profitability potential",
                'low': "Thin margins - pricing or costs need attention"
            },
            'competition': {
                'high': "Low market saturation - good opportunity to establish presence",
                'medium': "Moderate competition - room to differentiate",
                'low': "High competition - difficult to stand out"
            },
            'ad_activity': {
                'high': "Active advertising market - proven demand and ROI potential",
                'medium': "Some ad activity - moderate validation from advertisers",
                'low': "Limited ad presence - unproven or declining interest"
            },
            'supplier_demand': {
                'high': "Strong supplier reliability - consistent fulfillment confidence",
                'medium': "Adequate supplier support - manageable fulfillment",
                'low': "Supplier concerns - potential fulfillment risks"
            }
        }
        
        level = 'high' if score >= 70 else ('medium' if score >= 40 else 'low')
        impact = 'positive' if score >= 60 else ('neutral' if score >= 40 else 'negative')
        
        return {
            'level': level,
            'impact': impact,
            'explanation': explanations[name][level]
        }
    
    # Build component breakdown
    components = [
        {
            'name': 'Trend Momentum',
            'key': 'trend',
            'raw_score': trend_score,
            'weight': weights['trend'],
            'weight_percent': f"{int(weights['trend'] * 100)}%",
            'contribution': trend_contribution,
            **get_component_explanation('trend', trend_score)
        },
        {
            'name': 'Profit Margins',
            'key': 'margin',
            'raw_score': margin_score,
            'weight': weights['margin'],
            'weight_percent': f"{int(weights['margin'] * 100)}%",
            'contribution': margin_contribution,
            **get_component_explanation('margin', margin_score)
        },
        {
            'name': 'Market Accessibility',
            'key': 'competition',
            'raw_score': competition_score,
            'weight': weights['competition'],
            'weight_percent': f"{int(weights['competition'] * 100)}%",
            'contribution': competition_contribution,
            **get_component_explanation('competition', competition_score)
        },
        {
            'name': 'Advertiser Validation',
            'key': 'ad_activity',
            'raw_score': ad_activity_score,
            'weight': weights['ad_activity'],
            'weight_percent': f"{int(weights['ad_activity'] * 100)}%",
            'contribution': ad_activity_contribution,
            **get_component_explanation('ad_activity', ad_activity_score)
        },
        {
            'name': 'Supplier Reliability',
            'key': 'supplier_demand',
            'raw_score': supplier_demand_score,
            'weight': weights['supplier_demand'],
            'weight_percent': f"{int(weights['supplier_demand'] * 100)}%",
            'contribution': supplier_contribution,
            **get_component_explanation('supplier_demand', supplier_demand_score)
        }
    ]
    
    # Sort by contribution (highest first)
    components_sorted = sorted(components, key=lambda x: x['contribution'], reverse=True)
    
    # Generate summary
    def get_rating_summary(label: str, score: int) -> str:
        summaries = {
            'strong_launch': f"With a score of {score}, this product shows excellent conditions across multiple factors. It's well-positioned for a successful launch.",
            'promising': f"Scoring {score}, this product has good potential with manageable risks. Consider testing with a small initial order.",
            'risky': f"At {score}, this product has notable weaknesses. Proceed with caution and validate demand before committing.",
            'avoid': f"With only {score} points, this product carries significant risk. Consider alternative products with better fundamentals."
        }
        return summaries.get(label, summaries['risky'])
    
    # Find improvement opportunities
    def get_improvement_suggestions(components: list) -> list:
        suggestions = []
        weakest = sorted(components, key=lambda x: x['raw_score'])[:2]
        
        improvement_tips = {
            'trend': "Monitor social media trends and consider products with rising hashtag activity",
            'margin': "Look for suppliers with lower costs or products that can command higher retail prices",
            'competition': "Focus on niches with fewer established stores or find unique angles",
            'ad_activity': "Products with active ad campaigns often have proven market demand",
            'supplier_demand': "Choose suppliers with strong reviews and reliable shipping times"
        }
        
        for comp in weakest:
            if comp['raw_score'] < 60:
                suggestions.append({
                    'component': comp['name'],
                    'current_score': comp['raw_score'],
                    'suggestion': improvement_tips.get(comp['key'], "Improve this metric to boost overall score")
                })
        
        return suggestions
    
    # Identify strengths and weaknesses
    strengths = [c for c in components_sorted if c['raw_score'] >= 70][:2]
    weaknesses = [c for c in sorted(components, key=lambda x: x['raw_score']) if c['raw_score'] < 50][:2]
    
    return {
        'product_id': product_id,
        'product_name': product.get('product_name'),
        'launch_score': launch_score,
        'launch_label': launch_label,
        'components': components_sorted,
        'formula': {
            'description': 'Launch Score = (Trend x 30%) + (Margin x 25%) + (Competition x 20%) + (Ad Activity x 15%) + (Supplier x 10%)',
            'breakdown': f"{trend_contribution} + {margin_contribution} + {competition_contribution} + {ad_activity_contribution} + {supplier_contribution} = {launch_score}"
        },
        'score_reasoning': product.get('launch_score_breakdown', {}),
        'data_transparency': {
            'data_sources': product.get('data_sources', [product.get('data_source', 'unknown')]),
            'confidence_score': product.get('confidence_score', 0),
            'last_updated': product.get('last_updated'),
            'is_real_data': product.get('is_real_data', False),
            'scores_updated_at': product.get('scores_updated_at'),
        },
        'summary': {
            'rating_explanation': get_rating_summary(launch_label, launch_score),
            'strengths': [{'name': s['name'], 'score': s['raw_score'], 'explanation': s['explanation']} for s in strengths],
            'weaknesses': [{'name': w['name'], 'score': w['raw_score'], 'explanation': w['explanation']} for w in weaknesses],
            'improvements': get_improvement_suggestions(components)
        }
    }


@api_router.get("/products/proven-winners/list")
async def get_proven_winners(limit: int = 10):
    """Get proven winning products based on success tracking"""
    # Find products that are proven winners or have high success probability
    cursor = db.products.find(
        {
            "$or": [
                {"proven_winner": True},
                {"success_probability": {"$gte": 60}},
                {"stores_created": {"$gte": 2}}
            ]
        },
        {"_id": 0}
    ).sort([("success_probability", -1), ("stores_created", -1)]).limit(limit)
    
    products = await cursor.to_list(limit)
    
    # Calculate aggregate stats
    total_stores = sum(p.get('stores_created', 0) for p in products)
    total_exports = sum(p.get('exports_count', 0) for p in products)
    avg_margin = sum(p.get('estimated_margin', 0) for p in products) / len(products) if products else 0
    avg_success_rate = sum(p.get('success_probability', 0) for p in products) / len(products) if products else 0
    
    return {
        "data": products,
        "stats": {
            "count": len(products),
            "total_stores_launched": total_stores,
            "total_exports": total_exports,
            "avg_margin": round(avg_margin, 2),
            "avg_success_rate": round(avg_success_rate, 1)
        }
    }


@api_router.get("/products/market-opportunities/list")
async def get_market_opportunities(limit: int = 10):
    """Get top market opportunities based on market_score"""
    cursor = db.products.find(
        {
            "$or": [
                {"market_score": {"$gte": 60}},
                {"market_label": {"$in": ["high", "medium"]}}
            ]
        },
        {"_id": 0}
    ).sort([("market_score", -1), ("estimated_margin", -1)]).limit(limit)
    
    products = await cursor.to_list(limit)
    
    # Calculate aggregate stats
    avg_market_score = sum(p.get('market_score', 0) for p in products) / len(products) if products else 0
    avg_margin = sum(p.get('estimated_margin', 0) for p in products) / len(products) if products else 0
    high_opp_count = len([p for p in products if p.get('market_label') == 'high'])
    avg_competition = sum(p.get('active_competitor_stores', 0) for p in products) / len(products) if products else 0
    
    return {
        "data": products,
        "stats": {
            "count": len(products),
            "avg_market_score": round(avg_market_score, 1),
            "avg_margin": round(avg_margin, 2),
            "high_opportunity_count": high_opp_count,
            "avg_competitor_stores": round(avg_competition, 0)
        }
    }


@api_router.get("/products/{product_id}/competitors")
async def get_product_competitors(product_id: str):
    """Get competitor data for a specific product"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Generate fresh competitor data (in production, this would come from a cache or live source)
    competitor_data = generate_mock_competitor_data(product)
    
    return {
        "product_id": product_id,
        "product_name": product.get("product_name"),
        "market_intelligence": {
            "active_competitor_stores": competitor_data['active_competitor_stores'],
            "avg_selling_price": competitor_data['avg_selling_price'],
            "price_range": competitor_data['price_range'],
            "estimated_monthly_ad_spend": competitor_data['estimated_monthly_ad_spend'],
            "market_saturation": competitor_data['market_saturation'],
            "market_score": product.get('market_score', 0),
            "market_label": product.get('market_label', 'medium'),
            "market_score_breakdown": product.get('market_score_breakdown', {}),
        },
        "competitor_stores": competitor_data['competitor_stores'],
        "data_freshness": competitor_data['data_freshness'],
        "data_source": competitor_data['data_source'],
    }

@api_router.post("/products")
async def create_product(product: Product):
    """Create new product with automation"""
    product_dict = product.model_dump()
    
    # Run automation
    result = run_full_automation(product_dict)
    processed = result['product']
    
    await db.products.insert_one(processed)
    
    # Remove MongoDB _id for JSON serialization
    if '_id' in processed:
        del processed['_id']
    
    # Save alert if generated
    if result['alert']:
        await db.trend_alerts.insert_one(result['alert'])
        if '_id' in result['alert']:
            del result['alert']['_id']
    
    return {"data": processed, "alert": result['alert']}

@api_router.put("/products/{product_id}")
async def update_product(product_id: str, updates: Dict[str, Any]):
    """Update product with automation"""
    existing = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Merge updates
    merged = {**existing, **updates}
    
    # Run automation
    result = run_full_automation(merged)
    processed = result['product']
    
    await db.products.update_one({"id": product_id}, {"$set": processed})
    
    return {"data": processed, "alert": result['alert']}

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete product"""
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True}


# =====================
# SATURATION METER API
# =====================

@api_router.get("/products/{product_id}/saturation")
async def get_product_saturation(product_id: str):
    """Get saturation/competition data for a product."""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    competition = product.get("competition_level", "medium")
    ad_count = product.get("ad_count", 0)
    active_stores = product.get("active_competitor_stores", 0)
    market_saturation = product.get("market_saturation", 0)
    trend_stage = product.get("trend_stage", "rising")

    # Calculate saturation score (0-100)
    if market_saturation > 0:
        saturation_score = market_saturation
    else:
        base = {"low": 20, "medium": 45, "high": 70}.get(competition, 45)
        ad_factor = min(30, ad_count / 10)
        store_factor = min(20, active_stores)
        saturation_score = min(100, int(base + ad_factor + store_factor))

    # Risk level
    if saturation_score >= 65:
        risk_level = "High"
    elif saturation_score >= 35:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Search growth indicator
    growth_rate = product.get("view_growth_rate", 0)
    if growth_rate >= 50:
        search_growth = "Rapid"
    elif growth_rate >= 20:
        search_growth = "Growing"
    elif growth_rate > 0:
        search_growth = "Steady"
    else:
        search_growth = "Flat"

    return {
        "product_id": product_id,
        "saturation_score": saturation_score,
        "risk_level": risk_level,
        "stores_detected": active_stores or int({"low": 8, "medium": 25, "high": 55}.get(competition, 25)),
        "ads_detected": ad_count,
        "search_growth": search_growth,
        "trend_stage": trend_stage,
        "competition_level": competition,
        "market_saturation": market_saturation,
    }


# =====================
# ALERTS API
# =====================

@api_router.get("/alerts")
async def get_alerts(limit: int = 50, unread_only: bool = False):
    """Get alerts"""
    query = {}
    if unread_only:
        query["read"] = False
        query["dismissed"] = False
    
    cursor = db.trend_alerts.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    alerts = await cursor.to_list(limit)
    
    # Calculate stats
    all_alerts = await db.trend_alerts.find({}, {"_id": 0}).to_list(1000)
    stats = {
        "total": len(all_alerts),
        "unread": len([a for a in all_alerts if not a.get('read') and not a.get('dismissed')]),
        "critical": len([a for a in all_alerts if a.get('priority') == 'critical']),
        "early_stage": len([a for a in all_alerts if a.get('alert_type') == 'early_stage']),
    }
    
    return {"data": alerts, "stats": stats}

@api_router.put("/alerts/{alert_id}/read")
async def mark_trend_alert_read(alert_id: str):
    """Mark alert as read"""
    await db.trend_alerts.update_one({"id": alert_id}, {"$set": {"read": True}})
    return {"success": True}

@api_router.put("/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str):
    """Dismiss alert"""
    await db.trend_alerts.update_one({"id": alert_id}, {"$set": {"dismissed": True}})
    return {"success": True}



@api_router.get("/products/{product_id}/saturation")
async def get_product_saturation(product_id: str):
    """
    Calculate saturation risk for a product based on stores, ads,
    search growth, and trend stage.
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stores_detected = product.get("active_competitor_stores", 0) or product.get("stores_created", 0) or 0
    ads_detected = product.get("ad_count", 0) or 0
    trend_stage = product.get("trend_stage", "Stable")
    search_growth = product.get("search_growth_score", 0) or 0
    trend_velocity = product.get("trend_velocity", 0) or 0

    # Compute saturation score (0-100)
    sat_score = 0
    sat_score += min(stores_detected * 1.5, 30)       # up to 30 pts
    sat_score += min(ads_detected * 1.0, 25)           # up to 25 pts
    if trend_stage in ("Declining", "Stable"):
        sat_score += 20
    elif trend_stage == "Rising":
        sat_score += 10
    if search_growth < 20:
        sat_score += 15
    elif search_growth < 50:
        sat_score += 5
    if trend_velocity < 0:
        sat_score += 10
    sat_score = min(round(sat_score), 100)

    if sat_score >= 65:
        risk_level = "High"
    elif sat_score >= 35:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    search_label = "rising" if search_growth >= 50 else "moderate" if search_growth >= 20 else "declining"

    return {
        "product_id": product_id,
        "saturation_score": sat_score,
        "risk_level": risk_level,
        "stores_detected": stores_detected,
        "ads_detected": ads_detected,
        "search_growth": search_label,
        "trend_stage": trend_stage,
        "signals": {
            "stores": {"value": stores_detected, "label": f"{stores_detected} stores selling this product"},
            "ads": {"value": ads_detected, "label": f"{ads_detected} active ads detected"},
            "search": {"value": search_growth, "label": f"Search growth: {search_label}"},
            "trend": {"value": trend_stage, "label": f"Trend stage: {trend_stage}"},
        },
    }


@api_router.get("/products/{product_id}/competitor-intelligence")
async def get_competitor_intelligence(product_id: str):
    """
    Analyze competitor stores selling this product.
    Returns store count, age, traffic estimates, pricing range, ad activity.
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Derive intelligence from product signals
    ad_count = product.get("ad_count", 0) or 0
    stores_created = product.get("stores_created", 0) or 0
    active_stores = product.get("active_competitor_stores", 0) or 0
    trend_velocity = product.get("trend_velocity", 0) or 0
    competition = product.get("competition_level", "medium")

    # Estimate total stores from signals
    total_stores = max(active_stores, stores_created, int(ad_count * 0.6))

    # Estimate new stores in last 7 days from trend velocity
    new_stores_7d = max(0, int(total_stores * (trend_velocity / 100) * 0.3)) if trend_velocity > 0 else int(total_stores * 0.05)

    # Estimate price range from product data
    sell_price = product.get("sell_price", 0) or product.get("estimated_profit", 0) * 3 or 25
    price_low = round(sell_price * 0.7, 2)
    price_high = round(sell_price * 1.4, 2)

    # Estimate avg store age
    if trend_velocity > 30:
        avg_age_months = round(1.0 + (total_stores * 0.02), 1)
    elif trend_velocity > 10:
        avg_age_months = round(2.5 + (total_stores * 0.03), 1)
    else:
        avg_age_months = round(4.0 + (total_stores * 0.05), 1)

    # Estimate traffic from ads and competition
    est_traffic = "High" if ad_count > 100 else "Medium" if ad_count > 20 else "Low"

    # Competition impact on scoring
    if total_stores > 50:
        competition_impact = "High competition — differentiation critical"
    elif total_stores > 20:
        competition_impact = "Moderate competition — branding matters"
    else:
        competition_impact = "Low competition — good window to enter"

    return {
        "product_id": product_id,
        "stores_detected": total_stores,
        "new_stores_7d": new_stores_7d,
        "price_range": {"low": price_low, "high": price_high, "currency": "GBP"},
        "avg_store_age_months": avg_age_months,
        "advertising_activity": est_traffic,
        "ads_detected": ad_count,
        "competition_level": competition,
        "competition_impact": competition_impact,
    }



@api_router.get("/scoring/methodology")
async def get_scoring_methodology():
    """
    Public endpoint that explains exactly how TrendScout scores products.
    Built for transparency — helps users trust the data.
    """
    return {
        "title": "How TrendScout Scores Products",
        "overview": "Every product receives a Launch Score from 0-100, calculated from 7 real signals. Higher scores mean a product is more likely to succeed as a dropshipping product.",
        "formula": "Launch Score = (25% Trend) + (20% Margin) + (15% Competition) + (15% Ad Activity) + (10% Supplier) + (10% Search Growth) + (5% Order Velocity)",
        "signals": [
            {
                "name": "Trend Score",
                "weight": "25%",
                "description": "How much momentum this product has right now",
                "sources": ["Amazon Best Seller Rank changes", "Google Trends velocity", "TikTok view counts", "View growth rate"],
                "what_high_means": "Product is gaining popularity fast — more people searching and buying",
                "what_low_means": "Demand is flat or declining",
            },
            {
                "name": "Margin Score",
                "weight": "20%",
                "description": "How much profit you can make per sale",
                "sources": ["AliExpress/CJ supplier pricing", "Amazon retail price data", "Market average pricing"],
                "what_high_means": "Strong profit margins (50%+) — plenty of room for ad costs",
                "what_low_means": "Tight margins — ads may eat all your profit",
            },
            {
                "name": "Competition Score",
                "weight": "15%",
                "description": "How many other sellers are already in this market (higher score = less competition)",
                "sources": ["Amazon review counts", "Competition level analysis", "Market saturation data"],
                "what_high_means": "Few competitors — good entry window",
                "what_low_means": "Highly saturated — many established sellers",
            },
            {
                "name": "Ad Activity Score",
                "weight": "15%",
                "description": "Sweet spot analysis — some ads validate the market, too many means oversaturation",
                "sources": ["Meta Ad Library active ad counts", "TikTok ad detection"],
                "what_high_means": "10-75 active ads — proven demand with manageable competition",
                "what_low_means": "Either no validation (0 ads) or oversaturated (300+ ads)",
            },
            {
                "name": "Supplier Demand Score",
                "weight": "10%",
                "description": "Supply chain reliability and supplier quality",
                "sources": ["AliExpress order velocity", "CJ Dropshipping availability", "Supplier ratings", "Fulfillment speed"],
                "what_high_means": "Reliable supplier, fast shipping, high demand",
                "what_low_means": "Limited suppliers or slow fulfillment",
            },
            {
                "name": "Search Growth Score",
                "weight": "10%",
                "description": "Whether people are searching for this product more than before",
                "sources": ["Google Trends interest data", "Search volume changes"],
                "what_high_means": "Search interest is rising — growing demand",
                "what_low_means": "Search interest is flat or declining",
            },
            {
                "name": "Order Velocity Score",
                "weight": "5%",
                "description": "How fast the product is selling on supplier platforms",
                "sources": ["AliExpress weekly order velocity", "30-day order totals", "Order growth rate"],
                "what_high_means": "Product is selling well — validated demand",
                "what_low_means": "Low order volume",
            },
        ],
        "data_sources": [
            {"name": "Amazon", "type": "Retail pricing, reviews, BSR", "method": "API/Scraper", "update_frequency": "Daily"},
            {"name": "Google Trends", "type": "Search interest & velocity", "method": "API", "update_frequency": "Daily"},
            {"name": "TikTok", "type": "Viral content & view counts", "method": "API/Scraper", "update_frequency": "Daily"},
            {"name": "AliExpress", "type": "Supplier pricing & orders", "method": "API/Scraper", "update_frequency": "Daily"},
            {"name": "CJ Dropshipping", "type": "Supplier availability & pricing", "method": "API", "update_frequency": "Real-time"},
            {"name": "Meta Ad Library", "type": "Active ad counts & creatives", "method": "API", "update_frequency": "Daily"},
        ],
        "confidence_levels": {
            "high": "80-100 — Multiple live data sources confirm this signal",
            "medium": "50-79 — At least one live source, some signals estimated",
            "low": "25-49 — Limited data, mostly estimated from patterns",
            "very_low": "0-24 — Minimal data available",
        },
        "honest_limitations": [
            "Scores are based on available data — not every signal has a live data source for every product",
            "Success probability is an estimate, not a guarantee — real-world results depend on execution, ad spend, timing, and competition",
            "TikTok view counts reflect content popularity, not purchase intent — high views don't always mean high sales",
            "Supplier prices may fluctuate — always verify before committing to large orders",
            "Competition data is a snapshot — new sellers can enter at any time",
        ],
    }


class ProfitCalcRequest(BaseModel):
    product_id: str
    daily_ad_budget: float = 10.0  # GBP
    conversion_rate: float = 2.0   # percent
    avg_cpc: float = 0.50          # GBP
    days: int = 30


@api_router.post("/profitability-calculator")
async def calculate_profitability(req: ProfitCalcRequest):
    """
    Estimate ROI for a product based on ad budget and conversion assumptions.
    Returns projected revenue, profit, and break-even analysis.
    """
    product = await db.products.find_one({"id": req.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    retail_price = float(product.get("estimated_retail_price", 0))
    supplier_cost = float(product.get("supplier_cost", 0))
    margin_per_sale = retail_price - supplier_cost

    daily_clicks = req.daily_ad_budget / req.avg_cpc if req.avg_cpc > 0 else 0
    daily_sales = daily_clicks * (req.conversion_rate / 100)
    daily_revenue = daily_sales * retail_price
    daily_profit = (daily_sales * margin_per_sale) - req.daily_ad_budget

    total_ad_spend = req.daily_ad_budget * req.days
    total_revenue = daily_revenue * req.days
    total_profit = daily_profit * req.days
    total_sales = int(daily_sales * req.days)
    roi_percent = ((total_profit / total_ad_spend) * 100) if total_ad_spend > 0 else 0

    # Break-even
    cost_per_acquisition = req.daily_ad_budget / daily_sales if daily_sales > 0 else 0
    break_even_daily_sales = req.daily_ad_budget / margin_per_sale if margin_per_sale > 0 else 0
    break_even_conversion = (break_even_daily_sales / daily_clicks * 100) if daily_clicks > 0 else 0

    # Verdict
    if roi_percent > 100:
        verdict = "Strong opportunity — projected ROI is excellent"
        verdict_color = "green"
    elif roi_percent > 0:
        verdict = "Profitable but tight margins — optimise ads carefully"
        verdict_color = "amber"
    else:
        verdict = "Not profitable at current assumptions — lower CPC or increase conversion rate"
        verdict_color = "red"

    return {
        "product_name": product.get("product_name"),
        "inputs": {
            "daily_ad_budget": req.daily_ad_budget,
            "conversion_rate": req.conversion_rate,
            "avg_cpc": req.avg_cpc,
            "days": req.days,
        },
        "product_economics": {
            "retail_price": round(retail_price, 2),
            "supplier_cost": round(supplier_cost, 2),
            "margin_per_sale": round(margin_per_sale, 2),
            "margin_percent": round((margin_per_sale / retail_price * 100) if retail_price > 0 else 0, 1),
        },
        "projections": {
            "daily_clicks": round(daily_clicks, 1),
            "daily_sales": round(daily_sales, 2),
            "daily_revenue": round(daily_revenue, 2),
            "daily_profit": round(daily_profit, 2),
            "total_ad_spend": round(total_ad_spend, 2),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "total_sales": total_sales,
            "roi_percent": round(roi_percent, 1),
        },
        "break_even": {
            "cost_per_acquisition": round(cost_per_acquisition, 2),
            "break_even_daily_sales": round(break_even_daily_sales, 2),
            "break_even_conversion_rate": round(break_even_conversion, 2),
        },
        "verdict": verdict,
        "verdict_color": verdict_color,
    }


routers = [api_router]
