"""
TrendScout API - Slim Entrypoint
All route handlers are in /routes/, shared code in /common/.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os
import logging
import sentry_sdk
from pathlib import Path

# Configure logging EARLY so all startup messages are captured
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("=== TrendScout API starting ===")
logger.info(f"MONGO_URL set: {'yes' if os.environ.get('MONGO_URL') else 'NO'}")
logger.info(f"DB_NAME set: {'yes' if os.environ.get('DB_NAME') else 'NO'}")
logger.info(f"SITE_URL: {os.environ.get('SITE_URL', 'not set')}")

# Load environment BEFORE importing anything else
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Sentry — error monitoring & performance
if os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        traces_sample_rate=0.3,
        profiles_sample_rate=0.1,
        environment=os.environ.get("ENV", "production"),
    )

# Rate limiter
from common.limiter import limiter

# Create the main app
app = FastAPI(title="TrendScout API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Import all route modules  (each exports a list of routers)
from routes.health import routers as health_routers
from routes.auth_routes import routers as auth_routers
from routes.user import routers as user_routers
from routes.stripe_routes import routers as stripe_routers
from routes.products import routers as product_routers
from routes.automation import routers as automation_routers
from routes.jobs import routers as jobs_routers
from routes.viral import routers as viral_routers
from routes.public import routers as public_routers
from routes.seo import routers as seo_routers
from routes.data_quality import routers as data_quality_routers
from routes.intelligence import routers as intelligence_routers
from routes.dashboard import routers as dashboard_routers
from routes.reports import routers as reports_routers
from routes.email import routers as email_routers
from routes.notifications import routers as notifications_routers
from routes.ingestion import routers as ingestion_routers
from routes.stores import routers as stores_routers
from routes.shopify import routers as shopify_routers
from routes.suppliers import routers as suppliers_routers
from routes.ads import routers as ads_routers
from routes.radar import routers as radar_routers
from routes.optimizer import routers as optimizer_routers
from routes.system_health import routers as system_health_routers
from routes.tools import routers as tools_routers
from routes.workspace import routers as workspace_routers
from routes.blog import routers as blog_routers
from routes.admin import routers as admin_routers
from routes.images import routers as images_routers
from routes.connections import routers as connections_routers
from routes.shopify_oauth import routers as shopify_oauth_routers
from routes.shopify_app import routers as shopify_app_routers
from routes.shopify_webhooks import routers as shopify_webhook_routers
from routes.winners import routers as winners_routers
from routes.api_access import routers as api_access_routers
from routes.admin_images import routers as admin_images_routers
from routes.cj_dropshipping import routers as cj_routers
from routes.trial import routers as trial_routers
from routes.leads import routers as leads_routers
from routes.accuracy import routers as accuracy_routers
from routes.webhooks import routers as webhook_routers
from routes.ws import routers as ws_routers
from routes.oauth import routers as oauth_routers
from routes.admin_oauth import routers as admin_oauth_routers
from routes.platform_sync import routers as platform_sync_routers
from routes.compare import routers as compare_routers
from routes.product_alerts import routers as product_alerts_routers

# Include all routers
all_router_groups = [
    health_routers, auth_routers, user_routers, stripe_routers,
    product_routers, automation_routers, jobs_routers, viral_routers,
    public_routers, seo_routers, data_quality_routers, intelligence_routers,
    dashboard_routers, reports_routers, email_routers, notifications_routers,
    ingestion_routers, stores_routers, shopify_routers, suppliers_routers,
    ads_routers, radar_routers, optimizer_routers, system_health_routers,
    tools_routers, workspace_routers, blog_routers, admin_routers,
    images_routers, connections_routers, shopify_oauth_routers,
    shopify_app_routers,
    shopify_webhook_routers,
    winners_routers,
    api_access_routers,
    admin_images_routers,
    cj_routers,
    trial_routers,
    leads_routers,
    accuracy_routers,
    webhook_routers,
    ws_routers,
    oauth_routers,
    admin_oauth_routers,
    platform_sync_routers,
    compare_routers,
    product_alerts_routers,
]

for group in all_router_groups:
    for router in group:
        app.include_router(router)

# Middleware (order matters - last added = first executed)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*", "x-csrf-token"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-RateLimit-Plan"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Security headers
from middleware.security_headers import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# Structured request logging + X-Request-ID + X-App-Version
from middleware.request_logging import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)

# CSRF protection (only for cookie-authenticated state-changing routes)
from middleware.csrf import CSRFMiddleware
app.add_middleware(CSRFMiddleware)

# Per-user, per-plan rate limiting
from middleware.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)


# Global exception handler — standardised error format
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content={"success": False, "error": detail})
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": f"HTTP_{exc.status_code}", "message": str(detail)}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )

# Bare /health for K8s readiness probes (no /api prefix, no DB dependency)
@app.get("/health")
async def k8s_health():
    return {"status": "ok"}

# Serve product images from local storage
IMAGES_DIR = ROOT_DIR / "static" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/api/images", StaticFiles(directory=str(IMAGES_DIR)), name="product-images")

# Serve React frontend static files in production
FRONTEND_BUILD_DIR = ROOT_DIR.parent / "frontend" / "build"
if FRONTEND_BUILD_DIR.exists() and (FRONTEND_BUILD_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        file_path = FRONTEND_BUILD_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_BUILD_DIR / "index.html"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_db():
    """Initialize database collections, indexes, and background services."""
    from common.database import db
    import asyncio

    # Create indexes in background — not needed before first request
    async def _create_indexes():
        try:
            await db.products.create_index("id", unique=True)
            await db.products.create_index("category")
            await db.products.create_index("trend_score")
            await db.products.create_index("trend_stage")
            await db.products.create_index("source")
            await db.products.create_index("fingerprint")
            await db.products.create_index("source_id")
            await db.products.create_index("market_score")
            await db.products.create_index("market_label")
            await db.trend_alerts.create_index("id", unique=True)
            await db.trend_alerts.create_index("product_id")
            await db.trend_alerts.create_index("created_at")
            await db.automation_logs.create_index("id", unique=True)
            await db.automation_logs.create_index("started_at")
            await db.automation_logs.create_index("job_type")
            await db.subscriptions.create_index("user_id", unique=True)
            await db.profiles.create_index("id", unique=True)
            await db.stores.create_index("id", unique=True)
            await db.stores.create_index("owner_id")
            await db.stores.create_index("status")
            await db.store_products.create_index("id", unique=True)
            await db.store_products.create_index("store_id")
            await db.store_products.create_index("original_product_id")
            await db.alerts.create_index("id", unique=True)
            await db.alerts.create_index("product_id")
            await db.alerts.create_index([("created_at", -1)])
            await db.reports.create_index("metadata.id", unique=True)
            await db.reports.create_index("metadata.slug", unique=True)
            await db.reports.create_index("metadata.report_type")
            await db.reports.create_index("metadata.is_latest")
            await db.reports.create_index([("metadata.generated_at", -1)])
            await db.scrape_cache.create_index("key", unique=True)
            await db.scrape_cache.create_index("cached_at")
            await db.source_health.create_index("source_name", unique=True)
            await db.ingestion_runs.create_index([("started_at", -1)])
            await db.tiktok_hashtags.create_index("hashtag", unique=True)
            logger.info("Database indexes created")
        except Exception as e:
            logger.error(f"Index creation failed (non-fatal): {e}")

    asyncio.create_task(_create_indexes())

    # Auto-seed products and accounts if the database is empty (non-blocking)
    import bcrypt
    import uuid
    from datetime import datetime, timezone, timedelta

    async def _auto_seed():
        """Idempotent seed — only creates what's missing, never deletes existing data."""
        try:
            product_count = await db.products.count_documents({})
            user_count = await db.auth_users.count_documents({})

            if product_count > 0 and user_count > 0:
                logger.info(f"Database already seeded (products={product_count}, users={user_count})")
                return

            # Seed users if missing (always check, never delete)
            if user_count == 0:
                logger.info("No users found — creating default accounts...")
                accounts = [
                    {"email": "reviewer@trendscout.click", "password": "ShopifyReview2026!", "full_name": "Admin", "role": "admin", "plan": "elite"},
                    {"email": "demo@trendscout.click", "password": "DemoReview2026!", "full_name": "Demo User", "role": "authenticated", "plan": "elite"},
                ]
                for acct in accounts:
                    existing = await db.auth_users.find_one({"email": acct["email"]})
                    if existing:
                        logger.info(f"  User {acct['email']} already exists")
                        continue
                    user_id = str(uuid.uuid4())
                    password_hash = bcrypt.hashpw(acct["password"].encode(), bcrypt.gensalt()).decode()
                    await db.auth_users.insert_one({
                        "id": user_id,
                        "email": acct["email"],
                        "password_hash": password_hash,
                        "full_name": acct["full_name"],
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    })
                    is_admin = acct["role"] == "admin"
                    await db.profiles.update_one(
                        {"email": acct["email"]},
                        {"$set": {
                            "id": user_id, "email": acct["email"], "name": acct["full_name"],
                            "is_admin": is_admin, "role": acct["role"], "plan": acct["plan"],
                            "subscription_plan": acct["plan"],
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }},
                        upsert=True,
                    )
                    await db.subscriptions.update_one(
                        {"user_id": user_id},
                        {"$set": {
                            "id": f"sub-{user_id[:8]}", "user_id": user_id,
                            "plan_name": acct["plan"], "status": "active",
                            "current_period_start": datetime.now(timezone.utc).isoformat(),
                            "current_period_end": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                            "cancel_at_period_end": False,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }},
                        upsert=True,
                    )
                    logger.info(f"  Created user: {acct['email']} ({acct['role']})")

            # Seed products if missing (import full seed script for product data)
            if product_count == 0:
                logger.info("No products found — running full product seed...")
                try:
                    from seed_database import seed_database
                    result = await seed_database()
                    count = result.get("products_processed", 0) if isinstance(result, dict) else 0
                    logger.info(f"Product seed complete: {count} products")
                except Exception as e:
                    logger.error(f"Product seed failed: {e}")
            else:
                logger.info(f"Products already exist ({product_count}), skipping product seed")

            final_products = await db.products.count_documents({})
            final_users = await db.auth_users.count_documents({})
            logger.info(f"Auto-seed finished: products={final_products}, users={final_users}")

        except Exception as e:
            logger.error(f"Auto-seed failed (non-fatal): {e}", exc_info=True)

    asyncio.create_task(_auto_seed())

    # Load OAuth credentials from DB into memory cache (non-blocking)
    async def _load_oauth():
        try:
            from services.oauth_service import load_db_credentials
            await load_db_credentials()
        except Exception as e:
            logger.warning(f"Could not load OAuth credentials from DB: {e}")

    asyncio.create_task(_load_oauth())

    # Non-blocking: sitemap + scheduler + worker
    async def _deferred_startup():
        try:
            from routes.seo import regenerate_sitemap
            await regenerate_sitemap()
        except Exception as e:
            logger.error(f"Sitemap generation failed (non-fatal): {e}")

        try:
            from services.jobs.worker import WorkerManager
            from services.jobs.scheduler import SchedulerManager
            worker_manager = WorkerManager.get_instance()
            worker_manager.initialize(db)
            await worker_manager.start()
            scheduler_manager = SchedulerManager.get_instance()
            scheduler_manager.initialize(db)
            await scheduler_manager.start()
            logger.info("Background worker and scheduler started")
        except Exception as e:
            logger.error(f"Failed to start background services: {e}")

    asyncio.create_task(_deferred_startup())
    logger.info("Startup complete — health endpoint ready")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Cleanup on shutdown."""
    from common.database import client
    try:
        from services.jobs.worker import WorkerManager
        from services.jobs.scheduler import SchedulerManager
        scheduler_manager = SchedulerManager.get_instance()
        await scheduler_manager.stop()
        worker_manager = WorkerManager.get_instance()
        await worker_manager.stop()
        logger.info("Background services stopped")
    except Exception as e:
        logger.error(f"Error stopping background services: {e}")
    client.close()
