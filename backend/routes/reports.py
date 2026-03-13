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

from services.reports import WeeklyWinningProductsReport, MonthlyMarketTrendsReport
from services.reports.report_generator import ReportType, ReportAccessLevel

reports_router = APIRouter(prefix="/api/reports")

def check_report_access(user_plan: str, required_level: str) -> bool:
    plan_levels = {"free": 0, "starter": 1, "pro": 2, "elite": 3}
    access_levels = {"free": 0, "starter": 1, "pro": 2, "elite": 3}
    return plan_levels.get(user_plan, 0) >= access_levels.get(required_level, 0)


def filter_report_by_access(report: dict, user_plan: str) -> dict:
    if not report:
        return report
    filtered = dict(report)
    sections = filtered.get("sections", {})
    
    # Handle both list and dict formats for sections
    if isinstance(sections, list):
        # Sections is a list - filter by access_level
        filtered_sections = []
        for section in sections:
            section_access = section.get("access_level", "free") if isinstance(section, dict) else "free"
            if check_report_access(user_plan, section_access):
                filtered_sections.append(section)
        filtered["sections"] = filtered_sections
    elif isinstance(sections, dict):
        # Sections is a dict - filter by access_level
        filtered_sections = {}
        for key, section in sections.items():
            section_access = section.get("access_level", "free") if isinstance(section, dict) else "free"
            if check_report_access(user_plan, section_access):
                filtered_sections[key] = section
        filtered["sections"] = filtered_sections
    
    return filtered

@reports_router.get("/")
async def list_reports(
    report_type: Optional[str] = None,
    limit: int = 20
):
    """List available reports - public endpoint"""
    query = {"metadata.status": "completed"}
    
    if report_type:
        query["metadata.report_type"] = report_type
    
    cursor = db.reports.find(
        query,
        {"_id": 0, "metadata": 1, "summary": 1, "public_preview": 1}
    ).sort("metadata.generated_at", -1).limit(limit)
    
    reports = await cursor.to_list(limit)
    
    # Get latest of each type
    weekly_latest = await db.reports.find_one(
        {"metadata.report_type": "weekly_winning_products", "metadata.is_latest": True},
        {"_id": 0, "metadata.slug": 1, "metadata.title": 1}
    )
    monthly_latest = await db.reports.find_one(
        {"metadata.report_type": "monthly_market_trends", "metadata.is_latest": True},
        {"_id": 0, "metadata.slug": 1, "metadata.title": 1}
    )
    
    return {
        "reports": reports,
        "count": len(reports),
        "latest": {
            "weekly": weekly_latest,
            "monthly": monthly_latest
        }
    }


@reports_router.get("/weekly-winning-products")
async def get_weekly_report(
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get the latest weekly winning products report"""
    report = await db.reports.find_one(
        {
            "metadata.report_type": "weekly_winning_products",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0}
    )
    
    if not report:
        # Generate report if none exists
        generator = WeeklyWinningProductsReport(db)
        generated = await generator.generate()
        report = generated.model_dump()
        report["metadata"]["report_type"] = generated.metadata.report_type.value
        report["metadata"]["status"] = generated.metadata.status.value
        report["metadata"]["access_level"] = generated.metadata.access_level.value
        report["metadata"]["period_start"] = generated.metadata.period_start.isoformat()
        report["metadata"]["period_end"] = generated.metadata.period_end.isoformat()
        report["metadata"]["generated_at"] = generated.metadata.generated_at.isoformat()
    
    # Determine user's plan
    user_plan = "free"
    if current_user:
        profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0, "plan": 1})
        user_plan = profile.get("plan", "free") if profile else "free"
    
    # Filter by access level
    filtered_report = filter_report_by_access(report, user_plan)
    
    return {
        "report": filtered_report,
        "user_plan": user_plan,
        "is_authenticated": current_user is not None
    }


@reports_router.get("/monthly-market-trends")
async def get_monthly_report(
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get the latest monthly market trends report"""
    report = await db.reports.find_one(
        {
            "metadata.report_type": "monthly_market_trends",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0}
    )
    
    if not report:
        # Generate report if none exists
        generator = MonthlyMarketTrendsReport(db)
        generated = await generator.generate()
        report = generated.model_dump()
        report["metadata"]["report_type"] = generated.metadata.report_type.value
        report["metadata"]["status"] = generated.metadata.status.value
        report["metadata"]["access_level"] = generated.metadata.access_level.value
        report["metadata"]["period_start"] = generated.metadata.period_start.isoformat()
        report["metadata"]["period_end"] = generated.metadata.period_end.isoformat()
        report["metadata"]["generated_at"] = generated.metadata.generated_at.isoformat()
    
    # Determine user's plan
    user_plan = "free"
    if current_user:
        profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0, "plan": 1})
        user_plan = profile.get("plan", "free") if profile else "free"
    
    # Filter by access level
    filtered_report = filter_report_by_access(report, user_plan)
    
    return {
        "report": filtered_report,
        "user_plan": user_plan,
        "is_authenticated": current_user is not None
    }


