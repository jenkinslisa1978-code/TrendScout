"""
AliExpress Open Platform API Client

Uses AliExpress Affiliate/Dropshipping API.
Config: ALIEXPRESS_API_KEY + ALIEXPRESS_API_SECRET in .env

Fallback chain: Official API → Scraper → Estimation → Hardcoded
"""

import os
import logging
import hashlib
import hmac
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

import aiohttp

logger = logging.getLogger("api.aliexpress")

_last_call_ts: float = 0
_MIN_INTERVAL = 1.0  # ~5000 calls/day ≈ 3.5/min


class AliExpressClient:
    # New international gateway
    BASE_URL = "https://api-sg.aliexpress.com/sync"
    LEGACY_URL = "https://gw.api.taobao.com/router/rest"

    def __init__(self):
        self.app_key = os.environ.get("ALIEXPRESS_API_KEY", "")
        self.app_secret = os.environ.get("ALIEXPRESS_API_SECRET", "")
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 1800

    @property
    def is_configured(self) -> bool:
        return bool(self.app_key and self.app_secret)

    def _sign(self, params: Dict[str, str]) -> str:
        """Generate MD5 signature per AliExpress API spec."""
        sorted_params = sorted(params.items())
        sign_str = self.app_secret
        for k, v in sorted_params:
            sign_str += f"{k}{v}"
        sign_str += self.app_secret
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

    async def health_check(self) -> Dict[str, Any]:
        """Test API connectivity."""
        if not self.is_configured:
            return {
                "status": "not_configured",
                "credential_detected": False,
                "mode": "estimation",
                "message": "ALIEXPRESS_API_KEY / ALIEXPRESS_API_SECRET not set in .env",
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
                "message": "API returned empty or auth failed",
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

    async def search_products(
        self,
        keywords: str,
        limit: int = 20,
        target_currency: str = "GBP",
        target_language: str = "EN",
        sort: str = "SALE_PRICE_ASC",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search AliExpress products via affiliate API.
        Returns normalized product list or None on failure.
        """
        if not self.is_configured:
            return None

        global _last_call_ts
        elapsed = time.time() - _last_call_ts
        if elapsed < _MIN_INTERVAL:
            await _async_sleep(_MIN_INTERVAL - elapsed)
        _last_call_ts = time.time()

        cache_key = hashlib.md5(f"search:{keywords}:{limit}".encode()).hexdigest()
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < self._cache_ttl:
            return cached["data"]

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        params = {
            "method": "aliexpress.affiliate.product.query",
            "app_key": self.app_key,
            "sign_method": "md5",
            "timestamp": timestamp,
            "format": "json",
            "v": "2.0",
            "keywords": keywords[:100],
            "target_currency": target_currency,
            "target_language": target_language,
            "sort": sort,
            "page_size": str(min(limit, 50)),
            "page_no": "1",
        }
        params["sign"] = self._sign(params)

        try:
            async with aiohttp.ClientSession() as session:
                # Try new gateway first, fall back to legacy
                for url in [self.BASE_URL, self.LEGACY_URL]:
                    try:
                        async with session.post(
                            url,
                            data=params,
                            timeout=aiohttp.ClientTimeout(total=20),
                        ) as resp:
                            if resp.status == 200:
                                body = await resp.json()
                                products = self._extract_products(body)
                                if products is not None:
                                    normalized = [self._normalize(p) for p in products]
                                    normalized = [n for n in normalized if n]
                                    self._cache[cache_key] = {"data": normalized, "ts": time.time()}
                                    logger.info(f"AliExpress API: {len(normalized)} products for '{keywords}'")
                                    return normalized
                            elif resp.status == 429:
                                logger.warning("AliExpress API rate limited")
                                return None
                    except aiohttp.ClientError:
                        continue

                logger.warning("AliExpress API: all endpoints failed")
                return None

        except Exception as e:
            logger.error(f"AliExpress API error: {e}")
            return None

    async def get_product_detail(
        self,
        product_ids: str,
        target_currency: str = "GBP",
    ) -> Optional[List[Dict[str, Any]]]:
        """Get product details by ID(s)."""
        if not self.is_configured:
            return None

        cache_key = f"detail:{product_ids}"
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < self._cache_ttl:
            return cached["data"]

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        params = {
            "method": "aliexpress.affiliate.productdetail.get",
            "app_key": self.app_key,
            "sign_method": "md5",
            "timestamp": timestamp,
            "format": "json",
            "v": "2.0",
            "product_ids": product_ids,
            "target_currency": target_currency,
            "target_language": "EN",
        }
        params["sign"] = self._sign(params)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.BASE_URL,
                    data=params,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 200:
                        body = await resp.json()
                        products = self._extract_products(body)
                        if products:
                            normalized = [self._normalize(p) for p in products]
                            normalized = [n for n in normalized if n]
                            self._cache[cache_key] = {"data": normalized, "ts": time.time()}
                            return normalized
            return None
        except Exception as e:
            logger.error(f"AliExpress detail API error: {e}")
            return None

    def _extract_products(self, body: Dict) -> Optional[List]:
        """Extract product list from AliExpress API response."""
        # Response structure varies by method
        for key in [
            "aliexpress_affiliate_product_query_response",
            "aliexpress_affiliate_productdetail_get_response",
        ]:
            if key in body:
                resp_data = body[key].get("resp_result", body[key])
                result = resp_data.get("result", resp_data)
                products = result.get("products", result.get("product", []))
                if isinstance(products, dict):
                    products = products.get("product", [])
                if products:
                    return products if isinstance(products, list) else [products]
        # Check for error
        error = body.get("error_response", {})
        if error:
            logger.warning(f"AliExpress API error: {error.get('msg', error)}")
        return None

    def _normalize(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Normalize AliExpress API product into standard format."""
        try:
            product_id = str(item.get("product_id", item.get("productId", "")))
            title = item.get("product_title", item.get("productTitle", ""))
            if not title:
                return None

            # Prices
            original_price = 0
            sale_price = 0
            for k in ["original_price", "originalPrice", "target_original_price"]:
                val = item.get(k)
                if val:
                    try:
                        original_price = float(str(val).replace(",", ""))
                        break
                    except (ValueError, TypeError):
                        pass

            for k in ["sale_price", "salePrice", "target_sale_price", "app_sale_price"]:
                val = item.get(k)
                if val:
                    try:
                        sale_price = float(str(val).replace(",", ""))
                        break
                    except (ValueError, TypeError):
                        pass

            cost = sale_price if sale_price > 0 else original_price

            # Rating
            rating = 0
            for k in ["evaluate_rate", "evaluateRate", "avg_evaluation_rating"]:
                val = item.get(k)
                if val:
                    try:
                        r = float(str(val).replace("%", ""))
                        rating = r / 20 if r > 5 else r  # Convert % to 5-star if needed
                        break
                    except (ValueError, TypeError):
                        pass

            # Orders
            orders = 0
            for k in ["lastest_volume", "orders", "latest_volume", "sale_count"]:
                val = item.get(k)
                if val:
                    try:
                        orders = int(val)
                        break
                    except (ValueError, TypeError):
                        pass

            # Shipping
            shipping_info = item.get("shipping_info", {})
            if isinstance(shipping_info, dict):
                shipping_days = int(shipping_info.get("delivery_days", 14) or 14)
            else:
                shipping_days = 14

            return {
                "aliexpress_id": product_id,
                "product_name": title[:200],
                "supplier_cost": round(cost, 2),
                "original_price": round(original_price, 2),
                "orders_30d": orders,
                "rating": round(rating, 1),
                "reviews": int(item.get("evaluate_count", item.get("evaluateCount", 0)) or 0),
                "shipping_days": shipping_days,
                "processing_days": 3,
                "moq": 1,
                "availability": "in_stock" if orders > 0 or cost > 0 else "unknown",
                "variants_count": 1,
                "product_url": item.get("product_detail_url", item.get("productUrl", "")),
                "image_url": item.get("product_main_image_url", item.get("imageUrl", "")),
                "commission_rate": item.get("commission_rate", ""),
                "shop_url": item.get("shop_url", ""),
            }
        except Exception as e:
            logger.debug(f"AliExpress normalize error: {e}")
            return None


async def _async_sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)
