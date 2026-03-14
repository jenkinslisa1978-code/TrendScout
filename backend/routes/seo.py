from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response
from typing import Optional
from datetime import datetime, timezone
import os
import logging

from auth import get_current_user, get_optional_user, AuthenticatedUser
from common.database import db
from common.cache import get_cached, set_cached, slugify

logger = logging.getLogger(__name__)

seo_router = APIRouter()

SITE_BASE = "https://trendscout.click"

STATIC_PAGES = [
    {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
    {"loc": "/trending-products", "priority": "0.9", "changefreq": "daily"},
    {"loc": "/trending-products-today", "priority": "0.9", "changefreq": "daily"},
    {"loc": "/trending-products-this-week", "priority": "0.8", "changefreq": "weekly"},
    {"loc": "/trending-products-this-month", "priority": "0.8", "changefreq": "monthly"},
    {"loc": "/top-trending-products", "priority": "0.9", "changefreq": "daily"},
    {"loc": "/pricing", "priority": "0.7", "changefreq": "monthly"},
    {"loc": "/tools", "priority": "0.6", "changefreq": "monthly"},
    {"loc": "/blog", "priority": "0.7", "changefreq": "weekly"},
    {"loc": "/login", "priority": "0.3", "changefreq": "monthly"},
    {"loc": "/register", "priority": "0.3", "changefreq": "monthly"},
    {"loc": "/reports/weekly-winning-products", "priority": "0.7", "changefreq": "weekly"},
    {"loc": "/reports/monthly-market-trends", "priority": "0.6", "changefreq": "monthly"},
]


async def _build_sitemap_xml() -> str:
    """Build a complete, valid XML sitemap."""
    base = SITE_BASE.rstrip("/")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    entries = []

    # Static pages
    for p in STATIC_PAGES:
        entries.append(
            f"  <url>\n"
            f"    <loc>{base}{p['loc']}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{p['changefreq']}</changefreq>\n"
            f"    <priority>{p['priority']}</priority>\n"
            f"  </url>"
        )

    # Dynamic product pages — include all trending products
    products = await db.products.find(
        {"launch_score": {"$gte": 20}},
        {"_id": 0, "id": 1, "product_name": 1, "last_updated": 1, "launch_score": 1, "category": 1},
    ).sort("launch_score", -1).limit(500).to_list(500)

    # Category pages
    categories_seen = set()
    for prod in products:
        cat = prod.get("category")
        if cat and cat not in categories_seen:
            categories_seen.add(cat)
            cat_slug = slugify(cat)
            if cat_slug:
                entries.append(
                    f"  <url>\n"
                    f"    <loc>{base}/category/{cat_slug}</loc>\n"
                    f"    <lastmod>{today}</lastmod>\n"
                    f"    <changefreq>weekly</changefreq>\n"
                    f"    <priority>0.7</priority>\n"
                    f"  </url>"
                )

    seen = set()
    for prod in products:
        pid = prod.get("id", "")
        if not pid or pid in seen:
            continue
        seen.add(pid)

        slug = slugify(prod.get("product_name", ""))
        lastmod = prod.get("last_updated", today)
        if isinstance(lastmod, str) and "T" in lastmod:
            lastmod = lastmod.split("T")[0]
        elif not isinstance(lastmod, str):
            lastmod = today

        score = prod.get("launch_score", 0)
        priority = "0.9" if score >= 70 else "0.8" if score >= 50 else "0.7"

        # Product detail page (/product/{id})
        entries.append(
            f"  <url>\n"
            f"    <loc>{base}/product/{pid}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

        # SEO-friendly slug URL (/trending/{slug}) if slug exists
        if slug:
            entries.append(
                f"  <url>\n"
                f"    <loc>{base}/trending/{slug}</loc>\n"
                f"    <lastmod>{lastmod}</lastmod>\n"
                f"    <changefreq>weekly</changefreq>\n"
                f"    <priority>{priority}</priority>\n"
                f"  </url>"
            )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    return xml


# ── /sitemap.xml (served via /api prefix internally) ────────────

@seo_router.get("/api/sitemap.xml")
async def sitemap_xml():
    """Serve a valid XML sitemap with correct Content-Type."""
    cached = get_cached("sitemap_xml")
    if cached:
        xml = cached
    else:
        xml = await _build_sitemap_xml()
        set_cached("sitemap_xml", xml, ttl=3600)

    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Type": "application/xml; charset=utf-8",
            "Cache-Control": "public, max-age=3600",
            "X-Content-Type-Options": "nosniff",
        },
    )


# ── /robots.txt ─────────────────────────────────────────────────

@seo_router.get("/api/robots.txt")
async def robots_txt():
    """Serve robots.txt pointing to sitemap."""
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "Disallow: /dashboard\n"
        "Disallow: /admin\n"
        "Disallow: /api/\n"
        "Disallow: /settings/\n"
        f"\nSitemap: {SITE_BASE}/sitemap.xml\n"
    )
    return Response(content=content, media_type="text/plain")


# ── Regenerate static sitemap.xml ───────────────────────────────

async def regenerate_sitemap():
    """Write sitemap.xml to frontend public folder for static serving."""
    try:
        xml = await _build_sitemap_xml()
        with open("/app/frontend/public/sitemap.xml", "w") as f:
            f.write(xml)
        set_cached("sitemap_xml", xml, ttl=3600)
        url_count = xml.count("<url>")
        logger.info(f"Sitemap regenerated: {url_count} URLs")
    except Exception as e:
        logger.error(f"Sitemap generation failed: {e}")


routers = [seo_router]
