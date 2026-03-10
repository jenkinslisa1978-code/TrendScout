"""
Real Data Scraping Infrastructure

Base utilities for web scraping with:
- Rate limiting (1-2 req/sec)
- 24-hour caching
- Exponential backoff retry
- Source health monitoring
- User-agent rotation
"""

import asyncio
import aiohttp
import hashlib
import logging
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SourceHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"


@dataclass
class SourceHealth:
    """Health status for a data source"""
    source_name: str
    status: SourceHealthStatus = SourceHealthStatus.HEALTHY
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests_24h: int = 0
    success_rate_24h: float = 100.0
    avg_response_time_ms: float = 0.0
    last_error: Optional[str] = None
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ScraperConfig:
    """Configuration for web scrapers"""
    name: str
    base_url: str
    rate_limit_per_second: float = 1.0  # Requests per second
    cache_ttl_hours: int = 24
    retry_attempts: int = 3
    initial_retry_delay: float = 2.0  # Seconds
    max_retry_delay: float = 60.0
    timeout_seconds: int = 30
    enabled: bool = True


# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


class BaseScraper(ABC):
    """
    Abstract base class for web scrapers.
    
    Features:
    - Rate limiting at 1-2 requests/second
    - 24-hour caching
    - Exponential backoff retry
    - Source health monitoring
    - User-agent rotation
    """
    
    def __init__(self, db, config: ScraperConfig):
        self.db = db
        self.config = config
        self.logger = logging.getLogger(f"scraper.{config.name}")
        self._last_request_time: Optional[datetime] = None
        self._health = SourceHealth(source_name=config.name)
        self._response_times: List[float] = []
    
    @abstractmethod
    async def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Main scraping method - must be implemented by subclasses.
        
        Returns:
            List of raw scraped product data
        """
        pass
    
    @abstractmethod
    def parse_product(self, raw_html: Any, **kwargs) -> Dict[str, Any]:
        """
        Parse product data from HTML - must be implemented by subclasses.
        
        Returns:
            Parsed product dictionary
        """
        pass
    
    async def fetch_with_retry(self, url: str, **kwargs) -> Tuple[Optional[str], bool]:
        """
        Fetch URL with rate limiting, caching, and exponential backoff retry.
        
        Returns:
            Tuple of (html_content, success_bool)
        """
        # Check cache first
        cached = await self._get_cached(url)
        if cached:
            self.logger.debug(f"Cache hit for {url}")
            return cached, True
        
        # Apply rate limiting
        await self._apply_rate_limit()
        
        # Retry with exponential backoff
        delay = self.config.initial_retry_delay
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                start_time = datetime.now(timezone.utc)
                html = await self._make_request(url, **kwargs)
                response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                # Track success
                self._track_response_time(response_time)
                self._record_success()
                
                # Cache result
                await self._set_cache(url, html)
                
                return html, True
                
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limited
                    self._health.status = SourceHealthStatus.RATE_LIMITED
                    self.logger.warning(f"Rate limited on {self.config.name}, waiting longer...")
                    delay = min(delay * 3, self.config.max_retry_delay)
                else:
                    last_error = f"HTTP {e.status}: {e.message}"
                    self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                    
            except asyncio.TimeoutError:
                last_error = "Request timeout"
                self.logger.warning(f"Attempt {attempt + 1} timed out for {url}")
                
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.config.retry_attempts - 1:
                jitter = random.uniform(0, delay * 0.3)
                wait_time = delay + jitter
                self.logger.info(f"Waiting {wait_time:.1f}s before retry...")
                await asyncio.sleep(wait_time)
                delay = min(delay * 2, self.config.max_retry_delay)
        
        # Record failure
        self._record_failure(last_error)
        return None, False
    
    async def _make_request(self, url: str, **kwargs) -> str:
        """Make HTTP request with proper headers"""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        # Merge any custom headers
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, **kwargs) as response:
                response.raise_for_status()
                return await response.text()
    
    async def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        if self._last_request_time:
            min_interval = 1.0 / self.config.rate_limit_per_second
            elapsed = (datetime.now(timezone.utc) - self._last_request_time).total_seconds()
            
            if elapsed < min_interval:
                wait_time = min_interval - elapsed
                self.logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
        
        self._last_request_time = datetime.now(timezone.utc)
    
    async def _get_cached(self, url: str) -> Optional[str]:
        """Get cached response from database"""
        cache_key = self._get_cache_key(url)
        
        cached = await self.db.scrape_cache.find_one(
            {"key": cache_key},
            {"_id": 0}
        )
        
        if cached:
            cached_at = datetime.fromisoformat(cached['cached_at'])
            ttl = timedelta(hours=self.config.cache_ttl_hours)
            
            if datetime.now(timezone.utc) - cached_at < ttl:
                return cached['content']
            else:
                # Delete expired cache
                await self.db.scrape_cache.delete_one({"key": cache_key})
        
        return None
    
    async def _set_cache(self, url: str, content: str):
        """Cache response to database"""
        cache_key = self._get_cache_key(url)
        
        await self.db.scrape_cache.update_one(
            {"key": cache_key},
            {
                "$set": {
                    "key": cache_key,
                    "url": url,
                    "content": content,
                    "source": self.config.name,
                    "cached_at": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(f"{self.config.name}:{url}".encode()).hexdigest()
    
    def _track_response_time(self, time_ms: float):
        """Track response time for health monitoring"""
        self._response_times.append(time_ms)
        # Keep last 100 response times
        if len(self._response_times) > 100:
            self._response_times = self._response_times[-100:]
        
        self._health.avg_response_time_ms = sum(self._response_times) / len(self._response_times)
    
    def _record_success(self):
        """Record successful request"""
        self._health.last_success = datetime.now(timezone.utc)
        self._health.consecutive_failures = 0
        self._health.total_requests_24h += 1
        
        if self._health.status in [SourceHealthStatus.RATE_LIMITED, SourceHealthStatus.UNAVAILABLE]:
            self._health.status = SourceHealthStatus.HEALTHY
        
        self._update_success_rate()
    
    def _record_failure(self, error: Optional[str] = None):
        """Record failed request"""
        self._health.last_failure = datetime.now(timezone.utc)
        self._health.consecutive_failures += 1
        self._health.total_requests_24h += 1
        self._health.last_error = error
        
        # Update status based on consecutive failures
        if self._health.consecutive_failures >= 5:
            self._health.status = SourceHealthStatus.UNAVAILABLE
        elif self._health.consecutive_failures >= 2:
            self._health.status = SourceHealthStatus.DEGRADED
        
        self._update_success_rate()
    
    def _update_success_rate(self):
        """Update 24-hour success rate"""
        if self._health.total_requests_24h > 0:
            successes = self._health.total_requests_24h - self._health.consecutive_failures
            self._health.success_rate_24h = (successes / self._health.total_requests_24h) * 100
    
    def get_health(self) -> SourceHealth:
        """Get current health status"""
        self._health.checked_at = datetime.now(timezone.utc)
        return self._health
    
    async def save_health_to_db(self):
        """Save health status to database for monitoring"""
        health_dict = {
            "source_name": self._health.source_name,
            "status": self._health.status.value,
            "last_success": self._health.last_success.isoformat() if self._health.last_success else None,
            "last_failure": self._health.last_failure.isoformat() if self._health.last_failure else None,
            "consecutive_failures": self._health.consecutive_failures,
            "total_requests_24h": self._health.total_requests_24h,
            "success_rate_24h": self._health.success_rate_24h,
            "avg_response_time_ms": self._health.avg_response_time_ms,
            "last_error": self._health.last_error,
            "checked_at": self._health.checked_at.isoformat()
        }
        
        await self.db.source_health.update_one(
            {"source_name": self.config.name},
            {"$set": health_dict},
            upsert=True
        )
    
    def is_healthy(self) -> bool:
        """Check if source is healthy enough to use"""
        return self._health.status in [SourceHealthStatus.HEALTHY, SourceHealthStatus.DEGRADED]


class DataIngestionResult:
    """Result from data ingestion operation"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.success = False
        self.products_fetched = 0
        self.products_created = 0
        self.products_updated = 0
        self.products_failed = 0
        self.started_at = datetime.now(timezone.utc)
        self.completed_at: Optional[datetime] = None
        self.errors: List[str] = []
        self.health_status: Optional[SourceHealthStatus] = None
        self.confidence_level: str = "unknown"
    
    def complete(self, success: bool = True):
        """Mark ingestion as complete"""
        self.success = success
        self.completed_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "source_name": self.source_name,
            "success": self.success,
            "products_fetched": self.products_fetched,
            "products_created": self.products_created,
            "products_updated": self.products_updated,
            "products_failed": self.products_failed,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": (self.completed_at - self.started_at).total_seconds() if self.completed_at else None,
            "errors": self.errors,
            "health_status": self.health_status.value if self.health_status else None,
            "confidence_level": self.confidence_level
        }
