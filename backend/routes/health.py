"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime, timezone

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "ViralScout API v1.0.0", "status": "healthy"}


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}


routers = [api_router]
