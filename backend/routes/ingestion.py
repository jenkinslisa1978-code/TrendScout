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

from services.data_ingestion.tiktok_import import TikTokImporter
from services.data_ingestion.amazon_import import AmazonImporter
from services.data_ingestion.supplier_import import SupplierImporter

ingestion_router = APIRouter(prefix="/api/ingestion")

@ingestion_router.get("/sources")
async def get_data_sources():
    """Get available data sources and their status"""
    tiktok = TikTokImporter(db)
    amazon = AmazonImporter(db)
    supplier = SupplierImporter(db)
    
    return {
        "sources": [
            {
                "id": "tiktok",
                "name": "TikTok Creative Center",
                "description": "Trending products from TikTok viral content",
                "config": tiktok.get_source_config(),
                "status": "active",
            },
            {
                "id": "amazon",
                "name": "Amazon Movers & Shakers",
                "description": "Fast-rising products from Amazon rankings",
                "config": amazon.get_source_config(),
                "status": "active",
            },
            {
                "id": "supplier",
                "name": "Supplier Feeds",
                "description": "Products from AliExpress, CJ Dropshipping, etc.",
                "config": supplier.get_source_config(),
                "status": "active",
            },
        ]
    }

@ingestion_router.post("/tiktok")
async def run_tiktok_import(request: ImportRequest):
    """Import trending products from TikTok"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "tiktok_import",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "tiktok",
    }
    await db.automation_logs.insert_one(log)
    await notify_job_started("tiktok_import", source="tiktok")
    
    try:
        importer = TikTokImporter(db)
        result = await importer.import_products(
            category=request.category,
            limit=request.limit
        )
        
        if result.get('products'):
            for p in result['products']:
                p.pop('_id', None)
            await notify_job_progress("tiktok_import", len(result['products']), request.limit, source="tiktok", detail="Running automation on imported products")
            automation_result = await run_automation_on_products(result['products'])
            result['automation'] = automation_result
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": result.get('inserted', 0) + result.get('updated', 0),
                "alerts_generated": result.get('automation', {}).get('alerts_generated', 0),
            }}
        )
        
        result.pop('products', None)
        await notify_job_completed("tiktok_import", source="tiktok", result={"inserted": result.get('inserted', 0), "updated": result.get('updated', 0)})
        return result
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        await notify_job_failed("tiktok_import", source="tiktok", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@ingestion_router.post("/amazon")
async def run_amazon_import(request: ImportRequest):
    """Import trending products from Amazon Movers & Shakers"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "amazon_import",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "amazon",
    }
    await db.automation_logs.insert_one(log)
    await notify_job_started("amazon_import", source="amazon")
    
    try:
        importer = AmazonImporter(db)
        result = await importer.import_products(
            category=request.category,
            limit=request.limit
        )
        
        if result.get('products'):
            for p in result['products']:
                p.pop('_id', None)
            await notify_job_progress("amazon_import", len(result['products']), request.limit, source="amazon", detail="Running automation on imported products")
            automation_result = await run_automation_on_products(result['products'])
            result['automation'] = automation_result
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": result.get('inserted', 0) + result.get('updated', 0),
                "alerts_generated": result.get('automation', {}).get('alerts_generated', 0),
            }}
        )
        
        result.pop('products', None)
        await notify_job_completed("amazon_import", source="amazon", result={"inserted": result.get('inserted', 0), "updated": result.get('updated', 0)})
        return result
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        await notify_job_failed("amazon_import", source="amazon", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@ingestion_router.post("/supplier")
async def run_supplier_import(request: ImportRequest):
    """Import products from supplier feeds"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "supplier_import",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "supplier",
    }
    await db.automation_logs.insert_one(log)
    await notify_job_started("supplier_import", source="supplier")
    
    try:
        importer = SupplierImporter(db)
        result = await importer.import_products(
            category=request.category,
            limit=request.limit
        )
        
        if result.get('products'):
            for p in result['products']:
                p.pop('_id', None)
            await notify_job_progress("supplier_import", len(result['products']), request.limit, source="supplier", detail="Running automation")
            automation_result = await run_automation_on_products(result['products'])
            result['automation'] = automation_result
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": result.get('inserted', 0) + result.get('updated', 0),
                "alerts_generated": result.get('automation', {}).get('alerts_generated', 0),
            }}
        )
        
        result.pop('products', None)
        await notify_job_completed("supplier_import", source="supplier", result={"inserted": result.get('inserted', 0), "updated": result.get('updated', 0)})
        return result
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        await notify_job_failed("supplier_import", source="supplier", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@ingestion_router.post("/supplier/csv")
async def import_from_csv(request: CSVImportRequest):
    """Import products from CSV content"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "product_import",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "csv_upload",
    }
    await db.automation_logs.insert_one(log)
    
    try:
        importer = SupplierImporter(db)
        result = await importer.import_from_csv(request.csv_content)
        
        # Run automation on imported products
        if result.get('products'):
            automation_result = await run_automation_on_products(result['products'])
            result['automation'] = automation_result
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": result.get('inserted', 0) + result.get('updated', 0),
                "alerts_generated": result.get('automation', {}).get('alerts_generated', 0),
            }}
        )
        
        return result
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))

