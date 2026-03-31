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
import uuid
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
    name="scan_threshold_subscriptions",
    description="Scan products against user threshold subscriptions and send alerts",
    default_schedule="0 */6 * * *"  # Every 6 hours
)
async def scan_threshold_subscriptions(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan all active threshold subscriptions and generate notifications
    for products that cross user-defined score thresholds.
    """
    from services.notification_service import create_notification_service, NotificationType
    ns = create_notification_service(db)

    subs = await db.threshold_subscriptions.find(
        {"enabled": True},
        {"_id": 0}
    ).to_list(500)

    if not subs:
        return {"records_processed": 0, "details": {"subscriptions": 0, "notifications": 0}}

    products = await db.products.find(
        {"launch_score": {"$gte": 40}},
        {"_id": 0}
    ).sort("launch_score", -1).limit(50).to_list(50)

    total_notifs = 0
    for sub in subs:
        threshold = sub.get("score_threshold", 75)
        cats = sub.get("categories", [])
        user_id = sub["user_id"]

        matching = [
            p for p in products
            if p.get("launch_score", 0) >= threshold
            and (not cats or p.get("category") in cats)
        ]

        for product in matching[:5]:
            try:
                notif = await ns.create_notification(
                    user_id=user_id,
                    notification_type=NotificationType.SCORE_MILESTONE,
                    product=product,
                )
                if notif:
                    total_notifs += 1
            except Exception:
                pass

    return {
        "records_processed": total_notifs,
        "details": {"subscriptions": len(subs), "notifications": total_notifs, "products_scanned": len(products)},
    }



@TaskRegistry.register(
    name="weekly_competitor_scan",
    description="Re-scan all tracked competitor stores and notify users of changes",
    default_schedule="0 6 * * 1"  # Every Monday at 6 AM
)
async def weekly_competitor_scan(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Weekly scan of all tracked competitor stores.
    Detects product additions/removals and creates notifications.
    """
    import aiohttp
    from services.notification_service import create_notification_service, NotificationType

    stores = await db.competitor_stores.find({}, {"_id": 0}).to_list(500)
    if not stores:
        return {"records_processed": 0, "details": {"stores": 0}}

    ns = create_notification_service(db)
    scanned = 0
    changes = 0

    for store in stores:
        domain = store.get("domain")
        if not domain:
            continue

        try:
            url = f"https://{domain}/products.json?limit=250"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=15),
                    headers={"User-Agent": "TrendScout/1.0"}
                ) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()

            raw = data.get("products", [])
            new_count = len(raw)
            prev_count = store.get("product_count", 0)
            change = new_count - prev_count

            prices = []
            cats = {}
            for p in raw:
                for v in p.get("variants", []):
                    try:
                        prices.append(float(v.get("price", 0)))
                    except (ValueError, TypeError):
                        pass
                pt = (p.get("product_type") or "").strip() or "Uncategorized"
                cats[pt] = cats.get(pt, 0) + 1

            scan_entry = {
                "date": datetime.now(timezone.utc).isoformat(),
                "product_count": new_count,
                "change": change,
            }

            await db.competitor_stores.update_one(
                {"id": store["id"]},
                {"$set": {
                    "product_count": new_count,
                    "categories": sorted([{"name": k, "count": v} for k, v in cats.items()], key=lambda c: c["count"], reverse=True)[:5],
                    "price_range": {
                        "min": round(min(prices), 2) if prices else 0,
                        "max": round(max(prices), 2) if prices else 0,
                        "avg": round(sum(prices) / len(prices), 2) if prices else 0,
                    },
                    "last_scan_at": datetime.now(timezone.utc).isoformat(),
                    "product_change": change,
                }, "$push": {
                    "scan_history": {"$each": [scan_entry], "$slice": -30}
                }}
            )

            scanned += 1

            # Notify user if significant change
            if abs(change) >= 3:
                changes += 1
                try:
                    await ns.create_notification(
                        user_id=store["user_id"],
                        notification_type=NotificationType.SCORE_MILESTONE,
                        product={
                            "product_name": f"Competitor: {store.get('name', domain)}",
                            "launch_score": 0,
                            "category": f"{'+'if change>0 else ''}{change} products",
                        },
                    )
                except Exception:
                    pass

        except Exception as e:
            logging.warning(f"Weekly scan failed for {domain}: {e}")
            continue

    return {
        "records_processed": scanned,
        "details": {"stores_scanned": scanned, "stores_with_changes": changes, "total_stores": len(stores)},
    }



