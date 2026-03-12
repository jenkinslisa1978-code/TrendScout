"""
System Health Dashboard Service

Aggregates health checks across all platform components:
  - Data ingestion & scrapers
  - API integrations (TikTok, AliExpress, Meta, CJ, Zendrop)
  - Core systems (scoring, opportunity feed, ad blueprint, store pipeline)
  - Infrastructure (MongoDB, Stripe, scheduled jobs)
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def _status(ok: bool, warn: bool = False) -> str:
    if not ok:
        return "error"
    if warn:
        return "warning"
    return "healthy"


def _age_hours(iso_str) -> float:
    """Hours since an ISO timestamp."""
    if not iso_str:
        return 999
    try:
        if isinstance(iso_str, str):
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        else:
            dt = iso_str
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except Exception:
        return 999


async def check_data_ingestion(db) -> List[Dict[str, Any]]:
    """Check data ingestion pipelines."""
    checks = []

    # Opportunity feed
    feed_count = await db.opportunity_feed.count_documents({})
    latest_feed = await db.opportunity_feed.find_one(
        {}, {"_id": 0, "created_at": 1}, sort=[("created_at", -1)]
    )
    latest_ts = latest_feed.get("created_at") if latest_feed else None
    age = _age_hours(latest_ts)
    checks.append({
        "name": "Opportunity Feed",
        "category": "data_ingestion",
        "status": _status(feed_count > 0, age > 12),
        "last_success": latest_ts,
        "message": f"{feed_count} events, latest {age:.1f}h ago" if latest_ts else "No events yet",
        "uptime": 100 if feed_count > 0 else 0,
    })

    # Scraper activity — check automation_logs
    scrapers = [
        ("Amazon Scraper", "scrape_real_data"),
        ("Google Trends Enrichment", "enrich_google_trends"),
        ("Score Recomputation", "recompute_scores"),
    ]
    for label, job_type in scrapers:
        last_job = await db.jobs.find_one(
            {"job_type": job_type}, {"_id": 0}, sort=[("created_at", -1)]
        )
        if last_job:
            completed = last_job.get("completed_at") or last_job.get("created_at")
            err = last_job.get("error")
            job_status = last_job.get("status", "unknown")
            age = _age_hours(completed)
            checks.append({
                "name": label,
                "category": "data_ingestion",
                "status": _status(job_status == "completed", age > 8),
                "last_success": completed if job_status == "completed" else None,
                "message": f"Last run: {job_status}" + (f" — {err}" if err else ""),
                "uptime": 100 if job_status == "completed" else 50,
            })
        else:
            checks.append({
                "name": label,
                "category": "data_ingestion",
                "status": "warning",
                "last_success": None,
                "message": "No job history found",
                "uptime": 0,
            })

    # Last successful ingestion timestamp (any product updated)
    newest_product = await db.products.find_one(
        {}, {"_id": 0, "last_updated": 1, "updated_at": 1}, sort=[("last_updated", -1)]
    )
    ts = None
    if newest_product:
        ts = newest_product.get("last_updated") or newest_product.get("updated_at")
    age = _age_hours(ts)
    checks.append({
        "name": "Product Data Freshness",
        "category": "data_ingestion",
        "status": _status(ts is not None, age > 24),
        "last_success": ts,
        "message": f"Freshest product updated {age:.1f}h ago" if ts else "No products",
        "uptime": max(0, 100 - int(age)),
    })

    return checks


async def check_api_integrations(db) -> List[Dict[str, Any]]:
    """Check external API integration statuses."""
    integrations = [
        ("TikTok API", "TIKTOK_API_KEY", "tiktok_trends"),
        ("AliExpress Data Source", "ALIEXPRESS_API_KEY", "aliexpress_supplier"),
        ("Meta Ad Library", "META_AD_LIBRARY_KEY", None),
        ("CJ Dropshipping", "CJ_API_KEY", "cj_dropshipping"),
        ("Zendrop", "ZENDROP_API_KEY", None),
    ]
    checks = []
    for label, env_key, source_name in integrations:
        key_present = bool(os.environ.get(env_key))
        # Check if we have data from this source
        data_count = 0
        last_ts = None
        if source_name:
            data_count = await db.products.count_documents({"data_source": source_name})
            latest = await db.products.find_one(
                {"data_source": source_name},
                {"_id": 0, "last_updated": 1},
                sort=[("last_updated", -1)],
            )
            if latest:
                last_ts = latest.get("last_updated")

        if key_present:
            status = "healthy"
            msg = f"API key configured, {data_count} products"
        elif data_count > 0:
            status = "warning"
            msg = f"No API key — using simulated data ({data_count} products)"
        else:
            status = "error"
            msg = f"No API key ({env_key}) — not configured"

        checks.append({
            "name": label,
            "category": "api_integrations",
            "status": status,
            "last_success": last_ts,
            "message": msg,
            "uptime": 100 if key_present else (50 if data_count > 0 else 0),
        })
    return checks


async def check_core_systems(db) -> List[Dict[str, Any]]:
    """Check core platform systems."""
    checks = []

    # Product scoring engine
    scored = await db.products.count_documents({"trend_score": {"$exists": True, "$gt": 0}})
    total = await db.products.count_documents({})
    pct = round(scored / max(total, 1) * 100)
    checks.append({
        "name": "Product Scoring Engine",
        "category": "core_systems",
        "status": _status(scored > 0, pct < 80),
        "last_success": None,
        "message": f"{scored}/{total} products scored ({pct}%)",
        "uptime": pct,
    })

    # Opportunity feed generation
    recent_events = await db.opportunity_feed.count_documents({
        "created_at": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()}
    })
    checks.append({
        "name": "Opportunity Feed Generation",
        "category": "core_systems",
        "status": _status(recent_events > 0, recent_events < 5),
        "last_success": None,
        "message": f"{recent_events} events in last 24h",
        "uptime": min(100, recent_events * 10),
    })

    # Ad blueprint generator (check ad_tests collection)
    ad_tests_count = await db.ad_tests.count_documents({})
    checks.append({
        "name": "Ad Blueprint Generator",
        "category": "core_systems",
        "status": _status(True),
        "last_success": None,
        "message": f"{ad_tests_count} ad tests created",
        "uptime": 100,
    })

    # Store launch pipeline
    stores_count = await db.stores.count_documents({})
    checks.append({
        "name": "Store Launch Pipeline",
        "category": "core_systems",
        "status": _status(True),
        "last_success": None,
        "message": f"{stores_count} stores launched",
        "uptime": 100,
    })

    return checks


async def check_infrastructure(db, scheduler_manager=None) -> List[Dict[str, Any]]:
    """Check infrastructure components."""
    checks = []

    # MongoDB connectivity
    try:
        await db.command("ping")
        colls = await db.list_collection_names()
        checks.append({
            "name": "MongoDB",
            "category": "infrastructure",
            "status": "healthy",
            "last_success": datetime.now(timezone.utc).isoformat(),
            "message": f"Connected, {len(colls)} collections",
            "uptime": 100,
        })
    except Exception as e:
        checks.append({
            "name": "MongoDB",
            "category": "infrastructure",
            "status": "error",
            "last_success": None,
            "message": str(e)[:120],
            "uptime": 0,
        })

    # Stripe webhook health
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    # Check recent webhook events
    recent_webhooks = await db.stripe_events.count_documents({}) if "stripe_events" in await db.list_collection_names() else -1

    if stripe_key and webhook_secret:
        status = "healthy"
        msg = "Keys configured" + (f", {recent_webhooks} webhook events logged" if recent_webhooks >= 0 else "")
    elif stripe_key:
        status = "warning"
        msg = "Secret key set but no webhook secret"
    else:
        status = "error"
        msg = "Stripe not configured"
    checks.append({
        "name": "Stripe Payments",
        "category": "infrastructure",
        "status": status,
        "last_success": None,
        "message": msg,
        "uptime": 100 if stripe_key else 0,
    })

    # Scheduled jobs
    if scheduler_manager:
        sched_status = scheduler_manager.get_status()
        running = sched_status.get("running", False)
        job_count = sched_status.get("scheduled_jobs", 0)
        jobs_list = sched_status.get("jobs", [])

        # Find next upcoming run
        next_run = None
        for j in jobs_list:
            nr = j.get("next_run")
            if nr and (not next_run or nr < next_run):
                next_run = nr

        checks.append({
            "name": "Job Scheduler",
            "category": "infrastructure",
            "status": _status(running, job_count < 5),
            "last_success": None,
            "message": f"{'Running' if running else 'Stopped'}, {job_count} jobs" + (f", next at {next_run[:16]}" if next_run else ""),
            "uptime": 100 if running else 0,
            "extra": {"jobs": jobs_list[:10]} if jobs_list else {},
        })
    else:
        checks.append({
            "name": "Job Scheduler",
            "category": "infrastructure",
            "status": "warning",
            "last_success": None,
            "message": "Scheduler manager not available",
            "uptime": 0,
        })

    # Job queue worker (check recent job completions)
    recent_completed = await db.jobs.count_documents({
        "status": "completed",
        "completed_at": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()},
    })
    recent_failed = await db.jobs.count_documents({
        "status": "failed",
        "completed_at": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()},
    })
    checks.append({
        "name": "Job Queue Worker",
        "category": "infrastructure",
        "status": _status(True, recent_failed > 0),
        "last_success": None,
        "message": f"Last hour: {recent_completed} completed, {recent_failed} failed",
        "uptime": round(recent_completed / max(recent_completed + recent_failed, 1) * 100),
    })

    return checks


async def get_full_system_health(db, scheduler_manager=None) -> Dict[str, Any]:
    """Aggregate all health checks into a single response."""
    all_checks = []
    all_checks.extend(await check_data_ingestion(db))
    all_checks.extend(await check_api_integrations(db))
    all_checks.extend(await check_core_systems(db))
    all_checks.extend(await check_infrastructure(db, scheduler_manager))

    # Compute overall status
    statuses = [c["status"] for c in all_checks]
    errors = statuses.count("error")
    warnings = statuses.count("warning")
    healthy = statuses.count("healthy")

    if errors > 0:
        overall = "error"
    elif warnings > 2:
        overall = "warning"
    else:
        overall = "healthy"

    avg_uptime = round(sum(c.get("uptime", 0) for c in all_checks) / max(len(all_checks), 1))

    # Group by category
    grouped = {}
    for c in all_checks:
        cat = c.get("category", "other")
        grouped.setdefault(cat, []).append(c)

    return {
        "overall_status": overall,
        "total_checks": len(all_checks),
        "healthy": healthy,
        "warnings": warnings,
        "errors": errors,
        "avg_uptime": avg_uptime,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "categories": grouped,
        "checks": all_checks,
    }
