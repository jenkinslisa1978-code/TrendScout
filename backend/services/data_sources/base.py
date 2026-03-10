"""
Base Data Source Framework

Abstract base class and common utilities for all data sources.
Ensures consistent interface, error handling, and data normalization.
"""

import os
import logging
import asyncio
import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp

logger = logging.getLogger(__name__)


class DataSourceType(str, Enum):
    TREND = "trend"
    SUPPLIER = "supplier"
    COMPETITOR = "competitor"
    AD_SIGNALS = "ad_signals"


class DataConfidenceLevel(str, Enum):
    HIGH = "high"          # Live API data
    MEDIUM = "medium"      # Scraped or estimated
    LOW = "low"           # Simulated/calculated
    UNKNOWN = "unknown"


@dataclass
class DataSourceConfig:
    """Configuration for a data source"""
    name: str
    source_type: DataSourceType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit_per_minute: int = 60
    cache_ttl_minutes: int = 60
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    timeout_seconds: int = 30
    enabled: bool = True


@dataclass
class DataSourceResult:
    """Result from a data source fetch operation"""
    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    source_name: str = ""
    source_type: DataSourceType = DataSourceType.TREND
    confidence_level: DataConfidenceLevel = DataConfidenceLevel.UNKNOWN
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data_freshness: str = "unknown"
    items_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.items_count = len(self.data)


