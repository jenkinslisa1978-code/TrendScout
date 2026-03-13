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

logger = logging.getLogger(__name__)

seo_router = APIRouter()

# ── Sitemap.xml ─────────────────────────────────────────────────
from fastapi.responses import Response

@seo_router.get("/api/sitemap.xml", response_class=Response)
async def sitemap_xml():
    """
    Dynamic sitemap.xml for SEO crawlers.
    """
    base_url = os.environ.get("SITE_URL", "https://trendscout.click").rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Static pages
    static_pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
        {"loc": "/trending-products", "priority": "0.9", "changefreq": "daily"},
        {"loc": "/pricing", "priority": "0.7", "changefreq": "monthly"},
        {"loc": "/tools", "priority": "0.6", "changefreq": "monthly"},
        {"loc": "/reports/weekly-winning-products", "priority": "0.7", "changefreq": "weekly"},
        {"loc": "/reports/monthly-market-trends", "priority": "0.6", "changefreq": "monthly"},
    ]

    # Dynamic product pages
    products = await db.products.find(
        {"launch_score": {"$gte": 30}},
        {"_id": 0, "product_name": 1, "last_updated": 1}
    ).sort("launch_score", -1).limit(200).to_list(200)

    urls = []
    for p in static_pages:
        urls.append(
            f'  <url>\n'
            f'    <loc>{base_url}{p["loc"]}</loc>\n'
            f'    <lastmod>{now}</lastmod>\n'
            f'    <changefreq>{p["changefreq"]}</changefreq>\n'
            f'    <priority>{p["priority"]}</priority>\n'
            f'  </url>'
        )

    seen_slugs = set()
    for prod in products:
        slug = slugify(prod.get("product_name", ""))
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        lastmod = prod.get("last_updated", now)
        if isinstance(lastmod, str) and "T" in lastmod:
            lastmod = lastmod.split("T")[0]
        urls.append(
            f'  <url>\n'
            f'    <loc>{base_url}/trending/{slug}</loc>\n'
            f'    <lastmod>{lastmod}</lastmod>\n'
            f'    <changefreq>weekly</changefreq>\n'
            f'    <priority>0.8</priority>\n'
            f'  </url>'
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>"
    )

    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "CDN-Cache-Control": "no-store",
            "Cloudflare-CDN-Cache-Control": "no-store",
        },
    )


@seo_router.get("/api/robots.txt", response_class=Response)
async def robots_txt():
    """Serve robots.txt pointing to sitemap."""
    base_url = os.environ.get("SITE_URL", "https://trendscout.click").rstrip("/")
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "Disallow: /dashboard\n"
        "Disallow: /admin\n"
        "Disallow: /api/\n"
        f"\nSitemap: {base_url}/sitemap.xml\n"
    )
    return Response(content=content, media_type="text/plain")



async def regenerate_sitemap():
    """Regenerate /app/frontend/public/sitemap.xml from current products."""
    try:
        base_url = os.environ.get("SITE_URL", "https://trendscout.click").rstrip("/")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        static_pages = [
            {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
            {"loc": "/trending-products", "priority": "0.9", "changefreq": "daily"},
            {"loc": "/pricing", "priority": "0.7", "changefreq": "monthly"},
        ]

        products = await db.products.find(
            {"launch_score": {"$gte": 30}},
            {"_id": 0, "product_name": 1, "last_updated": 1}
        ).sort("launch_score", -1).limit(200).to_list(200)

        urls = []
        for p in static_pages:
            urls.append(
                f'  <url>\n'
                f'    <loc>{base_url}{p["loc"]}</loc>\n'
                f'    <lastmod>{now}</lastmod>\n'
                f'    <changefreq>{p["changefreq"]}</changefreq>\n'
                f'    <priority>{p["priority"]}</priority>\n'
                f'  </url>'
            )

        seen_slugs = set()
        for prod in products:
            slug = slugify(prod.get("product_name", ""))
            if not slug or slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            urls.append(
                f'  <url>\n'
                f'    <loc>{base_url}/trending/{slug}</loc>\n'
                f'    <lastmod>{now}</lastmod>\n'
                f'    <changefreq>weekly</changefreq>\n'
                f'    <priority>0.8</priority>\n'
                f'  </url>'
            )

        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls)
            + "\n</urlset>"
        )

        with open("/app/frontend/public/sitemap.xml", "w") as f:
            f.write(xml)
        logger.info(f"Sitemap regenerated: {len(urls)} URLs ({len(seen_slugs)} products)")
    except Exception as e:
        logger.error(f"Sitemap generation failed: {e}")



routers = [seo_router]
