"""
Data Ingestion Orchestrator

Coordinates data ingestion from multiple sources with:
- Parallel execution where safe
- Health monitoring
- Graceful fallbacks
- Result aggregation
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from .aliexpress_scraper import AliExpressScraper
from .tiktok_scraper import TikTokTrendsScraper
from .amazon_scraper import AmazonMoversScraper
from .cj_scraper import CJDropshippingScraper
from . import DataIngestionResult

logger = logging.getLogger(__name__)


class DataIngestionOrchestrator:
    """
    Orchestrates data ingestion from all sources.
    
    Features:
    - Sequential execution to respect rate limits
    - Health monitoring per source
    - Graceful fallback when sources fail
    - Aggregated results and statistics
    """
    
    def __init__(self, db):
        self.db = db
        self.scrapers = {
            'aliexpress': AliExpressScraper(db),
            'tiktok_trends': TikTokTrendsScraper(db),
            'amazon_movers': AmazonMoversScraper(db),
            'cj_dropshipping': CJDropshippingScraper(db),
        }
    
    async def run_full_ingestion(
        self,
        sources: Optional[List[str]] = None,
        max_products_per_source: int = 30
    ) -> Dict[str, Any]:
        """
        Run full data ingestion from all or selected sources.
        
        Args:
            sources: List of source names to run (None = all)
            max_products_per_source: Max products to fetch per source
            
        Returns:
            Aggregated results dictionary
        """
        started_at = datetime.now(timezone.utc)
        results = {}
        
        # Determine which sources to run
        source_list = sources or list(self.scrapers.keys())
        
        logger.info(f"Starting data ingestion from {len(source_list)} sources")
        
        # Run sources sequentially to avoid overwhelming rate limits
        for source_name in source_list:
            if source_name not in self.scrapers:
                logger.warning(f"Unknown source: {source_name}")
                continue
            
            scraper = self.scrapers[source_name]
            
            # Check if source is healthy enough to use
            if not scraper.is_healthy():
                logger.warning(f"Skipping {source_name}: source is unhealthy")
                results[source_name] = {
                    'success': False,
                    'error': 'Source marked as unhealthy',
                    'health_status': scraper.get_health().status.value
                }
                continue
            
            try:
                logger.info(f"Running ingestion for: {source_name}")
                
                if source_name == 'tiktok_trends':
                    result = await scraper.ingest_trends(max_items=max_products_per_source)
                else:
                    result = await scraper.ingest_products(max_products=max_products_per_source)
                
                results[source_name] = result.to_dict()
                
                # Brief pause between sources
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Ingestion failed for {source_name}: {e}")
                results[source_name] = {
                    'success': False,
                    'error': str(e),
                    'source_name': source_name
                }
        
        # Calculate totals
        completed_at = datetime.now(timezone.utc)
        
        total_fetched = sum(r.get('products_fetched', 0) for r in results.values())
        total_created = sum(r.get('products_created', 0) for r in results.values())
        total_updated = sum(r.get('products_updated', 0) for r in results.values())
        total_failed = sum(r.get('products_failed', 0) for r in results.values())
        successful_sources = sum(1 for r in results.values() if r.get('success'))
        
        summary = {
            'started_at': started_at.isoformat(),
            'completed_at': completed_at.isoformat(),
            'duration_seconds': (completed_at - started_at).total_seconds(),
            'sources_attempted': len(source_list),
            'sources_successful': successful_sources,
            'total_products_fetched': total_fetched,
            'total_products_created': total_created,
            'total_products_updated': total_updated,
            'total_products_failed': total_failed,
            'results_by_source': results
        }
        
        # Save ingestion run to database
        await self._save_ingestion_run(summary)
        
        logger.info(
            f"Ingestion complete: {total_fetched} fetched, "
            f"{total_created} created, {total_updated} updated"
        )
        
        return summary
    
    async def run_source_ingestion(
        self,
        source_name: str,
        max_products: int = 30
    ) -> DataIngestionResult:
        """
        Run ingestion for a single source.
        
        Args:
            source_name: Name of the source to run
            max_products: Max products to fetch
            
        Returns:
            DataIngestionResult for this source
        """
        if source_name not in self.scrapers:
            result = DataIngestionResult(source_name=source_name)
            result.errors.append(f"Unknown source: {source_name}")
            result.complete(success=False)
            return result
        
        scraper = self.scrapers[source_name]
        
        if source_name == 'tiktok_trends':
            return await scraper.ingest_trends(max_items=max_products)
        else:
            return await scraper.ingest_products(max_products=max_products)
    
    async def get_source_health(self, source_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health status for sources.
        
        Args:
            source_name: Specific source (None = all)
            
        Returns:
            Health status dictionary
        """
        if source_name:
            if source_name not in self.scrapers:
                return {'error': f'Unknown source: {source_name}'}
            
            scraper = self.scrapers[source_name]
            health = scraper.get_health()
            return {
                source_name: {
                    'status': health.status.value,
                    'last_success': health.last_success.isoformat() if health.last_success else None,
                    'last_failure': health.last_failure.isoformat() if health.last_failure else None,
                    'consecutive_failures': health.consecutive_failures,
                    'success_rate_24h': health.success_rate_24h,
                    'avg_response_time_ms': health.avg_response_time_ms,
                    'last_error': health.last_error
                }
            }
        
        # Return health for all sources
        health_status = {}
        
        for name, scraper in self.scrapers.items():
            health = scraper.get_health()
            health_status[name] = {
                'status': health.status.value,
                'last_success': health.last_success.isoformat() if health.last_success else None,
                'consecutive_failures': health.consecutive_failures,
                'success_rate_24h': health.success_rate_24h
            }
        
        # Also fetch from database
        cursor = self.db.source_health.find({}, {"_id": 0})
        db_health = await cursor.to_list(100)
        
        for item in db_health:
            name = item.get('source_name')
            if name and name not in health_status:
                health_status[name] = item
        
        return health_status
    
    async def get_ingestion_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent ingestion runs"""
        cursor = self.db.ingestion_runs.find(
            {},
            {"_id": 0}
        ).sort("started_at", -1).limit(limit)
        
        return await cursor.to_list(limit)
    
    async def _save_ingestion_run(self, summary: Dict[str, Any]):
        """Save ingestion run to database"""
        # Create a copy to avoid mutating the original with _id
        run_doc = {**summary}
        await self.db.ingestion_runs.insert_one(run_doc)
    
    async def get_data_quality_report(self) -> Dict[str, Any]:
        """
        Generate a data quality report showing:
        - Real vs simulated data breakdown
        - Confidence score distribution
        - Source coverage
        """
        # Count products by data source
        pipeline = [
            {
                "$group": {
                    "_id": "$data_source",
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence_score"},
                    "real_count": {
                        "$sum": {"$cond": [{"$eq": ["$is_real_data", True]}, 1, 0]}
                    }
                }
            }
        ]
        
        source_stats = await self.db.products.aggregate(pipeline).to_list(100)
        
        # Total counts
        total_products = await self.db.products.count_documents({})
        real_products = await self.db.products.count_documents({"is_real_data": True})
        simulated_products = total_products - real_products
        
        # Confidence distribution
        confidence_pipeline = [
            {
                "$bucket": {
                    "groupBy": "$confidence_score",
                    "boundaries": [0, 25, 50, 75, 100, 101],
                    "default": "unknown",
                    "output": {"count": {"$sum": 1}}
                }
            }
        ]
        
        confidence_dist = await self.db.products.aggregate(confidence_pipeline).to_list(10)
        
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_products": total_products,
            "real_data_products": real_products,
            "simulated_products": simulated_products,
            "real_data_percentage": round((real_products / total_products * 100), 1) if total_products > 0 else 0,
            "by_source": {
                item["_id"] or "unknown": {
                    "count": item["count"],
                    "avg_confidence": round(item["avg_confidence"] or 0, 1),
                    "real_count": item["real_count"]
                }
                for item in source_stats
            },
            "confidence_distribution": {
                f"{b['_id']}-{b['_id']+24}": b["count"]
                for b in confidence_dist
                if isinstance(b.get('_id'), (int, float))
            }
        }
