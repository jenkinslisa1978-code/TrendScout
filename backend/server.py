from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends, Header
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import io
import logging
import json
import hmac
import hashlib
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
import jwt
from datetime import datetime, timezone
from enum import Enum

# Load environment BEFORE importing auth module (which reads env vars at import time)
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import authentication module
from auth import get_current_user, get_optional_user, AuthenticatedUser

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
intelligence_router = APIRouter(prefix="/api/intelligence")
dashboard_router = APIRouter(prefix="/api/dashboard")
supplier_router = APIRouter(prefix="/api/suppliers")
reports_router = APIRouter(prefix="/api/reports")
email_router = APIRouter(prefix="/api/email")
notifications_router = APIRouter(prefix="/api/notifications")
user_router = APIRouter(prefix="/api/user")
auth_router = APIRouter(prefix="/api/auth")

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
    # Product Launch Score - Primary decision metric
    launch_score: int = 0  # 0-100 composite score for launch decision
    launch_score_label: str = "risky"  # strong_launch, promising, risky, avoid
    launch_score_reasoning: Optional[str] = None  # Human-readable explanation
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
    plan: str  # 'pro' or 'elite'
    success_url: str
    cancel_url: str
    price_id: Optional[str] = None  # Legacy, optional

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


# Watchlist & Alert Models
class WatchlistItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Snapshot at time of adding (for change detection)
    initial_success_probability: Optional[float] = None
    initial_trend_velocity: Optional[float] = None
    initial_competition_level: Optional[str] = None
    initial_margin_score: Optional[int] = None
    notes: Optional[str] = None


class WatchlistItemCreate(BaseModel):
    product_id: str
    notes: Optional[str] = None


class OpportunityAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    alert_type: str  # trend_spike, success_increase, competition_change, launch_opportunity
    title: str
    message: str
    severity: str = "info"  # info, warning, success
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Optional[Dict[str, Any]] = None


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


def calculate_launch_score(product: dict) -> tuple:
    """
    Calculate Product Launch Score - the primary decision metric.
    
    Formula:
    launch_score = 0.30 × trend_score + 0.25 × margin_score + 
                   0.20 × competition_score + 0.15 × ad_activity_score + 
                   0.10 × supplier_demand_score
    
    Returns: (launch_score, launch_score_label, launch_score_reasoning)
    
    Labels:
    - 80-100: Strong Launch Opportunity
    - 60-79: Promising
    - 40-59: Risky
    - 0-39: Avoid
    """
    # Get component scores (all 0-100)
    trend_score = product.get('trend_score', 0)
    margin_score = product.get('margin_score', 0)
    competition_score = product.get('competition_score', 0)
    ad_activity_score = product.get('ad_activity_score', 0)
    supplier_demand_score = product.get('supplier_demand_score', 0)
    
    # Calculate weighted launch score
    launch_score = (
        trend_score * 0.30 +
        margin_score * 0.25 +
        competition_score * 0.20 +
        ad_activity_score * 0.15 +
        supplier_demand_score * 0.10
    )
    
    launch_score = min(100, max(0, round(launch_score)))
    
    # Determine label
    if launch_score >= 80:
        label = 'strong_launch'
    elif launch_score >= 60:
        label = 'promising'
    elif launch_score >= 40:
        label = 'risky'
    else:
        label = 'avoid'
    
    # Generate reasoning
    reasoning_parts = []
    
    # Identify top strengths
    scores = {
        'Trend momentum': trend_score,
        'Profit margins': margin_score,
        'Market accessibility': competition_score,
        'Advertiser validation': ad_activity_score,
        'Supplier reliability': supplier_demand_score
    }
    
    # Sort by score value
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Top 2 strengths
    strengths = [name for name, score in sorted_scores[:2] if score >= 60]
    weaknesses = [name for name, score in sorted_scores if score < 40]
    
    if strengths:
        reasoning_parts.append(f"Strong: {', '.join(strengths)}")
    
    if weaknesses and label in ['risky', 'avoid']:
        reasoning_parts.append(f"Weak: {', '.join(weaknesses[:2])}")
    
    # Add specific insights based on label
    if label == 'strong_launch':
        reasoning_parts.append("Excellent conditions for launch")
    elif label == 'promising':
        reasoning_parts.append("Good potential with manageable risks")
    elif label == 'risky':
        reasoning_parts.append("Proceed with caution - test small first")
    else:
        reasoning_parts.append("High risk - consider alternatives")
    
    reasoning = ". ".join(reasoning_parts) if reasoning_parts else "Insufficient data for analysis"
    
    return launch_score, label, reasoning


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
    
    # Calculate Product Launch Score - PRIMARY DECISION METRIC
    launch_score, launch_label, launch_reasoning = calculate_launch_score(product)
    product['launch_score'] = launch_score
    product['launch_score_label'] = launch_label
    product['launch_score_reasoning'] = launch_reasoning
    
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
    products_with_launch_score = await db.products.count_documents({"launch_score": {"$gte": 1}})
    high_opportunity = await db.products.count_documents({"market_label": {"$in": ["massive", "strong"]}})
    strong_launch = await db.products.count_documents({"launch_score": {"$gte": 80}})
    
    # Get data freshness
    latest_product = await db.products.find_one({}, {"_id": 0, "last_updated": 1}, sort=[("last_updated", -1)])
    
    return {
        "pipeline_health": "healthy" if recent_runs and recent_runs[0].get("success") else "unknown",
        "last_run": recent_runs[0] if recent_runs else None,
        "recent_runs": recent_runs,
        "product_stats": {
            "total": total_products,
            "with_scores": products_with_scores,
            "with_launch_score": products_with_launch_score,
            "high_opportunity": high_opportunity,
            "strong_launch": strong_launch,
        },
        "data_freshness": latest_product.get("last_updated") if latest_product else None,
        "sources": {
            "amazon_movers": {"status": "live", "description": "Amazon Movers & Shakers - real-time trending products"},
            "aliexpress_search": {"status": "generated", "description": "AliExpress supplier links auto-generated from product names"},
            "tiktok_trends": {"status": "pending", "description": "TikTok Creative Center - blocked by anti-bot"},
            "cj_dropshipping": {"status": "pending", "description": "CJ Dropshipping - blocked by anti-bot"},
        }
    }


