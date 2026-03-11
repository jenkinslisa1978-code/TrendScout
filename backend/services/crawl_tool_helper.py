"""
Crawl Tool Helper

Async wrapper for web scraping using curl_cffi.
Used by ad discovery and supplier services.
"""

import asyncio
import logging
from curl_cffi import requests as cffi_requests

logger = logging.getLogger(__name__)


async def crawl_url(url: str, context: str = "") -> str:
    """
    Fetch a URL using curl_cffi with browser impersonation.
    Returns the text content of the page.
    """
    try:
        response = await asyncio.to_thread(
            cffi_requests.get,
            url,
            impersonate="chrome",
            timeout=15,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        if response.status_code == 200:
            return response.text
        else:
            logger.warning(f"Crawl {url} returned status {response.status_code}")
            return ""
    except Exception as e:
        logger.warning(f"Crawl failed for {url}: {e}")
        return ""
