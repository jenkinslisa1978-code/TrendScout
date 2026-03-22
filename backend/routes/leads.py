from fastapi import APIRouter, Request
from datetime import datetime, timezone
import os
import logging
from common.database import db

logger = logging.getLogger(__name__)

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
        viability_result = body.get("viability_result")
        
        if not email or "@" not in email:
            return {"status": "error", "message": "Invalid email"}
        
        # db imported from common.database
        now = datetime.now(timezone.utc).isoformat()
        
        # Upsert to avoid duplicates
        update_fields = {
            "email": email,
            "source": source,
            "context": context,
            "updated_at": now,
        }
        if viability_result:
            update_fields["viability_result"] = viability_result
        
        await db.leads.update_one(
            {"email": email},
            {"$set": update_fields, "$setOnInsert": {
                "created_at": now,
                "digest_opt_in": True,
                "drip_emails_sent": [],
            }},
            upsert=True
        )
        
        # Send instant viability result email (Drip Email 1) if from viability gate
        if source == "quick_viability_gate" and viability_result:
            try:
                from services.email_service import email_service
                await email_service.send_viability_result_email(
                    to_email=email,
                    product_name=viability_result.get("product_name", ""),
                    score=viability_result.get("score", 0),
                    verdict=viability_result.get("verdict", ""),
                    summary=viability_result.get("summary", ""),
                    strengths=viability_result.get("strengths", []),
                    risks=viability_result.get("risks", []),
                )
                await db.leads.update_one(
                    {"email": email},
                    {"$addToSet": {"drip_emails_sent": {"type": "viability_result", "sent_at": now}}}
                )
            except Exception as e:
                logger.error(f"Failed to send viability email to {email}: {e}")
        
        return {"status": "ok"}
    except Exception:
        return {"status": "ok"}  # Never fail visibly for lead capture


@router.post("/send-digest")
async def send_weekly_digest(request: Request):
    """Admin endpoint: send weekly product digest email to all opted-in leads."""
    try:
        body = await request.json()
        admin_key = body.get("admin_key", "")
        
        # Simple auth check — admin only
        if admin_key != os.environ.get("STRIPE_WEBHOOK_SECRET", ""):
            return {"status": "error", "message": "Unauthorized"}
        
        # db imported from common.database
        
        # Get opted-in leads
        leads = await db.leads.find(
            {"digest_opt_in": {"$ne": False}},
            {"_id": 0, "email": 1}
        ).to_list(5000)
        
        if not leads:
            return {"status": "ok", "sent": 0, "message": "No subscribers"}
        
        # Get top trending products for the digest content
        products = await db.products.find(
            {},
            {"_id": 0, "name": 1, "viability_score": 1, "trend_score": 1, "category": 1, "price_range": 1}
        ).sort("trend_score", -1).limit(5).to_list(5)
        
        # Build email content
        product_rows = ""
        for p in products:
            name = p.get("name", "Unknown Product")
            score = p.get("viability_score", p.get("trend_score", "N/A"))
            category = p.get("category", "General")
            product_rows += f"""
            <tr>
              <td style="padding:12px 16px;border-bottom:1px solid #f1f5f9;font-size:14px;color:#334155;">{name}</td>
              <td style="padding:12px 16px;border-bottom:1px solid #f1f5f9;font-size:14px;color:#334155;text-align:center;">{category}</td>
              <td style="padding:12px 16px;border-bottom:1px solid #f1f5f9;font-size:14px;font-weight:600;color:#4f46e5;text-align:center;">{score}</td>
            </tr>"""
        
        if not product_rows:
            product_rows = """
            <tr>
              <td colspan="3" style="padding:16px;text-align:center;color:#64748b;font-size:14px;">
                No trending products this week — check back soon.
              </td>
            </tr>"""
        
        site_url = os.environ.get("SITE_URL", "https://trendscout.click")
        
        html_body = f"""
        <div style="font-family:'Inter',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;padding:32px 24px;">
          <div style="text-align:center;margin-bottom:24px;">
            <h1 style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:700;color:#0f172a;margin:0;">
              TrendScout Weekly Digest
            </h1>
            <p style="font-size:14px;color:#64748b;margin:8px 0 0;">Top trending UK products this week</p>
          </div>
          
          <table style="width:100%;border-collapse:collapse;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;">
            <thead>
              <tr style="background:#f8fafc;">
                <th style="padding:12px 16px;text-align:left;font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.05em;">Product</th>
                <th style="padding:12px 16px;text-align:center;font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.05em;">Category</th>
                <th style="padding:12px 16px;text-align:center;font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.05em;">Score</th>
              </tr>
            </thead>
            <tbody>
              {product_rows}
            </tbody>
          </table>
          
          <div style="text-align:center;margin-top:24px;">
            <a href="{site_url}/trending-products?utm_source=email&utm_medium=digest&utm_campaign=lead_digest&utm_content=cta_trending" style="display:inline-block;background:#4f46e5;color:#fff;padding:12px 28px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;">
              See all trending products
            </a>
          </div>
          
          <div style="margin-top:24px;padding-top:16px;border-top:1px solid #e2e8f0;">
            <p style="font-size:12px;color:#94a3b8;text-align:center;margin:0;">
              You are receiving this because you signed up at TrendScout.
              <br/>To unsubscribe, reply to this email with "unsubscribe".
            </p>
          </div>
        </div>
        """
        
        # Send via Resend
        resend_key = os.environ.get("RESEND_API_KEY")
        sender_email = os.environ.get("SENDER_EMAIL", "noreply@trendscout.click")
        
        if not resend_key:
            return {"status": "error", "message": "Email service not configured"}
        
        import httpx
        sent_count = 0
        errors = []
        
        async with httpx.AsyncClient() as client:
            for lead in leads:
                try:
                    resp = await client.post(
                        "https://api.resend.com/emails",
                        headers={
                            "Authorization": f"Bearer {resend_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "from": f"TrendScout <{sender_email}>",
                            "to": [lead["email"]],
                            "subject": "Your weekly UK product trends",
                            "html": html_body,
                        },
                        timeout=10,
                    )
                    if resp.status_code in (200, 201):
                        sent_count += 1
                    else:
                        errors.append(f"{lead['email']}: {resp.status_code}")
                except Exception as e:
                    errors.append(f"{lead['email']}: {str(e)}")
        
        # Log digest send
        await db.digest_log.insert_one({
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "total_leads": len(leads),
            "sent_count": sent_count,
            "errors": errors[:10],
        })
        
        return {"status": "ok", "sent": sent_count, "total": len(leads), "errors": len(errors)}
        
    except Exception as e:
        logger.error(f"Digest send failed: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/share-result")
async def get_share_result(request: Request):
    """Generate a shareable result card for free tool calculations."""
    params = dict(request.query_params)
    tool = params.get("tool", "calculator")
    result_text = params.get("result", "")
    detail = params.get("detail", "")
    
    site_url = os.environ.get("SITE_URL", "https://trendscout.click")
    
    return {
        "status": "ok",
        "share": {
            "title": f"My UK {tool} result — TrendScout",
            "text": f"{result_text} {detail}".strip(),
            "url": f"{site_url}/tools",
            "hashtags": "ecommerce,UK,productresearch",
        }
    }
