"""
Data Ingestion Service - Base Module

Provides the foundation for all data source importers.
Handles normalization, deduplication, and automation triggering.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import hashlib
import logging

logger = logging.getLogger(__name__)


class ProductNormalizer:
    """
    Normalizes product data from various sources into a standard format.
    """
    
    REQUIRED_FIELDS = ['product_name', 'category']
    
    CATEGORY_MAPPING = {
        # TikTok categories
        'beauty': 'Beauty',
        'fashion': 'Fashion',
        'electronics': 'Electronics',
        'home': 'Home Decor',
        'kitchen': 'Kitchen',
        'fitness': 'Health & Fitness',
        'pets': 'Pet Supplies',
        'baby': 'Baby & Kids',
        'outdoor': 'Outdoor',
        'automotive': 'Automotive',
        # Amazon categories
        'appliances': 'Electronics',
        'cell phones': 'Mobile Accessories',
        'computers': 'Electronics',
        'camera': 'Electronics',
        'office': 'Home Office',
        'sports': 'Health & Fitness',
        'toys': 'Toys & Games',
        'garden': 'Home & Garden',
        # Generic mappings
        'tech': 'Electronics',
        'decor': 'Home Decor',
        'health': 'Health & Fitness',
        'accessories': 'Fashion',
    }
    
    @classmethod
    def normalize_category(cls, raw_category: str) -> str:
        """Normalize category to standard format"""
        if not raw_category:
            return 'General'
        
        lower_cat = raw_category.lower().strip()
        
        # Direct mapping
        if lower_cat in cls.CATEGORY_MAPPING:
            return cls.CATEGORY_MAPPING[lower_cat]
        
        # Partial matching
        for key, value in cls.CATEGORY_MAPPING.items():
            if key in lower_cat or lower_cat in key:
                return value
        
        # Title case the original if no mapping found
        return raw_category.title()
    
    @classmethod
    def normalize_competition(cls, value: Any) -> str:
        """Normalize competition level"""
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ['low', 'medium', 'high']:
                return value
            if 'low' in value or 'easy' in value:
                return 'low'
            if 'high' in value or 'hard' in value or 'saturated' in value:
                return 'high'
        elif isinstance(value, (int, float)):
            if value < 33:
                return 'low'
            elif value < 66:
                return 'medium'
            else:
                return 'high'
        return 'medium'
    
    @classmethod
    def normalize_product(cls, raw_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Normalize raw product data to standard format.
        
        Args:
            raw_data: Raw product data from source
            source: Source identifier (tiktok, amazon, supplier)
            
        Returns:
            Normalized product dictionary
        """
        # Generate unique fingerprint for deduplication
        fingerprint_data = f"{raw_data.get('product_name', '')}-{raw_data.get('source_id', '')}-{source}"
        fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()[:16]
        
        normalized = {
            'id': raw_data.get('id') or str(uuid.uuid4()),
            'product_name': raw_data.get('product_name', raw_data.get('name', 'Unknown Product')),
            'category': cls.normalize_category(raw_data.get('category', '')),
            'short_description': raw_data.get('short_description', raw_data.get('description', '')),
            'supplier_cost': float(raw_data.get('supplier_cost', raw_data.get('cost', 0)) or 0),
            'estimated_retail_price': float(raw_data.get('estimated_retail_price', raw_data.get('price', 0)) or 0),
            'estimated_margin': 0,  # Calculated later
            'tiktok_views': int(raw_data.get('tiktok_views', raw_data.get('views', 0)) or 0),
            'ad_count': int(raw_data.get('ad_count', raw_data.get('ads', 0)) or 0),
            'competition_level': cls.normalize_competition(raw_data.get('competition_level', raw_data.get('competition', 'medium'))),
            'trend_score': int(raw_data.get('trend_score', 0) or 0),
            'trend_stage': raw_data.get('trend_stage', 'rising'),
            'opportunity_rating': raw_data.get('opportunity_rating', 'medium'),
            'ai_summary': raw_data.get('ai_summary', ''),
            'supplier_link': raw_data.get('supplier_link', raw_data.get('url', '')),
            'is_premium': raw_data.get('is_premium', False),
            'source': source,
            'source_id': raw_data.get('source_id', raw_data.get('external_id', '')),
            'fingerprint': fingerprint,
            'source_url': raw_data.get('source_url', ''),
            'image_url': raw_data.get('image_url', raw_data.get('image', '')),
            'created_at': raw_data.get('created_at', datetime.now(timezone.utc).isoformat()),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'last_synced_at': datetime.now(timezone.utc).isoformat(),
        }
        
        # Calculate margin
        if normalized['estimated_retail_price'] > 0 and normalized['supplier_cost'] > 0:
            normalized['estimated_margin'] = normalized['estimated_retail_price'] - normalized['supplier_cost']
        
        return normalized


