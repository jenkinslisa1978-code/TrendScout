"""
CJ Dropshipping Official API Client

Uses CJ API v2.0 at developers.cjdropshipping.com
Config: CJ_API_KEY in .env (CJ-Access-Token)

Fallback chain: Official API → Scraper → Estimation → Hardcoded
"""

import os
import logging
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

import aiohttp

logger = logging.getLogger("api.cj_dropshipping")

_last_call_ts: float = 0
_MIN_INTERVAL = 1.0  # CJ allows ~600 calls/min


class CJDropshippingClient:
    BASE_URL = "https://developers.cjdropshipping.com/api2.0/v1"

    def __init__(self):
        self.api_key = os.environ.get("CJ_API_KEY", "")
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
                "message": "CJ_API_KEY not set in .env",
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

    async def search_products(
        self,
        keyword: str,
        limit: int = 20,
        page: int = 1,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search CJ products by keyword.
        Returns list of normalized product dicts or None on failure.
        """
        if not self.is_configured:
            return None

        # Rate limiting
        global _last_call_ts
        elapsed = time.time() - _last_call_ts
        if elapsed < _MIN_INTERVAL:
            await _async_sleep(_MIN_INTERVAL - elapsed)
        _last_call_ts = time.time()

        # Cache
        cache_key = hashlib.md5(f"search:{keyword}:{page}:{limit}".encode()).hexdigest()
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < self._cache_ttl:
            return cached["data"]

        url = f"{self.BASE_URL}/product/list"
        params = {
            "keyWord": keyword[:200],
            "page": page,
            "size": min(limit, 100),
            "orderBy": 1,  # sort by listing count
            "sort": "desc",
        }
        headers = {
            "CJ-Access-Token": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=20),
                ) as resp:
                    if resp.status == 200:
                        body = await resp.json()
                        if body.get("result") is True or body.get("code") == 200:
                            products = body.get("data", {}).get("productList", [])
                            if not products and isinstance(body.get("data"), list):
                                products = body["data"]

                            normalized = [self._normalize(p) for p in products if p]
                            normalized = [n for n in normalized if n]

                            self._cache[cache_key] = {"data": normalized, "ts": time.time()}
                            logger.info(f"CJ API: {len(normalized)} products for '{keyword}'")
                            return normalized
                        else:
                            msg = body.get("message", body.get("msg", "Unknown error"))
                            logger.warning(f"CJ API error: {msg}")
                            return None

                    elif resp.status == 429:
                        logger.warning("CJ API rate limited")
                        return None
                    elif resp.status == 401:
                        logger.error("CJ API: Invalid or expired token")
                        return None
                    else:
                        text = await resp.text()
                        logger.warning(f"CJ API error {resp.status}: {text[:200]}")
                        return None

        except aiohttp.ClientError as e:
            logger.error(f"CJ API connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"CJ API unexpected error: {e}")
            return None

    async def get_product_detail(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed product info by CJ product ID."""
        if not self.is_configured:
            return None

        cache_key = f"detail:{product_id}"
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < self._cache_ttl:
            return cached["data"]

        url = f"{self.BASE_URL}/product/query"
        headers = {
            "CJ-Access-Token": self.api_key,
            "Content-Type": "application/json",
        }
        params = {"pid": product_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 200:
                        body = await resp.json()
                        if body.get("result") is True or body.get("code") == 200:
                            data = body.get("data", {})
                            result = self._normalize(data) if data else None
                            if result:
                                self._cache[cache_key] = {"data": result, "ts": time.time()}
                            return result
                    return None
        except Exception as e:
            logger.error(f"CJ detail API error: {e}")
            return None

    def _normalize(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Normalize CJ API response into standard supplier intelligence format."""
        try:
            pid = str(item.get("pid", item.get("productId", item.get("id", ""))))
            name = item.get("productName", item.get("productNameEn", ""))
            if not name:
                return None

            # Price
            price = 0
            for key in ["sellPrice", "salePrice", "price", "cost"]:
                if key in item:
                    try:
                        price = float(item[key])
                        if price > 0:
                            break
                    except (ValueError, TypeError):
                        continue

            # Variants
            variants = []
            for key in ["variants", "skuList", "skus"]:
                raw = item.get(key, [])
                if isinstance(raw, list):
                    for v in raw:
                        variants.append({
                            "name": v.get("propName", v.get("name", "")),
                            "price": float(v.get("sellPrice", v.get("price", price)) or price),
                            "stock": int(v.get("stock", v.get("inventory", 0)) or 0),
                            "sku_id": v.get("skuId", v.get("vid", "")),
                        })
                    break

            # Shipping
            shipping_days = 10
            for key in ["logisticDay", "deliveryDays", "shippingDays"]:
                val = item.get(key)
                if val:
                    try:
                        shipping_days = int(val)
                        break
                    except (ValueError, TypeError):
                        pass

            processing_days = 2
            for key in ["packingDay", "handleDay", "processingDays"]:
                val = item.get(key)
                if val:
                    try:
                        processing_days = int(val)
                        break
                    except (ValueError, TypeError):
                        pass

            # Stock
            stock = 0
            for key in ["stock", "inventory", "availableStock"]:
                val = item.get(key)
                if val:
                    try:
                        stock = int(val)
                        break
                    except (ValueError, TypeError):
                        pass

            availability = "in_stock" if stock > 0 else ("check_supplier" if price > 0 else "out_of_stock")

            # Warehouse
            warehouse = item.get("warehouseCode", item.get("warehouse", item.get("originCode", "CN")))
            if isinstance(warehouse, list) and warehouse:
                warehouse = warehouse[0]

            # Image
            image = item.get("productImage", item.get("bigImage", item.get("image", "")))
            if isinstance(image, list) and image:
                image = image[0]

            return {
                "cj_product_id": pid,
                "product_name": name[:200],
                "cj_price": price,
                "cj_shipping_days": shipping_days,
                "cj_processing_days": processing_days,
                "cj_availability": availability,
                "cj_stock": stock,
                "cj_variants": variants[:20],
                "cj_variants_count": len(variants) if variants else (int(item.get("variantCount", 1)) or 1),
                "cj_warehouse": warehouse,
                "cj_fulfillment_type": item.get("fulfillmentType", "dropshipping"),
                "cj_product_url": item.get("productUrl", f"https://cjdropshipping.com/product/{pid}"),
                "cj_image_url": image,
                "cj_category": item.get("categoryName", item.get("category", "")),
                "cj_last_sync": datetime.now(timezone.utc).isoformat(),
                "estimated_retail_price": round(price * 2.5, 2) if price > 0 else 0,
            }
        except Exception as e:
            logger.debug(f"CJ normalize error: {e}")
            return None


async def _async_sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)