class BaseDataSource(ABC):
    """
    Abstract base class for all data sources.
    
    Provides:
    - Consistent interface for fetching data
    - Rate limiting and retry logic
    - Caching support
    - Error handling and logging
    - Data normalization to ViralScout schema
    """
    
    def __init__(self, db, config: DataSourceConfig):
        self.db = db
        self.config = config
        self.logger = logging.getLogger(f"datasource.{config.name}")
        self._cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self._request_timestamps: List[datetime] = []
    
    @abstractmethod
    async def fetch_raw_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch raw data from the source.
        Must be implemented by subclasses.
        
        Returns:
            List of raw product data from the source
        """
        pass
    
    @abstractmethod
    def normalize_product(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw product data to ViralScout schema.
        Must be implemented by subclasses.
        
        Args:
            raw_data: Raw product data from source
            
        Returns:
            Normalized product dict matching ViralScout Product model
        """
        pass
    
    def get_confidence_level(self) -> DataConfidenceLevel:
        """Get the confidence level for this data source"""
        if self.config.api_key:
            return DataConfidenceLevel.HIGH
        return DataConfidenceLevel.LOW
    
    async def fetch(self, **kwargs) -> DataSourceResult:
        """
        Main fetch method with caching, rate limiting, and error handling.
        
        Returns:
            DataSourceResult with fetched and normalized data
        """
        if not self.config.enabled:
            return DataSourceResult(
                success=False,
                source_name=self.config.name,
                source_type=self.config.source_type,
                error_message="Data source is disabled"
            )
        
        # Check cache
        cache_key = self._get_cache_key(kwargs)
        cached = self._get_cached(cache_key)
        if cached:
            self.logger.info(f"Returning cached data for {self.config.name}")
            return cached
        
        # Apply rate limiting
        await self._apply_rate_limit()
        
        # Fetch with retry logic
        raw_data = []
        error_message = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                raw_data = await self.fetch_raw_data(**kwargs)
                break
            except Exception as e:
                error_message = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed for {self.config.name}: {e}")
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay_seconds)
        
        if not raw_data and error_message:
            return DataSourceResult(
                success=False,
                source_name=self.config.name,
                source_type=self.config.source_type,
                confidence_level=self.get_confidence_level(),
                error_message=error_message
            )
        
        # Normalize data
        normalized_data = []
        for item in raw_data:
            try:
                normalized = self.normalize_product(item)
                normalized['data_source'] = self.config.name
                normalized['data_source_type'] = self.config.source_type.value
                normalized['confidence_score'] = self._calculate_confidence_score(normalized)
                normalized['last_updated'] = datetime.now(timezone.utc).isoformat()
                normalized_data.append(normalized)
            except Exception as e:
                self.logger.error(f"Failed to normalize product: {e}")
        
        result = DataSourceResult(
            success=True,
            data=normalized_data,
            source_name=self.config.name,
            source_type=self.config.source_type,
            confidence_level=self.get_confidence_level(),
            data_freshness=self._get_data_freshness(),
            metadata={
                'raw_items': len(raw_data),
                'normalized_items': len(normalized_data),
                'fetch_params': kwargs,
            }
        )
        
        # Cache result
        self._set_cache(cache_key, result)
        
        return result
    
    async def update_database(self, result: DataSourceResult) -> Dict[str, int]:
        """
        Update database with fetched products.
        Updates existing products or creates new ones.
        
        Returns:
            Dict with counts: created, updated, failed
        """
        stats = {'created': 0, 'updated': 0, 'failed': 0}
        
        for product in result.data:
            try:
                # Check if product exists by name (case-insensitive match)
                existing = await self.db.products.find_one({
                    "product_name": {"$regex": f"^{product['product_name']}$", "$options": "i"}
                })
                
                if existing:
                    # Update existing product, preserving some fields
                    update_data = {k: v for k, v in product.items() 
                                 if k not in ['id', 'created_at', 'stores_created', 'exports_count']}
                    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
                    
                    await self.db.products.update_one(
                        {"id": existing['id']},
                        {"$set": update_data}
                    )
                    stats['updated'] += 1
                else:
                    # Create new product
                    import uuid
                    product['id'] = str(uuid.uuid4())
                    product['created_at'] = datetime.now(timezone.utc).isoformat()
                    product['stores_created'] = 0
                    product['exports_count'] = 0
                    
                    await self.db.products.insert_one(product)
                    stats['created'] += 1
                    
            except Exception as e:
                self.logger.error(f"Failed to update product {product.get('product_name')}: {e}")
                stats['failed'] += 1
        
        return stats
    
    def _calculate_confidence_score(self, product: Dict[str, Any]) -> int:
        """Calculate confidence score (0-100) based on data completeness"""
        score = 0
        
        # Required fields present
        if product.get('product_name'):
            score += 20
        if product.get('supplier_cost', 0) > 0:
            score += 15
        if product.get('estimated_retail_price', 0) > 0:
            score += 15
        if product.get('image_url'):
            score += 10
        
        # Signal quality
        if product.get('tiktok_views', 0) > 0:
            score += 15
        if product.get('ad_count', 0) > 0:
            score += 10
        if product.get('supplier_order_velocity', 0) > 0:
            score += 15
        
        # Confidence level bonus
        if self.get_confidence_level() == DataConfidenceLevel.HIGH:
            score = min(100, score + 20)
        elif self.get_confidence_level() == DataConfidenceLevel.MEDIUM:
            score = min(100, score + 10)
        
        return min(100, score)
    
    def _get_data_freshness(self) -> str:
        """Get data freshness description"""
        return f"{self.config.cache_ttl_minutes} minutes"
    
    def _get_cache_key(self, params: Dict) -> str:
        """Generate cache key from parameters"""
        param_str = str(sorted(params.items()))
        return hashlib.md5(f"{self.config.name}:{param_str}".encode()).hexdigest()
    
    def _get_cached(self, key: str) -> Optional[DataSourceResult]:
        """Get cached result if not expired"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            ttl = timedelta(minutes=self.config.cache_ttl_minutes)
            if datetime.now(timezone.utc) - timestamp < ttl:
                return data
            del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: DataSourceResult):
        """Cache result"""
        self._cache[key] = (data, datetime.now(timezone.utc))
    
    async def _apply_rate_limit(self):
        """Apply rate limiting"""
        now = datetime.now(timezone.utc)
        minute_ago = now - timedelta(minutes=1)
        
        # Remove old timestamps
        self._request_timestamps = [
            ts for ts in self._request_timestamps if ts > minute_ago
        ]
        
        # Wait if at limit
        if len(self._request_timestamps) >= self.config.rate_limit_per_minute:
            oldest = min(self._request_timestamps)
            wait_time = (oldest + timedelta(minutes=1) - now).total_seconds()
            if wait_time > 0:
                self.logger.info(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self._request_timestamps.append(now)
    
    async def _make_request(
        self, 
        url: str, 
        method: str = "GET",
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with timeout and error handling"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(
                method, 
                url, 
                headers=headers,
                params=params,
                json=data if method != "GET" else None
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")


class SimulatedDataSource(BaseDataSource):
    """
    Base class for simulated data sources.
    Used when live API is not available.
    Generates realistic data based on patterns.
    """
    
    def get_confidence_level(self) -> DataConfidenceLevel:
        return DataConfidenceLevel.LOW
    
    def _add_variation(self, value: float, percent: float = 0.1) -> float:
        """Add random variation to simulate live data"""
        import random
        variation = value * percent
        return value + random.uniform(-variation, variation)
    
    def _add_int_variation(self, value: int, percent: float = 0.15) -> int:
        """Add random integer variation"""
        return int(self._add_variation(float(value), percent))
