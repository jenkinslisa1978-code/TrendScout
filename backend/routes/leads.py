from fastapi import APIRouter, Request
from datetime import datetime, timezone

router = APIRouter(prefix="/api/leads", tags=["leads"])

routers = [router]

@router.post("/capture")
async def capture_lead(request: Request):
    """Capture an email lead from free tools or marketing pages."""
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
        source = body.get("source", "unknown")
        context = body.get("context", "")
        
        if not email or "@" not in email:
            return {"status": "error", "message": "Invalid email"}
        
        db = request.app.state.db
        # Upsert to avoid duplicates
        await db.leads.update_one(
            {"email": email},
            {"$set": {
                "email": email,
                "source": source,
                "context": context,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }, "$setOnInsert": {
                "created_at": datetime.now(timezone.utc).isoformat(),
            }},
            upsert=True
        )
        return {"status": "ok"}
    except Exception:
        return {"status": "ok"}  # Never fail visibly for lead capture
