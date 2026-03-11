"""
Google Trends Scraper

Fetches real trend velocity data from Google Trends using pytrends.
Provides keyword interest data over time for product trend analysis.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)


class GoogleTrendsScraper:
    """
    Fetches trend velocity data from Google Trends.
    
    For each product, queries Google Trends for the product keyword
    and calculates trend_velocity (rate of change in interest).
    """
    
    def __init__(self, db):
        self.db = db
        self._pytrends = None
    
    @property
    def pytrends(self):
        if self._pytrends is None:
            self._pytrends = TrendReq(hl='en-GB', tz=0, timeout=(10, 25))
        return self._pytrends
    
    def _extract_keyword(self, product_name: str) -> str:
        """Extract a clean search keyword from a product name."""
        # Remove brand names, model numbers, measurements
        cleaned = re.sub(r'\b\d+\s*(ml|g|kg|cm|mm|inch|oz|pack|pcs|x)\b', '', product_name, flags=re.IGNORECASE)
        cleaned = re.sub(r'[,\-\(\)\[\]\/]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        # Take first 3-4 meaningful words
        words = [w for w in cleaned.split() if len(w) > 2]
        keyword = ' '.join(words[:4])
        return keyword[:50] if keyword else product_name[:50]
    
    def _get_trend_data(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Fetch trend data for a single keyword (sync)."""
        try:
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='GB')
            interest = self.pytrends.interest_over_time()
            
            if interest.empty or keyword not in interest.columns:
                return None
            
            values = interest[keyword].tolist()
            if len(values) < 4:
                return None
            
            current = values[-1]
            avg_all = sum(values) / len(values) if values else 0
            recent_avg = sum(values[-4:]) / 4  # Last 4 weeks
            older_avg = sum(values[:4]) / 4 if len(values) >= 8 else avg_all  # First 4 weeks
            max_val = max(values)
            
            # Velocity = rate of change
            velocity = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            
            return {
                'keyword': keyword,
                'current_interest': int(current),
                'average_interest': round(avg_all, 1),
                'recent_average': round(recent_avg, 1),
                'max_interest': int(max_val),
                'trend_velocity': round(velocity, 1),
                'data_points': len(values),
                'fetched_at': datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.warning(f"Google Trends error for '{keyword}': {e}")
            return None
    
    async def enrich_products(self, max_products: int = 50) -> Dict[str, Any]:
        """
        Enrich products with Google Trends velocity data.
        
        Fetches trend data for products that don't have recent trend_velocity.
        """
        started_at = datetime.now(timezone.utc)
        stats = {'enriched': 0, 'failed': 0, 'skipped': 0}
        
        # Get products needing trend data (no google_trends_data or stale)
        cursor = self.db.products.find(
            {"is_canonical": {"$ne": False}},
            {"_id": 0, "id": 1, "product_name": 1, "google_trends_data": 1}
        ).limit(max_products)
        products = await cursor.to_list(max_products)
        
        logger.info(f"Enriching {len(products)} products with Google Trends data")
        
        loop = asyncio.get_event_loop()
        
        for product in products:
            pid = product.get('id')
            name = product.get('product_name', '')
            
            if not name:
                stats['skipped'] += 1
                continue
            
            keyword = self._extract_keyword(name)
            
            try:
                # Run sync pytrends call in executor
                trend_data = await loop.run_in_executor(None, self._get_trend_data, keyword)
                
                if trend_data:
                    await self.db.products.update_one(
                        {"id": pid},
                        {"$set": {
                            "google_trends_data": trend_data,
                            "trend_velocity": trend_data['trend_velocity'],
                            "google_trends_updated": trend_data['fetched_at'],
                        }}
                    )
                    stats['enriched'] += 1
                    logger.debug(f"  {keyword}: velocity={trend_data['trend_velocity']}%")
                else:
                    # Mark as unavailable, don't fabricate
                    await self.db.products.update_one(
                        {"id": pid},
                        {"$set": {
                            "google_trends_data": {"status": "unavailable", "keyword": keyword},
                            "google_trends_updated": datetime.now(timezone.utc).isoformat(),
                        }}
                    )
                    stats['failed'] += 1
                
                # Rate limit: Google Trends has strict limits
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error enriching {name}: {e}")
                stats['failed'] += 1
                await asyncio.sleep(5)  # Back off on errors
        
        completed_at = datetime.now(timezone.utc)
        
        return {
            'source': 'google_trends',
            'started_at': started_at.isoformat(),
            'completed_at': completed_at.isoformat(),
            'duration_seconds': (completed_at - started_at).total_seconds(),
            **stats,
        }
