"""
Supplier Data Sources

Fetches product data from supplier platforms like AliExpress and CJ Dropshipping.
Provides supplier cost, demand signals, and product availability.
"""

import os
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from .base import (
    BaseDataSource,
    SimulatedDataSource,
    DataSourceConfig,
    DataSourceType,
    DataConfidenceLevel
)


# Simulated supplier products with realistic pricing and demand
SUPPLIER_PRODUCTS = [
    {
        'sku': 'AE-LED-001',
        'name': 'LED Sunset Projection Lamp',
        'category': 'Home Decor',
        'supplier': 'AliExpress',
        'cost': 6.80,
        'shipping': 1.70,
        'moq': 1,
        'orders_30d': 4500,
        'rating': 4.7,
        'reviews': 2800,
        'processing_days': 3,
        'shipping_days': 12,
        'variants': ['Sunset Orange', 'Rainbow', 'Northern Lights'],
        'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=600&fit=crop',
    },
    {
        'sku': 'CJ-SLIDE-002',
        'name': 'Cloud Pillow Slides',
        'category': 'Fashion',
        'supplier': 'CJ Dropshipping',
        'cost': 3.50,
        'shipping': 0.70,
        'moq': 2,
        'orders_30d': 12000,
        'rating': 4.5,
        'reviews': 5600,
        'processing_days': 1,
        'shipping_days': 8,
        'variants': ['36-37', '38-39', '40-41', '42-43', '44-45'],
        'image': 'https://images.unsplash.com/photo-1603487742131-4160ec999306?w=600&h=600&fit=crop',
    },
    {
        'sku': 'AE-FAN-003',
        'name': 'Portable Bladeless Neck Fan',
        'category': 'Electronics',
        'supplier': 'AliExpress',
        'cost': 7.20,
        'shipping': 1.80,
        'moq': 1,
        'orders_30d': 3200,
        'rating': 4.4,
        'reviews': 1900,
        'processing_days': 2,
        'shipping_days': 15,
        'variants': ['White', 'Black', 'Pink', 'Blue'],
        'image': 'https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=600&h=600&fit=crop',
    },
    {
        'sku': 'CJ-BEAUTY-004',
        'name': 'Ice Roller Face Massager',
        'category': 'Beauty',
        'supplier': 'CJ Dropshipping',
        'cost': 2.10,
        'shipping': 0.70,
        'moq': 1,
        'orders_30d': 8900,
        'rating': 4.6,
        'reviews': 3400,
        'processing_days': 1,
        'shipping_days': 7,
        'variants': ['Silver', 'Rose Gold'],
        'image': 'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=600&h=600&fit=crop',
    },
    {
        'sku': 'AE-PROJ-005',
        'name': 'Smart Galaxy Star Projector',
        'category': 'Home Decor',
        'supplier': 'AliExpress',
        'cost': 12.50,
        'shipping': 2.50,
        'moq': 1,
        'orders_30d': 5600,
        'rating': 4.5,
        'reviews': 4200,
        'processing_days': 3,
        'shipping_days': 14,
        'variants': ['Black', 'White', 'Wood Grain'],
        'image': 'https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=600&h=600&fit=crop',
    },
    {
        'sku': 'CJ-HAIR-006',
        'name': 'Scalp Massager Shampoo Brush',
        'category': 'Beauty',
        'supplier': 'CJ Dropshipping',
        'cost': 0.90,
        'shipping': 0.30,
        'moq': 3,
        'orders_30d': 15000,
        'rating': 4.7,
        'reviews': 8900,
        'processing_days': 1,
        'shipping_days': 6,
        'variants': ['Pink', 'Blue', 'Green', 'Purple', 'Black'],
        'image': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&h=600&fit=crop',
    },
    {
        'sku': 'AE-PROJ-007',
        'name': 'Mini Pocket Projector 1080P',
        'category': 'Electronics',
        'supplier': 'AliExpress',
        'cost': 38.00,
        'shipping': 7.00,
        'moq': 1,
        'orders_30d': 1800,
        'rating': 4.3,
        'reviews': 950,
        'processing_days': 4,
        'shipping_days': 18,
        'variants': ['Black', 'White'],
        'image': 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=600&h=600&fit=crop',
    },
    {
        'sku': 'CJ-MOUNT-008',
        'name': 'MagSafe Car Phone Mount',
        'category': 'Electronics',
        'supplier': 'CJ Dropshipping',
        'cost': 4.20,
        'shipping': 1.30,
        'moq': 2,
        'orders_30d': 6700,
        'rating': 4.4,
        'reviews': 2100,
        'processing_days': 1,
        'shipping_days': 9,
        'variants': ['Black', 'Silver'],
        'image': 'https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=600&h=600&fit=crop',
    },
    {
        'sku': 'AE-DESK-009',
        'name': 'Clear Acrylic Desk Organizer',
        'category': 'Home Office',
        'supplier': 'AliExpress',
        'cost': 6.50,
        'shipping': 1.50,
        'moq': 1,
        'orders_30d': 2400,
        'rating': 4.6,
        'reviews': 1600,
        'processing_days': 3,
        'shipping_days': 16,
        'variants': ['Clear', 'Smoke'],
        'image': 'https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=600&h=600&fit=crop',
    },
    {
        'sku': 'CJ-AUDIO-010',
        'name': 'Premium ANC Wireless Earbuds',
        'category': 'Electronics',
        'supplier': 'CJ Dropshipping',
        'cost': 11.50,
        'shipping': 2.50,
        'moq': 1,
        'orders_30d': 9200,
        'rating': 4.3,
        'reviews': 4800,
        'processing_days': 2,
        'shipping_days': 10,
        'variants': ['Black', 'White', 'Pink'],
        'image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&h=600&fit=crop',
    },
    {
        'sku': 'AE-HEALTH-011',
        'name': 'Adjustable Posture Corrector',
        'category': 'Health & Fitness',
        'supplier': 'AliExpress',
        'cost': 4.80,
        'shipping': 1.20,
        'moq': 1,
        'orders_30d': 5100,
        'rating': 4.2,
        'reviews': 2900,
        'processing_days': 2,
        'shipping_days': 13,
        'variants': ['S/M', 'L/XL', 'XXL'],
        'image': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop',
    },
    {
        'sku': 'CJ-PET-012',
        'name': 'Reusable Pet Hair Remover',
        'category': 'Pet Supplies',
        'supplier': 'CJ Dropshipping',
        'cost': 2.80,
        'shipping': 0.70,
        'moq': 2,
        'orders_30d': 7800,
        'rating': 4.5,
        'reviews': 3600,
        'processing_days': 1,
        'shipping_days': 7,
        'variants': ['Blue', 'Green', 'Purple'],
        'image': 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=600&fit=crop',
    },
    {
        'sku': 'AE-KITCHEN-013',
        'name': 'USB Rechargeable Blender Cup',
        'category': 'Kitchen',
        'supplier': 'AliExpress',
        'cost': 9.00,
        'shipping': 2.00,
        'moq': 1,
        'orders_30d': 6300,
        'rating': 4.4,
        'reviews': 3100,
        'processing_days': 2,
        'shipping_days': 14,
        'variants': ['Pink', 'Blue', 'Green', 'Purple'],
        'image': 'https://images.unsplash.com/photo-1570197571499-166b36435e9f?w=600&h=600&fit=crop',
    },
    {
        'sku': 'CJ-LED-014',
        'name': 'RGB LED Strip Lights 50ft',
        'category': 'Home Decor',
        'supplier': 'CJ Dropshipping',
        'cost': 4.00,
        'shipping': 1.00,
        'moq': 1,
        'orders_30d': 11500,
        'rating': 4.3,
        'reviews': 6200,
        'processing_days': 1,
        'shipping_days': 8,
        'variants': ['15m/50ft', '10m/33ft', '5m/16ft'],
        'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop',
    },
    {
        'sku': 'AE-LUNCH-015',
        'name': 'Electric Heated Lunch Box',
        'category': 'Kitchen',
        'supplier': 'AliExpress',
        'cost': 10.00,
        'shipping': 2.00,
        'moq': 1,
        'orders_30d': 3400,
        'rating': 4.5,
        'reviews': 1800,
        'processing_days': 3,
        'shipping_days': 15,
        'variants': ['White', 'Pink', 'Blue'],
        'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=600&fit=crop',
    },
]


