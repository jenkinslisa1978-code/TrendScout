"""Image enrichment and pipeline endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timezone

from auth import get_current_user, AuthenticatedUser
from common.database import db
from common.helpers import require_admin

images_router = APIRouter()


@images_router.post("/api/images/enrich/{product_id}")
async def enrich_product_images(product_id: str, user=Depends(get_current_user)):
    """Enrich a single product with high-quality images."""
    from services.image_service import ImageService
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(404, "Product not found")
    svc = ImageService(db)
    result = await svc.enrich_product_images(product)
    return result


@images_router.post("/api/images/batch-enrich")
async def batch_enrich_images(
    limit: int = Query(20, ge=1, le=100),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Trigger batch image enrichment for products missing images."""
    await require_admin(user)
    from services.image_service import ImageService
    svc = ImageService(db)
    result = await svc.batch_enrich(limit=limit)
    return result


@images_router.get("/api/images/pipeline/stats")
async def get_image_pipeline_stats(user: AuthenticatedUser = Depends(get_current_user)):
    """Get image pipeline statistics for the admin dashboard."""
    await require_admin(user)

    total = await db.products.count_documents({})
    with_images = await db.products.count_documents({"image_url": {"$ne": None, "$ne": ""}})
    enriched = await db.products.count_documents({"image_enriched": True})
    pending_review = await db.products.count_documents({"image_review_status": "pending"})
    approved = await db.products.count_documents({"image_review_status": {"$in": ["approved", "auto_approved"]}})
    rejected = await db.products.count_documents({"image_review_status": "rejected"})

    # Confidence distribution
    high_conf = await db.products.count_documents({"image_confidence": {"$gte": 70}})
    mid_conf = await db.products.count_documents({"image_confidence": {"$gte": 40, "$lt": 70}})
    low_conf = await db.products.count_documents({"image_confidence": {"$lt": 40, "$exists": True}})

    return {
        "total_products": total,
        "with_images": with_images,
        "without_images": total - with_images,
        "enriched": enriched,
        "coverage_pct": round(with_images / total * 100, 1) if total else 0,
        "review_queue": {
            "pending": pending_review,
            "approved": approved,
            "rejected": rejected,
        },
        "confidence_distribution": {
            "high": high_conf,
            "medium": mid_conf,
            "low": low_conf,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@images_router.get("/api/images/pipeline/queue")
async def get_image_review_queue(
    status: str = "pending",
    limit: int = Query(20, ge=1, le=100),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Get products queued for image review."""
    await require_admin(user)

    query = {}
    if status != "all":
        query["image_review_status"] = status

    products = await db.products.find(
        query,
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "image_url": 1,
         "candidate_images": 1, "image_confidence": 1, "image_review_status": 1,
         "image_sources": 1, "image_enriched_at": 1, "gallery_images": 1}
    ).sort("image_confidence", 1).limit(limit).to_list(limit)

    return {"products": products, "count": len(products), "status_filter": status}


@images_router.post("/api/images/pipeline/review/{product_id}")
async def review_product_image(
    product_id: str,
    action: str = Query(..., regex="^(approve|reject|select)$"),
    selected_url: Optional[str] = None,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Admin review action on a product's image."""
    await require_admin(user)

    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(404, "Product not found")

    update = {
        "image_reviewed_at": datetime.now(timezone.utc).isoformat(),
        "image_reviewed_by": user.user_id,
    }

    if action == "approve":
        update["image_review_status"] = "approved"
    elif action == "reject":
        update["image_review_status"] = "rejected"
        update["image_url"] = None
    elif action == "select" and selected_url:
        update["image_review_status"] = "approved"
        update["image_url"] = selected_url

    await db.products.update_one({"id": product_id}, {"$set": update})
    return {"status": "success", "action": action, "product_id": product_id}


routers = [images_router]
