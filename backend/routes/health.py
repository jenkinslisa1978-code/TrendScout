"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime, timezone
from common.database import db

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "TrendScout API v1.0.0", "status": "healthy"}


@api_router.get("/health")
async def health_check():
    """Health check — returns 200 immediately; DB status is best-effort."""
    result = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        product_count = await db.products.count_documents({})
        user_count = await db.auth_users.count_documents({})
        result["db"] = {
            "products": product_count,
            "users": user_count,
            "connected": True,
        }
    except Exception as e:
        result["db"] = {"connected": False, "error": str(e)}
    return result


routers = [api_router]
