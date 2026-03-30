"""
Avasam UK Supplier API integration service.
Handles authentication, product search, and supplier data enrichment.
Mirrors the CJ Dropshipping service structure.
"""
import os
import json
import logging
import aiohttp
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

AVASAM_BASE = "https://app.avasam.com/api"
_TOKEN_FILE = "/tmp/avasam_api_token.json"

# Module-level token cache
_token_cache = {"access_token": None, "expires_at": None}


def _load_token_cache():
    """Load persisted Avasam token from file (survives server restarts)."""
    global _token_cache
    try:
        with open(_TOKEN_FILE, "r") as f:
            data = json.load(f)
        exp = data.get("expires_at", "")
        if exp and datetime.fromisoformat(exp) > datetime.now(timezone.utc):
            _token_cache = data
            logger.info("Avasam: Loaded cached token from file")
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
    """Get or refresh Avasam API access token using consumer key/secret."""
    now = datetime.now(timezone.utc)

    # Return cached token if still valid
    if _token_cache["access_token"] and _token_cache["expires_at"]:
        expires = _token_cache["expires_at"]
        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires)
        if now < expires:
            return _token_cache["access_token"]

    consumer_key = os.environ.get("AVASAM_CONSUMER_KEY", "")
    consumer_secret = os.environ.get("AVASAM_CONSUMER_SECRET", "")
    if not consumer_key or not consumer_secret:
        raise ValueError("AVASAM_CONSUMER_KEY / AVASAM_CONSUMER_SECRET not configured")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AVASAM_BASE}/auth/request-token",
            json={"consumer_key": consumer_key, "secret_key": consumer_secret},
            headers={"Content-Type": "application/json"},
        ) as resp:
            data = await resp.json()
            token = data.get("access_token") or data.get("token")
            if token:
                expires_at = data.get("expires_at")
                if expires_at:
                    _token_cache["expires_at"] = expires_at
                else:
                    _token_cache["expires_at"] = (now + timedelta(hours=12)).isoformat()
                _token_cache["access_token"] = token
                _save_token_cache()
                logger.info("Avasam: obtained new access token")
                return token
            else:
                msg = data.get("message") or data.get("error") or "Unknown error"
                logger.error(f"Avasam auth failed: {msg}")
                raise ValueError(f"Avasam auth failed: {msg}")


async def search_products(query: str, page: int = 1, page_size: int = 20, category_id: str = "") -> dict:
    """Search Avasam products by keyword."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e), "products": []}

    params = {
        "keyword": query,
        "page": page,
        "per_page": min(page_size, 50),
    }
    if category_id:
        params["category_id"] = category_id

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{AVASAM_BASE}/products/search",
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json()

                # Avasam may return different response shapes
                items = []
                total = 0
                if isinstance(data, dict):
                    items = data.get("data", data.get("products", data.get("results", [])))
                    total = data.get("total", data.get("meta", {}).get("total", len(items)))
                elif isinstance(data, list):
                    items = data
                    total = len(data)

                products = [_map_avasam_product(p) for p in items if isinstance(p, dict)]
                return {
                    "success": True,
                    "products": products,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "source": "avasam",
                }
    except aiohttp.ClientError as e:
        logger.error(f"Avasam product search error: {e}")
        return {"success": False, "error": str(e), "products": []}


async def get_product_detail(product_id: str) -> dict:
    """Get detailed product info from Avasam by product ID."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e)}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{AVASAM_BASE}/products/{product_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json()
                product = data.get("data", data) if isinstance(data, dict) else None
                if product and isinstance(product, dict):
                    return {"success": True, "product": _map_avasam_product_detail(product)}
                return {"success": False, "error": data.get("message", "Product not found")}
    except aiohttp.ClientError as e:
        logger.error(f"Avasam product detail error: {e}")
        return {"success": False, "error": str(e)}


