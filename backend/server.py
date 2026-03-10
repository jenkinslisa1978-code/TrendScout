from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import hmac
import hashlib
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum

# Import authentication module
from auth import get_current_user, get_optional_user, AuthenticatedUser

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="ViralScout API", version="1.0.0")

# Create routers
api_router = APIRouter(prefix="/api")
stripe_router = APIRouter(prefix="/api/stripe")
automation_router = APIRouter(prefix="/api/automation")
ingestion_router = APIRouter(prefix="/api/ingestion")
stores_router = APIRouter(prefix="/api/stores")
jobs_router = APIRouter(prefix="/api/jobs")
viral_router = APIRouter(prefix="/api/viral")
data_integrity_router = APIRouter(prefix="/api/data-integrity")

# =====================
# MODELS
# =====================

class AutomationStatus(str, Enum):
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

class AutomationJobType(str, Enum):
    FULL_PIPELINE = "full_pipeline"
    TREND_SCORING = "trend_scoring"
    OPPORTUNITY_RATING = "opportunity_rating"
    TREND_STAGE = "trend_stage"
    AI_SUMMARY = "ai_summary"
    ALERT_GENERATION = "alert_generation"
    PRODUCT_IMPORT = "product_import"
    SCHEDULED_DAILY = "scheduled_daily"
    TIKTOK_IMPORT = "tiktok_import"
    AMAZON_IMPORT = "amazon_import"
    SUPPLIER_IMPORT = "supplier_import"
    FULL_DATA_SYNC = "full_data_sync"

class AutomationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_type: AutomationJobType
    status: AutomationStatus = AutomationStatus.STARTED
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    products_processed: int = 0
    alerts_generated: int = 0
    import_source: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AutomationLogCreate(BaseModel):
    job_type: AutomationJobType
    import_source: Optional[str] = None

class AutomationLogUpdate(BaseModel):
    status: Optional[AutomationStatus] = None
    products_processed: Optional[int] = None
    alerts_generated: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    category: str = "General"
    short_description: Optional[str] = None
    supplier_cost: float = 0
    estimated_retail_price: float = 0
    estimated_margin: float = 0
    tiktok_views: int = 0
    ad_count: int = 0
    competition_level: str = "medium"
    trend_score: int = 0
    trend_stage: str = "rising"
    opportunity_rating: str = "medium"
    # Early Trend Detection fields
    early_trend_score: int = 0
    early_trend_label: str = "stable"
    view_growth_rate: float = 0.0  # Percentage growth velocity
    engagement_rate: float = 0.0  # Engagement as percentage
    supplier_order_velocity: int = 0  # Orders per week
    # Product Success Tracking fields
    stores_created: int = 0  # Number of stores created with this product
    exports_count: int = 0  # Number of times exported
    success_signals: int = 0  # Estimated sales/success signals
    user_engagement_score: float = 0.0  # User interaction score
    success_probability: int = 0  # Calculated success probability (0-100)
    proven_winner: bool = False  # True if product is proven successful
    # Market Intelligence fields
    active_competitor_stores: int = 0  # Number of stores selling this product
    new_competitor_stores_week: int = 0  # New stores this week
    avg_selling_price: float = 0.0  # Average market selling price
    price_range: Optional[Dict[str, float]] = None  # Min/max prices
    estimated_monthly_ad_spend: int = 0  # Estimated monthly ad spend in GBP
    market_saturation: int = 0  # Market saturation score (0-100)
    market_score: int = 0  # Combined market opportunity score (0-100)
    market_label: str = "medium"  # massive, strong, competitive, saturated
    market_description: Optional[str] = None
    market_score_breakdown: Optional[Dict[str, int]] = None  # Component scores
    # Scoring Engine fields
    margin_score: int = 0
    competition_score: int = 0
    ad_activity_score: int = 0
    supplier_demand_score: int = 0
    # Ad Activity fields
    recent_ad_growth: float = 0.0
    new_ads_this_week: int = 0
    ad_platform_distribution: Optional[Dict[str, int]] = None
    ad_validation_level: str = "unknown"
    # Supplier fields
    supplier_link: Optional[str] = None
    supplier_rating: float = 0.0
    supplier_reviews: int = 0
    supplier_orders_30d: int = 0
    supplier_processing_days: int = 3
    supplier_shipping_days: int = 15
    product_variants: Optional[List[str]] = None
    # Data source tracking
    data_source: str = "manual"
    data_source_type: str = "manual"
    confidence_score: int = 50
    last_updated: Optional[str] = None
    scores_updated_at: Optional[str] = None
    competitor_last_updated: Optional[str] = None
    ad_activity_last_updated: Optional[str] = None
    supplier_data_updated: Optional[str] = None
    # Legacy fields
    ai_summary: Optional[str] = None
    is_premium: bool = False
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CheckoutSessionRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

class PortalSessionRequest(BaseModel):
    return_url: str

class SubscriptionUpdate(BaseModel):
    new_plan_id: str
    new_price_id: str

class CancelSubscription(BaseModel):
    cancel_at_period_end: bool = True

