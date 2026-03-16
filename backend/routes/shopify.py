from fastapi import APIRouter, HTTPException, Request, Depends, Header, BackgroundTasks
from fastapi.responses import StreamingResponse, Response, JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import uuid
import json
import logging
import re

from auth import get_current_user, get_optional_user, AuthenticatedUser
from common.database import db
from common.cache import get_cached, set_cached, slugify, get_margin_range
from common.helpers import (
    get_user_plan, require_plan, require_admin, build_winning_reasons,
    track_product_store_created, track_product_exported, run_automation_on_products,
)
from common.scoring import (
    calculate_trend_score, calculate_trend_stage, calculate_opportunity_rating,
    generate_ai_summary, calculate_early_trend_score, calculate_market_score,
    calculate_launch_score, generate_mock_competitor_data, calculate_success_probability,
    should_generate_alert, generate_alert, run_full_automation, generate_early_trend_alert,
    should_generate_early_trend_alert,
)
from common.models import *

from services.shopify_service import (
    is_shopify_configured,
    get_oauth_url,
    exchange_code_for_token,
    ShopifyPublisher,
    format_store_for_export,
    get_connection_status,
    test_connection
)
import secrets

shopify_integration_router = APIRouter(prefix="/api/shopify")

@shopify_integration_router.get("/status")
async def shopify_status():
    """Check if Shopify integration is configured"""
    return {
        "configured": is_shopify_configured(),
        "features": {
            "export": True,  # Always available
            "direct_publish": is_shopify_configured(),
            "oauth_connect": is_shopify_configured(),
        },
        "message": "Shopify API configured" if is_shopify_configured() else "Export-only mode (Shopify credentials not configured)"
    }

