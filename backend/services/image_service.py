"""
Image Intelligence Service for TrendScout.

Multi-source image fetching, quality filtering, optimization, and storage.
Priority: Amazon > web search > supplier fallback.
Stores optimized images locally and serves via /api/images/.
"""

import os
import io
import re
import uuid
import hashlib
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any, List
from PIL import Image

logger = logging.getLogger("services.image")

IMAGES_DIR = Path("/app/backend/static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

MIN_WIDTH = 400
MIN_HEIGHT = 400
TARGET_SIZE = (800, 800)
JPEG_QUALITY = 82
MAX_DOWNLOAD_SIZE = 10 * 1024 * 1024  # 10MB

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}


class ImageService:
    def __init__(self, db):
        self.db = db

    # ── Public API ────────────────────────────────────────────

    async def enrich_product_images(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find, validate, and store high-quality images for a product.
        Returns dict with primary_image and gallery urls.
        """
        product_id = product.get("id", "")
        product_name = product.get("product_name", "")
        existing_url = product.get("image_url", "")
        logger.info(f"Image enrichment for: {product_name[:50]}")

        images_found: List[Dict[str, Any]] = []

        # Source 1: Try existing URL first (validate quality)
        if existing_url:
            img = await self._fetch_and_validate(existing_url, source="existing")
            if img:
                images_found.append(img)

        # Source 2: Amazon product search
        amazon_imgs = await self._search_amazon_images(product_name)
        images_found.extend(amazon_imgs)

        # Source 3: Web image search via DuckDuckGo
        web_imgs = await self._search_web_images(product_name)
        images_found.extend(web_imgs)

        if not images_found:
            logger.warning(f"No valid images found for: {product_name[:50]}")
            return {"primary_image": existing_url, "gallery": []}

        # Deduplicate by hash
        images_found = self._deduplicate(images_found)

        # Sort by quality score (resolution * source priority)
        images_found.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

        # Store top images locally
        stored = []
        for img_data in images_found[:5]:
            local_url = await self._store_image(img_data, product_id)
            if local_url:
                stored.append({
                    "url": local_url,
                    "source": img_data.get("source", "unknown"),
                    "width": img_data.get("width", 0),
                    "height": img_data.get("height", 0),
                    "quality_score": img_data.get("quality_score", 0),
                })

        primary = stored[0]["url"] if stored else existing_url
        gallery = [s["url"] for s in stored]

        # Update product in DB
        await self.db.products.update_one(
            {"id": product_id},
            {"$set": {
                "image_url": primary,
                "gallery_images": gallery,
                "image_enriched": True,
                "image_sources": [s["source"] for s in stored],
            }}
        )

        logger.info(f"Stored {len(stored)} images for: {product_name[:50]}")
        return {"primary_image": primary, "gallery": gallery}

    async def batch_enrich(self, limit: int = 20):
        """Background job: enrich products that haven't been image-enriched yet."""
        products = await self.db.products.find(
            {"$or": [
                {"image_enriched": {"$ne": True}},
                {"image_url": {"$in": [None, ""]}},
            ]},
            {"_id": 0}
        ).sort("launch_score", -1).limit(limit).to_list(limit)

        logger.info(f"Image enrichment batch: {len(products)} products")
        results = {"enriched": 0, "failed": 0}

        for product in products:
            try:
                result = await self.enrich_product_images(product)
                if result.get("primary_image"):
                    results["enriched"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                logger.error(f"Image enrichment failed for {product.get('id')}: {e}")
                results["failed"] += 1
            await asyncio.sleep(2)  # Rate limiting

        return results

    # ── Image Sources ─────────────────────────────────────────

    async def _search_amazon_images(self, product_name: str) -> List[Dict]:
        """Search Amazon for product images."""
        try:
            # Clean product name for search
            query = re.sub(r'[^\w\s]', '', product_name)[:80]
            search_url = f"https://www.amazon.co.uk/s?k={query.replace(' ', '+')}&i=aps"

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return []
                    html = await resp.text()

            # Extract image URLs from search results
            img_urls = re.findall(r'https://m\.media-amazon\.com/images/I/[A-Za-z0-9._%-]+\.(?:jpg|png)', html)
            # Get high-res versions
            img_urls = list(set(
                url.replace('._AC_UL320_', '._AC_SL1500_').replace('._AC_UL160_', '._AC_SL1500_')
                for url in img_urls
            ))[:6]

            results = []
            for url in img_urls[:3]:
                img = await self._fetch_and_validate(url, source="amazon")
                if img:
                    img["quality_score"] *= 1.3  # Boost amazon quality
                    results.append(img)

            return results
        except Exception as e:
            logger.debug(f"Amazon image search failed: {e}")
            return []

    async def _search_web_images(self, product_name: str) -> List[Dict]:
        """Search DuckDuckGo for product images."""
        try:
            query = re.sub(r'[^\w\s]', '', product_name)[:60]
            url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}+product+photo&iax=images&ia=images"

            async with aiohttp.ClientSession() as session:
                # Use DDG lite for image results
                vqd_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
                async with session.get(vqd_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    text = await resp.text()

                # Extract vqd token
                vqd_match = re.search(r'vqd=["\']([^"\']+)', text)
                if not vqd_match:
                    return []
                vqd = vqd_match.group(1)

                img_url = f"https://duckduckgo.com/i.js?q={query.replace(' ', '+')}&o=json&vqd={vqd}"
                async with session.get(img_url, headers={**HEADERS, "Referer": "https://duckduckgo.com/"}, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json()

            results = []
            for item in (data.get("results") or [])[:4]:
                img_src = item.get("image", "")
                if not img_src or "amazon" in img_src:  # Skip amazon dupes
                    continue
                img = await self._fetch_and_validate(img_src, source="web")
                if img:
                    results.append(img)

            return results
        except Exception as e:
            logger.debug(f"Web image search failed: {e}")
            return []

    # ── Fetch, Validate, Optimize ─────────────────────────────

    async def _fetch_and_validate(self, url: str, source: str = "unknown") -> Optional[Dict]:
        """Download image, check quality, return metadata if valid."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return None
                    content_length = resp.headers.get("Content-Length", "0")
                    if int(content_length or 0) > MAX_DOWNLOAD_SIZE:
                        return None
                    data = await resp.read()

            if len(data) < 5000:  # Too small, likely placeholder
                return None

            img = Image.open(io.BytesIO(data))
            width, height = img.size

            # Quality checks
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                return None

            # Calculate quality score
            resolution_score = min(width * height / (1000 * 1000), 5.0)  # Max 5 for 1000x1000+
            source_bonus = {"amazon": 2.0, "existing": 1.5, "web": 1.0}.get(source, 0.5)
            aspect_ratio = min(width, height) / max(width, height)
            aspect_score = aspect_ratio  # Prefer square-ish

            quality_score = resolution_score * source_bonus * (0.5 + aspect_score * 0.5)

            # Image hash for dedup
            img_hash = hashlib.md5(data[:4096]).hexdigest()

            return {
                "url": url,
                "data": data,
                "source": source,
                "width": width,
                "height": height,
                "quality_score": round(quality_score, 2),
                "hash": img_hash,
                "format": img.format or "JPEG",
            }
        except Exception as e:
            logger.debug(f"Image fetch/validate failed ({url[:60]}): {e}")
            return None

    def _deduplicate(self, images: List[Dict]) -> List[Dict]:
        """Remove duplicate images by hash."""
        seen = set()
        unique = []
        for img in images:
            h = img.get("hash", "")
            if h and h not in seen:
                seen.add(h)
                unique.append(img)
        return unique

    async def _store_image(self, img_data: Dict, product_id: str) -> Optional[str]:
        """Optimize and store image locally. Returns local URL path."""
        try:
            data = img_data.get("data")
            if not data:
                return None

            img = Image.open(io.BytesIO(data))

            # Convert to RGB if needed
            if img.mode in ("RGBA", "P", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Crop to square (center crop)
            w, h = img.size
            short_side = min(w, h)
            left = (w - short_side) // 2
            top = (h - short_side) // 2
            img = img.crop((left, top, left + short_side, top + short_side))

            # Resize to target
            img = img.resize(TARGET_SIZE, Image.LANCZOS)

            # Save as optimized JPEG
            filename = f"{product_id}_{uuid.uuid4().hex[:8]}.jpg"
            filepath = IMAGES_DIR / filename
            img.save(filepath, "JPEG", quality=JPEG_QUALITY, optimize=True)

            return f"/api/images/{filename}"
        except Exception as e:
            logger.error(f"Image store failed: {e}")
            return None
