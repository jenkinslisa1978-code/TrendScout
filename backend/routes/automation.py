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
from services.ws_manager import notify_job_started, notify_job_progress, notify_job_completed, notify_job_failed

automation_router = APIRouter(prefix="/api/automation")

@automation_router.post("/run")
async def run_automation(request: RunAutomationRequest):
    """Run automation on products"""
    try:
        await notify_job_started(request.job_type.value)

        # Get products from request or database
        if request.products:
            products = request.products
        else:
            cursor = db.products.find({}, {"_id": 0})
            products = await cursor.to_list(1000)
        
        if not products:
            await notify_job_completed(request.job_type.value, result={"processed": 0, "message": "No products to process"})
            return {"success": True, "message": "No products to process", "processed": 0}
        
        # Create log entry
        log_doc = {
            "id": str(uuid.uuid4()),
            "job_type": request.job_type.value,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "products_processed": 0,
            "alerts_generated": 0,
        }
        await db.automation_logs.insert_one(log_doc)
        
        # Process products
        processed_products = []
        alerts = []
        total = len(products)
        
        for i, product in enumerate(products):
            result = run_full_automation(product)
            processed_products.append(result['product'])
            if result['alert']:
                alerts.append(result['alert'])
            if result.get('early_alert'):
                alerts.append(result['early_alert'])
            # Send progress every 20 products
            if (i + 1) % 20 == 0 or i == total - 1:
                await notify_job_progress(request.job_type.value, i + 1, total, detail=f"Processed {i + 1}/{total} products")
        
        # Update products in database
        for product in processed_products:
            await db.products.update_one(
                {"id": product['id']},
                {"$set": product},
                upsert=True
            )
        
        # Save alerts
        if alerts:
            await db.trend_alerts.insert_many(alerts)
        
        # Update log
        await db.automation_logs.update_one(
            {"id": log_doc["id"]},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": len(processed_products),
                "alerts_generated": len(alerts),
            }}
        )

        await notify_job_completed(request.job_type.value, result={
            "processed": len(processed_products),
            "alerts_generated": len(alerts),
        })
        
        return {
            "success": True,
            "processed": len(processed_products),
            "alerts_generated": len(alerts),
            "log_id": log_doc["id"],
        }
        
    except Exception as e:
        logging.error(f"Automation error: {str(e)}")
        await notify_job_failed(request.job_type.value, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@automation_router.get("/logs")
async def get_automation_logs(limit: int = 50):
    """Get automation logs"""
    cursor = db.automation_logs.find({}, {"_id": 0}).sort("started_at", -1).limit(limit)
    logs = await cursor.to_list(limit)
    return {"data": logs}

@automation_router.get("/stats")
async def get_automation_stats():
    """Get automation statistics"""
    cursor = db.automation_logs.find({}, {"_id": 0})
    logs = await cursor.to_list(1000)
    
    if not logs:
        return {
            "total_runs": 0,
            "success_rate": 0,
            "products_processed": 0,
            "alerts_generated": 0,
            "last_run": None,
        }
    
    completed = [log for log in logs if log.get('status') == 'completed']
    
    return {
        "total_runs": len(logs),
        "success_rate": round(len(completed) / len(logs) * 100) if logs else 0,
        "products_processed": sum(log.get('products_processed', 0) for log in logs),
        "alerts_generated": sum(log.get('alerts_generated', 0) for log in logs),
        "last_run": logs[0].get('started_at') if logs else None,
    }

async def _run_daily_automation_task():
    """Background worker: CJ sync + product scoring. Runs after HTTP response is returned."""
    try:
        from services.jobs.tasks import sync_cj_products
        cj_result = await sync_cj_products(db, {})
        logging.info(f"Daily CJ sync: {cj_result.get('records_processed', 0)} new products")
    except Exception as e:
        logging.error(f"Daily CJ sync failed: {e}")

    try:
        await run_automation(RunAutomationRequest(job_type=AutomationJobType.SCHEDULED_DAILY))
        logging.info("Daily scoring automation complete")
    except Exception as e:
        logging.error(f"Daily scoring automation failed: {e}")


@automation_router.post("/scheduled/daily")
async def run_daily_automation(
    background_tasks: BackgroundTasks,
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Run daily scheduled automation.
    Returns immediately (202 Accepted) and runs CJ sync + scoring in background.
    Protected endpoint - requires API key for external cron services.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')

    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    background_tasks.add_task(_run_daily_automation_task)
    return {"success": True, "status": "accepted", "message": "Daily automation started in background"}


# =====================
# ROUTES - Data Pipeline
# =====================

@automation_router.post("/pipeline/full")
async def run_full_pipeline(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Run the full data ingestion pipeline.
    Fetches from all sources, updates competitor/ad data, and recalculates scores.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key and api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        from services.pipeline import DataPipeline
        pipeline = DataPipeline(db)
        result = await pipeline.run_full_pipeline()
        
        return {
            "success": result.success,
            "duration_seconds": result.duration_seconds,
            "products_processed": result.products_processed,
            "products_created": result.products_created,
            "products_updated": result.products_updated,
            "alerts_generated": result.alerts_generated,
            "source_results": result.source_results,
            "errors": result.errors if result.errors else None,
        }
    except Exception as e:
        logging.error(f"Pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@automation_router.post("/pipeline/quick-refresh")
async def run_quick_refresh():
    """
    Quick refresh - just update scores and competitor data.
    Faster than full pipeline, skips source fetching.
    """
    try:
        from services.pipeline import DataPipeline
        pipeline = DataPipeline(db)
        result = await pipeline.run_quick_refresh()
        
        return {
            "success": result.success,
            "duration_seconds": result.duration_seconds,
            "products_updated": result.products_updated,
            "errors": result.errors if result.errors else None,
        }
    except Exception as e:
        logging.error(f"Quick refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@automation_router.post("/pipeline/source/{source_name}")
async def run_source_pipeline(source_name: str):
    """
    Run pipeline for a specific data source.
    Valid sources: tiktok, amazon, aliexpress, cj_dropshipping
    """
    valid_sources = ['tiktok', 'amazon', 'aliexpress', 'cj_dropshipping']
    if source_name not in valid_sources:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid source. Must be one of: {', '.join(valid_sources)}"
        )
    
    try:
        from services.pipeline import DataPipeline
        pipeline = DataPipeline(db)
        result = await pipeline.run_source_only(source_name)
        
        return {
            "success": result.success,
            "source": source_name,
            "duration_seconds": result.duration_seconds,
            "products_created": result.products_created,
            "products_updated": result.products_updated,
            "source_results": result.source_results.get(source_name, {}),
            "errors": result.errors if result.errors else None,
        }
    except Exception as e:
        logging.error(f"Source pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@automation_router.get("/pipeline/status")
async def get_pipeline_status():
    """
    Get status of data sources and pipeline health.
    """
    # Get latest pipeline runs
    cursor = db.automation_logs.find(
        {"job_type": "full_pipeline"},
        {"_id": 0}
    ).sort("started_at", -1).limit(5)
    recent_runs = await cursor.to_list(5)
    
    # Get product counts
    total_products = await db.products.count_documents({})
    products_with_scores = await db.products.count_documents({"market_score": {"$gte": 0}})
    products_with_launch_score = await db.products.count_documents({"launch_score": {"$gte": 1}})
    high_opportunity = await db.products.count_documents({"market_label": {"$in": ["massive", "strong"]}})
    strong_launch = await db.products.count_documents({"launch_score": {"$gte": 80}})
    
    # Get data freshness
    latest_product = await db.products.find_one({}, {"_id": 0, "last_updated": 1}, sort=[("last_updated", -1)])
    
    return {
        "pipeline_health": "healthy" if recent_runs and recent_runs[0].get("success") else "unknown",
        "last_run": recent_runs[0] if recent_runs else None,
        "recent_runs": recent_runs,
        "product_stats": {
            "total": total_products,
            "with_scores": products_with_scores,
            "with_launch_score": products_with_launch_score,
            "high_opportunity": high_opportunity,
            "strong_launch": strong_launch,
        },
        "data_freshness": latest_product.get("last_updated") if latest_product else None,
        "sources": {
            "amazon_movers": {"status": "live", "description": "Amazon Movers & Shakers - real-time trending products"},
            "aliexpress_search": {"status": "generated", "description": "AliExpress supplier links auto-generated from product names"},
            "tiktok_trends": {"status": "pending", "description": "TikTok Creative Center - blocked by anti-bot"},
            "cj_dropshipping": {"status": "pending", "description": "CJ Dropshipping - blocked by anti-bot"},
        }
    }


@automation_router.post("/compute-launch-scores")
async def compute_launch_scores_batch(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Batch compute Launch Scores for all products.
    This updates the launch_score, launch_score_label, and launch_score_reasoning fields.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        start_time = datetime.now(timezone.utc)
        
        # Get all products
        products = await db.products.find({}, {"_id": 0}).to_list(None)
        updated_count = 0
        
        for product in products:
            # Calculate launch score
            launch_score, launch_label, launch_reasoning = calculate_launch_score(product)
            
            # Update in database
            await db.products.update_one(
                {"id": product.get("id")},
                {
                    "$set": {
                        "launch_score": launch_score,
                        "launch_score_label": launch_label,
                        "launch_score_reasoning": launch_reasoning,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            updated_count += 1
        
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return {
            "success": True,
            "products_updated": updated_count,
            "duration_seconds": round(duration, 2),
            "message": f"Updated launch scores for {updated_count} products"
        }
    except Exception as e:
        logging.error(f"Launch score computation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# VIRAL PREDICTIONS
# =====================

@automation_router.post("/viral-predictions/generate")
async def trigger_viral_predictions(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Generate a fresh batch of TikTok viral predictions.
    Protected by API key — call this from cron-job.org every 6 hours.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        from routes.viral_predictions import _generate_predictions
        predictions = await _generate_predictions()
        return {
            "success": True,
            "count": len(predictions),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logging.error(f"Viral predictions generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# WEEKLY DIGEST PIPELINE
# =====================

@automation_router.post("/weekly-digest/trigger")
async def trigger_weekly_digest(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
    current_user: AuthenticatedUser = Depends(get_optional_user),
):
    """
    Trigger the full weekly digest pipeline:
    1. Generate digest content (top 5 products + viral predictions)
    2. Send enhanced emails to registered users
    3. Send lead subscriber digest

    Can be triggered by API key (cron) or authenticated admin user.
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    is_admin = current_user and getattr(current_user, 'role', '') == 'admin'
    is_api_key = api_key == expected_key

    if not is_admin and not is_api_key:
        raise HTTPException(status_code=401, detail="Admin or API key required")

    from services.jobs.tasks import generate_weekly_digest, send_weekly_email_digest, send_lead_subscriber_digest

    results = {"steps": {}, "errors": []}

    # Step 1: Generate digest
    try:
        digest_result = await generate_weekly_digest(db, {})
        results["steps"]["generate_digest"] = digest_result
    except Exception as e:
        results["errors"].append(f"generate_digest: {str(e)}")
        logging.error(f"Weekly digest generation failed: {e}")

    # Step 2: Send enhanced emails to registered users
    try:
        email_result = await _send_enhanced_weekly_emails(db)
        results["steps"]["send_user_emails"] = email_result
    except Exception as e:
        results["errors"].append(f"send_user_emails: {str(e)}")
        logging.error(f"Weekly user emails failed: {e}")

    # Step 3: Send to leads
    try:
        lead_result = await send_lead_subscriber_digest(db, {})
        results["steps"]["send_lead_emails"] = lead_result
    except Exception as e:
        results["errors"].append(f"send_lead_emails: {str(e)}")
        logging.error(f"Weekly lead emails failed: {e}")

    # Log
    await db.automation_logs.insert_one({
        "id": str(uuid.uuid4()),
        "job_name": "weekly_digest_pipeline",
        "status": "completed",
        "run_time": datetime.now(timezone.utc).isoformat(),
        "details": results,
    })

    return {"success": True, **results}


@automation_router.get("/weekly-digest/preview")
async def preview_weekly_digest(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Preview the weekly digest email HTML without sending."""
    html = await _build_enhanced_digest_html(db)
    if not html:
        raise HTTPException(status_code=404, detail="Not enough product data to generate digest")
    return Response(content=html, media_type="text/html")


async def _send_enhanced_weekly_emails(database):
    """Send the enhanced 'Products to Launch This Week' email to all registered users."""
    import httpx

    html = await _build_enhanced_digest_html(database)
    if not html:
        return {"records_processed": 0, "details": {"status": "skipped", "reason": "No content"}}

    # Get subscribed users
    users = await database.profiles.find(
        {"email_preferences.weekly_digest": {"$ne": False}},
        {"_id": 0, "email": 1, "name": 1},
    ).to_list(5000)

    if not users:
        users = await database.auth_users.find(
            {"email": {"$exists": True}},
            {"_id": 0, "email": 1},
        ).to_list(200)

    resend_key = os.environ.get("RESEND_API_KEY")
    sender = os.environ.get("SENDER_EMAIL", "noreply@trendscout.click")
    if not resend_key:
        return {"records_processed": 0, "details": {"status": "error", "reason": "Resend not configured"}}

    now = datetime.now(timezone.utc)
    subject = f"5 Products to Launch This Week — {now.strftime('%d %b %Y')}"

    sent = 0
    errors = []
    async with httpx.AsyncClient() as client:
        for user in users:
            email = user.get("email")
            if not email:
                continue
            try:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                    json={
                        "from": f"TrendScout <{sender}>",
                        "to": [email],
                        "subject": subject,
                        "html": html,
                    },
                    timeout=10,
                )
                if resp.status_code in (200, 201):
                    sent += 1
                else:
                    errors.append(f"{email}: {resp.status_code}")
            except Exception as e:
                errors.append(f"{email}: {str(e)}")

    logging.info(f"Enhanced weekly digest: sent {sent}/{len(users)}, errors: {len(errors)}")
    return {"records_processed": sent, "details": {"total": len(users), "sent": sent, "errors": len(errors)}}


async def _build_enhanced_digest_html(database):
    """Build the premium 'Products to Launch This Week' email HTML."""
    site_url = os.environ.get("SITE_URL", "https://trendscout.click")

    # Get top 5 products
    products = await database.products.find(
        {"launch_score": {"$gte": 40}},
        {"_id": 0, "id": 1, "product_name": 1, "category": 1, "launch_score": 1,
         "image_url": 1, "estimated_retail_price": 1, "supplier_cost": 1,
         "estimated_margin": 1, "competition_level": 1, "tiktok_views": 1,
         "launch_score_label": 1},
    ).sort("launch_score", -1).limit(5).to_list(5)

    if not products:
        return None

    # Get latest viral predictions
    viral = await database.viral_predictions.find_one(
        {}, {"_id": 0, "predictions": {"$slice": 3}},
        sort=[("generated_at", -1)],
    )
    viral_preds = viral.get("predictions", []) if viral else []

    now = datetime.now(timezone.utc)
    week_label = now.strftime("%d %b %Y")

    # Build product rows
    product_html = ""
    for i, p in enumerate(products, 1):
        score = p.get("launch_score", 0)
        margin = p.get("estimated_margin", 0)
        retail = p.get("estimated_retail_price", 0)
        img = p.get("image_url", "")
        pid = p.get("id", "")
        label = p.get("launch_score_label", "")
        comp = p.get("competition_level", "unknown")

        score_color = "#10b981" if score >= 65 else "#f59e0b" if score >= 45 else "#ef4444"
        badge_bg = "#ecfdf5" if score >= 65 else "#fffbeb" if score >= 45 else "#fef2f2"

        product_html += f"""
        <tr>
          <td style="padding:16px;border-bottom:1px solid #1e1e21;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
              <td width="60" valign="top">
                {"<img src='" + img + "' width='56' height='56' style='border-radius:8px;object-fit:cover;border:1px solid #27272a;' />" if img else "<div style='width:56px;height:56px;border-radius:8px;background:#18181b;'></div>"}
              </td>
              <td style="padding-left:12px;" valign="top">
                <div style="font-weight:700;color:#fafafa;font-size:14px;">{p.get('product_name', '')}</div>
                <div style="font-size:12px;color:#71717a;margin-top:2px;">{p.get('category', '')} &middot; {comp} competition</div>
                <div style="margin-top:6px;">
                  <span style="display:inline-block;background:{badge_bg};color:{score_color};font-weight:700;font-size:12px;padding:2px 8px;border-radius:4px;font-family:monospace;">{score}/100</span>
                  {f"<span style='display:inline-block;color:#71717a;font-size:11px;margin-left:8px;'>Margin: {margin:.0f}%</span>" if margin > 0 else ""}
                  {f"<span style='display:inline-block;color:#71717a;font-size:11px;margin-left:8px;'>Retail: £{retail:.2f}</span>" if retail > 0 else ""}
                </div>
              </td>
              <td width="120" valign="middle" align="right">
                <a href="{site_url}/quick-launch/{pid}?utm_source=email&utm_medium=digest&utm_campaign=weekly_launch" style="display:inline-block;background:#10b981;color:#fff;font-size:12px;font-weight:700;padding:8px 16px;border-radius:6px;text-decoration:none;letter-spacing:0.02em;">Launch</a>
              </td>
            </tr></table>
          </td>
        </tr>"""

    # Viral predictions section
    viral_html = ""
    if viral_preds:
        viral_rows = ""
        for vp in viral_preds[:3]:
            vs = vp.get("viral_score", 0)
            vs_color = "#ef4444" if vs >= 80 else "#f59e0b"
            viral_rows += f"""
            <tr>
              <td style="padding:10px 12px;border-bottom:1px solid #1e1e21;">
                <div style="font-weight:600;color:#fafafa;font-size:13px;">{vp.get('product_name', '')}</div>
                <div style="font-size:11px;color:#71717a;margin-top:2px;">{vp.get('tiktok_format', '')} &middot; {vp.get('urgency', '')} urgency</div>
              </td>
              <td style="padding:10px 8px;border-bottom:1px solid #1e1e21;text-align:center;">
                <span style="font-weight:700;font-family:monospace;color:{vs_color};font-size:16px;">{vs}</span>
              </td>
            </tr>"""

        viral_html = f"""
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:24px;background:#18181b;border-radius:12px;border:1px solid #27272a;">
          <tr><td style="padding:16px 16px 8px;">
            <div style="font-size:12px;font-weight:700;color:#f87171;text-transform:uppercase;letter-spacing:0.1em;">TikTok Viral Predictions</div>
            <div style="font-size:11px;color:#52525b;margin-top:2px;">Products predicted to trend in 48-72h</div>
          </td></tr>
          <tr><td style="padding:0 16px 12px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">{viral_rows}</table>
          </td></tr>
          <tr><td style="padding:0 16px 16px;text-align:center;">
            <a href="{site_url}/tiktok-viral?utm_source=email&utm_medium=digest&utm_campaign=weekly_viral" style="font-size:12px;color:#10b981;font-weight:600;text-decoration:none;">See all predictions &rarr;</a>
          </td></tr>
        </table>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#09090b;font-family:'Inter','Helvetica Neue',Helvetica,Arial,sans-serif;">
  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#09090b;">
    <tr><td align="center" style="padding:32px 16px;">
      <table cellpadding="0" cellspacing="0" border="0" width="560" style="max-width:560px;">
        <!-- Header -->
        <tr><td style="padding-bottom:24px;text-align:center;">
          <div style="font-size:20px;font-weight:800;color:#fafafa;letter-spacing:-0.02em;">TrendScout</div>
          <div style="font-size:12px;color:#52525b;margin-top:4px;">Products to Launch This Week &middot; {week_label}</div>
        </td></tr>

        <!-- Intro -->
        <tr><td style="padding-bottom:20px;">
          <div style="background:#18181b;border:1px solid #27272a;border-radius:12px;padding:20px;">
            <div style="font-size:15px;font-weight:700;color:#fafafa;">This week's top 5 launch candidates</div>
            <div style="font-size:13px;color:#a1a1aa;margin-top:6px;line-height:1.5;">
              AI-scored products with the highest launch potential for UK sellers. Each includes a one-click launch button to generate ad copy, profit projections, and store-ready exports.
            </div>
          </div>
        </td></tr>

        <!-- Products -->
        <tr><td>
          <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#18181b;border-radius:12px;border:1px solid #27272a;">
            <tr><td style="padding:12px 16px;border-bottom:1px solid #27272a;">
              <span style="font-size:11px;font-weight:700;color:#52525b;text-transform:uppercase;letter-spacing:0.1em;">Top Products</span>
            </td></tr>
            {product_html}
          </table>
        </td></tr>

        <!-- Viral Predictions -->
        <tr><td>{viral_html}</td></tr>

        <!-- CTA -->
        <tr><td style="padding:24px 0;text-align:center;">
          <a href="{site_url}/trending-products?utm_source=email&utm_medium=digest&utm_campaign=weekly_launch&utm_content=cta_browse" style="display:inline-block;background:#10b981;color:#fff;padding:12px 32px;border-radius:8px;font-size:14px;font-weight:700;text-decoration:none;letter-spacing:0.02em;">Browse All Trending Products</a>
        </td></tr>

        <!-- Quick links -->
        <tr><td style="padding-bottom:24px;text-align:center;">
          <a href="{site_url}/profit-simulator?utm_source=email&utm_medium=digest" style="font-size:12px;color:#10b981;text-decoration:none;margin:0 10px;">Profit Simulator</a>
          <a href="{site_url}/competitor-spy?utm_source=email&utm_medium=digest" style="font-size:12px;color:#10b981;text-decoration:none;margin:0 10px;">Competitor Spy</a>
          <a href="{site_url}/tiktok-viral?utm_source=email&utm_medium=digest" style="font-size:12px;color:#10b981;text-decoration:none;margin:0 10px;">TikTok Viral</a>
        </td></tr>

        <!-- Footer -->
        <tr><td style="border-top:1px solid #1e1e21;padding:16px 0;text-align:center;">
          <div style="font-size:11px;color:#3f3f46;">You're receiving this because you signed up at TrendScout.</div>
          <div style="font-size:11px;color:#3f3f46;margin-top:4px;">
            <a href="{site_url}/settings/notifications?utm_source=email" style="color:#52525b;text-decoration:underline;">Manage preferences</a> &middot;
            <a href="{site_url}/unsubscribe?utm_source=email" style="color:#52525b;text-decoration:underline;">Unsubscribe</a>
          </div>
          <div style="font-size:10px;color:#27272a;margin-top:8px;">TrendScout &middot; United Kingdom</div>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>"""

    return html


routers = [automation_router]
