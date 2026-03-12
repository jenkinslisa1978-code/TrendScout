"""
Task Registry and Definitions

Defines all background tasks that can be run:
- ingest_trending_products
- update_market_scores
- update_competitor_data
- generate_alerts

Each task is a self-contained unit that:
- Takes a database connection
- Performs the work
- Returns results with record counts
"""

import logging
from typing import Dict, Any, Callable, Awaitable, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# Type for task functions
TaskFunction = Callable[[Any, Dict[str, Any]], Awaitable[Dict[str, Any]]]


class TaskRegistry:
    """
    Registry of all available background tasks.
    
    Each task is registered with:
    - name: Unique identifier
    - function: Async function to execute
    - description: Human-readable description
    - default_schedule: Cron expression for automatic scheduling
    """
    
    _tasks: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(
        cls, 
        name: str, 
        description: str = "",
        default_schedule: str = None
    ):
        """Decorator to register a task"""
        def decorator(func: TaskFunction):
            cls._tasks[name] = {
                'name': name,
                'function': func,
                'description': description,
                'default_schedule': default_schedule,
            }
            logger.info(f"Registered task: {name}")
            return func
        return decorator
    
    @classmethod
    def get_task(cls, name: str) -> TaskFunction:
        """Get a task function by name"""
        task = cls._tasks.get(name)
        if task:
            return task['function']
        raise ValueError(f"Unknown task: {name}")
    
    @classmethod
    def get_all_tasks(cls) -> Dict[str, Dict[str, Any]]:
        """Get all registered tasks"""
        return {
            name: {
                'name': task['name'],
                'description': task['description'],
                'default_schedule': task['default_schedule'],
            }
            for name, task in cls._tasks.items()
        }
    
    @classmethod
    def get_scheduled_tasks(cls) -> List[Dict[str, Any]]:
        """Get tasks that have a default schedule"""
        return [
            {
                'name': task['name'],
                'description': task['description'],
                'schedule': task['default_schedule'],
            }
            for task in cls._tasks.values()
            if task['default_schedule']
        ]


# =====================
# TASK DEFINITIONS
# =====================

