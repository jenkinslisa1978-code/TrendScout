"""
CJ Dropshipping API v2 integration service.
Handles authentication, product search, and supplier data enrichment.
"""
import os
import json
import logging
import aiohttp
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

CJ_BASE = "https://developers.cjdropshipping.com/api2.0/v1"
_TOKEN_FILE = "/tmp/cj_api_token.json"

# Module-level token cache
_token_cache = {"access_token": None, "expires_at": None, "refresh_token": None}


def _load_token_cache():
    """Load persisted CJ token from file (survives server restarts)."""
    global _token_cache
    try:
        with open(_TOKEN_FILE, "r") as f:
            data = json.load(f)
        exp = data.get("expires_at", "")
        if exp and datetime.fromisoformat(exp) > datetime.now(timezone.utc):
            _token_cache = data
            logger.info("CJ Dropshipping: Loaded cached token from file")
    except Exception:
        pass


def _save_token_cache():
    """Persist token cache to file."""
    try:
        with open(_TOKEN_FILE, "w") as f:
            json.dump(_token_cache, f)
    except Exception:
        pass


# Load on module init
_load_token_cache()


async def _get_access_token() -> str:
    """Get or refresh CJ API access token."""
    now = datetime.now(timezone.utc)

    # Return cached token if still valid
    if _token_cache["access_token"] and _token_cache["expires_at"]:
        expires = _token_cache["expires_at"]
        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires)
        if now < expires:
            return _token_cache["access_token"]

    api_key = os.environ.get("CJ_DROPSHIPPING_API_KEY", "")
    if not api_key:
        raise ValueError("CJ_DROPSHIPPING_API_KEY not configured")

    # Try refresh first if we have a refresh token
    if _token_cache["refresh_token"]:
        token = await _refresh_token(_token_cache["refresh_token"])
        if token:
            return token

    # Get new token
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{CJ_BASE}/authentication/getAccessToken",
            json={"apiKey": api_key},
            headers={"Content-Type": "application/json"},
        ) as resp:
            data = await resp.json()
            if data.get("result") and data.get("code") == 200:
                result = data["data"]
                _token_cache["access_token"] = result["accessToken"]
                _token_cache["refresh_token"] = result.get("refreshToken")
                _token_cache["expires_at"] = (now + timedelta(days=14)).isoformat()
                _save_token_cache()
                logger.info("CJ Dropshipping: obtained new access token")
                return result["accessToken"]
            else:
                msg = data.get("message", "Unknown error")
                logger.error(f"CJ auth failed: {msg}")
                raise ValueError(f"CJ auth failed: {msg}")


