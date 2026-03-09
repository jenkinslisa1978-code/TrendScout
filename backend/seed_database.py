"""
Database Seeding Script for ViralScout

Run this script to populate the database with realistic sample data.
Usage: python seed_database.py
"""

import asyncio
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import random

# Load environment
load_dotenv()

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'viralscout')

# Sample product data
SAMPLE_PRODUCTS = [
    {
        "product_name": "Portable Neck Fan",
        "category": "Electronics",
        "short_description": "Hands-free personal cooling device with LED display and 3 speed settings",
        "supplier_cost": 8.50,
        "estimated_retail_price": 29.99,
        "tiktok_views": 15400000,
        "ad_count": 234,
        "competition_level": "medium",
        "supplier_link": "https://alibaba.com/example1",
        "is_premium": False
    },
    {
        "product_name": "Magnetic Phone Mount",
        "category": "Mobile Accessories",
        "short_description": "MagSafe compatible car mount with 360° rotation and strong magnets",
        "supplier_cost": 4.20,
        "estimated_retail_price": 24.99,
        "tiktok_views": 8200000,
        "ad_count": 156,
        "competition_level": "high",
        "supplier_link": "https://alibaba.com/example2",
        "is_premium": False
    },
    {
        "product_name": "Sunset Projection Lamp",
        "category": "Home Decor",
        "short_description": "USB-powered ambient light projector creating viral sunset aesthetics",
        "supplier_cost": 6.80,
        "estimated_retail_price": 32.99,
        "tiktok_views": 28900000,
        "ad_count": 89,
        "competition_level": "low",
        "supplier_link": "https://alibaba.com/example3",
        "is_premium": True
    },
    {
        "product_name": "LED Strip Lights RGB",
        "category": "Home Decor",
        "short_description": "App-controlled smart LED strips with music sync and 16M colors",
        "supplier_cost": 5.40,
        "estimated_retail_price": 19.99,
        "tiktok_views": 45000000,
        "ad_count": 412,
        "competition_level": "high",
        "supplier_link": "https://alibaba.com/example4",
        "is_premium": False
    },
    {
        "product_name": "Wireless Earbuds Pro",
        "category": "Audio",
        "short_description": "ANC wireless earbuds with 40hr battery life and premium sound",
        "supplier_cost": 12.00,
        "estimated_retail_price": 49.99,
        "tiktok_views": 12300000,
        "ad_count": 278,
        "competition_level": "high",
        "supplier_link": "https://alibaba.com/example5",
        "is_premium": False
    },
    {
        "product_name": "Cloud Slippers",
        "category": "Fashion",
        "short_description": "Ultra-soft EVA sole slippers with pressure-relief technology",
        "supplier_cost": 3.80,
        "estimated_retail_price": 22.99,
        "tiktok_views": 67000000,
        "ad_count": 523,
        "competition_level": "high",
        "supplier_link": "https://alibaba.com/example6",
        "is_premium": False
    },
    {
        "product_name": "Aesthetic Desk Organizer",
        "category": "Home Office",
        "short_description": "Minimalist acrylic desk organizer with multiple compartments",
        "supplier_cost": 7.20,
        "estimated_retail_price": 34.99,
        "tiktok_views": 4500000,
        "ad_count": 67,
        "competition_level": "low",
        "supplier_link": "https://alibaba.com/example7",
        "is_premium": True
    },
    {
        "product_name": "Smart Water Bottle",
        "category": "Health & Fitness",
        "short_description": "Temperature display water bottle with hydration reminders",
        "supplier_cost": 9.50,
        "estimated_retail_price": 39.99,
        "tiktok_views": 9800000,
        "ad_count": 145,
        "competition_level": "medium",
        "supplier_link": "https://alibaba.com/example8",
        "is_premium": False
    },
    {
        "product_name": "Portable Blender",
        "category": "Kitchen",
        "short_description": "USB-C rechargeable personal blender for smoothies on-the-go",
        "supplier_cost": 11.00,
        "estimated_retail_price": 44.99,
        "tiktok_views": 31000000,
        "ad_count": 389,
        "competition_level": "high",
        "supplier_link": "https://alibaba.com/example9",
        "is_premium": False
    },
    {
        "product_name": "Mini Projector",
        "category": "Electronics",
        "short_description": "Pocket-sized 1080p projector with WiFi casting and built-in speaker",
        "supplier_cost": 45.00,
        "estimated_retail_price": 149.99,
        "tiktok_views": 18700000,
        "ad_count": 198,
        "competition_level": "medium",
        "supplier_link": "https://alibaba.com/example10",
        "is_premium": True
    },
    {
        "product_name": "Posture Corrector",
        "category": "Health & Fitness",
        "short_description": "Adjustable back support brace for improved posture and reduced pain",
        "supplier_cost": 5.50,
        "estimated_retail_price": 28.99,
        "tiktok_views": 22000000,
        "ad_count": 312,
        "competition_level": "medium",
        "supplier_link": "https://alibaba.com/example11",
        "is_premium": False
    },
    {
        "product_name": "Car Phone Holder",
        "category": "Mobile Accessories",
        "short_description": "Dashboard mount with wireless charging and auto-grip sensor",
        "supplier_cost": 8.00,
        "estimated_retail_price": 35.99,
        "tiktok_views": 5600000,
        "ad_count": 89,
        "competition_level": "low",
        "supplier_link": "https://alibaba.com/example12",
        "is_premium": False
    },
    {
        "product_name": "Pet Hair Remover",
        "category": "Home Care",
        "short_description": "Self-cleaning lint roller for furniture, clothes, and car seats",
        "supplier_cost": 2.80,
        "estimated_retail_price": 16.99,
        "tiktok_views": 41000000,
        "ad_count": 456,
        "competition_level": "high",
        "supplier_link": "https://alibaba.com/example13",
        "is_premium": False
    },
    {
        "product_name": "Keyboard Cleaning Gel",
        "category": "Tech Accessories",
        "short_description": "Reusable cleaning putty for keyboards, vents, and electronics",
        "supplier_cost": 1.20,
        "estimated_retail_price": 9.99,
        "tiktok_views": 8900000,
        "ad_count": 178,
        "competition_level": "medium",
        "supplier_link": "https://alibaba.com/example14",
        "is_premium": False
    },
    {
        "product_name": "Galaxy Projector",
        "category": "Home Decor",
        "short_description": "Smart LED star projector with music sync and app control",
        "supplier_cost": 15.00,
        "estimated_retail_price": 54.99,
        "tiktok_views": 35000000,
        "ad_count": 267,
        "competition_level": "medium",
        "supplier_link": "https://alibaba.com/example15",
        "is_premium": True
    }
]