@TaskRegistry.register(
    name="ingest_trending_products",
    description="Fetch trending products from TikTok and Amazon sources",
    default_schedule="0 */4 * * *"  # Every 4 hours
)
async def ingest_trending_products(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest trending products from all sources.
    
    Sources: TikTok trends, Amazon BSR movers
    """
    from services.data_sources import TikTokTrends, AmazonTrends
    
    results = {
        'sources': {},
        'total_created': 0,
        'total_updated': 0,
        'errors': []
    }
    
    # TikTok trends
    try:
        tiktok = TikTokTrends(db)
        tiktok_result = await tiktok.fetch(limit=params.get('limit', 25))
        
        if tiktok_result.success:
            stats = await tiktok.update_database(tiktok_result)
            results['sources']['tiktok'] = {
                'fetched': tiktok_result.items_count,
                'created': stats['created'],
                'updated': stats['updated'],
            }
            results['total_created'] += stats['created']
            results['total_updated'] += stats['updated']
        else:
            results['errors'].append(f"TikTok: {tiktok_result.error_message}")
            
    except Exception as e:
        logger.error(f"TikTok ingestion error: {e}")
        results['errors'].append(f"TikTok: {str(e)}")
    
    # Amazon trends
    try:
        amazon = AmazonTrends(db)
        amazon_result = await amazon.fetch(limit=params.get('limit', 15))
        
        if amazon_result.success:
            stats = await amazon.update_database(amazon_result)
            results['sources']['amazon'] = {
                'fetched': amazon_result.items_count,
                'created': stats['created'],
                'updated': stats['updated'],
            }
            results['total_created'] += stats['created']
            results['total_updated'] += stats['updated']
        else:
            results['errors'].append(f"Amazon: {amazon_result.error_message}")
            
    except Exception as e:
        logger.error(f"Amazon ingestion error: {e}")
        results['errors'].append(f"Amazon: {str(e)}")
    
    return {
        'records_processed': results['total_created'] + results['total_updated'],
        'details': results,
    }


@TaskRegistry.register(
    name="update_market_scores",
    description="Recalculate market scores for all products",
    default_schedule="0 */2 * * *"  # Every 2 hours
)
async def update_market_scores(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update market scores using the scoring engine.
    
    Calculates: trend_score, margin_score, competition_score, 
                ad_activity_score, supplier_demand_score, market_score
    """
    from services.scoring import ScoringEngine
    
    scoring_engine = ScoringEngine(db)
    limit = params.get('limit', 500)
    
    stats = await scoring_engine.batch_update_scores(limit=limit)
    
    return {
        'records_processed': stats['updated'],
        'details': {
            'updated': stats['updated'],
            'failed': stats['failed'],
        },
    }


@TaskRegistry.register(
    name="update_competitor_data",
    description="Update competitor intelligence for all products",
    default_schedule="0 */6 * * *"  # Every 6 hours
)
async def update_competitor_data(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update competitor data (store counts, pricing, saturation).
    """
    from services.data_sources import CompetitorIntelligence
    
    analyzer = CompetitorIntelligence(db)
    limit = params.get('limit', 200)
    
    stats = await analyzer.batch_update_competitors(limit=limit)
    
    return {
        'records_processed': stats['updated'],
        'details': {
            'updated': stats['updated'],
            'failed': stats['failed'],
        },
    }


@TaskRegistry.register(
    name="update_ad_activity",
    description="Update ad activity signals for all products",
    default_schedule="0 */4 * * *"  # Every 4 hours
)
async def update_ad_activity(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update ad activity signals (ad counts, growth, platform distribution).
    """
    from services.data_sources import AdActivityAnalyzer
    
    analyzer = AdActivityAnalyzer(db)
    limit = params.get('limit', 200)
    
    stats = await analyzer.batch_update_ad_activity(limit=limit)
    
    return {
        'records_processed': stats['updated'],
        'details': {
            'updated': stats['updated'],
            'failed': stats['failed'],
        },
    }


@TaskRegistry.register(
    name="update_supplier_data",
    description="Merge supplier data from AliExpress and CJ Dropshipping",
    default_schedule="0 */6 * * *"  # Every 6 hours
)
async def update_supplier_data(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch and merge supplier data (costs, order velocity, shipping times).
    """
    from services.data_sources import AliExpressProducts, CJDropshippingProducts
    
    results = {
        'sources': {},
        'total_merged': 0,
        'errors': []
    }
    
    # AliExpress
    try:
        aliexpress = AliExpressProducts(db)
        ae_result = await aliexpress.fetch(limit=params.get('limit', 20))
        
        if ae_result.success:
            # Merge supplier data into existing products
            merged = await _merge_supplier_data(db, ae_result.data)
            results['sources']['aliexpress'] = {
                'fetched': ae_result.items_count,
                'merged': merged,
            }
            results['total_merged'] += merged
            
    except Exception as e:
        logger.error(f"AliExpress error: {e}")
        results['errors'].append(f"AliExpress: {str(e)}")
    
    # CJ Dropshipping
    try:
        cj = CJDropshippingProducts(db)
        cj_result = await cj.fetch(limit=params.get('limit', 15))
        
        if cj_result.success:
            merged = await _merge_supplier_data(db, cj_result.data)
            results['sources']['cj_dropshipping'] = {
                'fetched': cj_result.items_count,
                'merged': merged,
            }
            results['total_merged'] += merged
            
    except Exception as e:
        logger.error(f"CJ Dropshipping error: {e}")
        results['errors'].append(f"CJ: {str(e)}")
    
    return {
        'records_processed': results['total_merged'],
        'details': results,
    }


async def _merge_supplier_data(db, supplier_products: List[Dict]) -> int:
    """Helper to merge supplier data into existing products"""
    merged_count = 0
    
    for supplier_product in supplier_products:
        product_name = supplier_product.get('product_name', '')
        
        # Find matching product
        existing = await db.products.find_one({
            "product_name": {"$regex": product_name, "$options": "i"}
        })
        
        if existing:
            # Update supplier fields
            supplier_fields = {
                'supplier_cost': supplier_product.get('supplier_cost'),
                'supplier_link': supplier_product.get('supplier_link'),
                'supplier_order_velocity': supplier_product.get('supplier_order_velocity'),
                'supplier_rating': supplier_product.get('supplier_rating'),
                'supplier_reviews': supplier_product.get('supplier_reviews'),
                'supplier_orders_30d': supplier_product.get('supplier_orders_30d'),
                'supplier_processing_days': supplier_product.get('supplier_processing_days'),
                'supplier_shipping_days': supplier_product.get('supplier_shipping_days'),
                'product_variants': supplier_product.get('product_variants'),
            }
            
            # Remove None values
            supplier_fields = {k: v for k, v in supplier_fields.items() if v is not None}
            
            # Recalculate margin
            if supplier_fields.get('supplier_cost') and existing.get('estimated_retail_price'):
                supplier_fields['estimated_margin'] = (
                    existing['estimated_retail_price'] - supplier_fields['supplier_cost']
                )
            
            supplier_fields['supplier_data_updated'] = datetime.now(timezone.utc).isoformat()
            
            await db.products.update_one(
                {"id": existing['id']},
                {"$set": supplier_fields}
            )
            merged_count += 1
    
    return merged_count


@TaskRegistry.register(
    name="generate_alerts",
    description="Generate opportunity alerts for high-scoring products",
    default_schedule="0 * * * *"  # Every hour
)
async def generate_alerts(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate alerts for products meeting opportunity thresholds.
    
    Alerts generated for:
    - market_score >= 90: Massive opportunity
    - market_score >= 75 + early_trend: Early trend opportunity
    - market_score >= 75: Strong opportunity
    """
    import uuid
    
    alerts_created = 0
    
    # Find high-scoring products without recent alerts
    one_hour_ago = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    
    cursor = db.products.find({
        "market_score": {"$gte": 75}
    }, {"_id": 0}).limit(50)
    
    products = await cursor.to_list(50)
    
    for product in products:
        # Check if alert already exists for this product in the last hour
        existing_alert = await db.alerts.find_one({
            "product_id": product['id'],
            "created_at": {"$gte": one_hour_ago.isoformat()}
        })
        
        if existing_alert:
            continue
        
        # Create alert based on score
        market_score = product.get('market_score', 0)
        early_label = product.get('early_trend_label', 'stable')
        
        if market_score >= 90:
            alert_type = 'massive_opportunity'
            priority = 'critical'
            title = f"Massive Opportunity: {product['product_name']}"
        elif market_score >= 75 and early_label in ['exploding', 'rising']:
            alert_type = 'early_trend_opportunity'
            priority = 'high'
            title = f"Early Trend Detected: {product['product_name']}"
        elif market_score >= 75:
            alert_type = 'strong_opportunity'
            priority = 'medium'
            title = f"Strong Opportunity: {product['product_name']}"
        else:
            continue
        
        alert = {
            'id': str(uuid.uuid4()),
            'product_id': product['id'],
            'product_name': product['product_name'],
            'alert_type': alert_type,
            'priority': priority,
            'title': title,
            'message': _generate_alert_message(product),
            'market_score': market_score,
            'market_label': product.get('market_label', 'competitive'),
            'scores': product.get('market_score_breakdown', {}),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'read': False,
        }
        
        await db.alerts.insert_one(alert)
        alerts_created += 1
    
    return {
        'records_processed': alerts_created,
        'details': {
            'alerts_created': alerts_created,
            'products_scanned': len(products),
        },
    }


def _generate_alert_message(product: Dict[str, Any]) -> str:
    """Generate alert message from product data"""
    market_score = product.get('market_score', 0)
    margin = product.get('estimated_margin', 0)
    competition = product.get('competition_level', 'medium')
    competitors = product.get('active_competitor_stores', 0)
    
    parts = [
        f"Market Score: {market_score}/100",
        f"Est. Margin: £{margin:.2f}",
        f"Competition: {competition.title()} ({competitors} stores)",
    ]
    
    if product.get('early_trend_label') in ['exploding', 'rising']:
        parts.append(f"Trend: {product['early_trend_label'].title()}")
    
    return " | ".join(parts)


@TaskRegistry.register(
    name="full_pipeline",
    description="Run complete data pipeline (all sources + scoring + alerts)",
    default_schedule=None  # Manual only
)
async def full_pipeline(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete data pipeline.
    
    Steps:
    1. Ingest trending products
    2. Update supplier data
    3. Update competitor data
    4. Update ad activity
    5. Update market scores
    6. Generate alerts
    """
    results = {
        'steps': {},
        'total_records': 0,
        'errors': []
    }
    
    # Step 1: Ingest trending products
    try:
        step_result = await ingest_trending_products(db, params)
        results['steps']['ingest_trending'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"ingest_trending: {str(e)}")
    
    # Step 2: Update supplier data
    try:
        step_result = await update_supplier_data(db, params)
        results['steps']['update_supplier'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"update_supplier: {str(e)}")
    
    # Step 3: Update competitor data
    try:
        step_result = await update_competitor_data(db, params)
        results['steps']['update_competitor'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"update_competitor: {str(e)}")
    
    # Step 4: Update ad activity
    try:
        step_result = await update_ad_activity(db, params)
        results['steps']['update_ad_activity'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"update_ad_activity: {str(e)}")
    
    # Step 5: Update market scores
    try:
        step_result = await update_market_scores(db, params)
        results['steps']['update_scores'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"update_scores: {str(e)}")
    
    # Step 6: Generate alerts
    try:
        step_result = await generate_alerts(db, params)
        results['steps']['generate_alerts'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"generate_alerts: {str(e)}")
    
    return {
        'records_processed': results['total_records'],
        'details': results,
    }


@TaskRegistry.register(
    name="cleanup_stale_jobs",
    description="Clean up stale/stuck jobs",
    default_schedule="*/15 * * * *"  # Every 15 minutes
)
async def cleanup_stale_jobs(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """Clean up jobs that have been running too long"""
    from services.jobs.queue import JobQueue
    
    queue = JobQueue(db)
    cleaned = await queue.cleanup_stale_jobs()
    
    return {
        'records_processed': cleaned,
        'details': {
            'stale_jobs_cleaned': cleaned,
        },
    }


@TaskRegistry.register(
    name="generate_weekly_report",
    description="Generate weekly winning products report",
    default_schedule="0 6 * * 1"  # Every Monday at 6 AM UTC
)
async def generate_weekly_report(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the weekly winning products report"""
    from services.reports import WeeklyWinningProductsReport
    
    generator = WeeklyWinningProductsReport(db)
    report = await generator.generate()
    
    return {
        'records_processed': report.metadata.product_count,
        'details': {
            'report_id': report.metadata.id,
            'slug': report.metadata.slug,
            'title': report.metadata.title,
            'products_analyzed': report.metadata.product_count,
            'clusters_analyzed': report.metadata.cluster_count,
        },
    }


@TaskRegistry.register(
    name="generate_monthly_report",
    description="Generate monthly market trends report",
    default_schedule="0 6 1 * *"  # First day of each month at 6 AM UTC
)
async def generate_monthly_report(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the monthly market trends report"""
    from services.reports import MonthlyMarketTrendsReport
    
    generator = MonthlyMarketTrendsReport(db)
    report = await generator.generate()
    
    return {
        'records_processed': report.metadata.product_count,
        'details': {
            'report_id': report.metadata.id,
            'slug': report.metadata.slug,
            'title': report.metadata.title,
            'products_analyzed': report.metadata.product_count,
            'categories_analyzed': report.metadata.cluster_count,
        },
    }


@TaskRegistry.register(
    name="scrape_real_data",
    description="Scrape real product data from live sources",
    default_schedule="0 */4 * * *"  # Every 4 hours
)
async def scrape_real_data(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scrape real product data from:
    - AliExpress
    - TikTok Creative Center
    - Amazon Movers & Shakers
    - CJ Dropshipping
    """
    from services.scrapers.orchestrator import DataIngestionOrchestrator
    
    max_products = params.get('max_products_per_source', 30)
    sources = params.get('sources')  # None = all sources
    
    orchestrator = DataIngestionOrchestrator(db)
    result = await orchestrator.run_full_ingestion(
        sources=sources,
        max_products_per_source=max_products
    )
    
    return {
        'records_processed': result.get('total_products_fetched', 0),
        'details': {
            'sources_successful': result.get('sources_successful', 0),
            'products_created': result.get('total_products_created', 0),
            'products_updated': result.get('total_products_updated', 0),
            'duration_seconds': result.get('duration_seconds', 0),
        },
    }



@TaskRegistry.register(
    name="enrich_google_trends",
    description="Enrich products with Google Trends velocity data",
    default_schedule="0 */6 * * *"  # Every 6 hours
)
async def enrich_google_trends(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich products with Google Trends keyword velocity data."""
    from services.scrapers.google_trends_scraper import GoogleTrendsScraper
    
    scraper = GoogleTrendsScraper(db)
    max_products = params.get('max_products', 30)
    result = await scraper.enrich_products(max_products=max_products)
    
    return {
        'records_processed': result.get('enriched', 0),
        'details': result,
    }


@TaskRegistry.register(
    name="recompute_scores",
    description="Recompute all product scores using transparent scoring engine",
    default_schedule="0 */4 * * *"  # Every 4 hours (after scraping)
)
async def recompute_scores(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """Recompute all scores with transparent reasoning."""
    from services.scoring import ScoringEngine
    
    engine = ScoringEngine(db)
    stats = await engine.batch_update_scores(limit=500)
    
    return {
        'records_processed': stats.get('updated', 0),
        'details': stats,
    }



@TaskRegistry.register(
    name="run_deduplication",
    description="Run product deduplication to merge duplicates into canonical records",
    default_schedule="0 8 * * *"  # Daily at 8 AM UTC
)
async def run_deduplication(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run product deduplication process.
    
    Merges duplicate products from multiple sources into canonical records.
    """
    from services.product_identity import ProductIdentityService
    
    service = ProductIdentityService(db)
    result = await service.run_deduplication(dry_run=False)
    
    return {
        'records_processed': result.total_products_processed,
        'details': {
            'duplicate_groups_found': result.duplicate_groups_found,
            'products_merged': result.products_merged,
            'canonical_created': result.canonical_products_created,
            'canonical_updated': result.canonical_products_updated,
            'success': result.success
        },
    }



# =====================================================
# WEEKLY EMAIL DIGEST TASK
# =====================================================

@TaskRegistry.register(
    name="send_weekly_email_digest",
    description="Send weekly winning products digest to all subscribed users",
    default_schedule="0 10 * * 1"  # Every Monday at 10:00 AM UTC
)
async def send_weekly_email_digest(db, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send weekly email digest to all subscribed users.
    
    Runs every Monday at 10 AM UTC (after the weekly report is generated).
    """
    from services.email_service import email_service
    
    logger.info("Starting weekly email digest send...")
    
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
        logger.warning("No weekly report available for email digest")
        return {
            'records_processed': 0,
            'details': {
                'status': 'skipped',
                'reason': 'No weekly report available'
            }
        }
    
    # Get all users subscribed to weekly digest
    subscribed_users = await db.users.find(
        {"email_preferences.weekly_digest": True},
        {"_id": 0, "email": 1, "name": 1}
    ).to_list(None)
    
    # If no explicit subscribers, get users with verified emails (limit for safety)
    if not subscribed_users:
        subscribed_users = await db.users.find(
            {"email": {"$exists": True, "$ne": None}},
            {"_id": 0, "email": 1, "name": 1}
        ).to_list(100)
    
    sent_count = 0
    failed_count = 0
    errors = []
    
    for user in subscribed_users:
        try:
            result = await email_service.send_weekly_digest(
                to_email=user.get('email'),
                user_name=user.get('name', user.get('email', '').split('@')[0]),
                report_data=report
            )
            
            if result.get('status') == 'success':
                sent_count += 1
            else:
                failed_count += 1
                errors.append({
                    'email': user.get('email'),
                    'error': result.get('error')
                })
        except Exception as e:
            failed_count += 1
            errors.append({
                'email': user.get('email'),
                'error': str(e)
            })
            logger.error(f"Failed to send digest to {user.get('email')}: {str(e)}")
    
    logger.info(f"Weekly email digest completed: {sent_count} sent, {failed_count} failed")
    
    return {
        'records_processed': sent_count + failed_count,
        'details': {
            'status': 'completed',
            'total_subscribers': len(subscribed_users),
            'sent': sent_count,
            'failed': failed_count,
            'errors': errors[:5]  # Only keep first 5 errors
        }
    }



# =====================================================
# PRODUCT OF THE WEEK EMAIL TASK
# =====================================================

@TaskRegistry.register(
    name="send_product_of_the_week",
    description="Send Product of the Week email with referral links to all subscribers",
    default_schedule="0 11 * * 3"  # Every Wednesday at 11:00 AM UTC
)
async def send_product_of_the_week(db, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send Product of the Week email to all subscribed users.
    Includes personalized referral links for viral sharing.
    Runs every Wednesday at 11 AM UTC.
    """
    from services.email_service import email_service

    logger.info("Starting Product of the Week email send...")

    # Get top product by launch score
    cursor = db.products.find(
        {"launch_score": {"$gte": 60}},
        {"_id": 0}
    ).sort([("launch_score", -1), ("market_score", -1)]).limit(4)
    products = await cursor.to_list(4)

    if not products:
        logger.warning("No qualifying products for POTW email")
        return {
            'records_processed': 0,
            'details': {'status': 'skipped', 'reason': 'No qualifying products'}
        }

    featured = products[0]
    runners_up = products[1:4]

    def _get_margin_range(margin):
        if margin >= 50: return "£50+"
        elif margin >= 30: return "£30-50"
        elif margin >= 20: return "£20-30"
        elif margin >= 10: return "£10-20"
        return "Under £10"

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

    # Get all users with emails (from profiles and newsletter subscribers)
    recipients = []

    # Registered users
    profile_users = await db.profiles.find(
        {"email": {"$exists": True, "$ne": None}},
        {"_id": 0, "id": 1, "email": 1, "name": 1}
    ).to_list(200)
    for u in profile_users:
        recipients.append(u)

    # Newsletter subscribers (not yet registered users)
    newsletter_subs = await db.newsletter_subscribers.find(
        {"status": "active"},
        {"_id": 0, "email": 1}
    ).to_list(500)
    existing_emails = {r.get("email") for r in recipients}
    for sub in newsletter_subs:
        if sub.get("email") not in existing_emails:
            recipients.append({"email": sub["email"], "name": sub["email"].split("@")[0]})

    sent_count = 0
    failed_count = 0

    for user in recipients:
        # Get referral code for personalized viral link
        referral = await db.user_referrals.find_one(
            {"user_id": user.get("id")}, {"_id": 0, "referral_code": 1}
        ) if user.get("id") else None
        referral_code = referral.get("referral_code") if referral else None

        try:
            result = await email_service.send_product_of_the_week(
                to_email=user.get("email"),
                user_name=user.get("name", user.get("email", "").split("@")[0]),
                product=product_data,
                referral_code=referral_code,
            )
            if result.get("status") == "success":
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"POTW email error for {user.get('email')}: {e}")

    logger.info(f"POTW email completed: {sent_count} sent, {failed_count} failed")

    return {
        'records_processed': sent_count + failed_count,
        'details': {
            'status': 'completed',
            'product': featured.get("product_name"),
            'total_recipients': len(recipients),
            'sent': sent_count,
            'failed': failed_count,
        }
    }


@TaskRegistry.register(
    name="send_weekly_radar_digest",
    description="Send Weekly Radar Digest email every Monday morning with top 5 radar detections",
    default_schedule="0 8 * * 1"  # Every Monday at 08:00 AM UTC
)
async def send_weekly_radar_digest(db, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send Weekly Radar Digest to all subscribed users every Monday morning.
    Includes top 5 radar-detected products from the previous week.
    """
    from services.email_service import EmailService
    from datetime import timedelta

    logger.info("Starting Weekly Radar Digest...")

    # Get radar-detected products from last 7 days
    one_week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    cursor = db.products.find(
        {
            "radar_detected": True,
            "$or": [
                {"radar_detected_at": {"$gte": one_week_ago}},
                {"launch_score": {"$gte": 70}},
            ]
        },
        {"_id": 0}
    ).sort("launch_score", -1).limit(5)
    products = await cursor.to_list(5)

    if not products:
        # Fall back to top products by launch score
        cursor = db.products.find(
            {"launch_score": {"$gte": 65}},
            {"_id": 0}
        ).sort("launch_score", -1).limit(5)
        products = await cursor.to_list(5)

    if not products:
        logger.info("No qualifying products for radar digest")
        return {'records_processed': 0, 'details': {'status': 'skipped', 'reason': 'No products'}}

    # Build product rows HTML
    product_rows = ""
    for p in products:
        margin = p.get("estimated_margin", 0)
        retail = p.get("estimated_retail_price", 1)
        margin_pct = int((margin / retail) * 100) if retail > 0 else 0
        stage = p.get("early_trend_label", p.get("trend_stage", "—"))
        stage_color = {"exploding": "#dc2626", "rising": "#f59e0b", "emerging": "#3b82f6"}.get(stage, "#64748b")
        product_rows += f"""
        <tr style="border-bottom:1px solid #f1f5f9;">
            <td style="padding:14px 10px;font-weight:600;color:#1e293b;font-size:14px;">{p.get('product_name','Unknown')}</td>
            <td style="padding:14px 10px;text-align:center;">
                <span style="background:#eef2ff;color:#4f46e5;padding:5px 12px;border-radius:12px;font-weight:700;font-size:15px;">{p.get('launch_score',0)}</span>
            </td>
            <td style="padding:14px 10px;text-align:center;">
                <span style="background:{stage_color}15;color:{stage_color};padding:3px 10px;border-radius:8px;font-size:12px;font-weight:500;text-transform:capitalize;">{stage}</span>
            </td>
            <td style="padding:14px 10px;text-align:center;color:#059669;font-weight:600;font-size:14px;">{margin_pct}%</td>
        </tr>"""

    # Get all users subscribed to email alerts
    recipients = await db.profiles.find(
        {"id": {"$exists": True}},
        {"_id": 0, "id": 1, "full_name": 1}
    ).to_list(500)

    email_service = EmailService()
    sent_count = 0
    failed_count = 0
    import os
    frontend_url = os.environ.get('FRONTEND_URL', 'https://trendscout.click')

    for recipient in recipients:
        user = await db.auth_users.find_one(
            {"id": recipient["id"]},
            {"_id": 0, "email": 1}
        )
        if not user or not user.get("email"):
            continue

        user_name = recipient.get("full_name", "there")
        html = f"""
        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;background:#ffffff;">
            <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:36px 32px;text-align:center;border-radius:12px 12px 0 0;">
                <h1 style="color:white;margin:0;font-size:22px;font-weight:700;">Weekly Radar Digest</h1>
                <p style="color:#c7d2fe;margin:8px 0 0;font-size:14px;">Your top winning product detections this week</p>
            </div>
            <div style="padding:28px 24px;">
                <p style="color:#475569;font-size:14px;line-height:1.6;">Hi {user_name},</p>
                <p style="color:#475569;font-size:14px;line-height:1.6;">TrendScout Radar detected <strong style="color:#1e293b;">{len(products)} winning products</strong> this week. Here are the highlights:</p>
                <table style="width:100%;border-collapse:collapse;margin:20px 0;border-radius:8px;overflow:hidden;">
                    <thead>
                        <tr style="border-bottom:2px solid #e2e8f0;background:#f8fafc;">
                            <th style="padding:10px;text-align:left;color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Product</th>
                            <th style="padding:10px;text-align:center;color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Score</th>
                            <th style="padding:10px;text-align:center;color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Stage</th>
                            <th style="padding:10px;text-align:center;color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Margin</th>
                        </tr>
                    </thead>
                    <tbody>{product_rows}</tbody>
                </table>
                <div style="text-align:center;margin:28px 0;">
                    <a href="{frontend_url}/dashboard" style="display:inline-block;background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:600;font-size:14px;">View Full Analysis</a>
                </div>
                <p style="color:#94a3b8;font-size:11px;text-align:center;margin-top:24px;border-top:1px solid #f1f5f9;padding-top:16px;">
                    You're receiving this because you have a TrendScout account.
                </p>
            </div>
        </div>"""

        try:
            result = await email_service.send_email(
                to_email=user["email"],
                subject=f"TrendScout Weekly Radar: {len(products)} winning products detected",
                html_content=html
            )
            if result.get("success"):
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f"Failed to send radar digest to {user['email']}: {e}")
            failed_count += 1

    logger.info(f"Weekly Radar Digest complete: {sent_count} sent, {failed_count} failed")
    return {
        'records_processed': sent_count + failed_count,
        'details': {
            'status': 'completed',
            'products_featured': len(products),
            'sent': sent_count,
            'failed': failed_count,
        }
    }