@automation_router.post("/compute-launch-scores")
async def compute_launch_scores_batch(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Batch compute Launch Scores for all products.
    This updates the launch_score, launch_score_label, and launch_score_reasoning fields.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        start_time = datetime.now(timezone.utc)
        
        # Get all products
        products = await db.products.find({}, {"_id": 0}).to_list(None)
        updated_count = 0
        
        for product in products:
            # Calculate launch score
            launch_score, launch_label, launch_reasoning = calculate_launch_score(product)
            
            # Update in database
            await db.products.update_one(
                {"id": product.get("id")},
                {
                    "$set": {
                        "launch_score": launch_score,
                        "launch_score_label": launch_label,
                        "launch_score_reasoning": launch_reasoning,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            updated_count += 1
        
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return {
            "success": True,
            "products_updated": updated_count,
            "duration_seconds": round(duration, 2),
            "message": f"Updated launch scores for {updated_count} products"
        }
    except Exception as e:
        logging.error(f"Launch score computation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
            "name": "TrendScout",
            "tagline": "Find winning products before they go viral",
        }
    }


@api_router.get("/public/trending-products")
async def get_trending_products(limit: int = 10):
    """
    Public trending products endpoint for SEO page.
    Returns top products sorted by launch_score.
    """
    cursor = db.products.find(
        {"launch_score": {"$gte": 40}},
        {"_id": 0}
    ).sort([("launch_score", -1), ("market_score", -1)]).limit(limit)
    
    products = await cursor.to_list(limit)
    
    trending = []
    for product in products:
        trending.append({
            "id": product["id"],
            "product_name": product.get("product_name"),
            "category": product.get("category"),
            "image_url": product.get("image_url"),
            "launch_score": product.get("launch_score", 0),
            "launch_score_label": product.get("launch_score_label", "risky"),
            "trend_stage": product.get("trend_stage"),
            "trend_score": product.get("trend_score"),
            "market_score": product.get("market_score"),
            "early_trend_label": product.get("early_trend_label"),
            "margin_range": _get_margin_range(product.get("estimated_margin", 0)),
        })
    
    # If no products with launch_score >= 40, fallback to top by market_score
    if not trending:
        cursor = db.products.find(
            {},
            {"_id": 0}
        ).sort([("market_score", -1)]).limit(limit)
        products = await cursor.to_list(limit)
        for product in products:
            trending.append({
                "id": product["id"],
                "product_name": product.get("product_name"),
                "category": product.get("category"),
                "image_url": product.get("image_url"),
                "launch_score": product.get("launch_score", 0),
                "launch_score_label": product.get("launch_score_label", "risky"),
                "trend_stage": product.get("trend_stage"),
                "trend_score": product.get("trend_score"),
                "market_score": product.get("market_score"),
                "early_trend_label": product.get("early_trend_label"),
                "margin_range": _get_margin_range(product.get("estimated_margin", 0)),
            })
    
    return {
        "products": trending,
        "count": len(trending),
        "last_updated": datetime.now(timezone.utc).isoformat(),
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
    share_text += f"Margin: {_get_margin_range(product.get('estimated_margin', 0))}\n\n"
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
            "margin_range": _get_margin_range(product.get("estimated_margin", 0)),
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
async def get_early_trend_opportunities(limit: int = 20):
    """
    Get products showing early trend signals - best first-mover opportunities.
    """
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


@reports_router.get("/")
async def list_reports(
    report_type: Optional[str] = None,
    limit: int = 20
):
    """List available reports - public endpoint"""
    query = {"metadata.status": "completed"}
    
    if report_type:
        query["metadata.report_type"] = report_type
    
    cursor = db.reports.find(
        query,
        {"_id": 0, "metadata": 1, "summary": 1, "public_preview": 1}
    ).sort("metadata.generated_at", -1).limit(limit)
    
    reports = await cursor.to_list(limit)
    
    # Get latest of each type
    weekly_latest = await db.reports.find_one(
        {"metadata.report_type": "weekly_winning_products", "metadata.is_latest": True},
        {"_id": 0, "metadata.slug": 1, "metadata.title": 1}
    )
    monthly_latest = await db.reports.find_one(
        {"metadata.report_type": "monthly_market_trends", "metadata.is_latest": True},
        {"_id": 0, "metadata.slug": 1, "metadata.title": 1}
    )
    
    return {
        "reports": reports,
        "count": len(reports),
        "latest": {
            "weekly": weekly_latest,
            "monthly": monthly_latest
        }
    }


@reports_router.get("/weekly-winning-products")
async def get_weekly_report(
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get the latest weekly winning products report"""
    report = await db.reports.find_one(
        {
            "metadata.report_type": "weekly_winning_products",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0}
    )
    
    if not report:
        # Generate report if none exists
        generator = WeeklyWinningProductsReport(db)
        generated = await generator.generate()
        report = generated.model_dump()
        report["metadata"]["report_type"] = generated.metadata.report_type.value
        report["metadata"]["status"] = generated.metadata.status.value
        report["metadata"]["access_level"] = generated.metadata.access_level.value
        report["metadata"]["period_start"] = generated.metadata.period_start.isoformat()
        report["metadata"]["period_end"] = generated.metadata.period_end.isoformat()
        report["metadata"]["generated_at"] = generated.metadata.generated_at.isoformat()
    
    # Determine user's plan
    user_plan = "free"
    if current_user:
        profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0, "plan": 1})
        user_plan = profile.get("plan", "free") if profile else "free"
    
    # Filter by access level
    filtered_report = filter_report_by_access(report, user_plan)
    
    return {
        "report": filtered_report,
        "user_plan": user_plan,
        "is_authenticated": current_user is not None
    }


@reports_router.get("/monthly-market-trends")
async def get_monthly_report(
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get the latest monthly market trends report"""
    report = await db.reports.find_one(
        {
            "metadata.report_type": "monthly_market_trends",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0}
    )
    
    if not report:
        # Generate report if none exists
        generator = MonthlyMarketTrendsReport(db)
        generated = await generator.generate()
        report = generated.model_dump()
        report["metadata"]["report_type"] = generated.metadata.report_type.value
        report["metadata"]["status"] = generated.metadata.status.value
        report["metadata"]["access_level"] = generated.metadata.access_level.value
        report["metadata"]["period_start"] = generated.metadata.period_start.isoformat()
        report["metadata"]["period_end"] = generated.metadata.period_end.isoformat()
        report["metadata"]["generated_at"] = generated.metadata.generated_at.isoformat()
    
    # Determine user's plan
    user_plan = "free"
    if current_user:
        profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0, "plan": 1})
        user_plan = profile.get("plan", "free") if profile else "free"
    
    # Filter by access level
    filtered_report = filter_report_by_access(report, user_plan)
    
    return {
        "report": filtered_report,
        "user_plan": user_plan,
        "is_authenticated": current_user is not None
    }


@reports_router.get("/public/weekly-winning-products")
async def get_public_weekly_report():
    """Get public preview of weekly report - for SEO"""
    report = await db.reports.find_one(
        {
            "metadata.report_type": "weekly_winning_products",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0, "metadata": 1, "public_preview": 1, "summary": 1}
    )
    
    if not report:
        # Generate report if none exists
        generator = WeeklyWinningProductsReport(db)
        generated = await generator.generate()
        report = {
            "metadata": {
                "title": generated.metadata.title,
                "description": generated.metadata.description,
                "period_start": generated.metadata.period_start.isoformat(),
                "period_end": generated.metadata.period_end.isoformat(),
                "generated_at": generated.metadata.generated_at.isoformat(),
                "slug": generated.metadata.slug
            },
            "public_preview": generated.public_preview,
            "summary": generated.summary
        }
    
    return {
        "report": report,
        "cta": {
            "message": "Unlock the full report to see all winning products, detailed margins, and opportunity clusters.",
            "action": "Sign up for free",
            "url": "/signup"
        }
    }


@reports_router.get("/public/monthly-market-trends")
async def get_public_monthly_report():
    """Get public preview of monthly report - for SEO"""
    report = await db.reports.find_one(
        {
            "metadata.report_type": "monthly_market_trends",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0, "metadata": 1, "public_preview": 1, "summary": 1}
    )
    
    if not report:
        # Generate report if none exists
        generator = MonthlyMarketTrendsReport(db)
        generated = await generator.generate()
        report = {
            "metadata": {
                "title": generated.metadata.title,
                "description": generated.metadata.description,
                "period_start": generated.metadata.period_start.isoformat(),
                "period_end": generated.metadata.period_end.isoformat(),
                "generated_at": generated.metadata.generated_at.isoformat(),
                "slug": generated.metadata.slug
            },
            "public_preview": generated.public_preview,
            "summary": generated.summary
        }
    
    return {
        "report": report,
        "cta": {
            "message": "Unlock the full report to see all category insights, growth predictions, and market analysis.",
            "action": "Sign up for free",
            "url": "/signup"
        }
    }


@reports_router.get("/history/{report_type}")
async def get_report_history(
    report_type: str,
    limit: int = 20,
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get historical reports of a specific type"""
    valid_types = ["weekly_winning_products", "monthly_market_trends"]
    if report_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid report type. Must be one of: {valid_types}")
    
    # Determine user's plan
    user_plan = "free"
    if current_user:
        profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0, "plan": 1})
        user_plan = profile.get("plan", "free") if profile else "free"
    
    # Check access for historical reports
    if user_plan == "free":
        limit = 3  # Free users only see recent 3
    elif user_plan == "pro":
        limit = min(limit, 10)  # Pro users see 10
    # Elite users get full access
    
    cursor = db.reports.find(
        {"metadata.report_type": report_type, "metadata.status": "completed"},
        {"_id": 0, "metadata": 1, "summary": 1}
    ).sort("metadata.generated_at", -1).limit(limit)
    
    reports = await cursor.to_list(limit)
    
    return {
        "reports": reports,
        "count": len(reports),
        "user_plan": user_plan,
        "access_note": "Upgrade to Elite for full historical archive" if user_plan != "elite" else None
    }


@reports_router.get("/by-slug/{slug}")
async def get_report_by_slug(
    slug: str,
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get a specific report by its slug"""
    report = await db.reports.find_one(
        {"metadata.slug": slug, "metadata.status": "completed"},
        {"_id": 0}
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Determine user's plan
    user_plan = "free"
    if current_user:
        profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0, "plan": 1})
        user_plan = profile.get("plan", "free") if profile else "free"
    
    # Filter by access level
    filtered_report = filter_report_by_access(report, user_plan)
    
    return {
        "report": filtered_report,
        "user_plan": user_plan,
        "is_authenticated": current_user is not None
    }


@reports_router.post("/generate/weekly")
async def generate_weekly_report(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Manually trigger weekly report generation (admin only)"""
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    generator = WeeklyWinningProductsReport(db)
    report = await generator.generate()
    
    return {
        "success": True,
        "report_id": report.metadata.id,
        "slug": report.metadata.slug,
        "title": report.metadata.title
    }


@reports_router.post("/generate/monthly")
async def generate_monthly_report(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Manually trigger monthly report generation (admin only)"""
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    generator = MonthlyMarketTrendsReport(db)
    report = await generator.generate()
    
    return {
        "success": True,
        "report_id": report.metadata.id,
        "slug": report.metadata.slug,
        "title": report.metadata.title
    }


@reports_router.get("/weekly-winning-products/pdf")
async def download_weekly_report_pdf():
    """
    Download weekly winning products report as PDF.
    Returns a professionally formatted PDF document.
    """
    from services.pdf_generator import pdf_generator
    import traceback
    
    try:
        # Get latest weekly report
        report = await db.reports.find_one(
            {
                "metadata.report_type": "weekly_winning_products",
                "metadata.is_latest": True,
                "metadata.status": "completed"
            },
            {"_id": 0}
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="No weekly report available")
        
        logging.info(f"Generating PDF for report: {report.get('metadata', {}).get('title', 'Unknown')}")
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_weekly_report_pdf(report)
        
        # Generate filename
        week_num = report.get('metadata', {}).get('week_number', datetime.now(timezone.utc).isocalendar()[1])
        year = datetime.now(timezone.utc).year
        filename = f"viralscout_weekly_report_week{week_num}_{year}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


@reports_router.get("/monthly-market-trends/pdf")
async def download_monthly_report_pdf():
    """
    Download monthly market trends report as PDF.
    Returns a professionally formatted PDF document.
    """
    from services.pdf_generator import pdf_generator
    
    try:
        # Get latest monthly report
        report = await db.reports.find_one(
            {
                "metadata.report_type": "monthly_market_trends",
                "metadata.is_latest": True,
                "metadata.status": "completed"
            },
            {"_id": 0}
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="No monthly report available")
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_monthly_report_pdf(report)
        
        # Generate filename
        month_name = datetime.now(timezone.utc).strftime("%B")
        year = datetime.now(timezone.utc).year
        filename = f"viralscout_monthly_report_{month_name}_{year}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


@reports_router.get("/public/weekly-winning-products/pdf")
async def download_public_weekly_report_pdf():
    """
    Download public preview of weekly report as PDF.
    Available without authentication.
    """
    from services.pdf_generator import pdf_generator
    
    try:
        # Get latest weekly report
        report = await db.reports.find_one(
            {
                "metadata.report_type": "weekly_winning_products",
                "metadata.is_latest": True,
                "metadata.status": "completed"
            },
            {"_id": 0, "public_preview": 1, "metadata": 1, "summary": 1}
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="No weekly report available")
        
        # Build limited report for public PDF
        public_report = {
            'metadata': report.get('metadata', {}),
            'summary': report.get('summary', {}),
            'sections': [],
            'public_preview': report.get('public_preview', {})
        }
        
        # Add public preview as a section
        preview = report.get('public_preview', {})
        if preview.get('top_5_products'):
            public_report['sections'].append({
                'title': 'Top 5 Products Preview',
                'data': preview.get('top_5_products', [])
            })
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_weekly_report_pdf(public_report)
        
        week_num = report.get('metadata', {}).get('week_number', datetime.now(timezone.utc).isocalendar()[1])
        year = datetime.now(timezone.utc).year
        filename = f"viralscout_weekly_preview_week{week_num}_{year}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


# =====================================================
# EMAIL ENDPOINTS - Weekly Digest & Notifications
# =====================================================

@email_router.post("/send-test")
async def send_test_email(
    to_email: str,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send a test email to verify Resend integration (admin only).
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.email_service import email_service
    
    html_content = """
    <html>
    <body style="font-family: sans-serif; padding: 20px;">
        <h1 style="color: #4f46e5;">TrendScout Test Email</h1>
        <p>This is a test email from TrendScout to verify the email integration is working correctly.</p>
        <p style="color: #6b7280; font-size: 12px;">Sent via Resend API</p>
    </body>
    </html>
    """
    
    result = await email_service.send_email(
        to_email=to_email,
        subject="TrendScout - Test Email",
        html_content=html_content
    )
    
    return result


@email_router.post("/send-weekly-digest")
async def send_weekly_digest_to_user(
    to_email: str,
    user_name: Optional[str] = None,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send weekly digest email to a specific user (admin only).
    Uses latest weekly report data.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.email_service import email_service
    
    # Get latest weekly report
    report = await db.reports.find_one(
        {
            "metadata.report_type": "weekly_winning_products",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0}
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="No weekly report available")
    
    result = await email_service.send_weekly_digest(
        to_email=to_email,
        user_name=user_name or "there",
        report_data=report
    )
    
    return result


@email_router.post("/send-weekly-digest-all")
async def send_weekly_digest_to_all_subscribers(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send weekly digest email to all subscribed users (admin only).
    This is called by the scheduled job.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.email_service import email_service
    
    # Get latest weekly report
    report = await db.reports.find_one(
        {
            "metadata.report_type": "weekly_winning_products",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0}
    )
    
    if not report:
        return {"status": "skipped", "reason": "No weekly report available", "sent": 0}
    
    # Get all users subscribed to weekly digest
    subscribed_users = await db.users.find(
        {"email_preferences.weekly_digest": True},
        {"_id": 0, "email": 1, "name": 1}
    ).to_list(None)
    
    # If no explicit subscribers, check for users with email
    if not subscribed_users:
        subscribed_users = await db.users.find(
            {"email": {"$exists": True, "$ne": None}},
            {"_id": 0, "email": 1, "name": 1}
        ).to_list(50)  # Limit to 50 for safety
    
    results = {
        "status": "completed",
        "total_subscribers": len(subscribed_users),
        "sent": 0,
        "failed": 0,
        "errors": []
    }
    
    for user in subscribed_users:
        try:
            result = await email_service.send_weekly_digest(
                to_email=user.get('email'),
                user_name=user.get('name', user.get('email', '').split('@')[0]),
                report_data=report
            )
            if result.get('status') == 'success':
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'email': user.get('email'),
                    'error': result.get('error')
                })
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'email': user.get('email'),
                'error': str(e)
            })
    
    return results


@email_router.get("/subscription-status")
async def get_email_subscription_status(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Get current user's email subscription status.
    """
    user = await db.users.find_one(
        {"email": current_user.email},
        {"_id": 0, "email_preferences": 1}
    )
    
    default_prefs = {
        "weekly_digest": True,
        "product_alerts": True,
        "marketing": False
    }
    
    return {
        "email": current_user.email,
        "preferences": user.get("email_preferences", default_prefs) if user else default_prefs
    }


@email_router.post("/subscription-status")
async def update_email_subscription_status(
    weekly_digest: Optional[bool] = True,
    product_alerts: Optional[bool] = True,
    marketing: Optional[bool] = False,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Update current user's email subscription preferences.
    """
    preferences = {
        "weekly_digest": weekly_digest,
        "product_alerts": product_alerts,
        "marketing": marketing
    }
    
    await db.users.update_one(
        {"email": current_user.email},
        {
            "$set": {"email_preferences": preferences},
            "$setOnInsert": {"email": current_user.email}
        },
        upsert=True
    )
    
    return {
        "status": "updated",
        "email": current_user.email,
        "preferences": preferences
    }


@email_router.get("/product-of-the-week")
async def get_product_of_the_week():
    """
    Get the Product of the Week - the highest launch score product.
    Public endpoint for display on landing/trending pages.
    """
    cursor = db.products.find(
        {"launch_score": {"$gte": 60}},
        {"_id": 0}
    ).sort([("launch_score", -1), ("market_score", -1)]).limit(4)
    
    products = await cursor.to_list(4)
    
    if not products:
        # Fallback to any top product
        cursor = db.products.find({}, {"_id": 0}).sort([("market_score", -1)]).limit(4)
        products = await cursor.to_list(4)
    
    if not products:
        raise HTTPException(status_code=404, detail="No products available")
    
    featured = products[0]
    runners_up = products[1:4] if len(products) > 1 else []
    
    return {
        "product": {
            "id": featured["id"],
            "product_name": featured.get("product_name"),
            "category": featured.get("category"),
            "image_url": featured.get("image_url"),
            "launch_score": featured.get("launch_score", 0),
            "launch_score_label": featured.get("launch_score_label", "risky"),
            "trend_stage": featured.get("trend_stage"),
            "trend_score": featured.get("trend_score"),
            "market_score": featured.get("market_score"),
            "early_trend_label": featured.get("early_trend_label"),
            "margin_range": _get_margin_range(featured.get("estimated_margin", 0)),
        },
        "runners_up": [
            {
                "id": p["id"],
                "product_name": p.get("product_name"),
                "category": p.get("category"),
                "launch_score": p.get("launch_score", 0),
            }
            for p in runners_up
        ],
        "week_of": datetime.now(timezone.utc).strftime("%B %d, %Y"),
    }


@email_router.post("/send-product-of-the-week")
async def send_product_of_the_week_email(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send Product of the Week email to all subscribed users.
    Includes personalized referral links for viral loop.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.email_service import email_service
    
    # Get top product
    cursor = db.products.find(
        {"launch_score": {"$gte": 60}},
        {"_id": 0}
    ).sort([("launch_score", -1), ("market_score", -1)]).limit(4)
    products = await cursor.to_list(4)
    
    if not products:
        return {"status": "skipped", "reason": "No qualifying products", "sent": 0}
    
    featured = products[0]
    runners_up = products[1:4] if len(products) > 1 else []
    
    # Build product data with runners_up for the email template
    product_data = {
        "id": featured["id"],
        "product_name": featured.get("product_name"),
        "category": featured.get("category"),
        "launch_score": featured.get("launch_score", 0),
        "trend_stage": featured.get("trend_stage"),
        "margin_range": _get_margin_range(featured.get("estimated_margin", 0)),
        "_runners_up": [
            {
                "product_name": p.get("product_name"),
                "category": p.get("category"),
                "launch_score": p.get("launch_score", 0),
            }
            for p in runners_up
        ],
    }
    
    # Get subscribed users
    subscribed_users = await db.profiles.find(
        {"email": {"$exists": True, "$ne": None}},
        {"_id": 0, "id": 1, "email": 1, "name": 1}
    ).to_list(100)
    
    results = {"status": "completed", "total": len(subscribed_users), "sent": 0, "failed": 0, "product": featured.get("product_name")}
    
    for user in subscribed_users:
        # Get user's referral code for viral loop
        referral = await db.user_referrals.find_one({"user_id": user.get("id")}, {"_id": 0, "referral_code": 1})
        referral_code = referral.get("referral_code") if referral else None
        
        try:
            result = await email_service.send_product_of_the_week(
                to_email=user.get("email"),
                user_name=user.get("name", user.get("email", "").split("@")[0]),
                product=product_data,
                referral_code=referral_code,
            )
            if result.get("status") == "success":
                results["sent"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["failed"] += 1
            logger.error(f"POTW email error for {user.get('email')}: {e}")
    
    return results


@api_router.post("/newsletter/subscribe")
async def subscribe_newsletter(request: Request):
    """
    Subscribe an email to the Product of the Week newsletter.
    Public endpoint - no auth required.
    """
    body = await request.json()
    email = body.get("email", "").strip().lower()

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")

    # Check if already subscribed
    existing = await db.newsletter_subscribers.find_one({"email": email})
    if existing:
        if existing.get("status") == "active":
            return {"status": "already_subscribed", "email": email}
        # Reactivate
        await db.newsletter_subscribers.update_one(
            {"email": email},
            {"$set": {"status": "active", "resubscribed_at": datetime.now(timezone.utc).isoformat()}}
        )
        return {"status": "resubscribed", "email": email}

    await db.newsletter_subscribers.insert_one({
        "email": email,
        "status": "active",
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
        "source": "landing_page",
    })

    return {"status": "subscribed", "email": email}


@api_router.post("/newsletter/unsubscribe")
async def unsubscribe_newsletter(request: Request):
    """Unsubscribe from the newsletter."""
    body = await request.json()
    email = body.get("email", "").strip().lower()

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    result = await db.newsletter_subscribers.update_one(
        {"email": email},
        {"$set": {"status": "unsubscribed", "unsubscribed_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {"status": "unsubscribed", "email": email}

@notifications_router.get("/")
async def get_notifications(
    current_user: AuthenticatedUser = Depends(get_current_user),
    limit: int = 50,
    unread_only: bool = False,
    types: Optional[str] = None
):
    """
    Get user's notifications.
    
    Args:
        limit: Max notifications to return (default 50)
        unread_only: Only return unread notifications
        types: Comma-separated list of notification types to filter
    """
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    
    # Parse types if provided
    type_list = None
    if types:
        type_list = [t.strip() for t in types.split(",")]
    
    notifications = await notification_service.get_notifications(
        user_id=current_user.user_id,
        limit=limit,
        unread_only=unread_only,
        notification_types=type_list
    )
    
    unread_count = await notification_service.get_unread_count(current_user.user_id)
    
    return {
        "notifications": notifications,
        "count": len(notifications),
        "unread_count": unread_count
    }


@notifications_router.get("/unread-count")
async def get_unread_count(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get count of unread notifications"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    count = await notification_service.get_unread_count(current_user.user_id)
    
    return {"unread_count": count}


@notifications_router.post("/mark-read")
async def mark_notifications_read(
    notification_ids: List[str],
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Mark specific notifications as read"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    modified = await notification_service.mark_as_read(
        user_id=current_user.user_id,
        notification_ids=notification_ids
    )
    
    return {"status": "success", "modified_count": modified}


@notifications_router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Mark all notifications as read"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    modified = await notification_service.mark_all_as_read(current_user.user_id)
    
    return {"status": "success", "modified_count": modified}


@notifications_router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Delete a specific notification"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    deleted = await notification_service.delete_notification(
        user_id=current_user.user_id,
        notification_id=notification_id
    )
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"status": "deleted"}


@notifications_router.get("/preferences")
async def get_notification_preferences(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get user's notification preferences"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    prefs = await notification_service.get_user_preferences(current_user.user_id)
    
    return prefs


class NotificationPreferencesUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    alert_threshold: Optional[int] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    watchlist_priority_enabled: Optional[bool] = None
    notification_types: Optional[Dict[str, bool]] = None


@notifications_router.put("/preferences")
async def update_notification_preferences(
    updates: NotificationPreferencesUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update user's notification preferences"""
    from services.notification_service import create_notification_service
    
    notification_service = create_notification_service(db)
    
    # Convert to dict, excluding None values
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    
    prefs = await notification_service.update_user_preferences(
        user_id=current_user.user_id,
        updates=update_dict
    )
    
    return prefs


@notifications_router.post("/test-alert")
async def send_test_notification(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Send a test notification to the current user (for testing)"""
    from services.notification_service import create_notification_service, NotificationType
    
    notification_service = create_notification_service(db)
    
    # Get a sample product
    product = await db.products.find_one(
        {"launch_score": {"$gte": 75}},
        {"_id": 0}
    )
    
    if not product:
        raise HTTPException(status_code=404, detail="No products with high launch score found")
    
    notification = await notification_service.create_notification(
        user_id=current_user.user_id,
        notification_type=NotificationType.STRONG_LAUNCH,
        product=product,
        force=True  # Skip dedup for test
    )
    
    if notification:
        return {
            "status": "success",
            "message": "Test notification sent",
            "notification": notification
        }
    else:
        return {
            "status": "skipped",
            "message": "Notification was skipped (check preferences)"
        }



# =====================
# ROUTES - User / Onboarding
# =====================

@user_router.get("/onboarding-status")
async def get_onboarding_status(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Check if user has completed onboarding"""
    profile = await db.profiles.find_one(
        {"id": current_user.user_id},
        {"_id": 0, "onboarding_completed": 1}
    )
    
    return {
        "onboarding_completed": profile.get("onboarding_completed", False) if profile else False
    }


@user_router.post("/complete-onboarding")
async def complete_onboarding(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Mark onboarding as completed for the user"""
    await db.profiles.update_one(
        {"id": current_user.user_id},
        {
            "$set": {
                "onboarding_completed": True,
                "onboarding_completed_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    return {"status": "success", "onboarding_completed": True}


@user_router.post("/reset-onboarding")
async def reset_onboarding(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Reset onboarding status (for testing)"""
    await db.profiles.update_one(
        {"id": current_user.user_id},
        {
            "$set": {
                "onboarding_completed": False,
                "onboarding_completed_at": None
            }
        }
    )
    
    return {"status": "success", "onboarding_completed": False}


@user_router.get("/admin-status")
async def get_admin_status(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Check if current user is an admin"""
    profile = await db.profiles.find_one(
        {"id": current_user.user_id},
        {"_id": 0, "is_admin": 1, "email": 1}
    )
    
    is_admin = profile.get("is_admin", False) if profile else False
    
    return {
        "is_admin": is_admin,
        "user_id": current_user.user_id
    }


@user_router.post("/set-admin")
async def set_admin_status(
    email: str,
    is_admin: bool = True,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Set admin status for a user by email.
    Requires API key for security.
    """
    # Verify API key
    valid_key = os.environ.get('ADMIN_API_KEY', 'vs_admin_key_2024')
    if api_key != valid_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Find user by email
    profile = await db.profiles.find_one({"email": email}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"User with email {email} not found")
    
    # Update admin status
    await db.profiles.update_one(
        {"email": email},
        {"$set": {
            "is_admin": is_admin,
            "admin_set_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "status": "success",
        "email": email,
        "is_admin": is_admin
    }


# =====================
# ROUTES - Authentication
# =====================

@auth_router.get("/profile")
async def auth_profile(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Get the current user's profile."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile:
        # Create a minimal profile if one doesn't exist yet
        profile = {
            "id": current_user.user_id,
            "email": current_user.email,
            "is_admin": current_user.email == "jenkinslisa1978@gmail.com",
            "subscription_plan": "free",
        }
        await db.profiles.update_one(
            {"id": current_user.user_id},
            {"$set": profile},
            upsert=True,
        )
    return profile


@auth_router.post("/register")
async def auth_register(request: Request):
    """Register a new account."""
    import bcrypt
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    full_name = body.get("full_name", "")

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    # Check if email already registered
    existing = await db.auth_users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered. Try logging in.")

    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    await db.auth_users.insert_one({
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # Create profile
    is_admin = email == "jenkinslisa1978@gmail.com"
    await db.profiles.update_one(
        {"email": email},
        {"$set": {
            "id": user_id,
            "email": email,
            "name": full_name or email.split("@")[0],
            "is_admin": is_admin,
            "subscription_plan": "elite" if is_admin else "free",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )

    # Generate JWT
    token = _generate_auth_token(user_id, email)

    return {
        "token": token,
        "user": {"id": user_id, "email": email, "full_name": full_name},
    }


@auth_router.post("/login")
async def auth_login(request: Request):
    """Login using backend auth (bypasses Supabase)."""
    import bcrypt
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = await db.auth_users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _generate_auth_token(user["id"], email)

    return {
        "token": token,
        "user": {"id": user["id"], "email": email, "full_name": user.get("full_name", "")},
    }


def _generate_auth_token(user_id: str, email: str) -> str:
    """Generate a JWT compatible with the existing auth middleware."""
    import time
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "iat": int(time.time()),
        "exp": int(time.time()) + 60 * 60 * 24 * 7,  # 7 days
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@stripe_router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription upgrade"""
    from services.subscription_service import create_subscription_service
    
    subscription_service = create_subscription_service(db)
    
    # Get user email
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    user_email = profile.get("email") if profile else current_user.email
    
    result = await subscription_service.create_checkout_session(
        user_id=current_user.user_id,
        user_email=user_email,
        plan=request.plan,
        success_url=request.success_url,
        cancel_url=request.cancel_url
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Checkout failed"))
    
    return result


@stripe_router.post("/create-portal-session")
async def create_portal_session(
    request: PortalSessionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Create Stripe customer portal session for billing management"""
    from services.subscription_service import create_subscription_service
    
    subscription_service = create_subscription_service(db)
    
    result = await subscription_service.create_portal_session(
        user_id=current_user.user_id,
        return_url=request.return_url
    )
    
    if not result.get("success"):
        if result.get("demo_mode"):
            return {"url": request.return_url, "demo_mode": True}
        raise HTTPException(status_code=400, detail=result.get("error", "Portal session failed"))
    
    return result


@stripe_router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks for subscription events"""
    from services.subscription_service import create_subscription_service
    import stripe as stripe_module
    
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not stripe_key:
        return {"received": True, "demo_mode": True}
    
    try:
        stripe_module.api_key = stripe_key
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # Construct event (with or without signature verification)
        if webhook_secret and sig_header:
            event = stripe_module.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # No webhook secret - parse directly (less secure, for testing)
            import json
            event = json.loads(payload)
        
        subscription_service = create_subscription_service(db)
        result = await subscription_service.handle_webhook_event(event)
        
        return {"received": True, **result}
        
    except stripe_module.error.SignatureVerificationError as e:
        logging.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@stripe_router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Cancel authenticated user's subscription (downgrades to free at period end)"""
    from services.subscription_service import create_subscription_service
    
    subscription_service = create_subscription_service(db)
    result = await subscription_service.downgrade_to_free(current_user.user_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Cancellation failed"))
    
    return result


@stripe_router.get("/plans")
async def get_subscription_plans():
    """Get all available subscription plans with pricing in GBP"""
    from services.subscription_service import get_all_plans
    
    return {
        "plans": get_all_plans(),
        "currency": "gbp",
        "currency_symbol": "£"
    }


@stripe_router.get("/subscription")
async def get_user_subscription(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get current user's subscription status and features"""
    from services.subscription_service import create_subscription_service
    
    subscription_service = create_subscription_service(db)
    subscription = await subscription_service.get_user_subscription(current_user.user_id)
    
    return subscription


@stripe_router.get("/feature-access")
async def get_feature_access(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get user's feature access based on their plan"""
    from services.subscription_service import FeatureGate
    
    # Get user's plan
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    
    # Check if admin - admins get Elite features
    is_admin = profile.get("is_admin", False) if profile else False
    
    # Also check admin by email (for newly logged in admins)
    if not is_admin and current_user.email:
        admin_by_email = await db.profiles.find_one(
            {"email": current_user.email, "is_admin": True}, 
            {"_id": 0}
        )
        if admin_by_email:
            is_admin = True
            # Update the user's profile with admin status
            await db.profiles.update_one(
                {"id": current_user.user_id},
                {"$set": {"is_admin": True, "plan": "elite"}},
                upsert=True
            )
    
    if is_admin:
        plan = "elite"
    else:
        plan = profile.get("plan", "free") if profile else "free"
    
    # Get store count
    store_count = await db.stores.count_documents({"user_id": current_user.user_id})
    
    return {
        "plan": plan,
        "is_admin": is_admin,
        "admin_bypass": is_admin,
        "features": {
            "full_reports": FeatureGate.can_access_full_reports(plan),
            "full_insights": FeatureGate.can_access_full_insights(plan),
            "watchlist": FeatureGate.can_access_watchlist(plan),
            "alerts": FeatureGate.can_access_alerts(plan),
            "early_trends": FeatureGate.can_access_early_trends(plan),
            "automation_insights": FeatureGate.can_access_automation_insights(plan),
            "advanced_opportunities": FeatureGate.can_access_advanced_opportunities(plan),
            "max_stores": FeatureGate.get_max_stores(plan),
            "can_create_store": FeatureGate.can_create_store(plan, store_count),
            "current_store_count": store_count
        }
    }


# Legacy helper functions (kept for backwards compatibility)
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
    include_integrity: bool = False,  # Include data integrity metadata
    canonical_only: bool = True  # Only return canonical products (not merged duplicates)
):
    """Get products with filtering and optional data integrity metadata"""
    query = {}
    
    # Filter to canonical products only (excludes merged duplicates)
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
# ROUTES - Real Data Scraping
# =====================

from services.scrapers.orchestrator import DataIngestionOrchestrator


@ingestion_router.post("/scrape/full")
async def run_full_scrape(
    sources: Optional[List[str]] = None,
    max_products: int = 30,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Run full data scraping from real sources.
    
    Sources: aliexpress, tiktok_trends, amazon_movers, cj_dropshipping
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    orchestrator = DataIngestionOrchestrator(db)
    
    result = await orchestrator.run_full_ingestion(
        sources=sources,
        max_products_per_source=max_products
    )
    
    return result


@ingestion_router.post("/scrape/google-trends")
async def run_google_trends_enrichment(
    max_products: int = 20,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Enrich products with Google Trends velocity data."""
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.scrapers.google_trends_scraper import GoogleTrendsScraper
    scraper = GoogleTrendsScraper(db)
    result = await scraper.enrich_products(max_products=max_products)
    return result


@ingestion_router.post("/scores/recompute")
async def recompute_all_scores(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Recompute all product scores using transparent scoring engine."""
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.scoring import ScoringEngine
    engine = ScoringEngine(db)
    stats = await engine.batch_update_scores(limit=500)
    return stats


@ingestion_router.post("/scrape/{source_name}")
async def run_source_scrape(
    source_name: str,
    max_products: int = 30,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Run scraping for a specific source.
    
    Valid sources: aliexpress, tiktok_trends, amazon_movers, cj_dropshipping
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    valid_sources = ['aliexpress', 'tiktok_trends', 'amazon_movers', 'cj_dropshipping']
    if source_name not in valid_sources:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid source. Valid: {valid_sources}"
        )
    
    orchestrator = DataIngestionOrchestrator(db)
    result = await orchestrator.run_source_ingestion(source_name, max_products)
    
    return result.to_dict()


@ingestion_router.get("/scrape/health")
async def get_scraper_health(source_name: Optional[str] = None):
    """Get health status of scraping sources"""
    orchestrator = DataIngestionOrchestrator(db)
    return await orchestrator.get_source_health(source_name)


@ingestion_router.get("/scrape/history")
async def get_scrape_history(limit: int = 10):
    """Get recent scraping/ingestion runs"""
    orchestrator = DataIngestionOrchestrator(db)
    return await orchestrator.get_ingestion_history(limit)


@ingestion_router.get("/scrape/quality")
async def get_data_quality():
    """Get data quality report (real vs simulated breakdown)"""
    orchestrator = DataIngestionOrchestrator(db)
    return await orchestrator.get_data_quality_report()



# =====================
# ROUTES - Product Identity & Deduplication
# =====================

from services.product_identity import ProductIdentityService


@ingestion_router.post("/dedup/run")
async def run_deduplication(
    dry_run: bool = False,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Run product deduplication process.
    
    Args:
        dry_run: If True, only report duplicates without merging
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    service = ProductIdentityService(db)
    result = await service.run_deduplication(dry_run=dry_run)
    
    return {
        "success": result.success,
        "started_at": result.started_at,
        "completed_at": result.completed_at,
        "duration_seconds": result.duration_seconds,
        "total_products_processed": result.total_products_processed,
        "duplicate_groups_found": result.duplicate_groups_found,
        "products_merged": result.products_merged,
        "canonical_products_created": result.canonical_products_created,
        "canonical_products_updated": result.canonical_products_updated,
        "errors": result.errors
    }


@ingestion_router.get("/dedup/stats")
async def get_dedup_stats():
    """Get statistics about canonical products"""
    service = ProductIdentityService(db)
    return await service.get_canonical_stats()


@ingestion_router.get("/dedup/history")
async def get_dedup_history(limit: int = 10):
    """Get deduplication run history"""
    service = ProductIdentityService(db)
    return await service.get_dedup_history(limit)


@ingestion_router.get("/dedup/find/{product_id}")
async def find_product_duplicates(product_id: str):
    """Find potential duplicates for a specific product"""
    service = ProductIdentityService(db)
    duplicates = await service.find_duplicates_for_product(product_id)
    
    return {
        "product_id": product_id,
        "potential_duplicates": duplicates,
        "count": len(duplicates)
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


# ===================== SUPPLIER ENDPOINTS =====================

@supplier_router.get("/{product_id}")
async def get_product_suppliers(product_id: str):
    """Get all supplier listings for a product. Auto-discovers if none exist."""
    from services.supplier_service import SupplierService
    service = SupplierService(db)
    result = await service.find_suppliers(product_id)
    return result


@supplier_router.post("/{product_id}/find")
async def find_suppliers(product_id: str):
    """Trigger supplier discovery for a product."""
    from services.supplier_service import SupplierService
    service = SupplierService(db)
    
    # Delete existing to force refresh
    await db.product_suppliers.delete_many({"product_id": product_id})
    result = await service.find_suppliers(product_id)
    return result


@supplier_router.post("/{product_id}/select/{supplier_id}")
async def select_supplier(
    product_id: str,
    supplier_id: str,
    authorization: Optional[str] = Header(None),
):
    """Select a supplier for a product."""
    user_id = "anonymous"
    if authorization and authorization.startswith("Bearer "):
        try:
            import jwt
            token = authorization.split(" ")[1]
            payload = jwt.decode(token, os.environ.get('JWT_SECRET', ''), algorithms=["HS256"])
            user_id = payload.get("sub", "anonymous")
        except Exception:
            pass
    
    from services.supplier_service import SupplierService
    service = SupplierService(db)
    result = await service.select_supplier(product_id, supplier_id, user_id)
    return result



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
app.include_router(intelligence_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(email_router)
app.include_router(notifications_router)
app.include_router(user_router)
app.include_router(supplier_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React frontend static files in production
# The frontend build directory is created during deployment
FRONTEND_BUILD_DIR = Path(__file__).parent.parent / "frontend" / "build"

if FRONTEND_BUILD_DIR.exists() and (FRONTEND_BUILD_DIR / "static").exists():
    # Serve static assets (JS, CSS, images, etc.)
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "static")), name="static")
    
    # Catch-all route for SPA - must be AFTER all API routes
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve React app for all non-API routes (SPA catch-all)"""
        # If the request is for a file that exists, serve it
        file_path = FRONTEND_BUILD_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        # Otherwise serve index.html for client-side routing
        return FileResponse(str(FRONTEND_BUILD_DIR / "index.html"))

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
    
    # Report indexes
    await db.reports.create_index("metadata.id", unique=True)
    await db.reports.create_index("metadata.slug", unique=True)
    await db.reports.create_index("metadata.report_type")
    await db.reports.create_index("metadata.is_latest")
    await db.reports.create_index([("metadata.generated_at", -1)])
    
    # Scraping indexes
    await db.scrape_cache.create_index("key", unique=True)
    await db.scrape_cache.create_index("cached_at")
    await db.source_health.create_index("source_name", unique=True)
    await db.ingestion_runs.create_index([("started_at", -1)])
    await db.tiktok_hashtags.create_index("hashtag", unique=True)
    
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