# Automation calculation functions
def calculate_trend_score(product):
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    
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
    comp_scores = {'low': 100, 'medium': 60, 'high': 30}
    competition_score = comp_scores.get(competition_level, 50)
    
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
    
    weighted_score = (
        tiktok_score * 0.35 +
        ad_score * 0.20 +
        competition_score * 0.20 +
        margin_score * 0.25
    )
    
    return min(100, max(0, round(weighted_score)))

def calculate_trend_stage(product):
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    competition_level = product.get('competition_level', 'medium')
    
    signals = {'early': 0, 'rising': 0, 'peak': 0, 'saturated': 0}
    
    if tiktok_views >= 30000000:
        signals['peak'] += 40
    elif tiktok_views >= 5000000:
        signals['rising'] += 40
    else:
        signals['early'] += 40
    
    if ad_count >= 400:
        signals['saturated'] += 35
    elif ad_count >= 200:
        signals['peak'] += 35
    elif ad_count >= 50:
        signals['rising'] += 35
    else:
        signals['early'] += 35
    
    if competition_level == 'high':
        signals['saturated'] += 25
    elif competition_level == 'medium':
        signals['rising'] += 25
    else:
        signals['early'] += 25
    
    return max(signals, key=signals.get)

def calculate_opportunity_rating(product):
    trend_score = product.get('trend_score', 0)
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    margin_percent = (margin / product.get('estimated_retail_price', 1)) * 100 if product.get('estimated_retail_price', 0) > 0 else 0
    competition_level = product.get('competition_level', 'medium')
    trend_stage = product.get('trend_stage', 'rising')
    
    score = 0
    score += (trend_score / 100) * 40
    
    margin_score = 0
    if margin >= 50:
        margin_score += 50
    elif margin >= 25:
        margin_score += 40
    else:
        margin_score += 25
    
    if margin_percent >= 50:
        margin_score += 50
    else:
        margin_score += 30
    
    score += (margin_score / 100) * 25
    
    comp_scores = {'low': 100, 'medium': 60, 'high': 25}
    score += (comp_scores.get(competition_level, 50) / 100) * 20
    
    stage_scores = {'early': 100, 'rising': 85, 'peak': 50, 'saturated': 15}
    score += (stage_scores.get(trend_stage, 50) / 100) * 15
    
    score = min(100, max(0, score))
    
    if score >= 85:
        return 'very high'
    elif score >= 70:
        return 'high'
    elif score >= 50:
        return 'medium'
    return 'low'

