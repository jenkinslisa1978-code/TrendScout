from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
import uuid
import logging

from auth import get_current_user, AuthenticatedUser
from common.database import db

winners_router = APIRouter(prefix="/api/winners")


class SubmitWinnerRequest(BaseModel):
    product_id: str
    revenue_range: str  # e.g. "$1K-5K", "$5K-10K", "$10K-50K", "$50K+"
    timeframe: str  # "1 week", "1 month", "3 months"
    proof_description: str
    store_niche: Optional[str] = None
    ad_platform: Optional[str] = None
    tips: Optional[str] = None


@winners_router.post("/submit")
async def submit_winner(
    req: SubmitWinnerRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Submit proof of a winning product (anonymous to other users)."""
    product = await db.products.find_one({"id": req.product_id}, {"_id": 0, "id": 1, "product_name": 1, "image_url": 1, "category": 1, "launch_score": 1})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Prevent duplicate submissions
    existing = await db.verified_winners.find_one(
        {"user_id": current_user.user_id, "product_id": req.product_id}
    )
    if existing:
        raise HTTPException(status_code=409, detail="You already submitted proof for this product")

    submission = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.user_id,
        "product_id": req.product_id,
        "product_name": product.get("product_name", ""),
        "product_image": product.get("image_url", ""),
        "category": product.get("category", ""),
        "launch_score": product.get("launch_score", 0),
        "revenue_range": req.revenue_range,
        "timeframe": req.timeframe,
        "proof_description": req.proof_description,
        "store_niche": req.store_niche,
        "ad_platform": req.ad_platform,
        "tips": req.tips,
        "status": "pending",  # pending, verified, rejected
        "upvotes": 0,
        "upvoted_by": [],
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.verified_winners.insert_one(submission)
    submission.pop("_id", None)
    # Remove user_id for privacy
    submission.pop("user_id", None)
    return {"submission": submission}


@winners_router.get("/")
async def get_verified_winners(
    status: str = "verified",
    sort: str = "upvotes",
    category: Optional[str] = None,
    limit: int = 20,
):
    """Get verified winners — public leaderboard."""
    query: Dict[str, Any] = {"status": status}
    if category and category != "all":
        query["category"] = category

    sort_map = {
        "upvotes": [("upvotes", -1)],
        "recent": [("submitted_at", -1)],
        "revenue": [("revenue_range", -1)],
    }
    sort_order = sort_map.get(sort, sort_map["upvotes"])

    items = await db.verified_winners.find(
        query, {"_id": 0, "user_id": 0, "upvoted_by": 0}
    ).sort(sort_order).limit(min(limit, 50)).to_list(min(limit, 50))

    # Get all pending + verified for stats
    total_verified = await db.verified_winners.count_documents({"status": "verified"})
    total_pending = await db.verified_winners.count_documents({"status": "pending"})

    # Get categories
    categories = await db.verified_winners.distinct("category", {"status": status})

    return {
        "winners": items,
        "total": len(items),
        "total_verified": total_verified,
        "total_pending": total_pending,
        "categories": sorted([c for c in categories if c]),
    }


@winners_router.post("/{winner_id}/upvote")
async def upvote_winner(
    winner_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Upvote a verified winner submission."""
    winner = await db.verified_winners.find_one({"id": winner_id})
    if not winner:
        raise HTTPException(status_code=404, detail="Submission not found")

    upvoted = winner.get("upvoted_by", [])
    if current_user.user_id in upvoted:
        # Undo upvote
        await db.verified_winners.update_one(
            {"id": winner_id},
            {"$pull": {"upvoted_by": current_user.user_id}, "$inc": {"upvotes": -1}},
        )
        return {"upvoted": False, "upvotes": winner.get("upvotes", 1) - 1}
    else:
        await db.verified_winners.update_one(
            {"id": winner_id},
            {"$push": {"upvoted_by": current_user.user_id}, "$inc": {"upvotes": 1}},
        )
        return {"upvoted": True, "upvotes": winner.get("upvotes", 0) + 1}


@winners_router.get("/my-submissions")
async def get_my_submissions(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get current user's winner submissions."""
    items = await db.verified_winners.find(
        {"user_id": current_user.user_id}, {"_id": 0, "upvoted_by": 0}
    ).sort("submitted_at", -1).to_list(20)
    return {"submissions": items, "total": len(items)}


@winners_router.post("/{winner_id}/verify")
async def verify_winner(
    winner_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Admin: Verify or reject a winner submission."""
    profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0})
    if not profile or not profile.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")

    body = await request.json()
    new_status = body.get("status", "verified")
    if new_status not in ("verified", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be 'verified' or 'rejected'")

    result = await db.verified_winners.update_one(
        {"id": winner_id},
        {"$set": {"status": new_status, "verified_at": datetime.now(timezone.utc).isoformat()}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Submission not found")

    # If verified, badge the product
    if new_status == "verified":
        winner = await db.verified_winners.find_one({"id": winner_id}, {"_id": 0})
        if winner:
            await db.products.update_one(
                {"id": winner["product_id"]},
                {"$set": {"verified_winner": True, "verified_winner_at": datetime.now(timezone.utc).isoformat()}},
            )

    return {"status": new_status, "winner_id": winner_id}


routers = [winners_router]
