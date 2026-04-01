"""
Avasam UK Supplier API integration service.
Handles authentication, product search, and supplier data enrichment.

Actual API base: https://app.avasam.com
Auth:    POST https://app.avasam.com/api/auth/request-token
Search:  POST https://app.avasam.com/apiseeker/ProductModule/GetInventoryListWithFilter
List:    POST https://app.avasam.com/apiseeker/Products/GetSellerProductList
Stock:   POST https://app.avasam.com/apiseeker/Products/SellerStockList
"""
import os
import json
import logging
import aiohttp
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

AVASAM_BASE = "https://app.avasam.com"
_TOKEN_FILE = "/tmp/avasam_api_token.json"
_TIMEOUT = aiohttp.ClientTimeout(total=15, connect=8)

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

    try:
        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(
                f"{AVASAM_BASE}/api/auth/request-token",
                json={"consumer_key": consumer_key, "secret_key": consumer_secret},
                headers={"Content-Type": "application/json"},
            ) as resp:
                data = await resp.json(content_type=None)
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
    except aiohttp.ClientConnectorError as e:
        logger.error(f"Avasam: cannot reach {AVASAM_BASE} — DNS/connection error: {e}")
        raise ValueError(f"Avasam API unreachable: {e}")
    except aiohttp.ServerTimeoutError:
        logger.error("Avasam: auth request timed out")
        raise ValueError("Avasam API timed out")