# Referral System Models
class ReferralCode(BaseModel):
    code: str
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Referral(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referrer_id: str  # User who referred
    referred_id: str  # User who signed up
    referral_code: str
    status: str = "pending"  # pending, verified, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: Optional[datetime] = None

class UserReferralStats(BaseModel):
    user_id: str
    referral_code: str
    total_referrals: int = 0
    verified_referrals: int = 0
    bonus_store_slots: int = 0
    max_bonus_slots: int = 5
    remaining_bonus_capacity: int = 5

class RunAutomationRequest(BaseModel):
    job_type: Optional[AutomationJobType] = AutomationJobType.FULL_PIPELINE
    products: Optional[List[Dict[str, Any]]] = None

# Store Models
class StoreStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    EXPORTED = "exported"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class StoreCreate(BaseModel):
    name: str
    product_id: str  # Product to build store from
    plan: str = "starter"  # User's plan for limit checking

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    headline: Optional[str] = None
    status: Optional[StoreStatus] = None
    branding: Optional[Dict[str, Any]] = None
    faqs: Optional[List[Dict[str, str]]] = None
    policies: Optional[Dict[str, str]] = None

class StoreProductCreate(BaseModel):
    store_id: str
    product_id: str

class StoreProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None

class GenerateStoreRequest(BaseModel):
    product_id: str
    plan: str = "starter"
    store_name: Optional[str] = None  # Optional pre-selected name

class UpdateStoreStatusRequest(BaseModel):
    status: StoreStatus

# =====================
# AUTOMATION LOGIC
# =====================

def calculate_trend_score(product: dict) -> int:
    """Calculate trend score based on product signals"""
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    supplier_cost = product.get('supplier_cost', 0)
    retail_price = product.get('estimated_retail_price', 0)
    
    margin = retail_price - supplier_cost
    
    # TikTok score (35%)
    if tiktok_views >= 50000000:
        tiktok_score = 100
    elif tiktok_views >= 10000000:
        tiktok_score = 80
    elif tiktok_views >= 1000000:
        tiktok_score = 60
    elif tiktok_views >= 100000:
        tiktok_score = 40
    else:
        tiktok_score = min(40, (tiktok_views / 100000) * 40)
    
    # Ad count score (20%)
    if ad_count == 0:
        ad_score = 30
    elif ad_count < 50:
        ad_score = 60
    elif ad_count < 200:
        ad_score = 100
    elif ad_count < 500:
        ad_score = 70
    else:
        ad_score = 40
    
    # Competition score (20%)
    competition_scores = {'low': 100, 'medium': 60, 'high': 30}
    competition_score = competition_scores.get(competition_level, 50)
    
    # Margin score (25%)
    if margin >= 50:
        margin_score = 100
    elif margin >= 25:
        margin_score = 80
    elif margin >= 10:
        margin_score = 60
    elif margin > 0:
        margin_score = 40
    else:
        margin_score = 0
    
    # Weighted average
    weighted_score = (
        tiktok_score * 0.35 +
        ad_score * 0.20 +
        competition_score * 0.20 +
        margin_score * 0.25
    )
    
    return min(100, max(0, round(weighted_score)))

def calculate_trend_stage(product: dict) -> str:
    """Calculate trend stage based on signals"""
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    
    signals = {'early': 0, 'rising': 0, 'peak': 0, 'saturated': 0}
    
    # Views signal
    if tiktok_views >= 30000000:
        signals['peak'] += 40
    elif tiktok_views >= 5000000:
        signals['rising'] += 40
    elif tiktok_views >= 500000:
        signals['rising'] += 40
    else:
        signals['early'] += 40
    
    # Ad count signal
    if ad_count >= 400:
        signals['saturated'] += 35
    elif ad_count >= 200:
        signals['peak'] += 35
    elif ad_count >= 50:
        signals['rising'] += 35
    else:
        signals['early'] += 35
    
    # Competition signal
    if competition_level == 'high':
        signals['saturated'] += 25
    elif competition_level == 'medium':
        signals['rising'] += 25
    else:
        signals['early'] += 25
    
    return max(signals, key=signals.get)

def calculate_opportunity_rating(product: dict) -> str:
    """Calculate opportunity rating"""
    trend_score = product.get('trend_score', 0)
    supplier_cost = product.get('supplier_cost', 0)
    retail_price = product.get('estimated_retail_price', 0)
    competition_level = product.get('competition_level', 'medium')
    trend_stage = product.get('trend_stage', 'rising')
    
    margin = retail_price - supplier_cost
    margin_percent = (margin / retail_price * 100) if retail_price > 0 else 0
    
    score = 0
    
    # Trend score (40%)
    score += (trend_score / 100) * 40
    
    # Margin (25%)
    margin_score = 0
    if margin >= 50:
        margin_score += 50
    elif margin >= 25:
        margin_score += 40
    elif margin >= 15:
        margin_score += 30
    else:
        margin_score += 20
    
    if margin_percent >= 70:
        margin_score += 50
    elif margin_percent >= 50:
        margin_score += 40
    elif margin_percent >= 30:
        margin_score += 30
    else:
        margin_score += 20
    
    score += (margin_score / 100) * 25
    
    # Competition (20%)
    comp_scores = {'low': 100, 'medium': 60, 'high': 25}
    score += (comp_scores.get(competition_level, 50) / 100) * 20
    
    # Stage (15%)
    stage_scores = {'early': 100, 'rising': 85, 'peak': 50, 'saturated': 15}
    score += (stage_scores.get(trend_stage, 50) / 100) * 15
    
    # Bonuses
    if trend_score >= 80 and competition_level == 'low' and trend_stage == 'early':
        score += 10
    if trend_stage == 'rising' and margin_percent >= 50:
        score += 5
    if trend_stage == 'saturated' and competition_level == 'high':
        score -= 10
    
    score = min(100, max(0, score))
    
    if score >= 85:
        return 'very high'
    elif score >= 70:
        return 'high'
    elif score >= 50:
        return 'medium'
    return 'low'

def generate_ai_summary(product: dict) -> str:
    """Generate AI-style summary for product"""
    opportunity = product.get('opportunity_rating', 'medium')
    trend_score = product.get('trend_score', 50)
    stage = product.get('trend_stage', 'rising')
    competition = product.get('competition_level', 'medium')
    category = product.get('category', 'General')
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    early_trend_label = product.get('early_trend_label', 'stable')
    _ = stage  # Used in category insights
    
    # Add early trend context
    early_trend_context = ""
    if early_trend_label == 'exploding':
        early_trend_context = "🔥 EXPLODING - Extremely rapid growth detected. "
    elif early_trend_label == 'rising':
        early_trend_context = "📈 Rising fast with strong momentum. "
    elif early_trend_label == 'early_trend':
        early_trend_context = "🌱 Early trend indicators detected. "
    
    templates = {
        'very high': f"{early_trend_context}Exceptional viral potential with {competition} current competition. Strong TikTok presence driving consumer awareness. Perfect for content creators and lifestyle consumers. Act fast before market saturation.",
        'high': f"{early_trend_context}Solid opportunity with growing demand. {'Strong' if trend_score >= 80 else 'Building'} TikTok presence. {'Low advertiser activity creates favorable entry conditions.' if competition == 'low' else 'Moderate competition requires clear value proposition.'} Good time to test with controlled ad spend.",
        'medium': f"{early_trend_context}Moderate opportunity requiring differentiation. {'Market is getting competitive' if competition == 'high' else 'Some competition present'}. {'Moderate margins provide room for competitive pricing.' if margin >= 15 else 'Thin margins demand high volume strategy.'} Proceed with caution.",
        'low': f"Challenging market conditions. {'Crowded market demands strong differentiation.' if competition == 'high' else 'Limited market validation.'} Consider alternative products or unique angle.",
    }
    
    base = templates.get(opportunity, templates['medium'])
    
    # Add category insight
    category_insights = {
        'Electronics': 'Tech products benefit from early review content.',
        'Home Decor': 'Visual content performs well in this category.',
        'Fashion': 'Influencer seeding highly effective.',
        'Health & Fitness': 'Before/after content drives sales.',
    }
    
    insight = category_insights.get(category, '')
    return f"{base} {insight}".strip()


def calculate_early_trend_score(product: dict) -> tuple:
    """
    Calculate early trend score (0-100) based on acceleration signals.
    Returns (score, label) tuple.
    
    Signals:
    - View growth velocity (25%): How fast views are growing
    - Engagement rate (20%): User interaction level
    - Supplier order velocity (20%): Rising supplier demand
    - Ad activity level (20%): Early advertiser interest
    - Competition level (15%): Room for entry
    """
    # Get product metrics
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    view_growth_rate = product.get('view_growth_rate', 0)
    engagement_rate = product.get('engagement_rate', 0)
    supplier_order_velocity = product.get('supplier_order_velocity', 0)
    trend_stage = product.get('trend_stage', 'rising')
    
    # 1. View Growth Velocity Score (25%) - High growth = early trend
    if view_growth_rate >= 200:  # 200%+ growth
        growth_score = 100
    elif view_growth_rate >= 100:  # 100-200% growth
        growth_score = 85
    elif view_growth_rate >= 50:  # 50-100% growth
        growth_score = 70
    elif view_growth_rate >= 25:  # 25-50% growth
        growth_score = 55
    elif view_growth_rate >= 10:  # 10-25% growth
        growth_score = 40
    else:
        growth_score = max(0, view_growth_rate * 4)
    
    # 2. Engagement Rate Score (20%) - High engagement = viral potential
    if engagement_rate >= 15:  # 15%+ engagement
        engagement_score = 100
    elif engagement_rate >= 10:
        engagement_score = 85
    elif engagement_rate >= 5:
        engagement_score = 65
    elif engagement_rate >= 2:
        engagement_score = 45
    else:
        engagement_score = engagement_rate * 22.5
    
    # 3. Supplier Order Velocity Score (20%) - Rising orders = demand signal
    if supplier_order_velocity >= 500:  # 500+ orders/week
        supplier_score = 100
    elif supplier_order_velocity >= 200:
        supplier_score = 85
    elif supplier_order_velocity >= 100:
        supplier_score = 70
    elif supplier_order_velocity >= 50:
        supplier_score = 55
    elif supplier_order_velocity >= 20:
        supplier_score = 40
    else:
        supplier_score = supplier_order_velocity * 2
    
    # 4. Ad Activity Score (20%) - Sweet spot is medium activity (not saturated)
    # Low ads = early opportunity, Medium = validation, High = saturated
    if ad_count == 0:
        ad_activity_score = 60  # Very early, unvalidated
    elif ad_count < 30:
        ad_activity_score = 100  # Perfect early window
    elif ad_count < 80:
        ad_activity_score = 90  # Still early
    elif ad_count < 150:
        ad_activity_score = 70  # Getting competitive
    elif ad_count < 300:
        ad_activity_score = 45  # Competitive
    else:
        ad_activity_score = 20  # Saturated
    
    # 5. Competition Score (15%) - Low competition = better opportunity
    competition_scores = {'low': 100, 'medium': 55, 'high': 15}
    competition_score = competition_scores.get(competition_level, 50)
    
    # Bonus for early stage products with high views
    stage_bonus = 0
    if trend_stage == 'early' and tiktok_views >= 100000:
        stage_bonus = 10
    elif trend_stage == 'rising' and ad_count < 100:
        stage_bonus = 5
    
    # Calculate weighted score
    early_trend_score = (
        growth_score * 0.25 +
        engagement_score * 0.20 +
        supplier_score * 0.20 +
        ad_activity_score * 0.20 +
        competition_score * 0.15 +
        stage_bonus
    )
    
    early_trend_score = min(100, max(0, round(early_trend_score)))
    
    # Determine label
    if early_trend_score >= 85:
        label = 'exploding'
    elif early_trend_score >= 65:
        label = 'rising'
    elif early_trend_score >= 45:
        label = 'early_trend'
    else:
        label = 'stable'
    
    return early_trend_score, label


def should_generate_early_trend_alert(product: dict) -> bool:
    """Check if product qualifies for early trend alert"""
    early_trend_score = product.get('early_trend_score', 0)
    early_trend_label = product.get('early_trend_label', 'stable')
    return early_trend_score >= 70 or early_trend_label in ['exploding', 'rising']


# =====================
# MARKET INTELLIGENCE
# =====================

def calculate_market_score(product: dict) -> tuple:
    """
    Calculate market opportunity score (0-100) combining demand, margin, and competition.
    Returns (market_score, market_label, score_breakdown)
    
    Components:
    - Demand Score (35%): Based on TikTok views, engagement, trend velocity
    - Margin Score (35%): Based on estimated margin and margin percentage
    - Competition Score (30%): Based on active stores, ad activity, saturation
    """
    # Get product metrics
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    estimated_margin = product.get('estimated_margin', 0)
    estimated_retail_price = product.get('estimated_retail_price', 0)
    trend_score = product.get('trend_score', 0)
    early_trend_score = product.get('early_trend_score', 0)
    active_competitor_stores = product.get('active_competitor_stores', 0)
    market_saturation = product.get('market_saturation', 0)
    
    # Calculate margin percentage
    margin_percent = (estimated_margin / estimated_retail_price * 100) if estimated_retail_price > 0 else 0
    
    # 1. Demand Score (35%) - Market interest and momentum
    demand_signals = 0
    
    # TikTok views signal (40% of demand)
    if tiktok_views >= 50000000:
        views_score = 100
    elif tiktok_views >= 10000000:
        views_score = 85
    elif tiktok_views >= 1000000:
        views_score = 70
    elif tiktok_views >= 100000:
        views_score = 50
    else:
        views_score = min(50, (tiktok_views / 100000) * 50)
    
    demand_signals += views_score * 0.40
    
    # Trend momentum (40% of demand)
    combined_trend = (trend_score + early_trend_score) / 2
    demand_signals += combined_trend * 0.40
    
    # Ad activity as demand validation (20% of demand)
    if ad_count == 0:
        ad_demand_score = 30  # Unvalidated
    elif ad_count < 50:
        ad_demand_score = 70  # Early validation
    elif ad_count < 150:
        ad_demand_score = 100  # Strong validation
    elif ad_count < 300:
        ad_demand_score = 80  # Good demand
    else:
        ad_demand_score = 60  # Saturated but proven
    
    demand_signals += ad_demand_score * 0.20
    demand_score = min(100, demand_signals)
    
    # 2. Margin Score (35%) - Profit potential
    margin_signals = 0
    
    # Absolute margin (60% of margin score)
    if estimated_margin >= 40:
        abs_margin_score = 100
    elif estimated_margin >= 30:
        abs_margin_score = 85
    elif estimated_margin >= 20:
        abs_margin_score = 70
    elif estimated_margin >= 15:
        abs_margin_score = 55
    elif estimated_margin >= 10:
        abs_margin_score = 40
    else:
        abs_margin_score = max(0, estimated_margin * 4)
    
    margin_signals += abs_margin_score * 0.60
    
    # Margin percentage (40% of margin score)
    if margin_percent >= 70:
        pct_margin_score = 100
    elif margin_percent >= 50:
        pct_margin_score = 85
    elif margin_percent >= 35:
        pct_margin_score = 70
    elif margin_percent >= 25:
        pct_margin_score = 55
    else:
        pct_margin_score = max(0, margin_percent * 2.2)
    
    margin_signals += pct_margin_score * 0.40
    margin_score = min(100, margin_signals)
    
    # 3. Competition Score (30%) - Market accessibility
    competition_signals = 0
    
    # Active competitor stores (40% of competition)
    if active_competitor_stores == 0:
        stores_score = 90  # Blue ocean
    elif active_competitor_stores < 10:
        stores_score = 100  # Low competition, validated
    elif active_competitor_stores < 30:
        stores_score = 75  # Moderate competition
    elif active_competitor_stores < 60:
        stores_score = 50  # Getting crowded
    elif active_competitor_stores < 100:
        stores_score = 30  # High competition
    else:
        stores_score = 15  # Very saturated
    
    competition_signals += stores_score * 0.40
    
    # Competition level (30% of competition)
    comp_level_scores = {'low': 100, 'medium': 60, 'high': 25}
    competition_signals += comp_level_scores.get(competition_level, 50) * 0.30
    
    # Market saturation (30% of competition)
    saturation_score = max(0, 100 - market_saturation)
    competition_signals += saturation_score * 0.30
    
    competition_score = min(100, competition_signals)
    
    # Calculate final weighted score
    market_score = (
        demand_score * 0.35 +
        margin_score * 0.35 +
        competition_score * 0.30
    )
    
    market_score = min(100, max(0, round(market_score)))
    
    # Determine label
    if market_score >= 80:
        market_label = 'high'
    elif market_score >= 60:
        market_label = 'medium'
    elif market_score >= 40:
        market_label = 'low'
    else:
        market_label = 'very_low'
    
    # Build breakdown for UI
    score_breakdown = {
        'demand': round(demand_score),
        'margin': round(margin_score),
        'competition': round(competition_score),
        'ad_activity': ad_demand_score,
    }
    
    return market_score, market_label, score_breakdown


def generate_mock_competitor_data(product: dict) -> dict:
    """
    Generate simulated competitor data for a product.
    This is designed to be replaced with real data sources later.
    
    Returns competitor intelligence including:
    - active_competitor_stores: Number of stores selling this product
    - avg_selling_price: Average market price
    - price_range: Min/max prices found
    - estimated_ad_spend: Monthly ad activity estimate
    - market_saturation: Saturation percentage (0-100)
    - competitor_stores: List of simulated competitor stores
    """
    import random
    
    # Use product signals to generate realistic competitor data
    ad_count = product.get('ad_count', 0)
    trend_score = product.get('trend_score', 0)
    competition_level = product.get('competition_level', 'medium')
    estimated_retail_price = product.get('estimated_retail_price', 0)
    supplier_cost = product.get('supplier_cost', 0)
    category = product.get('category', 'General')
    
    # Base competitor count on ad activity and competition level
    base_stores = {
        'low': random.randint(3, 15),
        'medium': random.randint(15, 45),
        'high': random.randint(45, 120),
    }
    active_stores = base_stores.get(competition_level, 25)
    
    # Adjust based on ad count
    if ad_count > 200:
        active_stores = int(active_stores * 1.5)
    elif ad_count < 30:
        active_stores = int(active_stores * 0.6)
    
    # Generate price variations
    price_variation = estimated_retail_price * 0.25
    min_price = max(supplier_cost + 5, estimated_retail_price - price_variation)
    max_price = estimated_retail_price + price_variation
    avg_price = estimated_retail_price + random.uniform(-5, 10)
    
    # Calculate market saturation
    saturation_base = {
        'low': random.randint(15, 35),
        'medium': random.randint(35, 60),
        'high': random.randint(60, 90),
    }
    market_saturation = saturation_base.get(competition_level, 45)
    
    # Adjust saturation based on trend stage
    trend_stage = product.get('trend_stage', 'rising')
    if trend_stage == 'saturated':
        market_saturation = min(95, market_saturation + 20)
    elif trend_stage == 'early':
        market_saturation = max(10, market_saturation - 20)
    
    # Estimate ad spend based on ad count
    estimated_monthly_ad_spend = ad_count * random.randint(80, 200)  # GBP estimate
    
    # Generate mock competitor stores
    store_name_prefixes = ['Quick', 'Best', 'Top', 'Premium', 'Smart', 'Value', 'Direct', 'Pro', 'Elite', 'Super']
    store_name_suffixes = ['Shop', 'Store', 'Market', 'Deals', 'Hub', 'Zone', 'Express', 'Outlet', 'Central', 'Direct']
    
    competitor_stores = []
    num_visible_stores = min(10, active_stores)  # Show up to 10 competitor stores
    
    for i in range(num_visible_stores):
        store_price = round(random.uniform(min_price, max_price), 2)
        has_ads = random.random() < 0.6  # 60% have active ads
        
        competitor_stores.append({
            'id': f'comp_{product.get("id", "unknown")}_{i}',
            'name': f'{random.choice(store_name_prefixes)}{random.choice(store_name_suffixes)}',
            'price': store_price,
            'currency': 'GBP',
            'has_active_ads': has_ads,
            'estimated_monthly_sales': random.randint(10, 200) if has_ads else random.randint(5, 50),
            'rating': round(random.uniform(3.5, 5.0), 1),
            'reviews_count': random.randint(10, 500),
            'last_seen': datetime.now(timezone.utc).isoformat(),
        })
    
    # Sort by price
    competitor_stores.sort(key=lambda x: x['price'])
    
    return {
        'active_competitor_stores': active_stores,
        'avg_selling_price': round(avg_price, 2),
        'price_range': {
            'min': round(min_price, 2),
            'max': round(max_price, 2),
        },
        'estimated_monthly_ad_spend': estimated_monthly_ad_spend,
        'market_saturation': market_saturation,
        'competitor_stores': competitor_stores,
        'data_freshness': datetime.now(timezone.utc).isoformat(),
        'data_source': 'simulated',  # Will be 'live' when real data is integrated
    }


def calculate_success_probability(product: dict) -> tuple:
    """
    Calculate success probability (0-100) based on user actions and performance signals.
    Returns (success_probability, proven_winner, user_engagement_score)
    
    Signals:
    - Stores created (30%): How many users built stores with this product
    - Export count (20%): How many times exported
    - Success signals (20%): Estimated sales/conversion signals
    - Trend metrics (15%): Trend score and early trend score
    - Margin potential (15%): Estimated margin attractiveness
    """
    stores_created = product.get('stores_created', 0)
    exports_count = product.get('exports_count', 0)
    success_signals = product.get('success_signals', 0)
    trend_score = product.get('trend_score', 0)
    early_trend_score = product.get('early_trend_score', 0)
    estimated_margin = product.get('estimated_margin', 0)
    
    # 1. Stores Created Score (30%) - User validation
    if stores_created >= 20:
        stores_score = 100
    elif stores_created >= 10:
        stores_score = 90
    elif stores_created >= 5:
        stores_score = 75
    elif stores_created >= 3:
        stores_score = 60
    elif stores_created >= 1:
        stores_score = 40
    else:
        stores_score = 0
    
    # 2. Export Count Score (20%) - Action signals
    if exports_count >= 15:
        export_score = 100
    elif exports_count >= 8:
        export_score = 85
    elif exports_count >= 4:
        export_score = 70
    elif exports_count >= 2:
        export_score = 50
    elif exports_count >= 1:
        export_score = 30
    else:
        export_score = 0
    
    # 3. Success Signals Score (20%) - Estimated sales/conversions
    if success_signals >= 100:
        success_score = 100
    elif success_signals >= 50:
        success_score = 85
    elif success_signals >= 20:
        success_score = 70
    elif success_signals >= 10:
        success_score = 55
    elif success_signals >= 5:
        success_score = 40
    else:
        success_score = success_signals * 8
    
    # 4. Trend Metrics Score (15%) - Combined trend strength
    combined_trend = (trend_score + early_trend_score) / 2
    trend_metrics_score = min(100, combined_trend)
    
    # 5. Margin Score (15%) - Profit potential
    if estimated_margin >= 40:
        margin_score = 100
    elif estimated_margin >= 30:
        margin_score = 85
    elif estimated_margin >= 20:
        margin_score = 70
    elif estimated_margin >= 15:
        margin_score = 55
    elif estimated_margin >= 10:
        margin_score = 40
    else:
        margin_score = max(0, estimated_margin * 4)
    
    # Calculate weighted score
    success_probability = (
        stores_score * 0.30 +
        export_score * 0.20 +
        success_score * 0.20 +
        trend_metrics_score * 0.15 +
        margin_score * 0.15
    )
    
    success_probability = min(100, max(0, round(success_probability)))
    
    # Calculate user engagement score (for tracking)
    user_engagement_score = round(
        (stores_created * 10 + exports_count * 5 + success_signals * 2) / 3, 1
    )
    
    # Determine if proven winner
    proven_winner = (
        success_probability >= 70 and 
        stores_created >= 3 and 
        (exports_count >= 2 or success_signals >= 10)
    )
    
    return success_probability, proven_winner, user_engagement_score


async def track_product_store_created(product_id: str):
    """Track when a store is created for a product"""
    # Increment stores_created counter
    await db.products.update_one(
        {"id": product_id},
        {
            "$inc": {"stores_created": 1, "success_signals": 1},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    # Recalculate success probability
    await recalculate_product_success(product_id)


async def track_product_exported(product_id: str):
    """Track when a product is exported"""
    # Increment exports_count counter
    await db.products.update_one(
        {"id": product_id},
        {
            "$inc": {"exports_count": 1, "success_signals": 2},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    # Recalculate success probability
    await recalculate_product_success(product_id)


async def recalculate_product_success(product_id: str):
    """Recalculate success probability for a product"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        return
    
    success_probability, proven_winner, user_engagement_score = calculate_success_probability(product)
    
    await db.products.update_one(
        {"id": product_id},
        {
            "$set": {
                "success_probability": success_probability,
                "proven_winner": proven_winner,
                "user_engagement_score": user_engagement_score,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )

def should_generate_alert(product: dict) -> bool:
    """Check if product qualifies for alert"""
    trend_score = product.get('trend_score', 0)
    opportunity = product.get('opportunity_rating', 'low')
    return trend_score >= 75 and opportunity in ['high', 'very high']

def generate_alert(product: dict) -> Optional[dict]:
    """Generate alert for qualifying product"""
    if not should_generate_alert(product):
        return None
    
    trend_stage = product.get('trend_stage', 'rising')
    trend_score = product.get('trend_score', 0)
    opportunity = product.get('opportunity_rating', 'medium')
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    
    # Determine alert type
    if trend_stage == 'early' and trend_score >= 80:
        alert_type = 'early_stage'
        title = f"Early Stage Winner: {product.get('product_name')}"
    elif trend_stage == 'rising':
        alert_type = 'rising_trend'
        title = f"Rising Trend Alert: {product.get('product_name')}"
    elif margin >= 40:
        alert_type = 'high_margin'
        title = f"High Margin Opportunity: {product.get('product_name')}"
    else:
        alert_type = 'new_opportunity'
        title = f"New Opportunity: {product.get('product_name')}"
    
    # Determine priority
    if trend_score >= 90 and opportunity == 'very high':
        priority = 'critical'
    elif trend_score >= 80:
        priority = 'high'
    else:
        priority = 'medium'
    
    return {
        'id': str(uuid.uuid4()),
        'product_id': product.get('id'),
        'product_name': product.get('product_name'),
        'alert_type': alert_type,
        'priority': priority,
        'title': title,
        'body': f"Detected product with {trend_score} trend score and {opportunity} opportunity rating.",
        'trend_score': trend_score,
        'opportunity_rating': opportunity,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'read': False,
        'dismissed': False,
    }

def run_full_automation(product: dict) -> dict:
    """Run full automation pipeline on a product"""
    # Calculate all scores
    trend_stage = calculate_trend_stage(product)
    product['trend_stage'] = trend_stage
    
    trend_score = calculate_trend_score(product)
    product['trend_score'] = trend_score
    
    opportunity_rating = calculate_opportunity_rating(product)
    product['opportunity_rating'] = opportunity_rating
    
    # Calculate early trend score
    early_trend_score, early_trend_label = calculate_early_trend_score(product)
    product['early_trend_score'] = early_trend_score
    product['early_trend_label'] = early_trend_label
    
    ai_summary = generate_ai_summary(product)
    product['ai_summary'] = ai_summary
    
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    product['estimated_margin'] = margin
    
    # Generate competitor/market intelligence (mock data for now)
    competitor_data = generate_mock_competitor_data(product)
    product['active_competitor_stores'] = competitor_data['active_competitor_stores']
    product['avg_selling_price'] = competitor_data['avg_selling_price']
    product['price_range'] = competitor_data['price_range']
    product['estimated_monthly_ad_spend'] = competitor_data['estimated_monthly_ad_spend']
    product['market_saturation'] = competitor_data['market_saturation']
    
    # Calculate market score
    market_score, market_label, score_breakdown = calculate_market_score(product)
    product['market_score'] = market_score
    product['market_label'] = market_label
    product['market_score_breakdown'] = score_breakdown
    
    product['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    # Generate regular alert
    alert = generate_alert(product)
    
    # Generate early trend alert if applicable
    early_alert = generate_early_trend_alert(product)
    
    return {'product': product, 'alert': alert, 'early_alert': early_alert}


def generate_early_trend_alert(product: dict) -> Optional[dict]:
    """Generate alert for early trend detection"""
    if not should_generate_early_trend_alert(product):
        return None
    
    early_trend_score = product.get('early_trend_score', 0)
    early_trend_label = product.get('early_trend_label', 'stable')
    view_growth_rate = product.get('view_growth_rate', 0)
    engagement_rate = product.get('engagement_rate', 0)
    
    # Determine alert type and title based on label
    if early_trend_label == 'exploding':
        alert_type = 'exploding_trend'
        title = f"🔥 EXPLODING: {product.get('product_name')}"
        priority = 'critical'
    elif early_trend_label == 'rising':
        alert_type = 'rising_early_trend'
        title = f"📈 Rising Fast: {product.get('product_name')}"
        priority = 'high'
    else:
        alert_type = 'early_trend_detected'
        title = f"🌱 Early Trend: {product.get('product_name')}"
        priority = 'medium'
    
    body_parts = []
    if view_growth_rate >= 50:
        body_parts.append(f"{view_growth_rate:.0f}% view growth")
    if engagement_rate >= 5:
        body_parts.append(f"{engagement_rate:.1f}% engagement")
    body_parts.append(f"Early trend score: {early_trend_score}")
    
    return {
        'id': str(uuid.uuid4()),
        'product_id': product.get('id'),
        'product_name': product.get('product_name'),
        'alert_type': alert_type,
        'priority': priority,
        'title': title,
        'body': f"Early trend signals detected. {' | '.join(body_parts)}. Act before competition increases.",
        'trend_score': product.get('trend_score', 0),
        'early_trend_score': early_trend_score,
        'early_trend_label': early_trend_label,
        'opportunity_rating': product.get('opportunity_rating', 'medium'),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'read': False,
        'dismissed': False,
    }

# =====================
# ROUTES - Basic API
# =====================

@api_router.get("/")
async def root():
    return {"message": "ViralScout API v1.0.0", "status": "healthy"}

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected"
    }

# =====================
# ROUTES - Automation
# =====================

@automation_router.post("/run")
async def run_automation(request: RunAutomationRequest):
    """Run automation on products"""
    try:
        # Get products from request or database
        if request.products:
            products = request.products
        else:
            cursor = db.products.find({}, {"_id": 0})
            products = await cursor.to_list(1000)
        
        if not products:
            return {"success": True, "message": "No products to process", "processed": 0}
        
        # Create log entry
        log_doc = {
            "id": str(uuid.uuid4()),
            "job_type": request.job_type.value,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "products_processed": 0,
            "alerts_generated": 0,
        }
        await db.automation_logs.insert_one(log_doc)
        
        # Process products
        processed_products = []
        alerts = []
        
        for product in products:
            result = run_full_automation(product)
            processed_products.append(result['product'])
            if result['alert']:
                alerts.append(result['alert'])
            if result.get('early_alert'):
                alerts.append(result['early_alert'])
        
        # Update products in database
        for product in processed_products:
            await db.products.update_one(
                {"id": product['id']},
                {"$set": product},
                upsert=True
            )
        
        # Save alerts
        if alerts:
            await db.trend_alerts.insert_many(alerts)
        
        # Update log
        await db.automation_logs.update_one(
            {"id": log_doc["id"]},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": len(processed_products),
                "alerts_generated": len(alerts),
            }}
        )
        
        return {
            "success": True,
            "processed": len(processed_products),
            "alerts_generated": len(alerts),
            "log_id": log_doc["id"],
        }
        
    except Exception as e:
        logging.error(f"Automation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@automation_router.get("/logs")
async def get_automation_logs(limit: int = 50):
    """Get automation logs"""
    cursor = db.automation_logs.find({}, {"_id": 0}).sort("started_at", -1).limit(limit)
    logs = await cursor.to_list(limit)
    return {"data": logs}

@automation_router.get("/stats")
async def get_automation_stats():
    """Get automation statistics"""
    cursor = db.automation_logs.find({}, {"_id": 0})
    logs = await cursor.to_list(1000)
    
    if not logs:
        return {
            "total_runs": 0,
            "success_rate": 0,
            "products_processed": 0,
            "alerts_generated": 0,
            "last_run": None,
        }
    
    completed = [log for log in logs if log.get('status') == 'completed']
    
    return {
        "total_runs": len(logs),
        "success_rate": round(len(completed) / len(logs) * 100) if logs else 0,
        "products_processed": sum(log.get('products_processed', 0) for log in logs),
        "alerts_generated": sum(log.get('alerts_generated', 0) for log in logs),
        "last_run": logs[0].get('started_at') if logs else None,
    }

@automation_router.post("/scheduled/daily")
async def run_daily_automation(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Run daily scheduled automation.
    Protected endpoint - requires API key for external cron services.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return await run_automation(RunAutomationRequest(job_type=AutomationJobType.SCHEDULED_DAILY))


# =====================
# ROUTES - Data Pipeline
# =====================

@automation_router.post("/pipeline/full")
async def run_full_pipeline(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Run the full data ingestion pipeline.
    Fetches from all sources, updates competitor/ad data, and recalculates scores.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key and api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        from services.pipeline import DataPipeline
        pipeline = DataPipeline(db)
        result = await pipeline.run_full_pipeline()
        
        return {
            "success": result.success,
            "duration_seconds": result.duration_seconds,
            "products_processed": result.products_processed,
            "products_created": result.products_created,
            "products_updated": result.products_updated,
            "alerts_generated": result.alerts_generated,
            "source_results": result.source_results,
            "errors": result.errors if result.errors else None,
        }
    except Exception as e:
        logging.error(f"Pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@automation_router.post("/pipeline/quick-refresh")
async def run_quick_refresh():
    """
    Quick refresh - just update scores and competitor data.
    Faster than full pipeline, skips source fetching.
    """
    try:
        from services.pipeline import DataPipeline
        pipeline = DataPipeline(db)
        result = await pipeline.run_quick_refresh()
        
        return {
            "success": result.success,
            "duration_seconds": result.duration_seconds,
            "products_updated": result.products_updated,
            "errors": result.errors if result.errors else None,
        }
    except Exception as e:
        logging.error(f"Quick refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@automation_router.post("/pipeline/source/{source_name}")
async def run_source_pipeline(source_name: str):
    """
    Run pipeline for a specific data source.
    Valid sources: tiktok, amazon, aliexpress, cj_dropshipping
    """
    valid_sources = ['tiktok', 'amazon', 'aliexpress', 'cj_dropshipping']
    if source_name not in valid_sources:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid source. Must be one of: {', '.join(valid_sources)}"
        )
    
    try:
        from services.pipeline import DataPipeline
        pipeline = DataPipeline(db)
        result = await pipeline.run_source_only(source_name)
        
        return {
            "success": result.success,
            "source": source_name,
            "duration_seconds": result.duration_seconds,
            "products_created": result.products_created,
            "products_updated": result.products_updated,
            "source_results": result.source_results.get(source_name, {}),
            "errors": result.errors if result.errors else None,
        }
    except Exception as e:
        logging.error(f"Source pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@automation_router.get("/pipeline/status")
async def get_pipeline_status():
    """
    Get status of data sources and pipeline health.
    """
    # Get latest pipeline runs
    cursor = db.automation_logs.find(
        {"job_type": "full_pipeline"},
        {"_id": 0}
    ).sort("started_at", -1).limit(5)
    recent_runs = await cursor.to_list(5)
    
    # Get product counts
    total_products = await db.products.count_documents({})
    products_with_scores = await db.products.count_documents({"market_score": {"$gte": 0}})
    high_opportunity = await db.products.count_documents({"market_label": {"$in": ["massive", "strong"]}})
    
    # Get data freshness
    latest_product = await db.products.find_one({}, {"_id": 0, "last_updated": 1}, sort=[("last_updated", -1)])
    
    return {
        "pipeline_health": "healthy" if recent_runs and recent_runs[0].get("success") else "unknown",
        "last_run": recent_runs[0] if recent_runs else None,
        "recent_runs": recent_runs,
        "product_stats": {
            "total": total_products,
            "with_scores": products_with_scores,
            "high_opportunity": high_opportunity,
        },
        "data_freshness": latest_product.get("last_updated") if latest_product else None,
        "sources": {
            "tiktok_trends": {"status": "simulated", "description": "Curated trending products"},
            "amazon_trends": {"status": "simulated", "description": "BSR movers data"},
            "aliexpress_products": {"status": "simulated", "description": "Supplier pricing"},
            "cj_dropshipping": {"status": "simulated", "description": "Fast shipping suppliers"},
            "competitor_intelligence": {"status": "estimated", "description": "Store count estimates"},
            "ad_activity": {"status": "estimated", "description": "Ad spend estimates"},
        }
    }


# =====================
# ROUTES - Background Jobs
# =====================

@jobs_router.get("/status")
async def get_jobs_status():
    """
    Get overall status of the background job system.
    Shows worker status, scheduler status, and queue statistics.
    """
    try:
        from services.jobs.queue import JobQueue
        from services.jobs.worker import WorkerManager
        from services.jobs.scheduler import SchedulerManager
        from services.jobs.tasks import TaskRegistry
        
        queue = JobQueue(db)
        queue_stats = await queue.get_queue_stats()
        
        worker_manager = WorkerManager.get_instance()
        scheduler_manager = SchedulerManager.get_instance()
        
        return {
            "worker": worker_manager.get_status(),
            "scheduler": scheduler_manager.get_status(),
            "queue": queue_stats,
            "available_tasks": TaskRegistry.get_all_tasks(),
        }
    except Exception as e:
        logging.error(f"Jobs status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.get("/history")
async def get_job_history(
    job_type: Optional[str] = None,
    limit: int = 50
):
    """
    Get job execution history.
    Shows completed, failed, and running jobs.
    """
    try:
        from services.jobs.queue import JobQueue
        
        queue = JobQueue(db)
        jobs = await queue.get_job_history(job_type=job_type, limit=limit)
        
        return {
            "jobs": [j.to_dict() for j in jobs],
            "count": len(jobs),
        }
    except Exception as e:
        logging.error(f"Job history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.get("/running")
async def get_running_jobs():
    """Get currently running jobs"""
    try:
        from services.jobs.queue import JobQueue
        
        queue = JobQueue(db)
        running = await queue.get_running_jobs()
        pending = await queue.get_pending_jobs(limit=20)
        
        return {
            "running": [j.to_dict() for j in running],
            "pending": [j.to_dict() for j in pending],
            "running_count": len(running),
            "pending_count": len(pending),
        }
    except Exception as e:
        logging.error(f"Running jobs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.get("/{job_id}")
async def get_job_details(job_id: str):
    """Get details of a specific job"""
    try:
        from services.jobs.queue import JobQueue
        
        queue = JobQueue(db)
        job = await queue.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Job details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.post("/trigger/{task_name}")
async def trigger_job(
    task_name: str,
    params: Optional[Dict[str, Any]] = None
):
    """
    Manually trigger a background job.
    
    Available tasks:
    - ingest_trending_products
    - update_market_scores
    - update_competitor_data
    - update_ad_activity
    - update_supplier_data
    - generate_alerts
    - full_pipeline
    - cleanup_stale_jobs
    """
    try:
        from services.jobs.queue import JobQueue, TriggerSource
        from services.jobs.tasks import TaskRegistry
        
        # Validate task exists
        available_tasks = TaskRegistry.get_all_tasks()
        if task_name not in available_tasks:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown task: {task_name}. Available: {list(available_tasks.keys())}"
            )
        
        queue = JobQueue(db)
        job = await queue.enqueue(
            job_type=task_name,
            trigger_source=TriggerSource.MANUAL,
            params=params or {},
            allow_duplicate=False
        )
        
        if job:
            return {
                "success": True,
                "message": f"Job {task_name} enqueued",
                "job_id": job.id,
                "status": job.status.value,
            }
        else:
            return {
                "success": False,
                "message": f"Job {task_name} already running or pending",
                "job_id": None,
            }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Trigger job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a pending job"""
    try:
        from services.jobs.queue import JobQueue
        
        queue = JobQueue(db)
        cancelled = await queue.cancel(job_id)
        
        if cancelled:
            return {"success": True, "message": "Job cancelled"}
        else:
            return {"success": False, "message": "Job not found or already running"}
    except Exception as e:
        logging.error(f"Cancel job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.get("/scheduled/list")
async def get_scheduled_jobs():
    """Get all scheduled jobs with their next run times"""
    try:
        from services.jobs.scheduler import SchedulerManager
        
        scheduler_manager = SchedulerManager.get_instance()
        if scheduler_manager.scheduler:
            return {
                "scheduled_jobs": scheduler_manager.scheduler.get_scheduled_jobs(),
                "scheduler_running": scheduler_manager.get_status()['running'],
            }
        else:
            return {
                "scheduled_jobs": [],
                "scheduler_running": False,
            }
    except Exception as e:
        logging.error(f"Scheduled jobs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.post("/scheduled/{task_name}/pause")
async def pause_scheduled_job(task_name: str):
    """Pause a scheduled job"""
    try:
        from services.jobs.scheduler import SchedulerManager
        
        scheduler_manager = SchedulerManager.get_instance()
        if scheduler_manager.scheduler:
            paused = scheduler_manager.scheduler.pause_job(task_name)
            if paused:
                return {"success": True, "message": f"Scheduled job {task_name} paused"}
        
        return {"success": False, "message": f"Scheduled job {task_name} not found"}
    except Exception as e:
        logging.error(f"Pause job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.post("/scheduled/{task_name}/resume")
async def resume_scheduled_job(task_name: str):
    """Resume a paused scheduled job"""
    try:
        from services.jobs.scheduler import SchedulerManager
        
        scheduler_manager = SchedulerManager.get_instance()
        if scheduler_manager.scheduler:
            resumed = scheduler_manager.scheduler.resume_job(task_name)
            if resumed:
                return {"success": True, "message": f"Scheduled job {task_name} resumed"}
        
        return {"success": False, "message": f"Scheduled job {task_name} not found"}
    except Exception as e:
        logging.error(f"Resume job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# ROUTES - Viral Growth & Referrals
# =====================

def generate_referral_code(user_id: str) -> str:
    """Generate a unique referral code for a user"""
    import hashlib
    hash_input = f"{user_id}:{datetime.now(timezone.utc).timestamp()}"
    return f"VS{hashlib.sha256(hash_input.encode()).hexdigest()[:8].upper()}"


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
        "margin_range": _get_margin_range(product.get("estimated_margin", 0)),
        "has_supplier_data": bool(product.get("supplier_cost")),
        "has_competitor_data": bool(product.get("active_competitor_stores")),
        # Metadata
        "is_partial": True,
        "signup_cta": "Sign up to unlock full insights and build your store",
    }
    
    return public_data


def _get_margin_range(margin: float) -> str:
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
            "margin_range": _get_margin_range(product.get("estimated_margin", 0)),
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
            "name": "ViralScout",
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
    
    share_text = f"🔥 {product['product_name']} - {market_info.get(market_label, 'Strong')}!\n\n"
    share_text += f"📊 Market Score: {product.get('market_score', 0)}/100\n"
    share_text += f"📈 Trend: {product.get('trend_stage', 'rising').title()}\n"
    share_text += f"💰 Margin: {_get_margin_range(product.get('estimated_margin', 0))}\n\n"
    share_text += "Find more winning products on ViralScout 🚀"
    
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
            "margin_range": _get_margin_range(product.get("estimated_margin", 0)),
            "category": product.get("category"),
            "image_url": product.get("image_url"),
            "early_trend_label": product.get("early_trend_label"),
        },
        "branding": {
            "name": "ViralScout",
            "tagline": "Find winning products before they go viral",
            "url": "viralscout.com",
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
# ROUTES - Stripe
# =====================

@stripe_router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Create Stripe checkout session for authenticated user"""
    user_id = current_user.user_id
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        # Demo mode - return mock session
        return {
            "url": request.success_url,
            "session_id": f"cs_demo_{uuid.uuid4()}",
            "demo_mode": True,
        }
    
    try:
        import stripe
        stripe.api_key = stripe_key
        
        # Get or create customer
        customer = await get_or_create_stripe_customer(user_id)
        
        session = stripe.checkout.Session.create(
            customer=customer['id'],
            payment_method_types=['card'],
            line_items=[{
                'price': request.price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={'user_id': user_id},
        )
        
        return {"url": session.url, "session_id": session.id}
        
    except Exception as e:
        logging.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@stripe_router.post("/create-portal-session")
async def create_portal_session(
    request: PortalSessionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Create Stripe customer portal session for authenticated user"""
    user_id = current_user.user_id
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        return {"url": request.return_url, "demo_mode": True}
    
    try:
        import stripe
        stripe.api_key = stripe_key
        
        # Get customer
        customer = await get_stripe_customer(user_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        session = stripe.billing_portal.Session.create(
            customer=customer['stripe_customer_id'],
            return_url=request.return_url,
        )
        
        return {"url": session.url}
        
    except Exception as e:
        logging.error(f"Stripe portal error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@stripe_router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not stripe_key or not webhook_secret:
        return {"received": True, "demo_mode": True}
    
    try:
        import stripe
        stripe.api_key = stripe_key
        
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        
        # Handle events
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            await handle_checkout_completed(session)
            
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            await handle_subscription_updated(subscription)
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            await handle_subscription_deleted(subscription)
            
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            await handle_payment_failed(invoice)
        
        return {"received": True}
        
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@stripe_router.post("/cancel-subscription")
async def cancel_subscription(
    request: CancelSubscription,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Cancel authenticated user's subscription"""
    user_id = current_user.user_id
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        # Demo mode
        return {"cancelled": True, "demo_mode": True}
    
    try:
        import stripe
        stripe.api_key = stripe_key
        
        # Get subscription
        sub = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
        if not sub or not sub.get('stripe_subscription_id'):
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        if request.cancel_at_period_end:
            stripe.Subscription.modify(
                sub['stripe_subscription_id'],
                cancel_at_period_end=True
            )
        else:
            stripe.Subscription.delete(sub['stripe_subscription_id'])
        
        return {"cancelled": True}
        
    except Exception as e:
        logging.error(f"Cancel error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Stripe helper functions
async def get_or_create_stripe_customer(user_id: str):
    """Get or create Stripe customer for user"""
    existing = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
    
    if existing and existing.get('stripe_customer_id'):
        return {'id': existing['stripe_customer_id']}
    
    import stripe
    
    # Get user email from profiles
    profile = await db.profiles.find_one({"id": user_id}, {"_id": 0})
    email = profile.get('email') if profile else f"user_{user_id}@viralscout.com"
    
    customer = stripe.Customer.create(
        email=email,
        metadata={'user_id': user_id}
    )
    
    # Store customer ID
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {"$set": {"stripe_customer_id": customer.id}},
        upsert=True
    )
    
    return {'id': customer.id}

async def get_stripe_customer(user_id: str):
    """Get Stripe customer for user"""
    return await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})

async def handle_checkout_completed(session):
    """Handle successful checkout"""
    user_id = session['metadata'].get('user_id')
    subscription_id = session.get('subscription')
    customer_id = session.get('customer')
    
    if not user_id:
        return
    
    # Determine plan from price
    import stripe
    sub = stripe.Subscription.retrieve(subscription_id)
    price_id = sub['items']['data'][0]['price']['id']
    
    plan_map = {
        os.environ.get('STRIPE_PRO_PRICE_ID', ''): 'pro',
        os.environ.get('STRIPE_ELITE_PRICE_ID', ''): 'elite',
    }
    plan_name = plan_map.get(price_id, 'pro')
    
    # Update subscription
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "plan_name": plan_name,
            "status": "active",
            "stripe_subscription_id": subscription_id,
            "stripe_customer_id": customer_id,
            "current_period_start": datetime.now(timezone.utc).isoformat(),
            "current_period_end": datetime.fromtimestamp(sub['current_period_end'], tz=timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )
    
    # Update profile plan
    await db.profiles.update_one(
        {"id": user_id},
        {"$set": {"plan": plan_name}}
    )

async def handle_subscription_updated(subscription):
    """Handle subscription update"""
    customer_id = subscription['customer']
    
    sub_doc = await db.subscriptions.find_one({"stripe_customer_id": customer_id}, {"_id": 0})
    if not sub_doc:
        return
    
    status = subscription['status']
    
    await db.subscriptions.update_one(
        {"stripe_customer_id": customer_id},
        {"$set": {
            "status": status,
            "cancel_at_period_end": subscription.get('cancel_at_period_end', False),
            "current_period_end": datetime.fromtimestamp(subscription['current_period_end'], tz=timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

async def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    customer_id = subscription['customer']
    
    sub_doc = await db.subscriptions.find_one({"stripe_customer_id": customer_id}, {"_id": 0})
    if not sub_doc:
        return
    
    await db.subscriptions.update_one(
        {"stripe_customer_id": customer_id},
        {"$set": {
            "status": "canceled",
            "plan_name": "starter",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    
    # Downgrade profile
    await db.profiles.update_one(
        {"id": sub_doc['user_id']},
        {"$set": {"plan": "starter"}}
    )

async def handle_payment_failed(invoice):
    """Handle failed payment"""
    customer_id = invoice['customer']
    
    await db.subscriptions.update_one(
        {"stripe_customer_id": customer_id},
        {"$set": {
            "status": "past_due",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

# =====================
# PRODUCTS API
# =====================

@api_router.get("/products")
async def get_products(
    category: Optional[str] = None,
    trend_stage: Optional[str] = None,
    opportunity_rating: Optional[str] = None,
    early_trend_label: Optional[str] = None,
    market_label: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "trend_score",
    sort_order: str = "desc",
    limit: int = 100,
    include_integrity: bool = False  # Include data integrity metadata
):
    """Get products with filtering and optional data integrity metadata"""
    query = {}
    
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
    avg_confidence = sum(p.get("confidence_score", 0) for p in products) / len(products) if products else 0
    
    return {
        "data": products,
        "metadata": {
            "total_count": len(products),
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
async def mark_alert_read(alert_id: str):
    """Mark alert as read"""
    await db.trend_alerts.update_one({"id": alert_id}, {"$set": {"read": True}})
    return {"success": True}

@api_router.put("/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str):
    """Dismiss alert"""
    await db.trend_alerts.update_one({"id": alert_id}, {"$set": {"dismissed": True}})
    return {"success": True}

# =====================
# DATA INGESTION ROUTES
# =====================

# Import data ingestion services
import sys
sys.path.insert(0, str(ROOT_DIR / 'services'))
from data_ingestion.tiktok_import import TikTokImporter
from data_ingestion.amazon_import import AmazonImporter
from data_ingestion.supplier_import import SupplierImporter

class ImportRequest(BaseModel):
    category: Optional[str] = None
    limit: int = 20

class CSVImportRequest(BaseModel):
    csv_content: str

class JSONImportRequest(BaseModel):
    json_content: str

@ingestion_router.get("/sources")
async def get_data_sources():
    """Get available data sources and their status"""
    tiktok = TikTokImporter(db)
    amazon = AmazonImporter(db)
    supplier = SupplierImporter(db)
    
    return {
        "sources": [
            {
                "id": "tiktok",
                "name": "TikTok Creative Center",
                "description": "Trending products from TikTok viral content",
                "config": tiktok.get_source_config(),
                "status": "active",
            },
            {
                "id": "amazon",
                "name": "Amazon Movers & Shakers",
                "description": "Fast-rising products from Amazon rankings",
                "config": amazon.get_source_config(),
                "status": "active",
            },
            {
                "id": "supplier",
                "name": "Supplier Feeds",
                "description": "Products from AliExpress, CJ Dropshipping, etc.",
                "config": supplier.get_source_config(),
                "status": "active",
            },
        ]
    }

@ingestion_router.post("/tiktok")
async def run_tiktok_import(request: ImportRequest):
    """Import trending products from TikTok"""
    # Create automation log
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "tiktok_import",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "tiktok",
    }
    await db.automation_logs.insert_one(log)
    
    try:
        importer = TikTokImporter(db)
        result = await importer.import_products(
            category=request.category,
            limit=request.limit
        )
        
        # Clean _id from products
        if result.get('products'):
            for p in result['products']:
                p.pop('_id', None)
            automation_result = await run_automation_on_products(result['products'])
            result['automation'] = automation_result
        
        # Update log
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": result.get('inserted', 0) + result.get('updated', 0),
                "alerts_generated": result.get('automation', {}).get('alerts_generated', 0),
            }}
        )
        
        # Remove products from response to reduce payload size
        result.pop('products', None)
        
        return result
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))

@ingestion_router.post("/amazon")
async def run_amazon_import(request: ImportRequest):
    """Import trending products from Amazon Movers & Shakers"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "amazon_import",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "amazon",
    }
    await db.automation_logs.insert_one(log)
    
    try:
        importer = AmazonImporter(db)
        result = await importer.import_products(
            category=request.category,
            limit=request.limit
        )
        
        # Clean _id from products
        if result.get('products'):
            for p in result['products']:
                p.pop('_id', None)
            automation_result = await run_automation_on_products(result['products'])
            result['automation'] = automation_result
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": result.get('inserted', 0) + result.get('updated', 0),
                "alerts_generated": result.get('automation', {}).get('alerts_generated', 0),
            }}
        )
        
        result.pop('products', None)
        return result
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))

@ingestion_router.post("/supplier")
async def run_supplier_import(request: ImportRequest):
    """Import products from supplier feeds"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "supplier_import",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "supplier",
    }
    await db.automation_logs.insert_one(log)
    
    try:
        importer = SupplierImporter(db)
        result = await importer.import_products(
            category=request.category,
            limit=request.limit
        )
        
        # Clean _id from products
        if result.get('products'):
            for p in result['products']:
                p.pop('_id', None)
            automation_result = await run_automation_on_products(result['products'])
            result['automation'] = automation_result
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": result.get('inserted', 0) + result.get('updated', 0),
                "alerts_generated": result.get('automation', {}).get('alerts_generated', 0),
            }}
        )
        
        result.pop('products', None)
        return result
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))

@ingestion_router.post("/supplier/csv")
async def import_from_csv(request: CSVImportRequest):
    """Import products from CSV content"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "product_import",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "csv_upload",
    }
    await db.automation_logs.insert_one(log)
    
    try:
        importer = SupplierImporter(db)
        result = await importer.import_from_csv(request.csv_content)
        
        # Run automation on imported products
        if result.get('products'):
            automation_result = await run_automation_on_products(result['products'])
            result['automation'] = automation_result
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": result.get('inserted', 0) + result.get('updated', 0),
                "alerts_generated": result.get('automation', {}).get('alerts_generated', 0),
            }}
        )
        
        return result
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))

@ingestion_router.post("/full-sync")
async def run_full_data_sync(request: ImportRequest):
    """Run full data sync from all sources"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "full_data_sync",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "all",
    }
    await db.automation_logs.insert_one(log)
    
    results = {
        "tiktok": None,
        "amazon": None,
        "supplier": None,
        "total_imported": 0,
        "total_alerts": 0,
    }
    
    try:
        # Import from TikTok
        tiktok_importer = TikTokImporter(db)
        results["tiktok"] = await tiktok_importer.import_products(limit=request.limit)
        
        # Import from Amazon
        amazon_importer = AmazonImporter(db)
        results["amazon"] = await amazon_importer.import_products(limit=request.limit)
        
        # Import from Suppliers
        supplier_importer = SupplierImporter(db)
        results["supplier"] = await supplier_importer.import_products(limit=request.limit)
        
        # Collect all products for automation
        all_products = []
        for source in ["tiktok", "amazon", "supplier"]:
            if results[source] and results[source].get("products"):
                all_products.extend(results[source]["products"])
        
        # Run automation on all imported products
        if all_products:
            automation_result = await run_automation_on_products(all_products)
            results["automation"] = automation_result
            results["total_alerts"] = automation_result.get("alerts_generated", 0)
        
        # Calculate totals
        for source in ["tiktok", "amazon", "supplier"]:
            if results[source]:
                results["total_imported"] += results[source].get("inserted", 0) + results[source].get("updated", 0)
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": results["total_imported"],
                "alerts_generated": results["total_alerts"],
                "metadata": {
                    "tiktok": results["tiktok"].get("fetched", 0) if results["tiktok"] else 0,
                    "amazon": results["amazon"].get("fetched", 0) if results["amazon"] else 0,
                    "supplier": results["supplier"].get("fetched", 0) if results["supplier"] else 0,
                },
            }}
        )
        
        return {
            "success": True,
            "total_imported": results["total_imported"],
            "total_alerts": results["total_alerts"],
            "sources": {
                "tiktok": {"imported": results["tiktok"].get("inserted", 0) + results["tiktok"].get("updated", 0)} if results["tiktok"] else None,
                "amazon": {"imported": results["amazon"].get("inserted", 0) + results["amazon"].get("updated", 0)} if results["amazon"] else None,
                "supplier": {"imported": results["supplier"].get("inserted", 0) + results["supplier"].get("updated", 0)} if results["supplier"] else None,
            },
        }
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))

async def run_automation_on_products(products: List[Dict]) -> Dict:
    """Helper to run full automation pipeline on products"""
    alerts_generated = 0
    
    for product in products:
        # Remove _id if present (MongoDB adds it)
        product.pop('_id', None)
        
        # Run full automation
        result = run_full_automation(product)
        processed = result['product']
        
        # Remove _id from processed product too
        processed.pop('_id', None)
        
        # Update product in database
        await db.products.update_one(
            {"id": processed['id']},
            {"$set": processed},
            upsert=True
        )
        
        # Save alert if generated
        if result['alert']:
            result['alert'].pop('_id', None)
            await db.trend_alerts.insert_one(result['alert'])
            alerts_generated += 1
    
    return {
        "products_processed": len(products),
        "alerts_generated": alerts_generated,
    }

# =====================
# ROUTES - Stores
# =====================

from services.store_service import (
    StoreGenerator, 
    create_store_document, 
    create_store_product_document,
    can_create_store,
    get_store_limit,
    STORE_LIMITS
)

@stores_router.get("")
async def get_user_stores(
    status: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get all stores for the authenticated user"""
    user_id = current_user.user_id
    query = {"owner_id": user_id}
    if status:
        query["status"] = status
    
    stores = await db.stores.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    # Get product counts for each store
    for store in stores:
        product_count = await db.store_products.count_documents({"store_id": store["id"]})
        store["product_count"] = product_count
    
    return {
        "data": stores,
        "count": len(stores),
    }

@stores_router.get("/limits")
async def get_store_limits(plan: str = "starter"):
    """Get store limits for a plan"""
    limit = get_store_limit(plan)
    return {
        "plan": plan,
        "limit": limit if limit != float('inf') else "unlimited",
        "all_limits": {k: v if v != float('inf') else "unlimited" for k, v in STORE_LIMITS.items()}
    }

@stores_router.get("/{store_id}")
async def get_store(
    store_id: str,
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get a single store by ID. Requires ownership unless store is published."""
    store = await db.stores.find_one({"id": store_id}, {"_id": 0})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Check access: must be owner OR store must be published
    user_id = current_user.user_id if current_user else None
    is_owner = user_id and store["owner_id"] == user_id
    is_published = store.get("status") == "published"
    
    if not is_owner and not is_published:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get products for this store
    products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    store["products"] = products
    
    return {"data": store}

@stores_router.post("/generate")
async def generate_store(
    request: GenerateStoreRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Generate a store draft from a product (AI store builder)"""
    user_id = current_user.user_id
    # Check store limits
    current_count = await db.stores.count_documents({"owner_id": user_id})
    
    if not can_create_store(current_count, request.plan):
        limit = get_store_limit(request.plan)
        raise HTTPException(
            status_code=403, 
            detail=f"Store limit reached. Your {request.plan} plan allows {limit} store(s). Upgrade to create more stores."
        )
    
    # Get the product
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Generate store content
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(product, request.store_name)
    
    return {
        "success": True,
        "generation": generation_result,
        "product": product,
        "can_create": True,
        "stores_remaining": get_store_limit(request.plan) - current_count - 1 if get_store_limit(request.plan) != float('inf') else "unlimited",
    }

@stores_router.post("")
async def create_store(
    request: StoreCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Create a new store from generated content"""
    user_id = current_user.user_id
    # Check store limits
    current_count = await db.stores.count_documents({"owner_id": user_id})
    
    if not can_create_store(current_count, request.plan):
        limit = get_store_limit(request.plan)
        raise HTTPException(
            status_code=403, 
            detail=f"Store limit reached. Your {request.plan} plan allows {limit} store(s)."
        )
    
    # Get the product
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Generate store content
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(product, request.name)
    
    # Create store document
    store_doc = create_store_document(
        user_id=user_id,
        store_name=request.name,
        generation_result=generation_result,
        product=product
    )
    
    # Create store product document
    store_product_doc = create_store_product_document(
        store_id=store_doc["id"],
        product=product,
        generation_result=generation_result
    )
    
    # Insert into database
    await db.stores.insert_one(store_doc)
    await db.store_products.insert_one(store_product_doc)
    
    # Track product success - store created
    await track_product_store_created(request.product_id)
    
    # Remove _id for response
    store_doc.pop("_id", None)
    store_product_doc.pop("_id", None)
    
    return {
        "success": True,
        "store": store_doc,
        "product": store_product_doc,
        "stores_remaining": get_store_limit(request.plan) - current_count - 1 if get_store_limit(request.plan) != float('inf') else "unlimited",
    }

@stores_router.put("/{store_id}")
async def update_store(
    store_id: str,
    request: StoreUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update a store owned by the authenticated user"""
    user_id = current_user.user_id
    # Verify ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Build update dict
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.stores.update_one({"id": store_id}, {"$set": update_data})
    
    # Get updated store
    updated = await db.stores.find_one({"id": store_id}, {"_id": 0})
    
    return {"success": True, "store": updated}

@stores_router.delete("/{store_id}")
async def delete_store(
    store_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Delete a store and its products (requires ownership)"""
    user_id = current_user.user_id
    # Verify ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Delete store products
    await db.store_products.delete_many({"store_id": store_id})
    
    # Delete store
    await db.stores.delete_one({"id": store_id})
    
    return {"success": True, "message": "Store deleted"}

@stores_router.post("/{store_id}/products")
async def add_product_to_store(
    store_id: str,
    request: StoreProductCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Add a product to an existing store (requires ownership)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Get the product
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product already in store
    existing = await db.store_products.find_one({
        "store_id": store_id,
        "original_product_id": request.product_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Product already in store")
    
    # Generate content for this product
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(product)
    
    # Create store product
    store_product_doc = create_store_product_document(store_id, product, generation_result)
    store_product_doc["is_featured"] = False  # Not featured when adding to existing store
    
    await db.store_products.insert_one(store_product_doc)
    store_product_doc.pop("_id", None)
    
    return {"success": True, "product": store_product_doc}

@stores_router.get("/{store_id}/products")
async def get_store_products(store_id: str):
    """Get all products in a store"""
    products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    
    return {
        "data": products,
        "count": len(products),
    }

@stores_router.put("/{store_id}/products/{product_id}")
async def update_store_product(
    store_id: str,
    product_id: str,
    request: StoreProductUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update a product in a store (requires ownership)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Build update dict
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.store_products.update_one(
        {"id": product_id, "store_id": store_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in store")
    
    updated = await db.store_products.find_one({"id": product_id}, {"_id": 0})
    
    return {"success": True, "product": updated}

@stores_router.delete("/{store_id}/products/{product_id}")
async def delete_store_product(
    store_id: str,
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Remove a product from a store (requires ownership)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    result = await db.store_products.delete_one({"id": product_id, "store_id": store_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in store")
    
    return {"success": True, "message": "Product removed from store"}

@stores_router.post("/{store_id}/regenerate/{product_id}")
async def regenerate_product_copy(
    store_id: str,
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Regenerate AI copy for a store product (requires ownership)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Get store product
    store_product = await db.store_products.find_one({"id": product_id, "store_id": store_id})
    
    if not store_product:
        raise HTTPException(status_code=404, detail="Product not found in store")
    
    # Get original product
    original_product = await db.products.find_one(
        {"id": store_product["original_product_id"]}, 
        {"_id": 0}
    )
    
    if not original_product:
        raise HTTPException(status_code=404, detail="Original product not found")
    
    # Regenerate content
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(original_product)
    
    product_data = generation_result.get("product", {})
    pricing = product_data.get("pricing", {})
    
    # Update store product
    update_data = {
        "title": product_data.get("title"),
        "description": product_data.get("description"),
        "bullet_points": product_data.get("bullet_points"),
        "price": pricing.get("suggested_price"),
        "compare_at_price": pricing.get("compare_at_price"),
        "updated_at": datetime.now(timezone.utc),
    }
    
    await db.store_products.update_one({"id": product_id}, {"$set": update_data})
    
    updated = await db.store_products.find_one({"id": product_id}, {"_id": 0})
    
    return {"success": True, "product": updated, "regenerated": True}

@stores_router.get("/{store_id}/export")
async def export_store(
    store_id: str,
    format: str = "shopify",
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Export store data for Shopify or other platforms (requires ownership)"""
    from services.shopify_service import format_store_for_export
    
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id}, {"_id": 0})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Get products
    products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    
    if format == "shopify":
        export_data = format_store_for_export(store, products)
    else:
        # Raw JSON export
        export_data = {
            "store": store,
            "products": products,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
    
    # Track product export for success tracking
    for product in products:
        source_product_id = product.get("source_product_id")
        if source_product_id:
            await track_product_exported(source_product_id)
    
    # Update store status to exported (if not already published)
    if store.get("status") not in ["published", "exported"]:
        await db.stores.update_one(
            {"id": store_id},
            {"$set": {"status": "exported", "exported_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}}
        )
    
    return export_data

@stores_router.put("/{store_id}/status")
async def update_store_status(
    store_id: str,
    request: UpdateStoreStatusRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update store status (draft -> ready -> exported -> published)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    update_data = {
        "status": request.status.value,
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Add timestamp for status changes
    if request.status == StoreStatus.READY:
        update_data["ready_at"] = datetime.now(timezone.utc)
    elif request.status == StoreStatus.EXPORTED:
        update_data["exported_at"] = datetime.now(timezone.utc)
    elif request.status == StoreStatus.PUBLISHED:
        update_data["published_at"] = datetime.now(timezone.utc)
    
    await db.stores.update_one({"id": store_id}, {"$set": update_data})
    
    updated = await db.stores.find_one({"id": store_id}, {"_id": 0})
    
    return {"success": True, "store": updated}

@stores_router.get("/{store_id}/preview")
async def get_store_preview(store_id: str):
    """Get store data for public preview page"""
    store = await db.stores.find_one({"id": store_id}, {"_id": 0})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Get featured product
    featured_product = await db.store_products.find_one(
        {"store_id": store_id, "is_featured": True}, 
        {"_id": 0}
    )
    
    # If no featured, get first product
    if not featured_product:
        featured_product = await db.store_products.find_one({"store_id": store_id}, {"_id": 0})
    
    # Get all products
    all_products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    
    return {
        "store": store,
        "featured_product": featured_product,
        "all_products": all_products,
        "is_published": store.get("status") == "published",
    }


# =====================
# ROUTES - Shopify Integration
# =====================

from services.shopify_service import (
    is_shopify_configured,
    get_oauth_url,
    exchange_code_for_token,
    ShopifyPublisher,
    format_store_for_export,
    get_connection_status,
    test_connection
)
import secrets

shopify_integration_router = APIRouter(prefix="/api/shopify")

@shopify_integration_router.get("/status")
async def shopify_status():
    """Check if Shopify integration is configured"""
    return {
        "configured": is_shopify_configured(),
        "features": {
            "export": True,  # Always available
            "direct_publish": is_shopify_configured(),
            "oauth_connect": is_shopify_configured(),
        },
        "message": "Shopify API configured" if is_shopify_configured() else "Export-only mode (Shopify credentials not configured)"
    }

@shopify_integration_router.post("/connect/init")
async def init_shopify_connection(
    shop_domain: str,
    redirect_uri: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Initialize Shopify OAuth connection for authenticated user
    
    Returns URL to redirect user to for authorization
    """
    user_id = current_user.user_id
    if not is_shopify_configured():
        raise HTTPException(
            status_code=503, 
            detail="Shopify integration not configured. Contact admin to set up SHOPIFY_API_KEY and SHOPIFY_API_SECRET."
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state temporarily (in production, use Redis or DB)
    # For now, we'll encode user_id in state
    state_data = f"{state}:{user_id}"
    
    oauth_url = get_oauth_url(shop_domain, redirect_uri, state_data)
    
    return {
        "oauth_url": oauth_url,
        "state": state,
        "message": "Redirect user to oauth_url to authorize Shopify access"
    }

@shopify_integration_router.post("/connect/callback")
async def shopify_oauth_callback(shop_domain: str, code: str, state: str):
    """
    Handle Shopify OAuth callback
    
    Exchange authorization code for access token
    """
    if not is_shopify_configured():
        raise HTTPException(status_code=503, detail="Shopify integration not configured")
    
    try:
        # Extract user_id from state
        state_parts = state.split(':')
        user_id = state_parts[1] if len(state_parts) > 1 else None
        
        # Exchange code for token
        token_data = await exchange_code_for_token(shop_domain, code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        # Store in user profile
        shopify_data = {
            "shop_domain": shop_domain,
            "access_token": access_token,
            "scope": token_data.get('scope'),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }
        
        if user_id:
            await db.profiles.update_one(
                {"id": user_id},
                {"$set": {"shopify": shopify_data}}
            )
        
        return {
            "success": True,
            "shop_domain": shop_domain,
            "message": "Shopify connected successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@shopify_integration_router.get("/connection")
async def get_user_shopify_status(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get Shopify connection status for authenticated user"""
    user_id = current_user.user_id
    profile = await db.profiles.find_one({"id": user_id}, {"_id": 0})
    
    if not profile:
        return get_connection_status({})
    
    return get_connection_status(profile)

@shopify_integration_router.post("/publish/{store_id}")
async def publish_to_shopify(
    store_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Publish store products directly to Shopify
    
    Requires user to have connected Shopify account
    """
    user_id = current_user.user_id
    # Get user's Shopify credentials
    profile = await db.profiles.find_one({"id": user_id}, {"_id": 0})
    shopify_data = profile.get('shopify', {}) if profile else {}
    
    if not shopify_data.get('access_token'):
        raise HTTPException(
            status_code=400, 
            detail="Shopify not connected. Please connect your Shopify store first."
        )
    
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Get store products
    products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    
    if not products:
        raise HTTPException(status_code=400, detail="No products to publish")
    
    # Initialize publisher and publish
    publisher = ShopifyPublisher(
        shopify_data['shop_domain'],
        shopify_data['access_token']
    )
    
    try:
        results = await publisher.publish_store_products(products)
        
        # Update store status
        await db.stores.update_one(
            {"id": store_id},
            {"$set": {
                "status": "published",
                "published_at": datetime.now(timezone.utc),
                "shopify_publish_results": results,
            }}
        )
        
        return {
            "success": True,
            "results": results,
            "message": f"Published {len(results['success'])} products to Shopify"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publish failed: {str(e)}")

@shopify_integration_router.delete("/disconnect")
async def disconnect_shopify(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Disconnect Shopify from authenticated user's account"""
    user_id = current_user.user_id
    await db.profiles.update_one(
        {"id": user_id},
        {"$unset": {"shopify": ""}}
    )
    
    return {"success": True, "message": "Shopify disconnected"}


# Include routers
app.include_router(api_router)
app.include_router(stripe_router)
app.include_router(automation_router)
app.include_router(ingestion_router)
app.include_router(stores_router)
app.include_router(jobs_router)
app.include_router(viral_router)
app.include_router(shopify_integration_router)
app.include_router(data_integrity_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    """Initialize database collections, indexes, and background services"""
    # Create indexes
    await db.products.create_index("id", unique=True)
    await db.products.create_index("category")
    await db.products.create_index("trend_score")
    await db.products.create_index("trend_stage")
    await db.products.create_index("source")
    await db.products.create_index("fingerprint")
    await db.products.create_index("source_id")
    await db.products.create_index("market_score")
    await db.products.create_index("market_label")
    
    await db.trend_alerts.create_index("id", unique=True)
    await db.trend_alerts.create_index("product_id")
    await db.trend_alerts.create_index("created_at")
    
    await db.automation_logs.create_index("id", unique=True)
    await db.automation_logs.create_index("started_at")
    await db.automation_logs.create_index("job_type")
    
    await db.subscriptions.create_index("user_id", unique=True)
    await db.profiles.create_index("id", unique=True)
    
    # Store indexes
    await db.stores.create_index("id", unique=True)
    await db.stores.create_index("owner_id")
    await db.stores.create_index("status")
    await db.store_products.create_index("id", unique=True)
    await db.store_products.create_index("store_id")
    await db.store_products.create_index("original_product_id")
    
    # Alert indexes
    await db.alerts.create_index("id", unique=True)
    await db.alerts.create_index("product_id")
    await db.alerts.create_index([("created_at", -1)])
    
    logger.info("Database indexes created")
    
    # Start background worker and scheduler
    try:
        from services.jobs.worker import WorkerManager
        from services.jobs.scheduler import SchedulerManager
        
        # Initialize and start the worker
        worker_manager = WorkerManager.get_instance()
        worker_manager.initialize(db)
        await worker_manager.start()
        
        # Initialize and start the scheduler
        scheduler_manager = SchedulerManager.get_instance()
        scheduler_manager.initialize(db)
        await scheduler_manager.start()
        
        logger.info("Background worker and scheduler started")
    except Exception as e:
        logger.error(f"Failed to start background services: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup on shutdown"""
    # Stop background services
    try:
        from services.jobs.worker import WorkerManager
        from services.jobs.scheduler import SchedulerManager
        
        scheduler_manager = SchedulerManager.get_instance()
        await scheduler_manager.stop()
        
        worker_manager = WorkerManager.get_instance()
        await worker_manager.stop()
        
        logger.info("Background services stopped")
    except Exception as e:
        logger.error(f"Error stopping background services: {e}")
    
    client.close()