@ingestion_router.post("/full-sync")
async def run_full_data_sync(request: ImportRequest):
    """Run full data sync from all sources"""
    log_id = str(uuid.uuid4())
    log = {
        "id": log_id,
        "job_type": "full_data_sync",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "import_source": "all",
    }
    await db.automation_logs.insert_one(log)
    await notify_job_started("full_data_sync", source="all")
    
    results = {
        "tiktok": None,
        "amazon": None,
        "supplier": None,
        "total_imported": 0,
        "total_alerts": 0,
    }
    
    try:
        # Import from TikTok
        await notify_job_progress("full_data_sync", 1, 4, source="tiktok", detail="Importing from TikTok")
        tiktok_importer = TikTokImporter(db)
        results["tiktok"] = await tiktok_importer.import_products(limit=request.limit)
        
        # Import from Amazon
        await notify_job_progress("full_data_sync", 2, 4, source="amazon", detail="Importing from Amazon")
        amazon_importer = AmazonImporter(db)
        results["amazon"] = await amazon_importer.import_products(limit=request.limit)
        
        # Import from Suppliers
        await notify_job_progress("full_data_sync", 3, 4, source="supplier", detail="Importing from Suppliers")
        supplier_importer = SupplierImporter(db)
        results["supplier"] = await supplier_importer.import_products(limit=request.limit)
        
        # Collect all products for automation
        all_products = []
        for source in ["tiktok", "amazon", "supplier"]:
            if results[source] and results[source].get("products"):
                all_products.extend(results[source]["products"])
        
        # Run automation on all imported products
        await notify_job_progress("full_data_sync", 4, 4, detail=f"Running automation on {len(all_products)} products")
        if all_products:
            automation_result = await run_automation_on_products(all_products)
            results["automation"] = automation_result
            results["total_alerts"] = automation_result.get("alerts_generated", 0)
        
        # Calculate totals
        for source in ["tiktok", "amazon", "supplier"]:
            if results[source]:
                results["total_imported"] += results[source].get("inserted", 0) + results[source].get("updated", 0)
        
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "products_processed": results["total_imported"],
                "alerts_generated": results["total_alerts"],
                "metadata": {
                    "tiktok": results["tiktok"].get("fetched", 0) if results["tiktok"] else 0,
                    "amazon": results["amazon"].get("fetched", 0) if results["amazon"] else 0,
                    "supplier": results["supplier"].get("fetched", 0) if results["supplier"] else 0,
                },
            }}
        )
        
        await notify_job_completed("full_data_sync", source="all", result={
            "total_imported": results["total_imported"],
            "total_alerts": results["total_alerts"],
        })
        
        return {
            "success": True,
            "total_imported": results["total_imported"],
            "total_alerts": results["total_alerts"],
            "sources": {
                "tiktok": {"imported": results["tiktok"].get("inserted", 0) + results["tiktok"].get("updated", 0)} if results["tiktok"] else None,
                "amazon": {"imported": results["amazon"].get("inserted", 0) + results["amazon"].get("updated", 0)} if results["amazon"] else None,
                "supplier": {"imported": results["supplier"].get("inserted", 0) + results["supplier"].get("updated", 0)} if results["supplier"] else None,
            },
        }
        
    except Exception as e:
        await db.automation_logs.update_one(
            {"id": log_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        await notify_job_failed("full_data_sync", source="all", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def run_automation_on_products(products: List[Dict]) -> Dict:
    """Helper to run full automation pipeline on products"""
    alerts_generated = 0
    
    for product in products:
        # Remove _id if present (MongoDB adds it)
        product.pop('_id', None)
        
        # Run full automation
        result = run_full_automation(product)
        processed = result['product']
        
        # Remove _id from processed product too
        processed.pop('_id', None)
        
        # Update product in database
        await db.products.update_one(
            {"id": processed['id']},
            {"$set": processed},
            upsert=True
        )
        
        # Save alert if generated
        if result['alert']:
            result['alert'].pop('_id', None)
            await db.trend_alerts.insert_one(result['alert'])
            alerts_generated += 1
    
    return {
        "products_processed": len(products),
        "alerts_generated": alerts_generated,
    }


# =====================
# ROUTES - Real Data Scraping
# =====================

from services.scrapers.orchestrator import DataIngestionOrchestrator


@ingestion_router.post("/scrape/full")
async def run_full_scrape(
    sources: Optional[List[str]] = None,
    max_products: int = 30,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Run full data scraping from real sources.
    
    Sources: aliexpress, tiktok_trends, amazon_movers, cj_dropshipping
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    orchestrator = DataIngestionOrchestrator(db)
    
    result = await orchestrator.run_full_ingestion(
        sources=sources,
        max_products_per_source=max_products
    )
    
    return result


@ingestion_router.post("/scrape/google-trends")
async def run_google_trends_enrichment(
    max_products: int = 20,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Enrich products with Google Trends velocity data."""
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.scrapers.google_trends_scraper import GoogleTrendsScraper
    scraper = GoogleTrendsScraper(db)
    result = await scraper.enrich_products(max_products=max_products)
    return result


@ingestion_router.post("/scores/recompute")
async def recompute_all_scores(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Recompute all product scores using transparent scoring engine."""
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from services.scoring import ScoringEngine
    engine = ScoringEngine(db)
    stats = await engine.batch_update_scores(limit=500)
    return stats


@ingestion_router.post("/scrape/{source_name}")
async def run_source_scrape(
    source_name: str,
    max_products: int = 30,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Run scraping for a specific source.
    
    Valid sources: aliexpress, tiktok_trends, amazon_movers, cj_dropshipping
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    valid_sources = ['aliexpress', 'tiktok_trends', 'amazon_movers', 'cj_dropshipping']
    if source_name not in valid_sources:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid source. Valid: {valid_sources}"
        )
    
    orchestrator = DataIngestionOrchestrator(db)
    result = await orchestrator.run_source_ingestion(source_name, max_products)
    
    return result.to_dict()


@ingestion_router.get("/scrape/health")
async def get_scraper_health(source_name: Optional[str] = None):
    """Get health status of scraping sources"""
    orchestrator = DataIngestionOrchestrator(db)
    return await orchestrator.get_source_health(source_name)


@ingestion_router.get("/scrape/history")
async def get_scrape_history(limit: int = 10):
    """Get recent scraping/ingestion runs"""
    orchestrator = DataIngestionOrchestrator(db)
    return await orchestrator.get_ingestion_history(limit)


@ingestion_router.get("/scrape/quality")
async def get_data_quality():
    """Get data quality report (real vs simulated breakdown)"""
    orchestrator = DataIngestionOrchestrator(db)
    return await orchestrator.get_data_quality_report()



# =====================
# ROUTES - Product Identity & Deduplication
# =====================

from services.product_identity import ProductIdentityService


@ingestion_router.post("/dedup/run")
async def run_deduplication(
    dry_run: bool = False,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Run product deduplication process.
    
    Args:
        dry_run: If True, only report duplicates without merging
    """
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    service = ProductIdentityService(db)
    result = await service.run_deduplication(dry_run=dry_run)
    
    return {
        "success": result.success,
        "started_at": result.started_at,
        "completed_at": result.completed_at,
        "duration_seconds": result.duration_seconds,
        "total_products_processed": result.total_products_processed,
        "duplicate_groups_found": result.duplicate_groups_found,
        "products_merged": result.products_merged,
        "canonical_products_created": result.canonical_products_created,
        "canonical_products_updated": result.canonical_products_updated,
        "errors": result.errors
    }


@ingestion_router.get("/dedup/stats")
async def get_dedup_stats():
    """Get statistics about canonical products"""
    service = ProductIdentityService(db)
    return await service.get_canonical_stats()


@ingestion_router.get("/dedup/history")
async def get_dedup_history(limit: int = 10):
    """Get deduplication run history"""
    service = ProductIdentityService(db)
    return await service.get_dedup_history(limit)


@ingestion_router.get("/dedup/find/{product_id}")
async def find_product_duplicates(product_id: str):
    """Find potential duplicates for a specific product"""
    service = ProductIdentityService(db)
    duplicates = await service.find_duplicates_for_product(product_id)
    
    return {
        "product_id": product_id,
        "potential_duplicates": duplicates,
        "count": len(duplicates)
    }


# =====================
# ROUTES - Stores
# =====================

from services.store_service import (
    StoreGenerator, 
    create_store_document, 
    create_store_product_document,
    can_create_store,
    get_store_limit,
    STORE_LIMITS,
    export_store_for_shopify,
    export_store_as_shopify_csv,
    export_store_for_woocommerce,
)



routers = [ingestion_router]