@reports_router.get("/public/weekly-winning-products")
async def get_public_weekly_report():
    """Get public preview of weekly report - for SEO"""
    report = await db.reports.find_one(
        {
            "metadata.report_type": "weekly_winning_products",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0, "metadata": 1, "public_preview": 1, "summary": 1}
    )
    
    if not report:
        # Generate report if none exists
        generator = WeeklyWinningProductsReport(db)
        generated = await generator.generate()
        report = {
            "metadata": {
                "title": generated.metadata.title,
                "description": generated.metadata.description,
                "period_start": generated.metadata.period_start.isoformat(),
                "period_end": generated.metadata.period_end.isoformat(),
                "generated_at": generated.metadata.generated_at.isoformat(),
                "slug": generated.metadata.slug
            },
            "public_preview": generated.public_preview,
            "summary": generated.summary
        }
    
    return {
        "report": report,
        "cta": {
            "message": "Unlock the full report to see all winning products, detailed margins, and opportunity clusters.",
            "action": "Sign up for free",
            "url": "/signup"
        }
    }


@reports_router.get("/public/monthly-market-trends")
async def get_public_monthly_report():
    """Get public preview of monthly report - for SEO"""
    report = await db.reports.find_one(
        {
            "metadata.report_type": "monthly_market_trends",
            "metadata.is_latest": True,
            "metadata.status": "completed"
        },
        {"_id": 0, "metadata": 1, "public_preview": 1, "summary": 1}
    )
    
    if not report:
        # Generate report if none exists
        generator = MonthlyMarketTrendsReport(db)
        generated = await generator.generate()
        report = {
            "metadata": {
                "title": generated.metadata.title,
                "description": generated.metadata.description,
                "period_start": generated.metadata.period_start.isoformat(),
                "period_end": generated.metadata.period_end.isoformat(),
                "generated_at": generated.metadata.generated_at.isoformat(),
                "slug": generated.metadata.slug
            },
            "public_preview": generated.public_preview,
            "summary": generated.summary
        }
    
    return {
        "report": report,
        "cta": {
            "message": "Unlock the full report to see all category insights, growth predictions, and market analysis.",
            "action": "Sign up for free",
            "url": "/signup"
        }
    }


