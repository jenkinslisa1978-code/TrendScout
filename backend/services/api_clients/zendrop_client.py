"""
Zendrop Supplier API Client

Config: ZENDROP_API_KEY in .env

Fallback chain: Official API → Estimation → Hardcoded
When ZENDROP_API_KEY is set, uses live API data.
Otherwise, falls back to estimation mode using product data.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

import aiohttp

logger = logging.getLogger("api.zendrop")

_last_call_ts: float = 0
_MIN_INTERVAL = 1.0


class ZendropClient:
    BASE_URL = "https://api.zendrop.com/v1"

    def __init__(self):
        self.api_key = os.environ.get("ZENDROP_API_KEY", "")
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 1800  # 30 min

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def health_check(self) -> Dict[str, Any]:
        """Test API connectivity."""
        if not self.is_configured:
            return {
                "status": "not_configured",
                "credential_detected": False,
                "mode": "estimation",
                "message": "ZENDROP_API_KEY not set in .env",
            }
        try:
            result = await self.search_products("phone case", limit=1)
            if result is not None:
                return {
                    "status": "healthy",
                    "credential_detected": True,
                    "mode": "live",
                    "message": "API responding, found products",
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

    # ── HTTP helpers ──
    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated GET request to Zendrop API."""
        import time
        global _last_call_ts
        now = time.time()
        if now - _last_call_ts < _MIN_INTERVAL:
            import asyncio
            await asyncio.sleep(_MIN_INTERVAL - (now - _last_call_ts))
        _last_call_ts = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    logger.warning(f"Zendrop API {endpoint} returned {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"Zendrop API error on {endpoint}: {e}")
            return None

    # ── Product Search ──
    async def search_products(self, query: str, limit: int = 20) -> Optional[List[Dict]]:
        """Search Zendrop catalog for products."""
        if not self.is_configured:
            return None

        cache_key = f"search:{query}:{limit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        data = await self._get("/products", params={"q": query, "limit": limit})
        if data and "products" in data:
            products = data["products"]
            self._set_cached(cache_key, products)
            return products
        return None

    # ── Product Details ──
    async def get_product(self, sku: str) -> Optional[Dict]:
        """Get detailed product info from Zendrop."""
        if not self.is_configured:
            return None

        cache_key = f"product:{sku}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        data = await self._get(f"/products/{sku}")
        if data:
            self._set_cached(cache_key, data)
            return data
        return None

    # ── Shipping Estimate ──
    async def get_shipping_estimate(self, sku: str, country: str = "GB") -> Optional[Dict]:
        """Get shipping cost and time estimate."""
        if not self.is_configured:
            return None

        cache_key = f"shipping:{sku}:{country}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        data = await self._get(f"/products/{sku}/shipping", params={"destination_country": country})
        if data:
            result = {
                "shipping_cost": float(data.get("cost", 0)),
                "estimated_days": data.get("estimated_delivery_days", 7),
                "carrier": data.get("carrier", "Standard"),
            }
            self._set_cached(cache_key, result)
            return result
        return None

    # ── Availability ──
    async def check_availability(self, sku: str, quantity: int = 1) -> Optional[bool]:
        """Check if a product is available in the requested quantity."""
        if not self.is_configured:
            return None

        data = await self._get(f"/products/{sku}/availability", params={"quantity": quantity})
        if data:
            return data.get("available", False)
        return None

    # ── Estimation Fallback ──
    def estimate_supplier_data(self, product: Dict) -> Dict[str, Any]:
        """
        Generate estimated Zendrop supplier data from existing product info.
        Used when API key is not configured (estimation mode).
        """
        retail_price = product.get("estimated_retail_price", 0)
        existing_supplier_cost = product.get("supplier_cost", product.get("estimated_supplier_cost", 0))

        # Zendrop typically has slightly higher costs than AliExpress but faster shipping
        if existing_supplier_cost > 0:
            zendrop_cost = round(existing_supplier_cost * 1.15, 2)  # ~15% premium
        elif retail_price > 0:
            zendrop_cost = round(retail_price * 0.35, 2)  # ~35% of retail
        else:
            zendrop_cost = 0

        shipping_cost = round(max(3.50, zendrop_cost * 0.15), 2)  # Min £3.50 shipping
        handling_days = 2  # Zendrop typically faster than AliExpress

        # Reliability score estimation
        reliability = 88.0  # Zendrop generally reliable
        category = product.get("category", "").lower()
        if any(k in category for k in ["electronics", "beauty", "health"]):
            reliability = 85.0
        elif any(k in category for k in ["home", "garden", "kitchen"]):
            reliability = 92.0

        return {
            "source": "zendrop",
            "source_mode": "estimation",
            "supplier_cost": zendrop_cost,
            "shipping_cost": shipping_cost,
            "total_cost": round(zendrop_cost + shipping_cost, 2),
            "handling_time_days": handling_days,
            "estimated_delivery_days": handling_days + 5,  # US ~5 days, UK ~7
            "available": True,  # Assume available in estimation mode
            "reliability_score": reliability,
            "currency": "GBP",
            "notes": "Estimated — add ZENDROP_API_KEY to .env for live data",
        }

    # ── For the supplier matching system ──
    async def get_supplier_intelligence(self, product: Dict) -> Dict[str, Any]:
        """
        Main entry point for the supplier matching system.
        Returns Zendrop supplier data — live if configured, estimated if not.
        """
        if self.is_configured:
            # Try live API
            product_name = product.get("product_name", "")
            results = await self.search_products(product_name, limit=3)
            if results and len(results) > 0:
                best = results[0]
                shipping = await self.get_shipping_estimate(best.get("sku", ""), "GB")
                shipping_cost = shipping["shipping_cost"] if shipping else 3.50
                shipping_days = shipping["estimated_days"] if shipping else 7

                return {
                    "source": "zendrop",
                    "source_mode": "live",
                    "sku": best.get("sku"),
                    "supplier_cost": float(best.get("price", 0)),
                    "shipping_cost": shipping_cost,
                    "total_cost": round(float(best.get("price", 0)) + shipping_cost, 2),
                    "handling_time_days": best.get("handling_time", 2),
                    "estimated_delivery_days": shipping_days,
                    "available": best.get("in_stock", True),
                    "reliability_score": best.get("reliability_score", 90.0),
                    "currency": "GBP",
                    "title": best.get("title", product_name),
                }

        # Fallback to estimation
        return self.estimate_supplier_data(product)

    # ── Cache helpers ──
    def _get_cached(self, key: str) -> Optional[Any]:
        import time
        entry = self._cache.get(key)
        if entry and (time.time() - entry["ts"]) < self._cache_ttl:
            return entry["data"]
        return None

    def _set_cached(self, key: str, data: Any):
        import time
        self._cache[key] = {"data": data, "ts": time.time()}


# Singleton instance
zendrop_client = ZendropClient()
