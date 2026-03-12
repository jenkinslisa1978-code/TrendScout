"""
Meta Ad Library Official API Client

Uses Facebook Graph API v25.0 /ads_archive endpoint.
Config: META_AD_LIBRARY_TOKEN in .env

Fallback chain: Official API → Estimation → Hardcoded
"""

import os
import logging
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

import aiohttp

logger = logging.getLogger("api.meta_ads")

# Rate limit: ~200 calls/hour for standard tokens
_last_call_ts: float = 0
_MIN_INTERVAL = 2.0  # seconds between calls


class MetaAdLibraryClient:
    BASE_URL = "https://graph.facebook.com/v25.0/ads_archive"

    def __init__(self):
        self.token = os.environ.get("META_AD_LIBRARY_TOKEN", "")
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 3600  # 1 hour

    @property
    def is_configured(self) -> bool:
        return bool(self.token)

    async def health_check(self) -> Dict[str, Any]:
        """Test API connectivity."""
        if not self.is_configured:
            return {
                "status": "not_configured",
                "credential_detected": False,
                "mode": "estimation",
                "message": "META_AD_LIBRARY_TOKEN not set in .env",
            }
        try:
            result = await self.search_ads("test", country="US", limit=1)
            if result is not None:
                return {
                    "status": "healthy",
                    "credential_detected": True,
                    "mode": "live",
                    "message": "API responding normally",
                    "last_check": datetime.now(timezone.utc).isoformat(),
                }
            return {
                "status": "degraded",
                "credential_detected": True,
                "mode": "estimation",
                "message": "API returned empty response",
                "last_check": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "failed",
                "credential_detected": True,
                "mode": "estimation",
                "message": str(e)[:200],
                "last_check": datetime.now(timezone.utc).isoformat(),
            }

    async def search_ads(
        self,
        search_terms: str,
        country: str = "GB",
        limit: int = 50,
    ) -> Optional[Dict[str, Any]]:
        """
        Search Meta Ad Library for active ads matching search terms.
        Returns structured signals or None on failure.
        """
        if not self.is_configured:
            return None

        # Rate limiting
        global _last_call_ts
        elapsed = time.time() - _last_call_ts
        if elapsed < _MIN_INTERVAL:
            await _async_sleep(_MIN_INTERVAL - elapsed)
        _last_call_ts = time.time()

        # Cache check
        cache_key = hashlib.md5(f"{search_terms}:{country}".encode()).hexdigest()
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < self._cache_ttl:
            logger.debug(f"Meta cache hit: {search_terms}")
            return cached["data"]

        params = {
            "access_token": self.token,
            "search_terms": search_terms[:100],
            "ad_reached_countries": f'["{country}"]',
            "ad_active_status": "ACTIVE",
            "fields": "id,ad_delivery_start_time,page_name,publisher_platforms,ad_creative_bodies",
            "limit": limit,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=20),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ads = data.get("data", [])
                        result = self._parse_ads(ads, search_terms)

                        self._cache[cache_key] = {"data": result, "ts": time.time()}
                        logger.info(f"Meta API: {len(ads)} ads found for '{search_terms}'")
                        return result

                    elif resp.status == 429:
                        logger.warning("Meta API rate limited")
                        return None
                    else:
                        body = await resp.text()
                        logger.warning(f"Meta API error {resp.status}: {body[:200]}")
                        return None

        except aiohttp.ClientError as e:
            logger.error(f"Meta API connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Meta API unexpected error: {e}")
            return None

    def _parse_ads(self, ads: List[Dict], search_terms: str) -> Dict[str, Any]:
        """Parse raw ad data into structured signals."""
        if not ads:
            return {
                "meta_active_ads": 0,
                "meta_ad_growth_7d": 0.0,
                "meta_estimated_spend_monthly": 0,
                "meta_platforms": {},
                "meta_advertisers": [],
                "meta_earliest_ad": None,
            }

        # Count platform distribution
        platform_counts: Dict[str, int] = {}
        advertisers = set()
        earliest_date = None

        for ad in ads:
            # Platforms
            platforms = ad.get("publisher_platforms", [])
            for p in platforms:
                platform_counts[p] = platform_counts.get(p, 0) + 1

            # Advertiser
            page = ad.get("page_name", "")
            if page:
                advertisers.add(page)

            # Dates
            start = ad.get("ad_delivery_start_time")
            if start:
                if earliest_date is None or start < earliest_date:
                    earliest_date = start

        total = max(len(ads), 1)
        platform_dist = {k: round(v / total, 3) for k, v in platform_counts.items()}

        # Estimate recent growth (simple heuristic: >20 ads suggests growing)
        growth = 0.0
        if len(ads) > 30:
            growth = 0.15
        elif len(ads) > 10:
            growth = 0.05

        return {
            "meta_active_ads": len(ads),
            "meta_ad_growth_7d": growth,
            "meta_estimated_spend_monthly": len(ads) * 45,
            "meta_platforms": platform_dist,
            "meta_advertisers": list(advertisers)[:10],
            "meta_earliest_ad": earliest_date,
        }


async def _async_sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)
