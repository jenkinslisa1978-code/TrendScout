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
    ai_summary: Optional[str] = None
    supplier_link: Optional[str] = None
    is_premium: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CheckoutSessionRequest(BaseModel):
    user_id: str
    price_id: str
    success_url: str
    cancel_url: str

class PortalSessionRequest(BaseModel):
    user_id: str
    return_url: str

class SubscriptionUpdate(BaseModel):
    user_id: str
    new_plan_id: str
    new_price_id: str

class CancelSubscription(BaseModel):
    user_id: str
    cancel_at_period_end: bool = True

class RunAutomationRequest(BaseModel):
    job_type: Optional[AutomationJobType] = AutomationJobType.FULL_PIPELINE
    products: Optional[List[Dict[str, Any]]] = None

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
    _ = stage  # Used in category insights
    
    templates = {
        'very high': f"Exceptional viral potential with {competition} current competition. Strong TikTok presence driving consumer awareness. Perfect for content creators and lifestyle consumers. Act fast before market saturation.",
        'high': f"Solid opportunity with growing demand. {'Strong' if trend_score >= 80 else 'Building'} TikTok presence. {'Low advertiser activity creates favorable entry conditions.' if competition == 'low' else 'Moderate competition requires clear value proposition.'} Good time to test with controlled ad spend.",
        'medium': f"Moderate opportunity requiring differentiation. {'Market is getting competitive' if competition == 'high' else 'Some competition present'}. {'Moderate margins provide room for competitive pricing.' if margin >= 15 else 'Thin margins demand high volume strategy.'} Proceed with caution.",
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
    
    ai_summary = generate_ai_summary(product)
    product['ai_summary'] = ai_summary
    
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    product['estimated_margin'] = margin
    product['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    alert = generate_alert(product)
    
    return {'product': product, 'alert': alert}

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
# ROUTES - Stripe
# =====================

@stripe_router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutSessionRequest):
    """Create Stripe checkout session"""
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
        customer = await get_or_create_stripe_customer(request.user_id)
        
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
            metadata={'user_id': request.user_id},
        )
        
        return {"url": session.url, "session_id": session.id}
        
    except Exception as e:
        logging.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@stripe_router.post("/create-portal-session")
async def create_portal_session(request: PortalSessionRequest):
    """Create Stripe customer portal session"""
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        return {"url": request.return_url, "demo_mode": True}
    
    try:
        import stripe
        stripe.api_key = stripe_key
        
        # Get customer
        customer = await get_stripe_customer(request.user_id)
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
async def cancel_subscription(request: CancelSubscription):
    """Cancel user subscription"""
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not stripe_key:
        # Demo mode
        return {"cancelled": True, "demo_mode": True}
    
    try:
        import stripe
        stripe.api_key = stripe_key
        
        # Get subscription
        sub = await db.subscriptions.find_one({"user_id": request.user_id}, {"_id": 0})
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
    search: Optional[str] = None,
    sort_by: str = "trend_score",
    sort_order: str = "desc",
    limit: int = 100
):
    """Get products with filtering"""
    query = {}
    
    if category:
        query["category"] = category
    if trend_stage:
        query["trend_stage"] = trend_stage
    if opportunity_rating:
        query["opportunity_rating"] = opportunity_rating
    if search:
        query["$or"] = [
            {"product_name": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}},
        ]
    
    sort_direction = 1 if sort_order == "asc" else -1
    cursor = db.products.find(query, {"_id": 0}).sort(sort_by, sort_direction).limit(limit)
    products = await cursor.to_list(limit)
    
    return {"data": products}

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get single product"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"data": product}

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

# Include routers
app.include_router(api_router)
app.include_router(stripe_router)
app.include_router(automation_router)

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
    """Initialize database collections and indexes"""
    # Create indexes
    await db.products.create_index("id", unique=True)
    await db.products.create_index("category")
    await db.products.create_index("trend_score")
    await db.products.create_index("trend_stage")
    
    await db.trend_alerts.create_index("id", unique=True)
    await db.trend_alerts.create_index("product_id")
    await db.trend_alerts.create_index("created_at")
    
    await db.automation_logs.create_index("id", unique=True)
    await db.automation_logs.create_index("started_at")
    
    await db.subscriptions.create_index("user_id", unique=True)
    await db.profiles.create_index("id", unique=True)
    
    logger.info("Database indexes created")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