async def search_products(query: str, page: int = 1, page_size: int = 20, category_id: str = "") -> dict:
    """Search Avasam products by keyword using GetInventoryListWithFilter."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e), "products": []}

    # Avasam uses page index starting at 0
    page_index = max(0, page - 1)

    body = {
        "Supplier": query,          # searches by SKU or product title
        "Sortby": "Title",
        "SortStatus": "up",
        "limit": str(min(page_size, 50)),
        "page": page_index,
        "Category": category_id or "",
        "CategoryName": "",
        "IsMapped": "",
        "Variation": "",
    }

    try:
        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(
                f"{AVASAM_BASE}/apiseeker/ProductModule/GetInventoryListWithFilter",
                json=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json(content_type=None)

                items = []
                total = 0
                if isinstance(data, dict):
                    items = data.get("data", data.get("products", data.get("results", [])))
                    total = data.get("total", data.get("meta", {}).get("total", len(items)))
                elif isinstance(data, list):
                    items = data
                    total = len(data)

                if not isinstance(items, list):
                    items = []

                products = [_map_avasam_product(p) for p in items if isinstance(p, dict)]
                logger.info(f"Avasam search '{query}': found {len(products)} products (total={total})")
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


async def get_all_products(page: int = 1, page_size: int = 50) -> dict:
    """Get full seller product list from Avasam (no keyword filter)."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e), "products": []}

    body = {
        "Page": page,
        "Limit": min(page_size, 50),
    }

    try:
        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(
                f"{AVASAM_BASE}/apiseeker/Products/GetSellerProductList",
                json=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json(content_type=None)

                items = []
                total = 0
                if isinstance(data, dict):
                    items = data.get("data", data.get("products", []))
                    total = data.get("total", len(items))
                elif isinstance(data, list):
                    items = data
                    total = len(data)

                if not isinstance(items, list):
                    items = []

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
        logger.error(f"Avasam get_all_products error: {e}")
        return {"success": False, "error": str(e), "products": []}


async def get_product_detail(product_id: str) -> dict:
    """Get detailed product info from Avasam by product ID."""
    # Avasam doesn't have a single-product endpoint in the public docs;
    # fall back to searching by SKU via GetInventoryListWithFilter
    result = await search_products(product_id, page=1, page_size=1)
    if result.get("success") and result.get("products"):
        return {"success": True, "product": result["products"][0]}
    return {"success": False, "error": "Product not found"}


async def get_categories() -> dict:
    """Get Avasam product categories (derived from inventory data)."""
    # Avasam doesn't expose a standalone categories endpoint in the seller API.
    # Return a static list of common UK dropshipping categories.
    categories = [
        {"id": "home-garden", "name": "Home & Garden"},
        {"id": "beauty-health", "name": "Beauty & Health"},
        {"id": "electronics", "name": "Electronics"},
        {"id": "sports-fitness", "name": "Sports & Fitness"},
        {"id": "pet-supplies", "name": "Pet Supplies"},
        {"id": "toys-games", "name": "Toys & Games"},
        {"id": "clothing-accessories", "name": "Clothing & Accessories"},
        {"id": "kitchen", "name": "Kitchen & Dining"},
        {"id": "automotive", "name": "Automotive"},
        {"id": "office-stationery", "name": "Office & Stationery"},
    ]
    return {"success": True, "categories": categories}


async def get_stock(product_id: str) -> dict:
    """Get live stock levels for an Avasam product via SellerStockList."""
    try:
        token = await _get_access_token()
    except ValueError as e:
        return {"success": False, "error": str(e)}

    try:
        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(
                f"{AVASAM_BASE}/apiseeker/Products/SellerStockList",
                json={},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            ) as resp:
                data = await resp.json(content_type=None)
                # Filter for the specific product_id / SKU
                items = data if isinstance(data, list) else data.get("data", [])
                match = next((i for i in items if str(i.get("SKU", "")) == product_id), None)
                return {"success": True, "stock": match or data}
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
    """Map Avasam product to our internal format.

    Avasam API returns capitalised keys: SKU, Price, RetailPrice, Title,
    image, Stock, Category, IsActive, isMapped.
    """
    # Support both capitalised (real API) and lowercase (legacy/mock) keys
    cost = _parse_price(
        p.get("Price", p.get("cost_price", p.get("price", p.get("wholesale_price", 0))))
    )
    rrp = _parse_price(
        p.get("RetailPrice", p.get("rrp", p.get("retail_price", p.get("recommended_retail_price", 0))))
    )
    if rrp <= 0 and cost > 0:
        rrp = round(cost * 2.5, 2)

    image = p.get("image", p.get("image_url", p.get("main_image", "")))
    images = p.get("images", p.get("image_urls", []))
    if isinstance(images, str):
        try:
            images = json.loads(images)
        except (json.JSONDecodeError, TypeError):
            images = [images] if images else []
    if not isinstance(images, list):
        images = []
    # Ensure the main image is included
    if image and image not in images:
        images = [image] + images

    sku = p.get("SKU", p.get("sku", ""))
    pid = str(p.get("id", p.get("product_id", p.get("avasam_id", sku or ""))))

    stock_val = p.get("Stock", p.get("stock", p.get("quantity", 0)))
    try:
        in_stock = int(stock_val) > 0
    except (TypeError, ValueError):
        in_stock = p.get("IsActive", p.get("in_stock", False))

    return {
        "avasam_pid": pid,
        "product_name": p.get("Title", p.get("name", p.get("title", p.get("product_name", "")))),
        "category": p.get("Category", p.get("category", p.get("category_name", ""))),
        "category_id": str(p.get("category_id", "")),
        "image_url": image,
        "images": images,
        "supplier_cost": round(cost, 2),
        "sell_price": round(rrp, 2),
        "currency": "GBP",
        "stock_status": "in_stock" if in_stock else "limited",
        "stock_qty": int(stock_val) if isinstance(stock_val, (int, float)) else 0,
        "source": "avasam",
        "source_url": f"https://app.avasam.com/products/{pid}",
        "shipping_weight": p.get("weight", p.get("shipping_weight", 0)),
        "description": (p.get("description", p.get("Description", "")) or "")[:500],
        "variants_count": len(p.get("variants", [])),
        "sku": sku,
        "brand": p.get("brand", p.get("supplier_name", p.get("Supplier", ""))),
        "ean": p.get("ean", p.get("barcode", p.get("EAN", ""))),
    }


def _map_avasam_product_detail(p: dict) -> dict:
    """Map Avasam product detail to our internal format with variants."""
    base = _map_avasam_product(p)
    variants = p.get("variants", [])
    base["variants"] = [
        {
            "vid": str(v.get("id", v.get("variant_id", ""))),
            "name": v.get("name", v.get("title", "")),
            "sku": v.get("sku", v.get("SKU", "")),
            "price": round(_parse_price(v.get("price", v.get("Price", v.get("cost_price", 0)))), 2),
            "stock": v.get("stock", v.get("Stock", v.get("quantity", 0))),
            "image": v.get("image_url", v.get("image", "")),
            "ean": v.get("ean", v.get("barcode", v.get("EAN", ""))),
        }
        for v in variants
    ]
    base["properties"] = [
        {"name": prop.get("name", ""), "value": prop.get("value", "")}
        for prop in p.get("attributes", p.get("properties", []))
        if isinstance(prop, dict)
    ]
    return base
