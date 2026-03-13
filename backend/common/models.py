"""
Pydantic models shared across route modules.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


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
    early_trend_score: int = 0
    early_trend_label: str = "stable"
    view_growth_rate: float = 0.0
    engagement_rate: float = 0.0
    supplier_order_velocity: int = 0
    stores_created: int = 0
    exports_count: int = 0
    success_signals: int = 0
    user_engagement_score: float = 0.0
    success_probability: int = 0
    proven_winner: bool = False
    active_competitor_stores: int = 0
    new_competitor_stores_week: int = 0
    avg_selling_price: float = 0.0
    price_range: Optional[Dict[str, float]] = None
    estimated_monthly_ad_spend: int = 0
    market_saturation: int = 0
    market_score: int = 0
    market_label: str = "medium"
    market_description: Optional[str] = None
    market_score_breakdown: Optional[Dict[str, int]] = None
    margin_score: int = 0
    competition_score: int = 0
    ad_activity_score: int = 0
    supplier_demand_score: int = 0
    launch_score: int = 0
    launch_score_label: str = "risky"
    launch_score_reasoning: Optional[str] = None
    recent_ad_growth: float = 0.0
    new_ads_this_week: int = 0
    ad_platform_distribution: Optional[Dict[str, int]] = None
    ad_validation_level: str = "unknown"
    supplier_link: Optional[str] = None
    supplier_rating: float = 0.0
    supplier_reviews: int = 0
    supplier_orders_30d: int = 0
    supplier_processing_days: int = 3
    supplier_shipping_days: int = 15
    product_variants: Optional[List[str]] = None
    data_source: str = "manual"
    data_source_type: str = "manual"
    confidence_score: int = 50
    last_updated: Optional[str] = None
    scores_updated_at: Optional[str] = None
    competitor_last_updated: Optional[str] = None
    ad_activity_last_updated: Optional[str] = None
    supplier_data_updated: Optional[str] = None
    ai_summary: Optional[str] = None
    is_premium: bool = False
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CheckoutSessionRequest(BaseModel):
    plan: str
    success_url: str
    cancel_url: str
    price_id: Optional[str] = None

class PortalSessionRequest(BaseModel):
    return_url: str

class SubscriptionUpdate(BaseModel):
    new_plan_id: str
    new_price_id: str

class CancelSubscription(BaseModel):
    cancel_at_period_end: bool = True

class ReferralCode(BaseModel):
    code: str
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Referral(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referrer_id: str
    referred_id: str
    referral_code: str
    status: str = "pending"
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

class WatchlistItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
    alert_type: str
    title: str
    message: str
    severity: str = "info"
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Optional[Dict[str, Any]] = None

class RunAutomationRequest(BaseModel):
    job_type: Optional[AutomationJobType] = AutomationJobType.FULL_PIPELINE
    products: Optional[List[Dict[str, Any]]] = None

class StoreStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    EXPORTED = "exported"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class StoreCreate(BaseModel):
    name: str
    product_id: str
    plan: str = "starter"

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
    store_name: Optional[str] = None

class UpdateStoreStatusRequest(BaseModel):
    status: StoreStatus

class ImportRequest(BaseModel):
    category: Optional[str] = None
    limit: int = 20

class CSVImportRequest(BaseModel):
    csv_content: str

class JSONImportRequest(BaseModel):
    json_content: str

class StoreAnalyzeRequest(BaseModel):
    url: str


class LaunchStoreRequest(BaseModel):
    product_id: str
    store_name: Optional[str] = None
    supplier_id: Optional[str] = None

class NotificationPreferencesUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    alert_threshold: Optional[int] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    watchlist_priority_enabled: Optional[bool] = None
    notification_types: Optional[Dict[str, bool]] = None

class ThresholdSubscriptionUpdate(BaseModel):
    enabled: Optional[bool] = None
    score_threshold: Optional[int] = None
    categories: Optional[List[str]] = None
    email_alerts: Optional[bool] = None
    in_app_alerts: Optional[bool] = None

class CompetitorStoreCreate(BaseModel):
    url: str
    name: Optional[str] = None
    notes: Optional[str] = None