class BaseDataImporter(ABC):
    """
    Abstract base class for all data importers.
    Provides common functionality for fetching, normalizing, and storing products.
    """
    
    def __init__(self, db, source_name: str):
        self.db = db
        self.source_name = source_name
        self.normalizer = ProductNormalizer()
        self.logger = logging.getLogger(f"importer.{source_name}")
    
    @abstractmethod
    async def fetch_products(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch raw products from the data source.
        Must be implemented by each importer.
        """
        pass
    
    @abstractmethod
    def get_source_config(self) -> Dict[str, Any]:
        """
        Return source-specific configuration.
        """
        pass
    
    async def import_products(self, **kwargs) -> Dict[str, Any]:
        """
        Main import method. Fetches, normalizes, and stores products.
        
        Returns:
            Import result summary
        """
        result = {
            'source': self.source_name,
            'started_at': datetime.now(timezone.utc).isoformat(),
            'fetched': 0,
            'inserted': 0,
            'updated': 0,
            'skipped': 0,
            'errors': [],
            'products': [],
        }
        
        try:
            # Fetch raw products
            self.logger.info(f"Fetching products from {self.source_name}...")
            raw_products = await self.fetch_products(**kwargs)
            result['fetched'] = len(raw_products)
            
            # Normalize and store each product
            for raw_product in raw_products:
                try:
                    normalized = self.normalizer.normalize_product(raw_product, self.source_name)
                    store_result = await self._store_product(normalized)
                    
                    if store_result == 'inserted':
                        result['inserted'] += 1
                    elif store_result == 'updated':
                        result['updated'] += 1
                    else:
                        result['skipped'] += 1
                    
                    result['products'].append(normalized)
                    
                except Exception as e:
                    result['errors'].append(f"Error processing product: {str(e)}")
                    result['skipped'] += 1
            
            result['completed_at'] = datetime.now(timezone.utc).isoformat()
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(f"Import failed: {str(e)}")
            result['success'] = False
            self.logger.error(f"Import failed: {str(e)}")
        
        return result
    
    async def _store_product(self, product: Dict[str, Any]) -> str:
        """
        Store product with deduplication logic.
        
        Returns:
            'inserted', 'updated', or 'skipped'
        """
        # Check for existing product by fingerprint or source_id
        existing = await self.db.products.find_one({
            '$or': [
                {'fingerprint': product['fingerprint']},
                {'source_id': product['source_id'], 'source': product['source']} if product.get('source_id') else {'_id': None},
                {'product_name': product['product_name'], 'source': product['source']},
            ]
        }, {"_id": 0})
        
        if existing:
            # Update existing product
            product['id'] = existing.get('id', product['id'])
            product['created_at'] = existing.get('created_at', product['created_at'])
            
            await self.db.products.update_one(
                {'id': product['id']},
                {'$set': product}
            )
            return 'updated'
        else:
            # Insert new product
            await self.db.products.insert_one(product)
            return 'inserted'