def generate_ai_summary(product):
    opportunity = product.get('opportunity_rating', 'medium')
    competition = product.get('competition_level', 'medium')
    trend_score = product.get('trend_score', 50)
    margin = product.get('estimated_retail_price', 0) - product.get('supplier_cost', 0)
    
    templates = {
        'very high': f"Exceptional viral potential with {competition} current competition. Strong TikTok presence driving awareness. Perfect timing for market entry. Act fast before saturation.",
        'high': f"Solid opportunity with growing demand. {'Strong' if trend_score >= 80 else 'Building'} social presence. Good time to test with controlled ad spend.",
        'medium': f"Moderate opportunity requiring differentiation. Some competition present. {'Good margins available.' if margin >= 15 else 'Focus on volume.'} Proceed strategically.",
        'low': f"Challenging market conditions due to {competition} competition. Consider alternative products or unique positioning.",
    }
    
    return templates.get(opportunity, templates['medium'])

def process_product(product):
    """Process a product through the automation pipeline"""
    product['id'] = str(uuid.uuid4())
    product['trend_stage'] = calculate_trend_stage(product)
    product['trend_score'] = calculate_trend_score(product)
    product['opportunity_rating'] = calculate_opportunity_rating(product)
    product['ai_summary'] = generate_ai_summary(product)
    product['estimated_margin'] = product['estimated_retail_price'] - product['supplier_cost']
    product['created_at'] = datetime.now(timezone.utc).isoformat()
    product['updated_at'] = datetime.now(timezone.utc).isoformat()
    return product

async def seed_database():
    """Main seeding function"""
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("Clearing existing data...")
    await db.products.delete_many({})
    await db.trend_alerts.delete_many({})
    await db.automation_logs.delete_many({})
    
    print("Processing and inserting products...")
    processed_products = [process_product(p.copy()) for p in SAMPLE_PRODUCTS]
    await db.products.insert_many(processed_products)
    print(f"  Inserted {len(processed_products)} products")
    
    # Generate alerts for qualifying products
    print("Generating alerts...")
    alerts = []
    for product in processed_products:
        if product['trend_score'] >= 75 and product['opportunity_rating'] in ['high', 'very high']:
            alert = {
                'id': str(uuid.uuid4()),
                'product_id': product['id'],
                'product_name': product['product_name'],
                'alert_type': 'early_stage' if product['trend_stage'] == 'early' else 'rising_trend',
                'priority': 'critical' if product['trend_score'] >= 90 else 'high',
                'title': f"{'Early Stage Winner' if product['trend_stage'] == 'early' else 'Rising Trend'}: {product['product_name']}",
                'body': f"Product detected with {product['trend_score']} trend score and {product['opportunity_rating']} opportunity.",
                'trend_score': product['trend_score'],
                'opportunity_rating': product['opportunity_rating'],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'read': False,
                'dismissed': False,
            }
            alerts.append(alert)
    
    if alerts:
        await db.trend_alerts.insert_many(alerts)
        print(f"  Created {len(alerts)} alerts")
    
    # Create automation log
    print("Creating automation log...")
    log = {
        'id': str(uuid.uuid4()),
        'job_type': 'product_import',
        'status': 'completed',
        'started_at': datetime.now(timezone.utc).isoformat(),
        'completed_at': datetime.now(timezone.utc).isoformat(),
        'products_processed': len(processed_products),
        'alerts_generated': len(alerts),
        'import_source': 'seed_script',
        'metadata': {'seeded': True},
    }
    await db.automation_logs.insert_one(log)
    
    # Create sample demo profile
    print("Creating demo profile...")
    demo_profile = {
        'id': 'demo-user-id',
        'email': 'demo@viralscout.com',
        'full_name': 'Demo User',
        'role': 'admin',
        'plan': 'elite',
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    await db.profiles.update_one(
        {'id': demo_profile['id']},
        {'$set': demo_profile},
        upsert=True
    )
    
    # Create demo subscription
    print("Creating demo subscription...")
    demo_sub = {
        'id': 'demo-sub-id',
        'user_id': 'demo-user-id',
        'plan_name': 'elite',
        'status': 'active',
        'stripe_subscription_id': None,
        'stripe_customer_id': None,
        'current_period_start': datetime.now(timezone.utc).isoformat(),
        'current_period_end': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        'cancel_at_period_end': False,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    await db.subscriptions.update_one(
        {'user_id': demo_sub['user_id']},
        {'$set': demo_sub},
        upsert=True
    )
    
    print("\n✅ Database seeded successfully!")
    print(f"   - {len(processed_products)} products")
    print(f"   - {len(alerts)} alerts")
    print(f"   - 1 demo profile (admin/elite)")
    print(f"   - 1 automation log")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