async def _refresh_token(refresh_token: str) -> str:
    """Refresh an expired access token."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CJ_BASE}/authentication/refreshAccessToken",
                json={"refreshToken": refresh_token},
                headers={"Content-Type": "application/json"},
            ) as resp:
                data = await resp.json()
                if data.get("result") and data.get("code") == 200:
                    result = data["data"]
                    _token_cache["access_token"] = result["accessToken"]
                    _token_cache["refresh_token"] = result.get("refreshToken", refresh_token)
                    _token_cache["expires_at"] = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
                    _save_token_cache()
                    logger.info("CJ Dropshipping: refreshed access token")
                    return result["accessToken"]
    except Exception as e:
        logger.warning(f"CJ token refresh failed: {e}")
    return ""


async def search_products(query: str, page: int = 1, page_size: int = 20, category_id: str = "") -> dict:
    """Search CJ Dropshipping products by name."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e), "products": []}

    params = {
        "productNameEn": query,
        "pageNum": page,
        "pageSize": min(page_size, 50),
    }
    if category_id:
        params["categoryId"] = category_id

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CJ_BASE}/product/list",
                params=params,
                headers={
                    "CJ-Access-Token": token,
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json()
                if data.get("result") and data.get("code") == 200:
                    items = data.get("data", {}).get("list", [])
                    total = data.get("data", {}).get("total", 0)
                    products = [_map_cj_product(p) for p in items]
                    return {
                        "success": True,
                        "products": products,
                        "total": total,
                        "page": page,
                        "page_size": page_size,
                        "source": "cj_dropshipping",
                    }
                else:
                    msg = data.get("message", "Unknown error")
                    logger.warning(f"CJ product search failed: {msg}")
                    return {"success": False, "error": msg, "products": []}
    except Exception as e:
        logger.error(f"CJ product search error: {e}")
        return {"success": False, "error": str(e), "products": []}


async def get_product_detail(pid: str) -> dict:
    """Get detailed product info from CJ by product ID."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e)}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CJ_BASE}/product/query",
                params={"pid": pid},
                headers={
                    "CJ-Access-Token": token,
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json()
                if data.get("result") and data.get("code") == 200:
                    product = data.get("data")
                    if product:
                        return {"success": True, "product": _map_cj_product_detail(product)}
                return {"success": False, "error": data.get("message", "Product not found")}
    except Exception as e:
        logger.error(f"CJ product detail error: {e}")
        return {"success": False, "error": str(e)}


async def get_categories() -> dict:
    """Get CJ product categories."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e), "categories": []}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CJ_BASE}/product/getCategory",
                headers={
                    "CJ-Access-Token": token,
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json()
                if data.get("result") and data.get("code") == 200:
                    categories = data.get("data", [])
                    return {
                        "success": True,
                        "categories": [
                            {"id": c.get("categoryId", ""), "name": c.get("categoryName", "")}
                            for c in categories
                        ],
                    }
                return {"success": False, "error": data.get("message", ""), "categories": []}
    except Exception as e:
        logger.error(f"CJ categories error: {e}")
        return {"success": False, "error": str(e), "categories": []}


def _parse_price(val) -> float:
    """Parse CJ price which can be a number, string, or range like '0.17 -- 1.70'."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.strip()
        if " -- " in val:
            parts = val.split(" -- ")
            try:
                return float(parts[0].strip())
            except ValueError:
                return 0.0
        if " - " in val:
            parts = val.split(" - ")
            try:
                return float(parts[0].strip())
            except ValueError:
                return 0.0
        try:
            return float(val)
        except ValueError:
            return 0.0
    return 0.0


def _parse_image_url(val) -> str:
    """Parse image_url which may be a JSON array string or plain URL."""
    if not val:
        return ""
    if isinstance(val, str) and val.startswith("["):
        import json
        try:
            urls = json.loads(val)
            if isinstance(urls, list) and urls:
                return urls[0]
        except (json.JSONDecodeError, TypeError):
            pass
    return str(val)


def _map_cj_product(p: dict) -> dict:
    """Map CJ product to our internal format."""
    sell_price = _parse_price(p.get("sellPrice", 0))
    variants = p.get("variants", [])
    min_price = sell_price
    if variants:
        prices = [_parse_price(v.get("variantSellPrice", sell_price)) for v in variants if v.get("variantSellPrice")]
        if prices:
            min_price = min(prices)

    # Use supplier_cost as fallback when sell_price is 0
    effective_price = sell_price if sell_price > 0 else min_price

    # Parse image — CJ sometimes returns a JSON array string
    raw_image = p.get("productImage", "")
    image_url = _parse_image_url(raw_image)

    # Parse images list — may also be a JSON string
    raw_images = p.get("productImageSet", [])
    if isinstance(raw_images, str) and raw_images.startswith("["):
        import json
        try:
            raw_images = json.loads(raw_images)
        except (json.JSONDecodeError, TypeError):
            raw_images = []
    if not isinstance(raw_images, list):
        raw_images = []

    return {
        "cj_pid": p.get("pid", ""),
        "product_name": p.get("productNameEn", ""),
        "category": p.get("categoryName", ""),
        "category_id": p.get("categoryId", ""),
        "image_url": image_url,
        "images": raw_images,
        "supplier_cost": round(float(min_price), 2),
        "sell_price": round(float(effective_price), 2),
        "currency": "USD",
        "stock_status": "in_stock" if p.get("productStatus") == "SELLING" else "limited",
        "source": "cj_dropshipping",
        "source_url": f"https://cjdropshipping.com/product/{p.get('pid', '')}",
        "shipping_weight": p.get("productWeight", 0),
        "description": (p.get("description", "") or "")[:500],
        "variants_count": len(variants),
    }


def _map_cj_product_detail(p: dict) -> dict:
    """Map CJ product detail to our internal format with variants."""
    base = _map_cj_product(p)
    variants = p.get("variants", [])
    base["variants"] = [
        {
            "vid": v.get("vid", ""),
            "name": v.get("variantNameEn", ""),
            "sku": v.get("variantSku", ""),
            "price": round(_parse_price(v.get("variantSellPrice", 0)), 2),
            "stock": v.get("variantVolume", 0),
            "image": v.get("variantImage", ""),
        }
        for v in variants
    ]
    base["properties"] = [
        {"name": prop.get("propName", ""), "value": prop.get("propOriginalName", "")}
        for prop in p.get("productPropertyList", [])
    ]
    return base
