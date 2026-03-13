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

supplier_router = APIRouter(prefix="/api/suppliers")

@supplier_router.get("/{product_id}")
async def get_product_suppliers(product_id: str):
    """Get all supplier listings for a product. Auto-discovers if none exist."""
    from services.supplier_service import SupplierService
    service = SupplierService(db)
    result = await service.find_suppliers(product_id)
    return result


@supplier_router.post("/{product_id}/find")
async def find_suppliers(product_id: str):
    """Trigger supplier discovery for a product."""
    from services.supplier_service import SupplierService
    service = SupplierService(db)
    
    # Delete existing to force refresh
    await db.product_suppliers.delete_many({"product_id": product_id})
    result = await service.find_suppliers(product_id)
    return result


@supplier_router.post("/{product_id}/select/{supplier_id}")
async def select_supplier(
    product_id: str,
    supplier_id: str,
    authorization: Optional[str] = Header(None),
):
    """Select a supplier for a product."""
    user_id = "anonymous"
    if authorization and authorization.startswith("Bearer "):
        try:
            import jwt
            token = authorization.split(" ")[1]
            payload = jwt.decode(token, os.environ.get('JWT_SECRET', ''), algorithms=["HS256"])
            user_id = payload.get("sub", "anonymous")
        except Exception:
            pass
    
    from services.supplier_service import SupplierService
    service = SupplierService(db)
    result = await service.select_supplier(product_id, supplier_id, user_id)
    return result




# ===================== AD CREATIVE ENDPOINTS =====================



routers = [supplier_router]
