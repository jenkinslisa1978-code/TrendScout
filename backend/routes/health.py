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
    try:
        product_count = await db.products.count_documents({})
        user_count = await db.auth_users.count_documents({})
        return {
            "status": "ok",
            "db": {
                "products": product_count,
                "users": user_count,
                "connected": True,
            },
        }
    except Exception as e:
        return {"status": "degraded", "db": {"connected": False, "error": str(e)}}


routers = [api_router]
