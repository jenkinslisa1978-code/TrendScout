"""
Google Trends Scraper

Fetches real trend velocity data from Google Trends using pytrends.
Provides keyword interest data over time for product trend analysis.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

# How old google_trends_data must be before we refresh it (24 hours)
_STALE_AFTER_HOURS = 24
# Seconds to wait between individual keyword requests
_REQUEST_DELAY_SECS = 6
# Extra back-off when we hit a rate-limit (429) response
_RATE_LIMIT_BACKOFF_SECS = 60


class GoogleTrendsScraper:
    """
    Fetches trend velocity data from Google Trends.

    For each product, queries Google Trends for the product keyword
    and calculates trend_velocity (rate of change in interest).
    """

    def __init__(self, db):
        self.db = db
        self._pytrends = None

    def _make_pytrends(self) -> TrendReq:
        """Create a fresh TrendReq session (required after 429 blocks)."""
        return TrendReq(
            hl='en-GB',
            tz=0,
            timeout=(10, 30),
            retries=2,
            backoff_factor=0.5,
        )

    @property
    def pytrends(self):
        if self._pytrends is None:
            self._pytrends = self._make_pytrends()
        return self._pytrends

    def _reset_pytrends(self):
        """Discard the current session so it is recreated on next access."""
        self._pytrends = None

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

    def _is_rate_limit_error(self, exc: Exception) -> bool:
        """Return True if the exception looks like a Google 429 block."""
        msg = str(exc).lower()
        return '429' in msg or 'too many requests' in msg or 'quota' in msg

    def _get_trend_data(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Fetch trend data for a single keyword (sync, called in executor)."""
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
            # Re-raise so the async caller can handle 429 specifically
            raise

    async def enrich_products(self, max_products: int = 20) -> Dict[str, Any]:
        """
        Enrich products with Google Trends velocity data.

        Only fetches data for products whose google_trends_data is missing
        or older than _STALE_AFTER_HOURS hours, to avoid hammering the API.
        """
        started_at = datetime.now(timezone.utc)
        stats = {'enriched': 0, 'failed': 0, 'skipped': 0, 'rate_limited': 0}

        stale_cutoff = (datetime.now(timezone.utc) - timedelta(hours=_STALE_AFTER_HOURS)).isoformat()

        # Only fetch products that have no trends data or stale trends data
        cursor = self.db.products.find(
            {
                "is_canonical": {"$ne": False},
                "$or": [
                    {"google_trends_updated": {"$exists": False}},
                    {"google_trends_updated": {"$lt": stale_cutoff}},
                    {"google_trends_data.status": "unavailable"},
                ],
            },
            {"_id": 0, "id": 1, "product_name": 1}
        ).limit(max_products)
        products = await cursor.to_list(max_products)

        logger.info(f"Google Trends: enriching {len(products)} products (stale/missing data)")

        loop = asyncio.get_event_loop()
        consecutive_rate_limits = 0

        for product in products:
            pid = product.get('id')
            name = product.get('product_name', '')

            if not name:
                stats['skipped'] += 1
                continue

            keyword = self._extract_keyword(name)

            try:
                # Run sync pytrends call in thread executor
                trend_data = await loop.run_in_executor(None, self._get_trend_data, keyword)
                consecutive_rate_limits = 0  # Reset on success

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
                    logger.debug(f"  Google Trends '{keyword}': velocity={trend_data['trend_velocity']}%")
                else:
                    # Mark as unavailable so we don't retry until next stale window
                    await self.db.products.update_one(
                        {"id": pid},
                        {"$set": {
                            "google_trends_data": {"status": "unavailable", "keyword": keyword},
                            "google_trends_updated": datetime.now(timezone.utc).isoformat(),
                        }}
                    )
                    stats['failed'] += 1

                # Polite delay between requests
                await asyncio.sleep(_REQUEST_DELAY_SECS)

            except Exception as e:
                if self._is_rate_limit_error(e):
                    consecutive_rate_limits += 1
                    stats['rate_limited'] += 1
                    logger.warning(
                        f"Google Trends rate-limited on '{keyword}' "
                        f"(hit {consecutive_rate_limits}x in a row). "
                        f"Backing off {_RATE_LIMIT_BACKOFF_SECS}s and resetting session."
                    )
                    # Reset session — the blocked session won't recover
                    self._reset_pytrends()
                    await asyncio.sleep(_RATE_LIMIT_BACKOFF_SECS)
                    # Stop entirely if we're being repeatedly blocked
                    if consecutive_rate_limits >= 3:
                        logger.warning(
                            "Google Trends: 3 consecutive rate-limits — stopping enrichment early."
                        )
                        break
                else:
                    logger.warning(f"Google Trends error for '{keyword}': {e}")
                    stats['failed'] += 1
                    await asyncio.sleep(_REQUEST_DELAY_SECS)

        completed_at = datetime.now(timezone.utc)

        return {
            'source': 'google_trends',
            'started_at': started_at.isoformat(),
            'completed_at': completed_at.isoformat(),
            'duration_seconds': (completed_at - started_at).total_seconds(),
            **stats,
        }