async def get_categories() -> dict:
    """Get Avasam product categories."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e), "categories": []}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{AVASAM_BASE}/categories",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json()
                raw = data.get("data", data.get("categories", []))
                if not isinstance(raw, list):
                    raw = []
                return {
                    "success": True,
                    "categories": [
                        {
                            "id": str(c.get("id", c.get("category_id", ""))),
                            "name": c.get("name", c.get("category_name", "")),
                        }
                        for c in raw
                    ],
                }
    except aiohttp.ClientError as e:
        logger.error(f"Avasam categories error: {e}")
        return {"success": False, "error": str(e), "categories": []}


async def get_stock(product_id: str) -> dict:
    """Get live stock / inventory for an Avasam product."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e)}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{AVASAM_BASE}/stock/{product_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json()
                return {"success": True, "stock": data}
    except aiohttp.ClientError as e:
        logger.error(f"Avasam stock error: {e}")
        return {"success": False, "error": str(e)}


# ── Data mapping helpers ──────────────────────────────────────

def _parse_price(val) -> float:
    """Parse Avasam price which can be a number, string, or range."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.strip().lstrip("\u00a3$")  # strip currency symbols
        if " - " in val:
            try:
                return float(val.split(" - ")[0].strip())
            except ValueError:
                return 0.0
        try:
            return float(val)
        except ValueError:
            return 0.0
    return 0.0


def _map_avasam_product(p: dict) -> dict:
    """Map Avasam product to our internal format."""
    cost = _parse_price(p.get("cost_price", p.get("price", p.get("wholesale_price", 0))))
    rrp = _parse_price(p.get("rrp", p.get("retail_price", p.get("recommended_retail_price", 0))))
    if rrp <= 0 and cost > 0:
        rrp = round(cost * 2.5, 2)

    image = p.get("image_url", p.get("image", p.get("main_image", "")))
    images = p.get("images", p.get("image_urls", []))
    if isinstance(images, str):
        try:
            images = json.loads(images)
        except (json.JSONDecodeError, TypeError):
            images = [images] if images else []
    if not isinstance(images, list):
        images = []

    pid = str(p.get("id", p.get("product_id", p.get("avasam_id", ""))))

    return {
        "avasam_pid": pid,
        "product_name": p.get("name", p.get("title", p.get("product_name", ""))),
        "category": p.get("category", p.get("category_name", "")),
        "category_id": str(p.get("category_id", "")),
        "image_url": image,
        "images": images,
        "supplier_cost": round(cost, 2),
        "sell_price": round(rrp, 2),
        "currency": "GBP",
        "stock_status": "in_stock" if p.get("in_stock", p.get("stock_status")) in (True, "in_stock", "available") else "limited",
        "source": "avasam",
        "source_url": f"https://app.avasam.com/products/{pid}",
        "shipping_weight": p.get("weight", p.get("shipping_weight", 0)),
        "description": (p.get("description", "") or "")[:500],
        "variants_count": len(p.get("variants", [])),
        "sku": p.get("sku", ""),
        "brand": p.get("brand", p.get("supplier_name", "")),
        "ean": p.get("ean", p.get("barcode", "")),
    }


def _map_avasam_product_detail(p: dict) -> dict:
    """Map Avasam product detail to our internal format with variants."""
    base = _map_avasam_product(p)
    variants = p.get("variants", [])
    base["variants"] = [
        {
            "vid": str(v.get("id", v.get("variant_id", ""))),
            "name": v.get("name", v.get("title", "")),
            "sku": v.get("sku", ""),
            "price": round(_parse_price(v.get("price", v.get("cost_price", 0))), 2),
            "stock": v.get("stock", v.get("quantity", 0)),
            "image": v.get("image_url", v.get("image", "")),
            "ean": v.get("ean", v.get("barcode", "")),
        }
        for v in variants
    ]
    base["properties"] = [
        {"name": prop.get("name", ""), "value": prop.get("value", "")}
        for prop in p.get("attributes", p.get("properties", []))
        if isinstance(prop, dict)
    ]
    return base