@reports_router.get("/history/{report_type}")
async def get_report_history(
    report_type: str,
    limit: int = 20,
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get historical reports of a specific type"""
    valid_types = ["weekly_winning_products", "monthly_market_trends"]
    if report_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid report type. Must be one of: {valid_types}")
    
    # Determine user's plan
    user_plan = "free"
    if current_user:
        profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0, "plan": 1})
        user_plan = profile.get("plan", "free") if profile else "free"
    
    # Check access for historical reports
    if user_plan == "free":
        limit = 3  # Free users only see recent 3
    elif user_plan == "pro":
        limit = min(limit, 10)  # Pro users see 10
    # Elite users get full access
    
    cursor = db.reports.find(
        {"metadata.report_type": report_type, "metadata.status": "completed"},
        {"_id": 0, "metadata": 1, "summary": 1}
    ).sort("metadata.generated_at", -1).limit(limit)
    
    reports = await cursor.to_list(limit)
    
    return {
        "reports": reports,
        "count": len(reports),
        "user_plan": user_plan,
        "access_note": "Upgrade to Elite for full historical archive" if user_plan != "elite" else None
    }


@reports_router.get("/by-slug/{slug}")
async def get_report_by_slug(
    slug: str,
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """Get a specific report by its slug"""
    report = await db.reports.find_one(
        {"metadata.slug": slug, "metadata.status": "completed"},
        {"_id": 0}
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Determine user's plan
    user_plan = "free"
    if current_user:
        profile = await db.profiles.find_one({"id": current_user.user_id}, {"_id": 0, "plan": 1})
        user_plan = profile.get("plan", "free") if profile else "free"
    
    # Filter by access level
    filtered_report = filter_report_by_access(report, user_plan)
    
    return {
        "report": filtered_report,
        "user_plan": user_plan,
        "is_authenticated": current_user is not None
    }


@reports_router.post("/generate/weekly")
async def generate_weekly_report(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Manually trigger weekly report generation (admin only)"""
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    generator = WeeklyWinningProductsReport(db)
    report = await generator.generate()
    
    return {
        "success": True,
        "report_id": report.metadata.id,
        "slug": report.metadata.slug,
        "title": report.metadata.title
    }


@reports_router.post("/generate/monthly")
async def generate_monthly_report(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """Manually trigger monthly report generation (admin only)"""
    expected_key = os.environ.get('AUTOMATION_API_KEY', 'vs_automation_key_2024')
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    generator = MonthlyMarketTrendsReport(db)
    report = await generator.generate()
    
    return {
        "success": True,
        "report_id": report.metadata.id,
        "slug": report.metadata.slug,
        "title": report.metadata.title
    }


@reports_router.get("/weekly-winning-products/pdf")
async def download_weekly_report_pdf(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Download weekly winning products report as PDF.
    Requires Pro plan or above.
    """
    await require_plan(current_user, "pro", "PDF report exports")
    from services.pdf_generator import pdf_generator
    import traceback
    
    try:
        # Get latest weekly report
        report = await db.reports.find_one(
            {
                "metadata.report_type": "weekly_winning_products",
                "metadata.is_latest": True,
                "metadata.status": "completed"
            },
            {"_id": 0}
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="No weekly report available")
        
        logging.info(f"Generating PDF for report: {report.get('metadata', {}).get('title', 'Unknown')}")
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_weekly_report_pdf(report)
        
        # Generate filename
        week_num = report.get('metadata', {}).get('week_number', datetime.now(timezone.utc).isocalendar()[1])
        year = datetime.now(timezone.utc).year
        filename = f"viralscout_weekly_report_week{week_num}_{year}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


@reports_router.get("/monthly-market-trends/pdf")
async def download_monthly_report_pdf(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Download monthly market trends report as PDF.
    Requires Pro plan or above.
    """
    await require_plan(current_user, "pro", "PDF report exports")
    from services.pdf_generator import pdf_generator
    
    try:
        # Get latest monthly report
        report = await db.reports.find_one(
            {
                "metadata.report_type": "monthly_market_trends",
                "metadata.is_latest": True,
                "metadata.status": "completed"
            },
            {"_id": 0}
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="No monthly report available")
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_monthly_report_pdf(report)
        
        # Generate filename
        month_name = datetime.now(timezone.utc).strftime("%B")
        year = datetime.now(timezone.utc).year
        filename = f"viralscout_monthly_report_{month_name}_{year}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


@reports_router.get("/public/weekly-winning-products/pdf")
async def download_public_weekly_report_pdf():
    """Download public preview of weekly report as PDF."""
    import io
    from services.pdf_generator import pdf_generator

    try:
        report = await db.reports.find_one(
            {
                "metadata.report_type": "weekly_winning_products",
                "metadata.is_latest": True,
                "metadata.status": "completed"
            },
            {"_id": 0, "public_preview": 1, "metadata": 1, "summary": 1}
        )
        if not report:
            raise HTTPException(status_code=404, detail="No weekly report available")

        public_report = {
            'metadata': report.get('metadata', {}),
            'summary': report.get('summary', {}),
            'sections': [],
            'public_preview': report.get('public_preview', {})
        }
        preview = report.get('public_preview', {})
        if preview.get('top_5_products'):
            public_report['sections'].append({
                'title': 'Top 5 Products Preview',
                'data': preview.get('top_5_products', [])
            })

        pdf_bytes = pdf_generator.generate_weekly_report_pdf(public_report)
        week_num = report.get('metadata', {}).get('week_number', datetime.now(timezone.utc).isocalendar()[1])
        year = datetime.now(timezone.utc).year
        filename = f"viralscout_weekly_preview_week{week_num}_{year}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


routers = [reports_router]