@shopify_integration_router.post("/connect/init")
async def init_shopify_connection(
    shop_domain: str,
    redirect_uri: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Initialize Shopify OAuth connection for authenticated user
    
    Returns URL to redirect user to for authorization
    """
    user_id = current_user.user_id
    if not is_shopify_configured():
        raise HTTPException(
            status_code=503, 
            detail="Shopify integration not configured. Contact admin to set up SHOPIFY_API_KEY and SHOPIFY_API_SECRET."
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state temporarily (in production, use Redis or DB)
    # For now, we'll encode user_id in state
    state_data = f"{state}:{user_id}"
    
    oauth_url = get_oauth_url(shop_domain, redirect_uri, state_data)
    
    return {
        "oauth_url": oauth_url,
        "state": state,
        "message": "Redirect user to oauth_url to authorize Shopify access"
    }

@shopify_integration_router.post("/connect/callback")
async def shopify_oauth_callback(shop_domain: str, code: str, state: str):
    """
    Handle Shopify OAuth callback
    
    Exchange authorization code for access token
    """
    if not is_shopify_configured():
        raise HTTPException(status_code=503, detail="Shopify integration not configured")
    
    try:
        # Extract user_id from state
        state_parts = state.split(':')
        user_id = state_parts[1] if len(state_parts) > 1 else None
        
        # Exchange code for token
        token_data = await exchange_code_for_token(shop_domain, code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        # Store in user profile
        shopify_data = {
            "shop_domain": shop_domain,
            "access_token": access_token,
            "scope": token_data.get('scope'),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }
        
        if user_id:
            await db.profiles.update_one(
                {"id": user_id},
                {"$set": {"shopify": shopify_data}}
            )
        
        return {
            "success": True,
            "shop_domain": shop_domain,
            "message": "Shopify connected successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@shopify_integration_router.get("/connection")
async def get_user_shopify_status(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get Shopify connection status for authenticated user"""
    user_id = current_user.user_id
    profile = await db.profiles.find_one({"id": user_id}, {"_id": 0})
    
    if not profile:
        return get_connection_status({})
    
    return get_connection_status(profile)

@shopify_integration_router.post("/publish/{store_id}")
async def publish_to_shopify(
    store_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Publish store products directly to Shopify
    
    Requires Elite plan and connected Shopify account
    """
    await require_plan(current_user, "elite", "direct Shopify publishing")
    user_id = current_user.user_id
    # Get user's Shopify credentials
    profile = await db.profiles.find_one({"id": user_id}, {"_id": 0})
    shopify_data = profile.get('shopify', {}) if profile else {}
    
    if not shopify_data.get('access_token'):
        raise HTTPException(
            status_code=400, 
            detail="Shopify not connected. Please connect your Shopify store first."
        )
    
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Get store products
    products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    
    if not products:
        raise HTTPException(status_code=400, detail="No products to publish")
    
    # Initialize publisher and publish
    publisher = ShopifyPublisher(
        shopify_data['shop_domain'],
        shopify_data['access_token']
    )
    
    try:
        results = await publisher.publish_store_products(products)
        
        # Update store status
        await db.stores.update_one(
            {"id": store_id},
            {"$set": {
                "status": "published",
                "published_at": datetime.now(timezone.utc),
                "shopify_publish_results": results,
            }}
        )
        
        return {
            "success": True,
            "results": results,
            "message": f"Published {len(results['success'])} products to Shopify"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publish failed: {str(e)}")

@shopify_integration_router.delete("/disconnect")
async def disconnect_shopify(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Disconnect Shopify from authenticated user's account"""
    user_id = current_user.user_id
    await db.profiles.update_one(
        {"id": user_id},
        {"$unset": {"shopify": ""}}
    )
    
    return {"success": True, "message": "Shopify disconnected"}


# ===================== SUPPLIER ENDPOINTS =====================

class LaunchStoreRequest(BaseModel):
    product_id: str
    store_name: Optional[str] = None
    supplier_id: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# 1-Click Product Push to Shopify via Admin API
# ═══════════════════════════════════════════════════════════════════

@shopify_integration_router.post("/push-product")
async def push_product_to_shopify(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Push a product from TrendScout directly to the user's connected Shopify store.
    Creates a Shopify product with title, description, images, pricing, and tags.
    """
    import httpx

    body = await request.json()
    product_id = body.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")

    # 1. Get user's Shopify connection
    conn = await db.platform_connections.find_one(
        {"user_id": current_user.user_id, "platform": "shopify", "connection_type": "store", "status": "active"},
        {"_id": 0},
    )
    if not conn or not conn.get("access_token"):
        return JSONResponse(content={"success": False, "error": "No active Shopify connection. Go to Settings → Connections to connect your store."})

    # 2. Fetch the product from our DB
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 3. Build the Shopify product payload
    domain = conn["store_url"].replace("https://", "").replace("http://", "").rstrip("/")
    if not domain.endswith(".myshopify.com"):
        domain = f"{domain}.myshopify.com"

    # Build description
    desc = product.get("ai_summary") or product.get("short_description") or ""
    if product.get("estimated_retail_price"):
        desc += f"\n\nSuggested retail: ${product['estimated_retail_price']}"

    # Build tags
    tags = [
        product.get("category", ""),
        product.get("trend_stage", ""),
        f"launch-score-{product.get('launch_score', 0)}",
        "trendscout-import",
    ]
    tags = [t for t in tags if t]

    # Determine pricing
    retail_price = product.get("estimated_retail_price") or product.get("price_usd") or 29.99
    cost_price = product.get("estimated_cost") or product.get("supplier_price") or 0

    shopify_product = {
        "product": {
            "title": product.get("product_name", "Untitled Product"),
            "body_html": desc.replace("\n", "<br>"),
            "vendor": "TrendScout Import",
            "product_type": product.get("category", ""),
            "tags": ", ".join(tags),
            "status": "draft",
            "variants": [
                {
                    "price": str(round(float(retail_price), 2)),
                    "sku": f"TS-{product_id[:8]}",
                    "inventory_management": "shopify",
                    "inventory_quantity": 0,
                    "requires_shipping": True,
                }
            ],
        }
    }
    if cost_price:
        shopify_product["product"]["variants"][0]["cost"] = str(round(float(cost_price), 2))

    # Add images
    images = []
    if product.get("image_url"):
        images.append({"src": product["image_url"], "position": 1})
    for i, url in enumerate((product.get("image_urls") or [])[:4], start=2):
        images.append({"src": url, "position": i})
    if images:
        shopify_product["product"]["images"] = images

    # 4. Push to Shopify
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"https://{domain}/admin/api/2024-01/products.json",
                headers={
                    "X-Shopify-Access-Token": conn["access_token"],
                    "Content-Type": "application/json",
                },
                json=shopify_product,
            )
        if resp.status_code == 201:
            created = resp.json().get("product", {})
            # Track the export
            await db.shopify_exports.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": current_user.user_id,
                "product_id": product_id,
                "shopify_product_id": str(created.get("id", "")),
                "shopify_domain": domain,
                "status": "draft",
                "exported_at": datetime.now(timezone.utc).isoformat(),
            })
            return {
                "success": True,
                "shopify_product_id": created.get("id"),
                "admin_url": f"https://{domain}/admin/products/{created.get('id')}",
                "title": created.get("title"),
                "status": "draft",
            }
        elif resp.status_code == 401:
            return JSONResponse(content={"success": False, "error": "Shopify token expired or invalid. Reconnect in Settings."})
        else:
            err = resp.text[:200]
            logging.error(f"Shopify push failed ({resp.status_code}): {err}")
            return JSONResponse(content={"success": False, "error": f"Shopify returned {resp.status_code}. Check your store permissions."})
    except httpx.RequestError as e:
        return JSONResponse(content={"success": False, "error": f"Could not reach Shopify: {str(e)[:100]}"})


@shopify_integration_router.get("/exports")
async def get_shopify_exports(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get user's Shopify export history."""
    exports = await db.shopify_exports.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("exported_at", -1).to_list(50)
    return {"exports": exports, "total": len(exports)}


routers = [shopify_integration_router]
