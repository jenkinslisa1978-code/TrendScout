"""Image enrichment endpoints."""
from fastapi import APIRouter, HTTPException, Depends

from auth import get_current_user, AuthenticatedUser
from common.database import db

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
async def batch_enrich_images(user: AuthenticatedUser = Depends(get_current_user)):
    """Trigger batch image enrichment for products missing images."""
    profile = await db.profiles.find_one({"id": user.user_id}, {"_id": 0, "is_admin": 1})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(403, "Admin only")
    from services.image_service import ImageService
    svc = ImageService(db)
    result = await svc.batch_enrich(limit=10)
    return result


routers = [images_router]
