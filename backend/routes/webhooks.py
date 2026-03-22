"""Resend webhook handler for email event tracking (opens, clicks, bounces, etc.)."""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException
from common.database import db

logger = logging.getLogger(__name__)
webhook_router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@webhook_router.post("/resend")
async def resend_webhook(request: Request):
    """Handle Resend email events: delivered, opened, clicked, bounced, complained."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("type", "")
    data = payload.get("data", {})
    email_to = ""
    if isinstance(data.get("to"), list) and data["to"]:
        email_to = data["to"][0]
    elif isinstance(data.get("to"), str):
        email_to = data["to"]

    event_doc = {
        "event_type": event_type,
        "email": email_to,
        "email_id": data.get("email_id", ""),
        "subject": data.get("subject", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_data": {
            "from": data.get("from", ""),
            "click_url": data.get("click", {}).get("link", "") if isinstance(data.get("click"), dict) else "",
        },
    }

    await db.email_events.insert_one(event_doc)

    # Update lead record with engagement data
    if email_to and event_type in ("email.opened", "email.clicked"):
        update_field = "email_opened" if event_type == "email.opened" else "email_clicked"
        await db.leads.update_one(
            {"email": email_to},
            {
                "$set": {f"engagement.{update_field}": True, f"engagement.{update_field}_at": event_doc["timestamp"]},
                "$inc": {f"engagement.{update_field}_count": 1},
            },
        )

    if email_to and event_type in ("email.bounced", "email.complained"):
        await db.leads.update_one(
            {"email": email_to},
            {"$set": {"engagement.bounced": True, "engagement.bounced_at": event_doc["timestamp"]}},
        )

    logger.info(f"Resend webhook: {event_type} for {email_to}")
    return {"received": True}


@webhook_router.get("/resend/stats")
async def get_email_stats():
    """Aggregate email event statistics for the dashboard."""
    pipeline = [
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
    ]
    stats = {doc["_id"]: doc["count"] async for doc in db.email_events.aggregate(pipeline)}

    # Recent events
    recent = await db.email_events.find(
        {}, {"_id": 0, "event_type": 1, "email": 1, "subject": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(20).to_list(20)

    return {
        "total_sent": stats.get("email.sent", 0),
        "total_delivered": stats.get("email.delivered", 0),
        "total_opened": stats.get("email.opened", 0),
        "total_clicked": stats.get("email.clicked", 0),
        "total_bounced": stats.get("email.bounced", 0),
        "total_complained": stats.get("email.complained", 0),
        "open_rate": round(stats.get("email.opened", 0) / max(stats.get("email.delivered", 1), 1) * 100, 1),
        "click_rate": round(stats.get("email.clicked", 0) / max(stats.get("email.delivered", 1), 1) * 100, 1),
        "recent_events": recent,
    }


routers = [webhook_router]