@TaskRegistry.register(
    name="weekly_blog_generation",
    description="Auto-generate SEO blog posts for top product categories",
    default_schedule="0 8 * * 1"  # Every Monday at 8 AM
)
async def weekly_blog_generation(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate blog posts for the top categories with enough products."""
    import os
    llm_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
    if not llm_key:
        return {"records_processed": 0, "details": {"error": "No LLM key"}}

    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_score": {"$avg": "$launch_score"}}},
        {"$match": {"count": {"$gte": 3}}},
        {"$sort": {"avg_score": -1}},
        {"$limit": 5},
    ]
    categories = await db.products.aggregate(pipeline).to_list(5)

    generated = 0
    for cat in categories:
        cat_name = cat["_id"]
        if not cat_name:
            continue

        # Check if we already have a recent post for this category
        recent = await db.blog_posts.find_one({
            "category_slug": cat_name.lower().replace(" ", "-").replace("&", "and"),
            "published_at": {"$gte": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat()},
        })
        if recent:
            continue

        try:
            from routes.blog import _generate_blog_post
            await _generate_blog_post(cat_name.lower().replace(" ", "-").replace("&", "and"))
            generated += 1
            import asyncio
            await asyncio.sleep(5)  # Rate limit between generations
        except Exception as e:
            logging.warning(f"Blog generation failed for {cat_name}: {e}")

    return {
        "records_processed": generated,
        "details": {"categories_processed": len(categories), "posts_generated": generated},
    }


@TaskRegistry.register(
    name="sync_cj_products",
    description="Fetch trending products from CJ Dropshipping and import into TrendScout",
    default_schedule="0 */6 * * *"  # Every 6 hours
)
async def sync_cj_products(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Automated CJ Dropshipping product sync.

    Searches CJ for popular dropshipping categories, deduplicates against
    existing products, and inserts new ones with initial scoring.
    """
    import uuid as _uuid
    from services.cj_dropshipping import search_products
    from common.scoring import calculate_launch_score

    search_queries = params.get("queries", [
        "phone accessories",
        "home gadgets",
        "beauty tools",
        "pet supplies",
        "LED lights",
        "kitchen gadgets",
        "fitness accessories",
        "car accessories",
    ])
    page_size = params.get("page_size", 20)

    total_fetched = 0
    total_created = 0
    total_skipped = 0
    errors = []

    import asyncio as _asyncio

    for qi, query in enumerate(search_queries):
        # CJ API rate limit: 1 request/second
        if qi > 0:
            await _asyncio.sleep(1.2)

        try:
            result = await search_products(query, page=1, page_size=page_size)
            if not result.get("success"):
                errors.append(f"{query}: {result.get('error', 'unknown')}")
                continue

            products = result.get("products", [])
            total_fetched += len(products)

            for cj_prod in products:
                cj_pid = cj_prod.get("cj_pid", "")
                if not cj_pid:
                    continue

                # Deduplicate by cj_pid
                existing = await db.products.find_one(
                    {"cj_pid": cj_pid}, {"_id": 0, "id": 1}
                )
                if existing:
                    total_skipped += 1
                    continue

                product_id = str(_uuid.uuid4())
                sell_price = cj_prod.get("sell_price", 0)
                retail_price = round(sell_price * 2.5, 2) if sell_price > 0 else 0
                margin = round(
                    ((retail_price - sell_price) / retail_price) * 100, 1
                ) if retail_price > 0 else 0

                product = {
                    "id": product_id,
                    "cj_pid": cj_pid,
                    "product_name": cj_prod.get("product_name", ""),
                    "slug": cj_prod.get("product_name", "").lower().replace(" ", "-")[:80],
                    "category": cj_prod.get("category", query.title()),
                    "image_url": cj_prod.get("image_url", ""),
                    "images": cj_prod.get("images", []),
                    "estimated_retail_price": retail_price,
                    "estimated_cost": sell_price,
                    "estimated_margin": margin,
                    "supplier_cost": sell_price,
                    "currency": cj_prod.get("currency", "USD"),
                    "data_source": "cj_dropshipping",
                    "source_url": cj_prod.get("source_url", ""),
                    "stock_status": cj_prod.get("stock_status", "in_stock"),
                    "shipping_weight": cj_prod.get("shipping_weight", 0),
                    "description": cj_prod.get("description", ""),
                    "variants_count": cj_prod.get("variants_count", 0),
                    "suppliers": [{
                        "name": "CJ Dropshipping",
                        "country": "CN",
                        "rating": 4.3,
                        "unit_cost": sell_price,
                        "min_order": 1,
                        "lead_time_days": 8,
                        "shipping_cost": 3.50,
                    }],
                    "trend_score": 50,
                    "margin_score": min(100, max(0, round(margin))),
                    "competition_score": 50,
                    "ad_activity_score": 30,
                    "supplier_demand_score": 70,
                    "launch_score": 0,
                    "launch_score_label": "",
                    "launch_score_reasoning": "",
                    "tiktok_views": 0,
                    "ad_count": 0,
                    "competition_level": "unknown",
                    "market_saturation": 0,
                    "active_competitor_stores": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "imported_by": "cj_auto_sync",
                }

                score, label, reasoning = calculate_launch_score(product)
                product["launch_score"] = score
                product["launch_score_label"] = label
                product["launch_score_reasoning"] = reasoning

                await db.products.insert_one(product)
                product.pop("_id", None)
                total_created += 1

        except Exception as e:
            logger.error(f"CJ sync error for query '{query}': {e}")
            errors.append(f"{query}: {str(e)}")

    # Log the sync run
    await db.automation_logs.insert_one({
        "id": str(_uuid.uuid4()),
        "job_name": "sync_cj_products",
        "status": "completed",
        "run_time": datetime.now(timezone.utc).isoformat(),
        "details": {
            "fetched": total_fetched,
            "created": total_created,
            "skipped": total_skipped,
            "errors": errors[:10],
        },
    })

    logger.info(
        f"CJ sync complete: fetched={total_fetched}, created={total_created}, "
        f"skipped={total_skipped}, errors={len(errors)}"
    )

    return {
        "records_processed": total_created,
        "details": {
            "fetched": total_fetched,
            "created": total_created,
            "skipped": total_skipped,
            "queries": len(search_queries),
            "errors": errors[:10],
        },
    }


@TaskRegistry.register(
    name="sync_avasam_products",
    description="Fetch UK products from Avasam and import into TrendScout",
    default_schedule="0 */6 * * *"  # Every 6 hours
)
async def sync_avasam_products(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Automated Avasam UK product sync.

    Searches Avasam for popular UK dropshipping categories, deduplicates
    against existing products, and inserts new ones with initial scoring.
    """
    import uuid as _uuid
    from services.avasam import search_products
    from common.scoring import calculate_launch_score

    search_queries = params.get("queries", [
        "phone cases",
        "home decor",
        "beauty products",
        "pet accessories",
        "LED lighting",
        "kitchen accessories",
        "fitness equipment",
        "garden tools",
    ])
    page_size = params.get("page_size", 20)

    total_fetched = 0
    total_created = 0
    total_skipped = 0
    errors = []

    import asyncio as _asyncio

    for qi, query in enumerate(search_queries):
        if qi > 0:
            await _asyncio.sleep(1.2)

        try:
            result = await search_products(query, page=1, page_size=page_size)
            if not result.get("success"):
                errors.append(f"{query}: {result.get('error', 'unknown')}")
                continue

            products = result.get("products", [])
            total_fetched += len(products)

            for avasam_prod in products:
                avasam_pid = avasam_prod.get("avasam_pid", "")
                if not avasam_pid:
                    continue

                # Deduplicate by avasam_pid
                existing = await db.products.find_one(
                    {"avasam_pid": avasam_pid}, {"_id": 0, "id": 1}
                )
                if existing:
                    total_skipped += 1
                    continue

                product_id = str(_uuid.uuid4())
                cost = avasam_prod.get("supplier_cost", 0)
                rrp = avasam_prod.get("sell_price", 0)
                retail_price = rrp if rrp > 0 else round(cost * 2.5, 2)
                margin = round(
                    ((retail_price - cost) / retail_price) * 100, 1
                ) if retail_price > 0 and cost > 0 else 0

                product = {
                    "id": product_id,
                    "avasam_pid": avasam_pid,
                    "product_name": avasam_prod.get("product_name", ""),
                    "slug": avasam_prod.get("product_name", "").lower().replace(" ", "-")[:80],
                    "category": avasam_prod.get("category", query.title()),
                    "image_url": avasam_prod.get("image_url", ""),
                    "images": avasam_prod.get("images", []),
                    "estimated_retail_price": retail_price,
                    "estimated_cost": cost,
                    "estimated_margin": margin,
                    "supplier_cost": cost,
                    "currency": avasam_prod.get("currency", "GBP"),
                    "data_source": "avasam",
                    "source_url": avasam_prod.get("source_url", ""),
                    "stock_status": avasam_prod.get("stock_status", "in_stock"),
                    "shipping_weight": avasam_prod.get("shipping_weight", 0),
                    "description": avasam_prod.get("description", ""),
                    "variants_count": avasam_prod.get("variants_count", 0),
                    "sku": avasam_prod.get("sku", ""),
                    "brand": avasam_prod.get("brand", ""),
                    "ean": avasam_prod.get("ean", ""),
                    "suppliers": [{
                        "name": "Avasam",
                        "country": "GB",
                        "rating": 4.5,
                        "unit_cost": cost,
                        "min_order": 1,
                        "lead_time_days": 2,
                        "shipping_cost": 0,
                    }],
                    "trend_score": 55,
                    "margin_score": min(100, max(0, round(margin))),
                    "competition_score": 50,
                    "ad_activity_score": 30,
                    "supplier_demand_score": 75,
                    "launch_score": 0,
                    "launch_score_label": "",
                    "launch_score_reasoning": "",
                    "tiktok_views": 0,
                    "ad_count": 0,
                    "competition_level": "unknown",
                    "market_saturation": 0,
                    "active_competitor_stores": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "imported_by": "avasam_auto_sync",
                }

                score, label, reasoning = calculate_launch_score(product)
                product["launch_score"] = score
                product["launch_score_label"] = label
                product["launch_score_reasoning"] = reasoning

                await db.products.insert_one(product)
                product.pop("_id", None)
                total_created += 1

        except Exception as e:
            logger.error(f"Avasam sync error for query '{query}': {e}")
            errors.append(f"{query}: {str(e)}")

    # Log the sync run
    await db.automation_logs.insert_one({
        "id": str(_uuid.uuid4()),
        "job_name": "sync_avasam_products",
        "status": "completed",
        "run_time": datetime.now(timezone.utc).isoformat(),
        "details": {
            "fetched": total_fetched,
            "created": total_created,
            "skipped": total_skipped,
            "errors": errors[:10],
        },
    })

    logger.info(
        f"Avasam sync complete: fetched={total_fetched}, created={total_created}, "
        f"skipped={total_skipped}, errors={len(errors)}"
    )

    return {
        "records_processed": total_created,
        "details": {
            "fetched": total_fetched,
            "created": total_created,
            "skipped": total_skipped,
            "queries": len(search_queries),
            "errors": errors[:10],
        },
    }



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
    2. Sync CJ Dropshipping products
    3. Update supplier data
    4. Update competitor data
    5. Update ad activity
    6. Update market scores
    7. Generate alerts
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

    # Step 2: Sync CJ Dropshipping products
    try:
        step_result = await sync_cj_products(db, params)
        results['steps']['sync_cj_products'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"sync_cj_products: {str(e)}")

    # Step 2b: Sync Avasam UK products
    try:
        step_result = await sync_avasam_products(db, params)
        results['steps']['sync_avasam_products'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"sync_avasam_products: {str(e)}")
    
    # Step 3: Update supplier data
    try:
        step_result = await update_supplier_data(db, params)
        results['steps']['update_supplier'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"update_supplier: {str(e)}")
    
    # Step 4: Update competitor data
    try:
        step_result = await update_competitor_data(db, params)
        results['steps']['update_competitor'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"update_competitor: {str(e)}")
    
    # Step 5: Update ad activity
    try:
        step_result = await update_ad_activity(db, params)
        results['steps']['update_ad_activity'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"update_ad_activity: {str(e)}")
    
    # Step 6: Update market scores
    try:
        step_result = await update_market_scores(db, params)
        results['steps']['update_scores'] = step_result
        results['total_records'] += step_result['records_processed']
    except Exception as e:
        results['errors'].append(f"update_scores: {str(e)}")
    
    # Step 7: Generate alerts
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

async def _generate_user_next_steps(db, user_id: str) -> list:
    """Generate lightweight per-user next-step recommendations for email digest."""
    if not user_id:
        return []
    steps = []
    saved = await db.saved_products.count_documents({"user_id": user_id})
    stores = await db.stores.count_documents({"user_id": user_id})
    watchlist = await db.watchlist.count_documents({"user_id": user_id})
    unread = await db.alerts.count_documents({"user_id": user_id, "is_read": False})

    if unread > 0:
        steps.append({
            "title": f"You have {unread} unread alert{'s' if unread != 1 else ''}",
            "description": "New trend alerts may contain time-sensitive opportunities.",
            "action": {"label": "View Alerts", "href": "/dashboard?tab=alerts"},
        })
    if saved == 0:
        steps.append({
            "title": "Save your first product",
            "description": "Browse trending products and save ones you like.",
            "action": {"label": "Discover", "href": "/discover"},
        })
    if saved > 0 and stores == 0:
        steps.append({
            "title": "Build your first store",
            "description": f"You have {saved} saved product{'s' if saved != 1 else ''}. Create a store around your best pick.",
            "action": {"label": "Build Store", "href": "/discover"},
        })
    top = await db.products.find_one(
        {"launch_score": {"$gte": 70}},
        {"_id": 0, "id": 1, "product_name": 1, "launch_score": 1},
    )
    if top:
        steps.append({
            "title": f"Launch \"{top.get('product_name', 'Top Product')}\"",
            "description": f"Scored {top.get('launch_score', 0)}/100 — a strong launch candidate.",
            "action": {"label": "Start Launch", "href": f"/launch/{top['id']}"},
        })
    if watchlist == 0:
        steps.append({
            "title": "Start your watchlist",
            "description": "Track price and trend changes over time.",
            "action": {"label": "Browse", "href": "/discover"},
        })
    return steps[:3]


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
    subscribed_users = await db.profiles.find(
        {"email_preferences.weekly_digest": True},
        {"_id": 0, "id": 1, "email": 1, "name": 1}
    ).to_list(None)
    
    # If no explicit subscribers, get users with verified emails (limit for safety)
    if not subscribed_users:
        subscribed_users = await db.profiles.find(
            {"email": {"$exists": True, "$ne": None}},
            {"_id": 0, "id": 1, "email": 1, "name": 1}
        ).to_list(100)
    
    sent_count = 0
    failed_count = 0
    errors = []
    
    for user in subscribed_users:
        try:
            # Generate personalised next-steps for this user
            next_steps = await _generate_user_next_steps(db, user.get("id"))

            result = await email_service.send_weekly_digest(
                to_email=user.get('email'),
                user_name=user.get('name', user.get('email', '').split('@')[0]),
                report_data=report,
                next_steps=next_steps,
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



# =====================================================
# IMAGE ENRICHMENT PIPELINE TASK
# =====================================================

@TaskRegistry.register(
    name="enrich_product_images",
    description="Find and validate high-quality images for products missing or with low-confidence images",
    default_schedule="0 */8 * * *"  # Every 8 hours
)
async def enrich_product_images(db, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Image Resolution Pipeline (Parts 20-22):
    1. Find products missing images or with low confidence
    2. Source candidate images from multiple providers
    3. Validate candidates for relevance and quality
    4. Store best candidate and queue for admin review
    """
    from services.image_service import ImageService

    logger.info("Starting image enrichment pipeline...")
    params = params or {}
    limit = params.get('limit', 20)
    min_confidence = params.get('min_confidence', 50)

    svc = ImageService(db)

    # Find products needing image enrichment
    query = {
        "$or": [
            {"image_url": {"$exists": False}},
            {"image_url": None},
            {"image_url": ""},
            {"image_confidence": {"$lt": min_confidence}},
            {"image_review_status": "rejected"},
        ]
    }
    products = await db.products.find(
        query, {"_id": 0}
    ).sort("trend_score", -1).limit(limit).to_list(limit)

    enriched = 0
    failed = 0
    candidates_found = 0

    for product in products:
        try:
            result = await svc.enrich_product_images(product)
            if result and result.get("candidates"):
                candidates_found += len(result["candidates"])
                enriched += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Image enrichment failed for {product.get('id')}: {e}")
            failed += 1

    logger.info(f"Image enrichment complete: {enriched} enriched, {failed} failed, {candidates_found} candidates")

    return {
        'records_processed': enriched + failed,
        'details': {
            'products_processed': len(products),
            'enriched': enriched,
            'failed': failed,
            'candidates_found': candidates_found,
        }
    }


# ── Weekly Digest Auto-Generation ────────────────────────────

@TaskRegistry.register(
    name="generate_weekly_digest",
    description="Auto-generate weekly trending product digest every Monday at 9am UTC",
    default_schedule="0 9 * * 1"  # Monday 9:00 UTC
)
async def generate_weekly_digest(db, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate and publish the weekly trending product digest."""
    from common.cache import slugify

    products = await db.products.find(
        {"launch_score": {"$gte": 50}},
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "launch_score": 1,
         "trend_stage": 1, "image_url": 1, "ai_summary": 1, "tiktok_views": 1,
         "competition_level": 1, "estimated_retail_price": 1, "engagement_rate": 1,
         "slug": 1, "verified_winner": 1}
    ).sort("launch_score", -1).limit(20).to_list(20)

    # Pick top 5 with category diversity
    seen_cats = set()
    top5 = []
    for p in products:
        cat = p.get("category", "")
        if cat not in seen_cats or len(top5) < 3:
            top5.append(p)
            seen_cats.add(cat)
        if len(top5) >= 5:
            break
    for p in products:
        if len(top5) >= 5:
            break
        if p not in top5:
            top5.append(p)

    if not top5:
        return {"records_processed": 0, "details": {"error": "Not enough products"}}

    for p in top5:
        if not p.get("slug"):
            p["slug"] = slugify(p.get("product_name", ""))

    now = datetime.now(timezone.utc)
    week_label = now.strftime("Week of %B %d, %Y")
    avg_score = round(sum(p.get("launch_score", 0) for p in top5) / len(top5), 1)
    categories_featured = list(set(p.get("category", "") for p in top5 if p.get("category")))

    intro = (
        f"This week's top trending products for dropshipping, scored by our AI-powered 7-signal analysis. "
        f"Average launch score: {avg_score}/100 across {len(categories_featured)} categories."
    )

    enriched = []
    for i, p in enumerate(top5):
        insight = []
        if p.get("tiktok_views", 0) > 100000:
            insight.append(f"Strong TikTok presence with {p['tiktok_views']:,} views")
        if p.get("competition_level") in ("low", "medium"):
            insight.append(f"{p['competition_level'].capitalize()} competition")
        if p.get("trend_stage") == "emerging":
            insight.append("Emerging trend")
        if p.get("verified_winner"):
            insight.append("Community-verified winner")
        enriched.append({
            **p,
            "rank": i + 1,
            "insight": " | ".join(insight) if insight else f"Launch score: {p.get('launch_score', 0)}/100",
        })

    digest = {
        "id": str(uuid.uuid4()),
        "title": f"Top 5 Trending Products — {week_label}",
        "slug": slugify(f"top-5-trending-products-{now.strftime('%Y-%m-%d')}"),
        "week_label": week_label,
        "intro": intro,
        "products": enriched,
        "avg_score": avg_score,
        "categories_featured": categories_featured,
        "product_count": len(enriched),
        "status": "published",
        "published_at": now.isoformat(),
        "seo": {
            "title": f"Top 5 Trending Dropshipping Products — {week_label} | TrendScout",
            "description": f"AI-scored trending products for {week_label}. Average launch score: {avg_score}/100.",
            "og_image": enriched[0].get("image_url", "") if enriched else "",
        },
    }

    await db.weekly_digests.insert_one(digest)
    logger.info(f"Weekly digest published: {digest['title']}")

    return {
        "records_processed": len(enriched),
        "details": {
            "digest_id": digest["id"],
            "title": digest["title"],
            "products": len(enriched),
            "avg_score": avg_score,
        },
    }



@TaskRegistry.register(
    name="send_lead_subscriber_digest",
    description="Send weekly trending products digest to email leads/subscribers",
    default_schedule="0 9 * * 1"  # Every Monday at 9:00 AM UTC
)
async def send_lead_subscriber_digest(db, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send weekly trending product digest to all opted-in leads (non-registered subscribers).
    Runs every Monday at 9 AM UTC.
    """
    import os
    import httpx

    logger.info("Starting lead subscriber digest send...")

    leads = await db.leads.find(
        {"digest_opt_in": {"$ne": False}},
        {"_id": 0, "email": 1}
    ).to_list(5000)

    if not leads:
        return {"records_processed": 0, "details": {"status": "skipped", "reason": "No opted-in leads"}}

    products = await db.products.find(
        {},
        {"_id": 0, "name": 1, "viability_score": 1, "trend_score": 1, "category": 1}
    ).sort("trend_score", -1).limit(5).to_list(5)

    product_rows = ""
    for p in products:
        name = p.get("name", "Unknown Product")
        score = p.get("viability_score", p.get("trend_score", "N/A"))
        category = p.get("category", "General")
        product_rows += f'<tr><td style="padding:12px 16px;border-bottom:1px solid #f1f5f9;font-size:14px;color:#334155;">{name}</td><td style="padding:12px 16px;border-bottom:1px solid #f1f5f9;font-size:14px;color:#334155;text-align:center;">{category}</td><td style="padding:12px 16px;border-bottom:1px solid #f1f5f9;font-size:14px;font-weight:600;color:#4f46e5;text-align:center;">{score}</td></tr>'

    if not product_rows:
        product_rows = '<tr><td colspan="3" style="padding:16px;text-align:center;color:#64748b;font-size:14px;">No trending products this week.</td></tr>'

    site_url = os.environ.get("SITE_URL", "https://trendscout.click")
    html_body = f"""<div style="font-family:'Inter',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;padding:32px 24px;">
      <div style="text-align:center;margin-bottom:24px;">
        <h1 style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:700;color:#0f172a;margin:0;">TrendScout Weekly Digest</h1>
        <p style="font-size:14px;color:#64748b;margin:8px 0 0;">Top trending UK products this week</p>
      </div>
      <table style="width:100%;border-collapse:collapse;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;">
        <thead><tr style="background:#f8fafc;">
          <th style="padding:12px 16px;text-align:left;font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;">Product</th>
          <th style="padding:12px 16px;text-align:center;font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;">Category</th>
          <th style="padding:12px 16px;text-align:center;font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;">Score</th>
        </tr></thead>
        <tbody>{product_rows}</tbody>
      </table>
      <div style="text-align:center;margin-top:24px;">
        <a href="{site_url}/trending-products?utm_source=email&utm_medium=digest&utm_campaign=weekly_digest&utm_content=cta_see_all" style="display:inline-block;background:#4f46e5;color:#fff;padding:12px 28px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;">See all trending products</a>
      </div>
      <div style="margin-top:24px;padding-top:16px;border-top:1px solid #e2e8f0;">
        <p style="font-size:12px;color:#94a3b8;text-align:center;margin:0;">You received this because you subscribed at TrendScout.<br/>Reply with "unsubscribe" to stop.</p>
      </div>
    </div>"""

    resend_key = os.environ.get("RESEND_API_KEY")
    sender_email = os.environ.get("SENDER_EMAIL", "noreply@trendscout.click")

    if not resend_key:
        return {"records_processed": 0, "details": {"status": "error", "reason": "Resend not configured"}}

    sent_count = 0
    errors = []

    async with httpx.AsyncClient() as client:
        for lead in leads:
            try:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                    json={"from": f"TrendScout <{sender_email}>", "to": [lead["email"]], "subject": "Your weekly UK product trends", "html": html_body},
                    timeout=10,
                )
                if resp.status_code in (200, 201):
                    sent_count += 1
                else:
                    errors.append(f"{lead['email']}: {resp.status_code}")
            except Exception as e:
                errors.append(f"{lead['email']}: {str(e)}")

    await db.digest_log.insert_one({
        "type": "lead_subscriber_digest",
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "total_leads": len(leads),
        "sent_count": sent_count,
        "errors": errors[:10],
    })

    logger.info(f"Lead subscriber digest: sent {sent_count}/{len(leads)}, errors: {len(errors)}")
    return {"records_processed": sent_count, "details": {"total": len(leads), "sent": sent_count, "errors": len(errors)}}



@TaskRegistry.register(
    name="send_trial_expiry_notifications",
    description="Send email notifications when free trials expire",
    default_schedule="0 */2 * * *"  # Every 2 hours
)
async def send_trial_expiry_notifications(db, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Check for trials that have expired in the last 2 hours and send
    a notification email encouraging upgrade.
    """
    import os
    import httpx

    logger.info("Checking for expired trials...")

    now = datetime.now(timezone.utc)
    two_hours_ago = (now - timedelta(hours=2)).isoformat()

    # Find trials that expired in the last 2 hours and haven't been notified
    expired_trials = await db.trials.find(
        {
            "expires_at": {"$lte": now.isoformat(), "$gte": two_hours_ago},
            "expiry_notified": {"$ne": True},
        },
        {"_id": 0}
    ).to_list(100)

    if not expired_trials:
        return {"records_processed": 0, "details": {"status": "no_expired_trials"}}

    resend_key = os.environ.get("RESEND_API_KEY")
    sender_email = os.environ.get("SENDER_EMAIL", "noreply@trendscout.click")
    site_url = os.environ.get("SITE_URL", "https://trendscout.click")

    if not resend_key:
        return {"records_processed": 0, "details": {"status": "error", "reason": "Resend not configured"}}

    sent_count = 0

    async with httpx.AsyncClient() as client:
        for trial in expired_trials:
            email = trial.get("email")
            feature = trial.get("feature", "premium feature")
            feature_label = feature.replace("_", " ").title()

            if not email:
                continue

            html_body = f"""
            <div style="font-family:'Inter',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;padding:32px 24px;">
              <h1 style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:700;color:#0f172a;margin:0;">
                Your {feature_label} trial has ended
              </h1>
              <p style="font-size:14px;color:#64748b;margin:16px 0;">
                Your 24-hour free trial of {feature_label} on TrendScout has expired.
                During your trial, you experienced the full power of premium product intelligence.
              </p>

              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin:20px 0;">
                <h2 style="font-size:16px;font-weight:600;color:#0f172a;margin:0 0 12px;">What you are missing without premium:</h2>
                <ul style="margin:0;padding:0 0 0 20px;color:#475569;font-size:14px;line-height:1.8;">
                  <li>Real-time cross-channel trend detection</li>
                  <li>UK-specific viability scoring on every product</li>
                  <li>Competitor store analysis with revenue estimates</li>
                  <li>AI-generated ad copy and audience targeting</li>
                  <li>Profit simulation with detailed projections</li>
                </ul>
              </div>

              <p style="font-size:14px;color:#64748b;margin:16px 0;">
                UK ecommerce moves fast. The products trending today will not be trending next month.
                Upgrade now to keep your edge.
              </p>

              <div style="text-align:center;margin:24px 0;">
                <a href="{site_url}/pricing?utm_source=email&utm_medium=drip&utm_campaign=trial_expiry&utm_content=cta_choose_plan" style="display:inline-block;background:#4f46e5;color:#fff;padding:14px 32px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;">
                  Upgrade to Pro — £39/month
                </a>
              </div>

              <p style="font-size:12px;color:#94a3b8;text-align:center;margin-top:24px;">
                Still not sure? <a href="{site_url}/tools" style="color:#4f46e5;text-decoration:none;">Try our free tools</a>
                or <a href="{site_url}/sample-product-analysis" style="color:#4f46e5;text-decoration:none;">see a sample report</a>.
              </p>
            </div>
            """

            try:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                    json={
                        "from": f"TrendScout <{sender_email}>",
                        "to": [email],
                        "subject": f"Your {feature_label} trial has ended — here is what to do next",
                        "html": html_body,
                    },
                    timeout=10,
                )
                if resp.status_code in (200, 201):
                    sent_count += 1
                    await db.trials.update_one(
                        {"user_id": trial["user_id"]},
                        {"$set": {"expiry_notified": True, "notified_at": now.isoformat()}}
                    )
            except Exception as e:
                logger.error(f"Trial expiry email failed for {email}: {e}")

    logger.info(f"Trial expiry notifications: sent {sent_count}/{len(expired_trials)}")
    return {"records_processed": sent_count, "details": {"total": len(expired_trials), "sent": sent_count}}



@TaskRegistry.register(
    name="review_prediction_accuracy",
    description="Compare product prediction snapshots against current market data",
    default_schedule="0 6 * * *"  # Daily at 6 AM UTC
)
async def review_prediction_accuracy(db, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    1. Snapshot new products that don't have a prediction record yet.
    2. Review 30-day-old snapshots against current data.
    3. Review 90-day-old snapshots against current data.
    """
    from routes.accuracy import snapshot_prediction, review_prediction

    now = datetime.now(timezone.utc)
    reviewed_count = 0
    snapshotted_count = 0

    # Step 1: Snapshot products that have scores but no snapshot yet
    snapshotted_ids = set()
    async for snap in db.prediction_snapshots.find({}, {"product_id": 1, "_id": 0}):
        snapshotted_ids.add(snap["product_id"])

    products_to_snapshot = await db.products.find(
        {"launch_score": {"$exists": True, "$gt": 0}},
        {"_id": 0}
    ).limit(50).to_list(50)

    for p in products_to_snapshot:
        pid = p.get("id") or p.get("product_id", "")
        if pid and pid not in snapshotted_ids:
            try:
                await snapshot_prediction(db, pid, p)
                snapshotted_count += 1
            except Exception as e:
                logger.error(f"Failed to snapshot {pid}: {e}")

    # Step 2: Review snapshots that are 30+ days old and not yet reviewed
    thirty_days_ago = (now - timedelta(days=30)).isoformat()
    pending_30d = await db.prediction_snapshots.find(
        {"snapshot_date": {"$lte": thirty_days_ago}, "reviewed_30d": False}
    ).limit(20).to_list(20)

    for snap in pending_30d:
        pid = snap["product_id"]
        current = await db.products.find_one({"id": pid}, {"_id": 0})
        if not current:
            current = await db.products.find_one({"product_id": pid}, {"_id": 0})
        if current:
            try:
                await review_prediction(db, snap, current, "30d")
                reviewed_count += 1
            except Exception as e:
                logger.error(f"Failed 30d review for {pid}: {e}")

    # Step 3: Review snapshots that are 90+ days old and not yet reviewed
    ninety_days_ago = (now - timedelta(days=90)).isoformat()
    pending_90d = await db.prediction_snapshots.find(
        {"snapshot_date": {"$lte": ninety_days_ago}, "reviewed_90d": False}
    ).limit(20).to_list(20)

    for snap in pending_90d:
        pid = snap["product_id"]
        current = await db.products.find_one({"id": pid}, {"_id": 0})
        if not current:
            current = await db.products.find_one({"product_id": pid}, {"_id": 0})
        if current:
            try:
                await review_prediction(db, snap, current, "90d")
                reviewed_count += 1
            except Exception as e:
                logger.error(f"Failed 90d review for {pid}: {e}")

    logger.info(f"Accuracy review: {snapshotted_count} new snapshots, {reviewed_count} reviews completed")
    return {
        "records_processed": snapshotted_count + reviewed_count,
        "details": {
            "new_snapshots": snapshotted_count,
            "reviews_completed": reviewed_count,
        }
    }



@TaskRegistry.register(
    name="send_lead_drip_emails",
    description="Send follow-up drip emails to leads: Day 2 trending products, Day 5 trial reminder",
    default_schedule="0 9 * * *"  # Daily at 9 AM UTC
)
async def send_lead_drip_emails(db, params: dict = None) -> dict:
    """
    Drip email sequence for leads captured via quick viability search:
    - Day 2: Top 3 trending products
    - Day 5: Free trial reminder
    """
    from datetime import timedelta
    from services.email_service import email_service

    now = datetime.now(timezone.utc)
    sent_count = 0
    errors = []

    # Get all leads from viability gate that haven't been fully dripped
    leads = await db.leads.find(
        {"source": "quick_viability_gate", "digest_opt_in": {"$ne": False}},
        {"_id": 0, "email": 1, "created_at": 1, "drip_emails_sent": 1}
    ).to_list(5000)

    # Check if lead has already signed up (skip if they have)
    for lead in leads:
        email_addr = lead.get("email", "")
        created_at_str = lead.get("created_at", "")
        drip_sent = lead.get("drip_emails_sent", [])
        sent_types = [d.get("type") for d in drip_sent if isinstance(d, dict)]

        if not created_at_str:
            continue

        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue

        days_since = (now - created_at).days

        # Check if lead already registered as user (skip drip)
        existing_user = await db.users.find_one({"email": email_addr}, {"_id": 1})
        if existing_user:
            continue

        # Day 2: Send trending products email
        if days_since >= 2 and "trending_drip" not in sent_types:
            try:
                products = await db.products.find(
                    {},
                    {"_id": 0, "product_name": 1, "name": 1, "launch_score": 1, "viability_score": 1, "category": 1}
                ).sort("launch_score", -1).limit(3).to_list(3)

                result = await email_service.send_trending_drip_email(email_addr, products)
                if result.get("status") == "success":
                    await db.leads.update_one(
                        {"email": email_addr},
                        {"$addToSet": {"drip_emails_sent": {"type": "trending_drip", "sent_at": now.isoformat()}}}
                    )
                    sent_count += 1
                else:
                    errors.append(f"{email_addr}: {result.get('error', 'unknown')}")
            except Exception as e:
                errors.append(f"{email_addr}: {str(e)}")

        # Day 5: Send trial reminder email
        if days_since >= 5 and "trial_drip" not in sent_types:
            try:
                result = await email_service.send_trial_drip_email(email_addr)
                if result.get("status") == "success":
                    await db.leads.update_one(
                        {"email": email_addr},
                        {"$addToSet": {"drip_emails_sent": {"type": "trial_drip", "sent_at": now.isoformat()}}}
                    )
                    sent_count += 1
                else:
                    errors.append(f"{email_addr}: {result.get('error', 'unknown')}")
            except Exception as e:
                errors.append(f"{email_addr}: {str(e)}")

    logger.info(f"Drip emails: sent {sent_count}, errors: {len(errors)}")
    return {
        "records_processed": sent_count,
        "details": {
            "emails_sent": sent_count,
            "leads_checked": len(leads),
            "errors": errors[:10],
        }
    }



# ==================== AUTO-SYNC CONNECTED STORES ====================

@TaskRegistry.register(
    name="auto_sync_connected_stores",
    description="Auto-sync products from all connected stores every 6 hours",
    default_schedule="0 */6 * * *"
)
async def auto_sync_connected_stores(db, params: dict = None) -> dict:
    """
    Automatically sync products from all active store connections.
    Runs every 6 hours. Logs sync history for each platform.
    """
    from common.encryption import decrypt_token
    import httpx

    synced_total = 0
    errors = []
    sync_results = []

    # Find all active store connections
    connections = []
    cursor = db.platform_connections.find(
        {"status": "active", "connection_type": {"$in": ["store", "oauth"]}},
        {"_id": 0}
    )
    async for conn in cursor:
        connections.append(conn)

    logger.info(f"Auto-sync: Found {len(connections)} active store connections")

    for conn in connections:
        platform = conn.get("platform", "unknown")
        user_id = conn.get("user_id", "")
        shop = conn.get("store_url") or conn.get("shop_domain") or conn.get("shop_name", "")
        sync_start = datetime.now(timezone.utc)
        count = 0
        error_msg = None

        try:
            if platform == "shopify":
                count = await _sync_shopify_products(db, conn)
            elif platform == "etsy":
                count = await _sync_etsy_products(db, conn)
            elif platform == "woocommerce":
                count = await _sync_woocommerce_products(db, conn)
            else:
                continue

            synced_total += count
        except Exception as e:
            error_msg = str(e)[:200]
            errors.append(f"{platform}/{user_id}: {error_msg}")
            logger.warning(f"Auto-sync error for {platform}/{user_id}: {e}")

        # Log sync history
        await db.sync_history.insert_one({
            "user_id": user_id,
            "platform": platform,
            "shop": shop,
            "synced_count": count,
            "status": "success" if not error_msg else "error",
            "error": error_msg,
            "started_at": sync_start.isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "trigger": "scheduled",
        })

        sync_results.append({
            "platform": platform,
            "user_id": user_id,
            "count": count,
            "status": "success" if not error_msg else "error",
        })

    logger.info(f"Auto-sync complete: {synced_total} products synced, {len(errors)} errors")
    return {
        "records_processed": synced_total,
        "details": {
            "connections_processed": len(connections),
            "total_synced": synced_total,
            "results": sync_results,
            "errors": errors[:10],
        }
    }


async def _sync_shopify_products(db, conn: dict) -> int:
    """Sync products from a Shopify connection."""
    from common.encryption import decrypt_token
    import httpx

    access_token = conn.get("access_token", "")
    try:
        access_token = decrypt_token(access_token)
    except Exception:
        pass

    shop_domain = conn.get("store_url") or conn.get("shop_domain", "")
    if not shop_domain or not access_token:
        return 0

    base_url = shop_domain.rstrip("/")
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"

    count = 0
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{base_url}/admin/api/2024-07/products.json",
            headers={"X-Shopify-Access-Token": access_token},
            params={"limit": 250, "fields": "id,title,status,product_type,vendor,variants,images,handle"},
        )
        if resp.status_code != 200:
            raise Exception(f"Shopify API returned {resp.status_code}")

        products = resp.json().get("products", [])
        for prod in products:
            variant = prod.get("variants", [{}])[0] if prod.get("variants") else {}
            images = prod.get("images", [])
            doc = {
                "user_id": conn["user_id"],
                "platform": "shopify",
                "platform_id": str(prod["id"]),
                "shopify_id": prod["id"],
                "title": prod.get("title", ""),
                "status": prod.get("status", "active"),
                "product_type": prod.get("product_type", ""),
                "vendor": prod.get("vendor", ""),
                "price": str(variant.get("price", "0")),
                "inventory_quantity": variant.get("inventory_quantity", 0),
                "image_url": images[0]["src"] if images else "",
                "shop_domain": shop_domain,
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.synced_products.update_one(
                {"user_id": conn["user_id"], "platform": "shopify", "platform_id": doc["platform_id"]},
                {"$set": doc},
                upsert=True,
            )
            count += 1
    return count


async def _sync_etsy_products(db, conn: dict) -> int:
    """Sync products from an Etsy connection."""
    from common.encryption import decrypt_token
    import httpx

    access_token = conn.get("access_token", "")
    try:
        access_token = decrypt_token(access_token)
    except Exception:
        pass

    shop_id = conn.get("shop_id") or conn.get("store_url", "")
    if not shop_id or not access_token:
        return 0

    count = 0
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/active",
            headers={"Authorization": f"Bearer {access_token}", "x-api-key": conn.get("client_id", "")},
            params={"limit": 100},
        )
        if resp.status_code != 200:
            raise Exception(f"Etsy API returned {resp.status_code}")

        listings = resp.json().get("results", [])
        for listing in listings:
            doc = {
                "user_id": conn["user_id"],
                "platform": "etsy",
                "platform_id": str(listing.get("listing_id", "")),
                "title": listing.get("title", ""),
                "price": str(listing.get("price", {}).get("amount", 0) / listing.get("price", {}).get("divisor", 100)),
                "status": listing.get("state", "active"),
                "quantity": listing.get("quantity", 0),
                "shop_name": shop_id,
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.synced_products.update_one(
                {"user_id": conn["user_id"], "platform": "etsy", "platform_id": doc["platform_id"]},
                {"$set": doc},
                upsert=True,
            )
            count += 1
    return count


async def _sync_woocommerce_products(db, conn: dict) -> int:
    """Sync products from a WooCommerce connection."""
    from common.encryption import decrypt_token
    import httpx

    store_url = conn.get("store_url", "").rstrip("/")
    api_key = conn.get("api_key", "")
    api_secret = conn.get("api_secret", "")

    try:
        api_key = decrypt_token(api_key) if api_key else ""
    except Exception:
        pass
    try:
        api_secret = decrypt_token(api_secret) if api_secret else ""
    except Exception:
        pass

    if not store_url or not api_key or not api_secret:
        return 0

    count = 0
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{store_url}/wp-json/wc/v3/products",
            auth=(api_key, api_secret),
            params={"per_page": 100, "status": "publish"},
        )
        if resp.status_code != 200:
            raise Exception(f"WooCommerce API returned {resp.status_code}")

        products = resp.json()
        for prod in products:
            images = prod.get("images", [])
            doc = {
                "user_id": conn["user_id"],
                "platform": "woocommerce",
                "platform_id": str(prod.get("id", "")),
                "title": prod.get("name", ""),
                "price": prod.get("price", "0"),
                "status": prod.get("status", "publish"),
                "quantity": prod.get("stock_quantity") or 0,
                "image_url": images[0].get("src", "") if images else "",
                "shop_name": store_url.replace("https://", "").replace("http://", ""),
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.synced_products.update_one(
                {"user_id": conn["user_id"], "platform": "woocommerce", "platform_id": doc["platform_id"]},
                {"$set": doc},
                upsert=True,
            )
            count += 1
    return count
