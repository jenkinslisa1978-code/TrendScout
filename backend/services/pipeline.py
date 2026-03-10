"""
Data Pipeline Orchestrator

Coordinates all data sources and scoring for automated updates.
Runs on schedule or on-demand.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

from .data_sources import (
    TikTokTrends,
    AmazonTrends,
    AliExpressProducts,
    CJDropshippingProducts,
    CompetitorIntelligence,
    AdActivityAnalyzer,
)
from .scoring import ScoringEngine
from .opportunity_feed_service import create_feed_service
from .notification_service import create_notification_service, NotificationType

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result from a pipeline run"""
    success: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    products_processed: int = 0
    products_created: int = 0
    products_updated: int = 0
    alerts_generated: int = 0
    errors: List[str] = field(default_factory=list)
    source_results: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> float:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0


class DataPipeline:
    """
    Main data pipeline orchestrator.
    
    Workflow:
    1. Fetch data from all enabled sources
    2. Normalize and merge product data
    3. Update competitor intelligence
    4. Update ad activity signals
    5. Run scoring engine
    6. Generate alerts for high-opportunity products
    """
    
    def __init__(self, db):
        self.db = db
        
        # Initialize data sources
        self.sources = {
            'tiktok': TikTokTrends(db),
            'amazon': AmazonTrends(db),
            'aliexpress': AliExpressProducts(db),
            'cj_dropshipping': CJDropshippingProducts(db),
        }
        
        # Initialize analysis modules
        self.competitor_analyzer = CompetitorIntelligence(db)
        self.ad_analyzer = AdActivityAnalyzer(db)
        self.scoring_engine = ScoringEngine(db)
        self.feed_service = create_feed_service(db)
        self.notification_service = create_notification_service(db)
    
    async def run_full_pipeline(self, options: Dict[str, Any] = None) -> PipelineResult:
        """
        Run the complete data pipeline.
        
        Options:
            sources: List of sources to run (default: all)
            skip_scoring: Skip score calculation
            skip_alerts: Skip alert generation
            limit: Max products to process
        """
        options = options or {}
        result = PipelineResult(
            success=False,
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            # Step 1: Fetch from trend sources
            logger.info("Step 1: Fetching from trend sources...")
            await self._fetch_trend_sources(result, options)
            
            # Step 2: Fetch from supplier sources
            logger.info("Step 2: Fetching from supplier sources...")
            await self._fetch_supplier_sources(result, options)
            
            # Step 3: Update competitor intelligence
            logger.info("Step 3: Updating competitor intelligence...")
            await self._update_competitor_data(result, options)
            
            # Step 4: Update ad activity
            logger.info("Step 4: Updating ad activity signals...")
            await self._update_ad_activity(result, options)
            
            # Step 5: Run scoring engine
            if not options.get('skip_scoring'):
                logger.info("Step 5: Running scoring engine...")
                await self._run_scoring(result, options)
            
            # Step 6: Generate alerts
            if not options.get('skip_alerts'):
                logger.info("Step 6: Generating opportunity alerts...")
                await self._generate_alerts(result, options)
            
            # Step 7: Generate opportunity feed events
            if not options.get('skip_feed'):
                logger.info("Step 7: Generating opportunity feed events...")
                await self._generate_feed_events(result, options)
            
            # Step 8: Send user notifications for strong launches
            if not options.get('skip_notifications'):
                logger.info("Step 8: Sending user notifications...")
                await self._send_user_notifications(result, options)
            
            result.success = True
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            result.errors.append(str(e))
            result.success = False
        
        result.completed_at = datetime.now(timezone.utc)
        
        # Log pipeline run
        await self._log_pipeline_run(result)
        
        return result
    
    async def _fetch_trend_sources(self, result: PipelineResult, options: Dict):
        """Fetch from TikTok and Amazon trend sources"""
        sources_to_run = options.get('sources', ['tiktok', 'amazon'])
        
        for source_name in sources_to_run:
            if source_name not in ['tiktok', 'amazon']:
                continue
            
            source = self.sources.get(source_name)
            if not source:
                continue
            
            try:
                fetch_result = await source.fetch(limit=options.get('limit', 25))
                
                if fetch_result.success:
                    update_stats = await source.update_database(fetch_result)
                    result.products_created += update_stats['created']
                    result.products_updated += update_stats['updated']
                    result.source_results[source_name] = {
                        'fetched': fetch_result.items_count,
                        'created': update_stats['created'],
                        'updated': update_stats['updated'],
                        'confidence': fetch_result.confidence_level.value,
                    }
                else:
                    result.errors.append(f"{source_name}: {fetch_result.error_message}")
                    
            except Exception as e:
                logger.error(f"Error fetching {source_name}: {e}")
                result.errors.append(f"{source_name}: {str(e)}")
    
    async def _fetch_supplier_sources(self, result: PipelineResult, options: Dict):
        """Fetch from AliExpress and CJ Dropshipping"""
        sources_to_run = options.get('sources', ['aliexpress', 'cj_dropshipping'])
        
        for source_name in sources_to_run:
            if source_name not in ['aliexpress', 'cj_dropshipping']:
                continue
            
            source = self.sources.get(source_name)
            if not source:
                continue
            
            try:
                fetch_result = await source.fetch(limit=options.get('limit', 20))
                
                if fetch_result.success:
                    # Merge supplier data with existing products
                    merge_stats = await self._merge_supplier_data(fetch_result)
                    result.products_updated += merge_stats['updated']
                    result.source_results[source_name] = {
                        'fetched': fetch_result.items_count,
                        'merged': merge_stats['updated'],
                        'confidence': fetch_result.confidence_level.value,
                    }
                else:
                    result.errors.append(f"{source_name}: {fetch_result.error_message}")
                    
            except Exception as e:
                logger.error(f"Error fetching {source_name}: {e}")
                result.errors.append(f"{source_name}: {str(e)}")
    
    async def _merge_supplier_data(self, fetch_result) -> Dict[str, int]:
        """Merge supplier data into existing products"""
        stats = {'updated': 0, 'not_found': 0}
        
        for supplier_product in fetch_result.data:
            product_name = supplier_product.get('product_name', '')
            
            # Find matching product by name
            existing = await self.db.products.find_one({
                "product_name": {"$regex": product_name, "$options": "i"}
            })
            
            if existing:
                # Update supplier-specific fields
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
                
                await self.db.products.update_one(
                    {"id": existing['id']},
                    {"$set": supplier_fields}
                )
                stats['updated'] += 1
            else:
                stats['not_found'] += 1
        
        return stats
    
    async def _update_competitor_data(self, result: PipelineResult, options: Dict):
        """Update competitor intelligence for all products"""
        try:
            stats = await self.competitor_analyzer.batch_update_competitors(
                limit=options.get('limit', 100)
            )
            result.products_updated += stats['updated']
            result.source_results['competitor_intelligence'] = stats
        except Exception as e:
            logger.error(f"Competitor update error: {e}")
            result.errors.append(f"competitor_intelligence: {str(e)}")
    
    async def _update_ad_activity(self, result: PipelineResult, options: Dict):
        """Update ad activity signals for all products"""
        try:
            stats = await self.ad_analyzer.batch_update_ad_activity(
                limit=options.get('limit', 100)
            )
            result.products_updated += stats['updated']
            result.source_results['ad_activity'] = stats
        except Exception as e:
            logger.error(f"Ad activity update error: {e}")
            result.errors.append(f"ad_activity: {str(e)}")
    
    async def _run_scoring(self, result: PipelineResult, options: Dict):
        """Run scoring engine on all products"""
        try:
            stats = await self.scoring_engine.batch_update_scores(
                limit=options.get('limit', 100)
            )
            result.products_processed = stats['updated'] + stats['failed']
            result.source_results['scoring'] = stats
        except Exception as e:
            logger.error(f"Scoring error: {e}")
            result.errors.append(f"scoring: {str(e)}")
    
    async def _generate_alerts(self, result: PipelineResult, options: Dict):
        """Generate alerts for high-opportunity products"""
        try:
            # Find products with high market scores that don't have recent alerts
            cursor = self.db.products.find({
                "market_score": {"$gte": 75}
            }, {"_id": 0}).limit(20)
            
            products = await cursor.to_list(20)
            alerts_created = 0
            
            for product in products:
                alert = self._create_alert(product)
                if alert:
                    await self.db.alerts.insert_one(alert)
                    alerts_created += 1
            
            result.alerts_generated = alerts_created
            result.source_results['alerts'] = {'created': alerts_created}
            
        except Exception as e:
            logger.error(f"Alert generation error: {e}")
            result.errors.append(f"alerts: {str(e)}")
    
    def _create_alert(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an opportunity alert for a product"""
        import uuid
        
        market_score = product.get('market_score', 0)
        market_label = product.get('market_label', 'competitive')
        early_label = product.get('early_trend_label', 'stable')
        
        # Determine alert type and priority
        if market_score >= 90:
            alert_type = 'massive_opportunity'
            priority = 'critical'
            title = f"🚀 Massive Opportunity: {product['product_name']}"
        elif market_score >= 75 and early_label in ['exploding', 'rising']:
            alert_type = 'early_trend_opportunity'
            priority = 'high'
            title = f"🔥 Early Trend Detected: {product['product_name']}"
        elif market_score >= 75:
            alert_type = 'strong_opportunity'
            priority = 'medium'
            title = f"📈 Strong Opportunity: {product['product_name']}"
        else:
            return None
        
        return {
            'id': str(uuid.uuid4()),
            'product_id': product['id'],
            'product_name': product['product_name'],
            'alert_type': alert_type,
            'priority': priority,
            'title': title,
            'message': self._generate_alert_message(product),
            'market_score': market_score,
            'market_label': market_label,
            'scores': product.get('market_score_breakdown', {}),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'read': False,
        }
    
    def _generate_alert_message(self, product: Dict[str, Any]) -> str:
        """Generate alert message based on product signals"""
        market_score = product.get('market_score', 0)
        margin = product.get('estimated_margin', 0)
        competition = product.get('competition_level', 'medium')
        competitors = product.get('active_competitor_stores', 0)
        
        parts = []
        
        parts.append(f"Market Score: {market_score}/100")
        parts.append(f"Est. Margin: £{margin:.2f}")
        parts.append(f"Competition: {competition.title()} ({competitors} stores)")
        
        if product.get('early_trend_label') in ['exploding', 'rising']:
            parts.append(f"Trend: {product['early_trend_label'].title()}")
        
        return " | ".join(parts)
    
    async def _generate_feed_events(self, result: PipelineResult, options: Dict):
        """
        Generate opportunity feed events for products with significant signal changes.
        Creates meaningful events for the live dashboard feed.
        """
        from .opportunity_feed_service import FeedEventType
        
        try:
            events_created = 0
            
            # Get products with strong launch scores (for new high score events)
            strong_products = await self.db.products.find({
                "launch_score": {"$gte": 75}
            }, {"_id": 0}).sort("launch_score", -1).limit(15).to_list(15)
            
            for product in strong_products:
                # Check for strong launch opportunity (score >= 80)
                if product.get("launch_score", 0) >= 80:
                    event = await self.feed_service.create_event(
                        FeedEventType.ENTERED_STRONG_LAUNCH,
                        product,
                        reason=f"Launch Score of {product.get('launch_score')} - excellent conditions for launch",
                        change_data={"launch_score": product.get("launch_score")},
                        confidence=0.9
                    )
                    if event:
                        events_created += 1
                
                # New high score products (75-79)
                elif product.get("launch_score", 0) >= 75:
                    event = await self.feed_service.create_event(
                        FeedEventType.NEW_HIGH_SCORE,
                        product,
                        reason=f"Promising product with Launch Score {product.get('launch_score')} detected",
                        change_data={"launch_score": product.get("launch_score")},
                        confidence=0.85
                    )
                    if event:
                        events_created += 1
            
            # Get products with early trend signals
            trending_products = await self.db.products.find({
                "early_trend_label": {"$in": ["exploding", "rising"]}
            }, {"_id": 0}).sort("early_trend_score", -1).limit(10).to_list(10)
            
            for product in trending_products:
                if product.get("early_trend_label") == "exploding":
                    event = await self.feed_service.create_event(
                        FeedEventType.TREND_SPIKE,
                        product,
                        reason=f"Exploding trend detected with {product.get('view_growth_rate', 0):.0f}% growth velocity",
                        change_data={
                            "early_trend_label": product.get("early_trend_label"),
                            "view_growth_rate": product.get("view_growth_rate", 0)
                        },
                        confidence=0.85
                    )
                    if event:
                        events_created += 1
            
            # Check for approaching saturation
            saturating_products = await self.db.products.find({
                "market_saturation": {"$gte": 70}
            }, {"_id": 0}).limit(5).to_list(5)
            
            for product in saturating_products:
                event = await self.feed_service.create_event(
                    FeedEventType.APPROACHING_SATURATION,
                    product,
                    reason=f"Market saturation at {product.get('market_saturation', 70)}% - opportunity window narrowing",
                    change_data={"market_saturation": product.get("market_saturation")},
                    confidence=0.75
                )
                if event:
                    events_created += 1
            
            result.source_results['feed_events'] = {'created': events_created}
            logger.info(f"Generated {events_created} feed events")
            
        except Exception as e:
            logger.error(f"Feed event generation error: {e}")
            result.errors.append(f"feed_events: {str(e)}")

    async def _send_user_notifications(self, result: PipelineResult, options: Dict):
        """
        Send notifications to users for strong launch products and exploding trends.
        This runs after feed events are generated.
        """
        try:
            notifications_sent = 0
            
            # Get products that just entered Strong Launch (score >= 80)
            strong_launch_products = await self.db.products.find({
                "launch_score": {"$gte": 80}
            }, {"_id": 0}).sort("launch_score", -1).limit(10).to_list(10)
            
            for product in strong_launch_products:
                try:
                    await self.notification_service.process_strong_launch_alert(
                        product=product,
                        previous_score=0  # Assume new for pipeline run
                    )
                    notifications_sent += 1
                except Exception as e:
                    logger.warning(f"Failed to process strong launch notification for {product.get('product_name')}: {e}")
            
            # Get products with exploding trends
            exploding_products = await self.db.products.find({
                "early_trend_label": "exploding"
            }, {"_id": 0}).sort("early_trend_score", -1).limit(5).to_list(5)
            
            for product in exploding_products:
                try:
                    await self.notification_service.process_exploding_trend_alert(
                        product=product,
                        previous_label="rising"  # Assume trend just changed
                    )
                    notifications_sent += 1
                except Exception as e:
                    logger.warning(f"Failed to process exploding trend notification for {product.get('product_name')}: {e}")
            
            result.source_results['notifications'] = {'sent': notifications_sent}
            logger.info(f"Processed {notifications_sent} notification alerts")
            
        except Exception as e:
            logger.error(f"User notification error: {e}")
            result.errors.append(f"notifications: {str(e)}")

    
    async def _log_pipeline_run(self, result: PipelineResult):
        """Log pipeline run to database"""
        import uuid
        
        log_entry = {
            'id': str(uuid.uuid4()),
            'job_type': 'full_pipeline',
            'status': 'completed' if result.success else 'failed',
            'started_at': result.started_at.isoformat(),
            'completed_at': result.completed_at.isoformat() if result.completed_at else None,
            'duration_seconds': result.duration_seconds,
            'products_processed': result.products_processed,
            'products_created': result.products_created,
            'products_updated': result.products_updated,
            'alerts_generated': result.alerts_generated,
            'errors': result.errors,
            'source_results': result.source_results,
        }
        
        await self.db.automation_logs.insert_one(log_entry)
    
    async def run_quick_refresh(self) -> PipelineResult:
        """
        Quick refresh - just update scores and competitor data.
        Faster than full pipeline.
        """
        return await self.run_full_pipeline({
            'sources': [],  # Skip source fetching
            'skip_alerts': True,
        })
    
    async def run_source_only(self, source: str) -> PipelineResult:
        """Run pipeline for a single data source"""
        return await self.run_full_pipeline({
            'sources': [source],
            'skip_alerts': True,
        })
