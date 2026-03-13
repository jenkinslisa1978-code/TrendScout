from fastapi import APIRouter, HTTPException, Request, Depends, Header, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
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

from services.store_service import (
    export_store_for_shopify,
    export_store_as_shopify_csv,
    export_store_for_woocommerce,
    StoreGenerator,
    create_store_document,
    create_store_product_document,
    get_store_limit,
    can_create_store,
    STORE_LIMITS,
)

stores_router = APIRouter(prefix="/api/stores")

@stores_router.get("")
async def get_user_stores(
    status: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Get all stores for the authenticated user"""
    user_id = current_user.user_id
    query = {"owner_id": user_id}
    if status:
        query["status"] = status
    
    stores = await db.stores.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    # Get product counts for each store
    for store in stores:
        product_count = await db.store_products.count_documents({"store_id": store["id"]})
        store["product_count"] = product_count
    
    return {
        "data": stores,
        "count": len(stores),
    }

@stores_router.get("/limits")
async def get_store_limits(plan: str = "starter"):
    """Get store limits for a plan"""
    limit = get_store_limit(plan)
    return {
        "plan": plan,
        "limit": limit if limit != float('inf') else "unlimited",
        "all_limits": {k: v if v != float('inf') else "unlimited" for k, v in STORE_LIMITS.items()}
    }

@stores_router.get("/{store_id}")
async def get_store(
    store_id: str,
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get a single store by ID. Requires ownership unless store is published."""
    store = await db.stores.find_one({"id": store_id}, {"_id": 0})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Check access: must be owner OR store must be published
    user_id = current_user.user_id if current_user else None
    is_owner = user_id and store["owner_id"] == user_id
    is_published = store.get("status") == "published"
    
    if not is_owner and not is_published:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get products for this store
    products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    store["products"] = products
    
    return {"data": store}

@stores_router.post("/generate")
async def generate_store(
    request: GenerateStoreRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Generate a store draft from a product (AI store builder)"""
    user_id = current_user.user_id
    # Check store limits
    current_count = await db.stores.count_documents({"owner_id": user_id})
    
    if not can_create_store(current_count, request.plan):
        limit = get_store_limit(request.plan)
        raise HTTPException(
            status_code=403, 
            detail=f"Store limit reached. Your {request.plan} plan allows {limit} store(s). Upgrade to create more stores."
        )
    
    # Get the product
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Generate store content
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(product, request.store_name)
    
    return {
        "success": True,
        "generation": generation_result,
        "product": product,
        "can_create": True,
        "stores_remaining": get_store_limit(request.plan) - current_count - 1 if get_store_limit(request.plan) != float('inf') else "unlimited",
    }

@stores_router.post("")
async def create_store(
    request: StoreCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Create a new store from generated content"""
    user_id = current_user.user_id
    # Check store limits
    current_count = await db.stores.count_documents({"owner_id": user_id})
    
    if not can_create_store(current_count, request.plan):
        limit = get_store_limit(request.plan)
        raise HTTPException(
            status_code=403, 
            detail=f"Store limit reached. Your {request.plan} plan allows {limit} store(s)."
        )
    
    # Get the product
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Generate store content
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(product, request.name)
    
    # Create store document
    store_doc = create_store_document(
        user_id=user_id,
        store_name=request.name,
        generation_result=generation_result,
        product=product
    )
    
    # Create store product document
    store_product_doc = create_store_product_document(
        store_id=store_doc["id"],
        product=product,
        generation_result=generation_result
    )
    
    # Insert into database
    await db.stores.insert_one(store_doc)
    await db.store_products.insert_one(store_product_doc)
    
    # Track product success - store created
    await track_product_store_created(request.product_id)
    
    # Remove _id for response
    store_doc.pop("_id", None)
    store_product_doc.pop("_id", None)
    
    return {
        "success": True,
        "store": store_doc,
        "product": store_product_doc,
        "stores_remaining": get_store_limit(request.plan) - current_count - 1 if get_store_limit(request.plan) != float('inf') else "unlimited",
    }

@stores_router.put("/{store_id}")
async def update_store(
    store_id: str,
    request: StoreUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update a store owned by the authenticated user"""
    user_id = current_user.user_id
    # Verify ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Build update dict
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.stores.update_one({"id": store_id}, {"$set": update_data})
    
    # Get updated store
    updated = await db.stores.find_one({"id": store_id}, {"_id": 0})
    
    return {"success": True, "store": updated}

@stores_router.delete("/{store_id}")
async def delete_store(
    store_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Delete a store and its products (requires ownership)"""
    user_id = current_user.user_id
    # Verify ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Delete store products
    await db.store_products.delete_many({"store_id": store_id})
    
    # Delete store
    await db.stores.delete_one({"id": store_id})
    
    return {"success": True, "message": "Store deleted"}

@stores_router.post("/{store_id}/products")
async def add_product_to_store(
    store_id: str,
    request: StoreProductCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Add a product to an existing store (requires ownership)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Get the product
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product already in store
    existing = await db.store_products.find_one({
        "store_id": store_id,
        "original_product_id": request.product_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Product already in store")
    
    # Generate content for this product
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(product)
    
    # Create store product
    store_product_doc = create_store_product_document(store_id, product, generation_result)
    store_product_doc["is_featured"] = False  # Not featured when adding to existing store
    
    await db.store_products.insert_one(store_product_doc)
    store_product_doc.pop("_id", None)
    
    return {"success": True, "product": store_product_doc}

@stores_router.get("/{store_id}/products")
async def get_store_products(store_id: str):
    """Get all products in a store"""
    products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    
    return {
        "data": products,
        "count": len(products),
    }

@stores_router.put("/{store_id}/products/{product_id}")
async def update_store_product(
    store_id: str,
    product_id: str,
    request: StoreProductUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update a product in a store (requires ownership)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Build update dict
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.store_products.update_one(
        {"id": product_id, "store_id": store_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in store")
    
    updated = await db.store_products.find_one({"id": product_id}, {"_id": 0})
    
    return {"success": True, "product": updated}

@stores_router.delete("/{store_id}/products/{product_id}")
async def delete_store_product(
    store_id: str,
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Remove a product from a store (requires ownership)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    result = await db.store_products.delete_one({"id": product_id, "store_id": store_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in store")
    
    return {"success": True, "message": "Product removed from store"}

@stores_router.post("/{store_id}/regenerate/{product_id}")
async def regenerate_product_copy(
    store_id: str,
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Regenerate AI copy for a store product (requires ownership)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Get store product
    store_product = await db.store_products.find_one({"id": product_id, "store_id": store_id})
    
    if not store_product:
        raise HTTPException(status_code=404, detail="Product not found in store")
    
    # Get original product
    original_product = await db.products.find_one(
        {"id": store_product["original_product_id"]}, 
        {"_id": 0}
    )
    
    if not original_product:
        raise HTTPException(status_code=404, detail="Original product not found")
    
    # Regenerate content
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(original_product)
    
    product_data = generation_result.get("product", {})
    pricing = product_data.get("pricing", {})
    
    # Update store product
    update_data = {
        "title": product_data.get("title"),
        "description": product_data.get("description"),
        "bullet_points": product_data.get("bullet_points"),
        "price": pricing.get("suggested_price"),
        "compare_at_price": pricing.get("compare_at_price"),
        "updated_at": datetime.now(timezone.utc),
    }
    
    await db.store_products.update_one({"id": product_id}, {"$set": update_data})
    
    updated = await db.store_products.find_one({"id": product_id}, {"_id": 0})
    
    return {"success": True, "product": updated, "regenerated": True}

@stores_router.get("/{store_id}/export")
async def export_store(
    store_id: str,
    format: str = "shopify",
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Export store data for Shopify or other platforms (requires ownership)"""
    
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id}, {"_id": 0})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    # Get products
    products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    
    if format == "shopify":
        export_data = export_store_for_shopify(store, products)
    elif format == "shopify_csv":
        csv_content = export_store_as_shopify_csv(store, products)
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={store.get('name', 'store').replace(' ', '_')}_shopify.csv"}
        )
    elif format == "woocommerce":
        export_data = export_store_for_woocommerce(store, products)
    else:
        # Raw JSON export
        export_data = {
            "store": store,
            "products": products,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
    
    # Track product export for success tracking
    for product in products:
        source_product_id = product.get("source_product_id")
        if source_product_id:
            await track_product_exported(source_product_id)
    
    # Update store status to exported (if not already published)
    if store.get("status") not in ["published", "exported"]:
        await db.stores.update_one(
            {"id": store_id},
            {"$set": {"status": "exported", "exported_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}}
        )
    
    return export_data

@stores_router.put("/{store_id}/status")
async def update_store_status(
    store_id: str,
    request: UpdateStoreStatusRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Update store status (draft -> ready -> exported -> published)"""
    user_id = current_user.user_id
    # Verify store ownership
    store = await db.stores.find_one({"id": store_id, "owner_id": user_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found or access denied")
    
    update_data = {
        "status": request.status.value,
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Add timestamp for status changes
    if request.status == StoreStatus.READY:
        update_data["ready_at"] = datetime.now(timezone.utc)
    elif request.status == StoreStatus.EXPORTED:
        update_data["exported_at"] = datetime.now(timezone.utc)
    elif request.status == StoreStatus.PUBLISHED:
        update_data["published_at"] = datetime.now(timezone.utc)
    
    await db.stores.update_one({"id": store_id}, {"$set": update_data})
    
    updated = await db.stores.find_one({"id": store_id}, {"_id": 0})
    
    return {"success": True, "store": updated}

@stores_router.get("/{store_id}/preview")
async def get_store_preview(store_id: str):
    """Get store data for public preview page"""
    store = await db.stores.find_one({"id": store_id}, {"_id": 0})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Get featured product
    featured_product = await db.store_products.find_one(
        {"store_id": store_id, "is_featured": True}, 
        {"_id": 0}
    )
    
    # If no featured, get first product
    if not featured_product:
        featured_product = await db.store_products.find_one({"store_id": store_id}, {"_id": 0})
    
    # Get all products
    all_products = await db.store_products.find({"store_id": store_id}, {"_id": 0}).to_list(100)
    
    return {
        "store": store,
        "featured_product": featured_product,
        "all_products": all_products,
        "is_published": store.get("status") == "published",
    }


# =====================
# ROUTES - Shopify Integration
# =====================



@stores_router.post("/launch")
async def launch_store(
    request: LaunchStoreRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    ONE-CLICK STORE LAUNCH.
    
    Creates a complete store from a product in one API call:
    1. Fetches product data
    2. Attaches selected supplier (or auto-selects best)
    3. Generates store name, branding, product copy, shipping rules, policies
    4. Creates store + store product in database
    5. Returns complete store ready for export
    """
    user_id = current_user.user_id
    # Get user plan from subscription system
    from services.subscription_service import FeatureGate
    user_plan = await get_user_plan(user_id)
    
    # Check store limits
    current_count = await db.stores.count_documents({"owner_id": user_id})
    if not FeatureGate.can_create_store(user_plan, current_count):
        limit = FeatureGate.get_max_stores(user_plan)
        limit_text = "unlimited" if limit == -1 else str(limit)
        raise HTTPException(status_code=403, detail=f"Store limit reached ({limit_text} stores on {user_plan} plan). Upgrade to create more.")
    
    # Get product
    product = await db.products.find_one({"id": request.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get supplier
    supplier = None
    if request.supplier_id:
        supplier = await db.product_suppliers.find_one({"id": request.supplier_id}, {"_id": 0})
    else:
        # Auto-select: prefer selected, then cheapest
        supplier = await db.product_suppliers.find_one(
            {"product_id": request.product_id, "is_selected": True}, {"_id": 0}
        )
        if not supplier:
            # Find cheapest supplier
            cursor = db.product_suppliers.find(
                {"product_id": request.product_id}, {"_id": 0}
            ).sort("supplier_cost", 1).limit(1)
            suppliers = await cursor.to_list(1)
            if suppliers:
                supplier = suppliers[0]
            else:
                # Auto-discover suppliers
                from services.supplier_service import SupplierService
                svc = SupplierService(db)
                result = await svc.find_suppliers(request.product_id)
                if result.get('suppliers'):
                    supplier = result['suppliers'][0]
    
    # Generate store content
    generator = StoreGenerator()
    generation_result = generator.generate_full_store(product, request.store_name, supplier)
    store_name = request.store_name or generation_result['selected_name']
    
    # Create store
    store_doc = create_store_document(user_id, store_name, generation_result, product)
    store_product_doc = create_store_product_document(store_doc["id"], product, generation_result)
    
    await db.stores.insert_one(store_doc)
    await db.store_products.insert_one(store_product_doc)
    
    # Track
    await track_product_store_created(request.product_id)
    
    store_doc.pop("_id", None)
    store_product_doc.pop("_id", None)
    
    return {
        "success": True,
        "store": store_doc,
        "product": store_product_doc,
        "generation": generation_result,
        "supplier_connected": supplier is not None,
        "next_steps": [
            f"View your store at /stores/{store_doc['id']}",
            "Export to Shopify CSV or WooCommerce",
            "Customize branding and product copy",
        ],
    }




routers = [stores_router]
