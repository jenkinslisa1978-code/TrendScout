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

def generate_referral_code(user_id: str) -> str:
    import hashlib
    hash_val = hashlib.md5(f"{user_id}_referral".encode()).hexdigest()[:8]
    return f"TS-{hash_val.upper()}"

viral_router = APIRouter(prefix="/api/viral")

@viral_router.get("/referral/stats")
async def get_referral_stats(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Get referral statistics for the authenticated user"""
    user_id = current_user.user_id
    # Get or create referral code
    user_referral = await db.user_referrals.find_one({"user_id": user_id}, {"_id": 0})
    
    if not user_referral:
        # Create referral code for user
        referral_code = generate_referral_code(user_id)
        user_referral = {
            "user_id": user_id,
            "referral_code": referral_code,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.user_referrals.insert_one(user_referral)
    
    # Count referrals
    total_referrals = await db.referrals.count_documents({"referrer_id": user_id})
    verified_referrals = await db.referrals.count_documents({
        "referrer_id": user_id,
        "status": "verified"
    })
    
    # Calculate bonus slots (max 5)
    bonus_slots = min(verified_referrals, 5)
    
    return {
        "user_id": user_id,
        "referral_code": user_referral.get("referral_code"),
        "total_referrals": total_referrals,
        "verified_referrals": verified_referrals,
        "bonus_store_slots": bonus_slots,
        "max_bonus_slots": 5,
        "remaining_bonus_capacity": max(0, 5 - bonus_slots),
        "referral_link": f"/signup?ref={user_referral.get('referral_code')}",
    }


@viral_router.post("/referral/track")
async def track_referral(referral_code: str, referred_user_id: str):
    """Track a new referral when a user signs up with a code"""
    # Find referrer
    referrer = await db.user_referrals.find_one({"referral_code": referral_code}, {"_id": 0})
    
    if not referrer:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    
    # Prevent self-referral
    if referrer["user_id"] == referred_user_id:
        raise HTTPException(status_code=400, detail="Cannot use your own referral code")
    
    # Check if this user was already referred
    existing = await db.referrals.find_one({"referred_id": referred_user_id})
    if existing:
        raise HTTPException(status_code=400, detail="User already has a referral")
    
    # Create referral record
    referral = {
        "id": str(uuid.uuid4()),
        "referrer_id": referrer["user_id"],
        "referred_id": referred_user_id,
        "referral_code": referral_code,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.referrals.insert_one(referral)
    
    return {"success": True, "referral_id": referral["id"], "status": "pending"}


@viral_router.post("/referral/verify/{referral_id}")
async def verify_referral(referral_id: str):
    """Verify a referral (called after user completes signup/action)"""
    referral = await db.referrals.find_one({"id": referral_id}, {"_id": 0})
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    if referral["status"] == "verified":
        return {"success": True, "message": "Already verified"}
    
    # Update referral status
    await db.referrals.update_one(
        {"id": referral_id},
        {
            "$set": {
                "status": "verified",
                "verified_at": datetime.now(timezone.utc).isoformat(),
            }
        }
    )
    
    return {"success": True, "message": "Referral verified"}


@viral_router.get("/referral/history")
async def get_referral_history(
    limit: int = 20,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get referral history for the authenticated user"""
    user_id = current_user.user_id
    cursor = db.referrals.find(
        {"referrer_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    
    referrals = await cursor.to_list(limit)
    
    return {"referrals": referrals, "count": len(referrals)}


@viral_router.get("/public/product/{product_id}")
async def get_public_product(product_id: str):
    """
    Get public product insights (partial data for SEO/sharing).
    Full insights require authentication.
    """
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Return partial insights only
    public_data = {
        "id": product["id"],
        "product_name": product.get("product_name"),
        "category": product.get("category"),
        "image_url": product.get("image_url"),
        "trend_stage": product.get("trend_stage"),
        "trend_score": product.get("trend_score"),
        "market_label": product.get("market_label"),
        "market_score": product.get("market_score"),
        "early_trend_label": product.get("early_trend_label"),
        "competition_level": product.get("competition_level"),
        # Blurred/hidden data (shown as ranges or hidden)
        "margin_range": get_margin_range(product.get("estimated_margin", 0)),
        "has_supplier_data": bool(product.get("supplier_cost")),
        "has_competitor_data": bool(product.get("active_competitor_stores")),
        # Metadata
        "is_partial": True,
        "signup_cta": "Sign up to unlock full insights and build your store",
    }
    
    return public_data


def get_margin_range(margin: float) -> str:
    """Convert exact margin to a range for public display"""
    if margin >= 50:
        return "£50+"
    elif margin >= 30:
        return "£30-50"
    elif margin >= 20:
        return "£20-30"
    elif margin >= 10:
        return "£10-20"
    else:
        return "Under £10"


@viral_router.get("/public/weekly-winners")
async def get_weekly_winners(limit: int = 10):
    """
    Get weekly winning products (public page for SEO/sharing).
    Shows partial insights to drive signups.
    """
    # Get top products by market score
    cursor = db.products.find(
        {"market_score": {"$gte": 60}},
        {"_id": 0}
    ).sort([("market_score", -1), ("trend_score", -1)]).limit(limit)
    
    products = await cursor.to_list(limit)
    
    # Convert to public format
    public_products = []
    for idx, product in enumerate(products):
        public_products.append({
            "rank": idx + 1,
            "id": product["id"],
            "product_name": product.get("product_name"),
            "category": product.get("category"),
            "image_url": product.get("image_url"),
            "trend_stage": product.get("trend_stage"),
            "trend_score": product.get("trend_score"),
            "market_label": product.get("market_label"),
            "market_score": product.get("market_score"),
            "early_trend_label": product.get("early_trend_label"),
            "margin_range": get_margin_range(product.get("estimated_margin", 0)),
        })
    
    # Get week info
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())
    
    return {
        "week_of": week_start.strftime("%B %d, %Y"),
        "products": public_products,
        "count": len(public_products),
        "is_partial": True,
        "signup_cta": "Sign up to unlock full insights and build your store",
        "branding": {
            "name": "TrendScout",
            "tagline": "Find winning products before they go viral",
        }
    }




@viral_router.get("/share/product/{product_id}")
async def get_share_data(product_id: str):
    """Get share data for a product (for social sharing)"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    market_info = {
        "massive": "Massive Opportunity",
        "strong": "Strong Opportunity",
        "competitive": "Competitive",
        "saturated": "Saturated",
    }
    
    market_label = product.get("market_label", "competitive")
    
    share_text = f"Check out {product['product_name']} - {market_info.get(market_label, 'Strong')}!\n\n"
    share_text += f"Market Score: {product.get('market_score', 0)}/100\n"
    share_text += f"Trend: {product.get('trend_stage', 'rising').title()}\n"
    share_text += f"Margin: {get_margin_range(product.get('estimated_margin', 0))}\n\n"
    share_text += "Find more winning products on TrendScout"
    
    return {
        "product_id": product_id,
        "product_name": product.get("product_name"),
        "share_text": share_text,
        "share_url": f"/discover/product/{product_id}",
        "card_data": {
            "title": product.get("product_name"),
            "market_score": product.get("market_score", 0),
            "market_label": market_label,
            "market_label_text": market_info.get(market_label, "Strong Opportunity"),
            "trend_score": product.get("trend_score", 0),
            "trend_stage": product.get("trend_stage", "rising"),
            "margin_range": get_margin_range(product.get("estimated_margin", 0)),
            "category": product.get("category"),
            "image_url": product.get("image_url"),
            "early_trend_label": product.get("early_trend_label"),
        },
        "branding": {
            "name": "TrendScout",
            "tagline": "Find winning products before they go viral",
            "url": "trendscout.click",
            "color": "#4F46E5",
        }
    }


# =====================
# DATA INTEGRITY & SOURCE HEALTH MONITORING
# =====================

from services.data_integrity import (
    DataIntegrityService,
    ConfidenceLevel,
    SignalOrigin,
    DataFreshness,
)
from services.source_health import SourceHealthMonitor, SourceStatus

# Initialize services
data_integrity_service = DataIntegrityService(db)
source_health_monitor = SourceHealthMonitor(db)



routers = [viral_router]