class AliExpressProducts(SimulatedDataSource):
    """
    AliExpress product data source.
    
    Live API: AliExpress Affiliate API (requires account)
    Fallback: Curated supplier product database
    """
    
    def __init__(self, db):
        config = DataSourceConfig(
            name="aliexpress_products",
            source_type=DataSourceType.SUPPLIER,
            api_key=os.environ.get('ALIEXPRESS_API_KEY'),
            api_secret=os.environ.get('ALIEXPRESS_API_SECRET'),
            base_url="https://api-sg.aliexpress.com/sync",
            rate_limit_per_minute=20,
            cache_ttl_minutes=180,
        )
        super().__init__(db, config)
    
    async def fetch_raw_data(self, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch products from AliExpress"""
        
        if self.config.api_key:
            try:
                return await self._fetch_affiliate_api(category, limit)
            except Exception as e:
                self.logger.warning(f"AliExpress API failed: {e}")
        
        return self._get_simulated_data(category, limit, supplier='AliExpress')
    
    async def _fetch_affiliate_api(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Fetch from AliExpress Affiliate API"""
        # API implementation would go here
        # For now, fall back to simulated data
        raise NotImplementedError("AliExpress API not configured")
    
    def _get_simulated_data(self, category: Optional[str], limit: int, supplier: str = None) -> List[Dict[str, Any]]:
        """Generate simulated supplier data"""
        products = []
        
        for item in SUPPLIER_PRODUCTS:
            if supplier and item['supplier'] != supplier:
                continue
            if category and item['category'].lower() != category.lower():
                continue
            
            # Add realistic variation
            product = {
                **item,
                'orders_30d': self._add_int_variation(item['orders_30d'], 0.15),
                'cost': round(self._add_variation(item['cost'], 0.05), 2),
                'reviews': self._add_int_variation(item['reviews'], 0.08),
            }
            products.append(product)
            
            if len(products) >= limit:
                break
        
        return products
    
    def normalize_product(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize supplier data to ViralScout schema"""
        total_cost = raw_data.get('cost', 0) + raw_data.get('shipping', 0)
        orders = raw_data.get('orders_30d', 0)
        
        # Estimate retail price (typical 3-4x markup)
        markup = random.uniform(3.0, 4.5)
        estimated_retail = round(total_cost * markup, 2)
        
        # Calculate supplier order velocity (weekly from monthly)
        weekly_orders = int(orders / 4)
        
        return {
            'product_name': raw_data.get('name', ''),
            'category': raw_data.get('category', 'General'),
            'supplier_cost': total_cost,
            'estimated_retail_price': estimated_retail,
            'supplier_link': f"https://aliexpress.com/item/{raw_data.get('sku', '')}",
            'supplier_order_velocity': weekly_orders,
            'supplier_rating': raw_data.get('rating', 0),
            'supplier_reviews': raw_data.get('reviews', 0),
            'supplier_orders_30d': orders,
            'supplier_processing_days': raw_data.get('processing_days', 3),
            'supplier_shipping_days': raw_data.get('shipping_days', 15),
            'image_url': raw_data.get('image'),
            'product_variants': raw_data.get('variants', []),
        }


class CJDropshippingProducts(SimulatedDataSource):
    """
    CJ Dropshipping product data source.
    
    Live API: CJ Dropshipping API (requires account)
    Fallback: Curated supplier product database
    """
    
    def __init__(self, db):
        config = DataSourceConfig(
            name="cj_dropshipping",
            source_type=DataSourceType.SUPPLIER,
            api_key=os.environ.get('CJ_API_KEY'),
            base_url="https://developers.cjdropshipping.com/api",
            rate_limit_per_minute=30,
            cache_ttl_minutes=120,
        )
        super().__init__(db, config)
    
    async def fetch_raw_data(self, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch products from CJ Dropshipping"""
        
        if self.config.api_key:
            try:
                return await self._fetch_cj_api(category, limit)
            except Exception as e:
                self.logger.warning(f"CJ API failed: {e}")
        
        return self._get_simulated_data(category, limit)
    
    async def _fetch_cj_api(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Fetch from CJ Dropshipping API"""
        url = f"{self.config.base_url}/product/list"
        headers = {'CJ-Access-Token': self.config.api_key}
        params = {'pageNum': 1, 'pageSize': limit}
        if category:
            params['categoryName'] = category
        
        data = await self._make_request(url, headers=headers, params=params)
        return data.get('data', {}).get('list', [])
    
    def _get_simulated_data(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Generate simulated CJ data"""
        products = []
        
        for item in SUPPLIER_PRODUCTS:
            if item['supplier'] != 'CJ Dropshipping':
                continue
            if category and item['category'].lower() != category.lower():
                continue
            
            product = {
                **item,
                'orders_30d': self._add_int_variation(item['orders_30d'], 0.12),
                'cost': round(self._add_variation(item['cost'], 0.04), 2),
            }
            products.append(product)
            
            if len(products) >= limit:
                break
        
        return products
    
    def normalize_product(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize CJ data to ViralScout schema"""
        total_cost = raw_data.get('cost', 0) + raw_data.get('shipping', 0)
        orders = raw_data.get('orders_30d', 0)
        
        # CJ typically has faster shipping, better for higher markup
        markup = random.uniform(3.5, 5.0)
        estimated_retail = round(total_cost * markup, 2)
        
        weekly_orders = int(orders / 4)
        
        return {
            'product_name': raw_data.get('name', ''),
            'category': raw_data.get('category', 'General'),
            'supplier_cost': total_cost,
            'estimated_retail_price': estimated_retail,
            'supplier_link': f"https://cjdropshipping.com/product/{raw_data.get('sku', '')}",
            'supplier_order_velocity': weekly_orders,
            'supplier_rating': raw_data.get('rating', 0),
            'supplier_reviews': raw_data.get('reviews', 0),
            'supplier_orders_30d': orders,
            'supplier_processing_days': raw_data.get('processing_days', 2),
            'supplier_shipping_days': raw_data.get('shipping_days', 10),
            'image_url': raw_data.get('image'),
            'product_variants': raw_data.get('variants', []),
            'cj_fast_shipping': raw_data.get('shipping_days', 10) <= 10,
        }
