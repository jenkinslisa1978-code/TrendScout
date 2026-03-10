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
    default_schedule="0 */6 * * *"  # Every 6 hours
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

