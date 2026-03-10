"""
Trend Data Sources

Fetches trending product data from TikTok and Amazon.
Supports both live APIs (when available) and simulated data.
"""

import os
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import aiohttp

from .base import (
    BaseDataSource, 
    SimulatedDataSource,
    DataSourceConfig, 
    DataSourceType,
    DataConfidenceLevel
)


# Curated TikTok trending products (fallback data)
TIKTOK_TRENDING_PRODUCTS = [
    {
        'name': 'LED Sunset Projection Lamp',
        'category': 'Home Decor',
        'description': 'USB sunset projection lamp creating viral golden hour aesthetic for photos and room ambiance',
        'views': 45000000,
        'ads': 234,
        'competition': 'medium',
        'retail_price': 32.99,
        'supplier_cost': 8.50,
        'hashtags': ['sunsetlamp', 'roomdecor', 'aesthetic'],
        'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=600&fit=crop',
    },
    {
        'name': 'Cloud Pillow Slides',
        'category': 'Fashion',
        'description': 'Ultra-soft EVA pillow slides with thick cushioned sole for ultimate comfort',
        'views': 89000000,
        'ads': 567,
        'competition': 'high',
        'retail_price': 24.99,
        'supplier_cost': 4.20,
        'hashtags': ['cloudslides', 'comfyshoes', 'tiktokmademebuyit'],
        'image': 'https://images.unsplash.com/photo-1603487742131-4160ec999306?w=600&h=600&fit=crop',
    },
    {
        'name': 'Portable Bladeless Neck Fan',
        'category': 'Electronics',
        'description': 'Bladeless wearable neck fan with LED display and 3 cooling speeds',
        'views': 32000000,
        'ads': 189,
        'competition': 'medium',
        'retail_price': 29.99,
        'supplier_cost': 9.00,
        'hashtags': ['neckfan', 'summermustave', 'staycool'],
        'image': 'https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=600&h=600&fit=crop',
    },
    {
        'name': 'Ice Roller Face Massager',
        'category': 'Beauty',
        'description': 'Stainless steel ice roller for face depuffing and morning skincare routine',
        'views': 28000000,
        'ads': 145,
        'competition': 'low',
        'retail_price': 14.99,
        'supplier_cost': 2.80,
        'hashtags': ['iceroller', 'skincare', 'morningroutine'],
        'image': 'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=600&h=600&fit=crop',
    },
    {
        'name': 'Smart Galaxy Star Projector',
        'category': 'Home Decor',
        'description': 'LED star projector with music sync, app control and rotating nebula effect',
        'views': 52000000,
        'ads': 312,
        'competition': 'high',
        'retail_price': 49.99,
        'supplier_cost': 15.00,
        'hashtags': ['galaxyprojector', 'roomtour', 'ledlights'],
        'image': 'https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=600&h=600&fit=crop',
    },
    {
        'name': 'Scalp Massager Shampoo Brush',
        'category': 'Beauty',
        'description': 'Silicone scalp massager for hair growth stimulation and deep cleaning',
        'views': 41000000,
        'ads': 98,
        'competition': 'low',
        'retail_price': 8.99,
        'supplier_cost': 1.20,
        'hashtags': ['scalpmassager', 'hairgrowth', 'selfcare'],
        'image': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&h=600&fit=crop',
    },
    {
        'name': 'Mini Pocket Projector 1080P',
        'category': 'Electronics',
        'description': 'Pocket-sized portable projector with WiFi casting and HDMI input',
        'views': 23000000,
        'ads': 167,
        'competition': 'medium',
        'retail_price': 129.99,
        'supplier_cost': 45.00,
        'hashtags': ['miniprojector', 'movienight', 'hometheater'],
        'image': 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=600&h=600&fit=crop',
    },
    {
        'name': 'MagSafe Car Phone Mount',
        'category': 'Electronics',
        'description': 'Magnetic car phone mount compatible with MagSafe, 360° rotation',
        'views': 18000000,
        'ads': 223,
        'competition': 'high',
        'retail_price': 24.99,
        'supplier_cost': 5.50,
        'hashtags': ['phonemount', 'cardecor', 'magsafe'],
        'image': 'https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=600&h=600&fit=crop',
    },
    {
        'name': 'Clear Acrylic Desk Organizer',
        'category': 'Home Office',
        'description': 'Minimalist acrylic desk organizer with multiple compartments for WFH setup',
        'views': 15000000,
        'ads': 76,
        'competition': 'low',
        'retail_price': 34.99,
        'supplier_cost': 8.00,
        'hashtags': ['desksetup', 'organization', 'aesthetic'],
        'image': 'https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=600&h=600&fit=crop',
    },
    {
        'name': 'Premium ANC Wireless Earbuds',
        'category': 'Electronics',
        'description': 'Active noise cancelling earbuds with 40hr battery and premium sound',
        'views': 67000000,
        'ads': 445,
        'competition': 'high',
        'retail_price': 49.99,
        'supplier_cost': 14.00,
        'hashtags': ['wirelessearbuds', 'techreview', 'musthave'],
        'image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&h=600&fit=crop',
    },
    {
        'name': 'Adjustable Posture Corrector',
        'category': 'Health & Fitness',
        'description': 'Back support brace for improved posture during work and exercise',
        'views': 34000000,
        'ads': 198,
        'competition': 'medium',
        'retail_price': 24.99,
        'supplier_cost': 6.00,
        'hashtags': ['posturecorrector', 'backpain', 'wellness'],
        'image': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop',
    },
    {
        'name': 'Reusable Pet Hair Remover',
        'category': 'Pet Supplies',
        'description': 'Reusable lint roller for removing pet hair from furniture and clothes',
        'views': 29000000,
        'ads': 134,
        'competition': 'low',
        'retail_price': 16.99,
        'supplier_cost': 3.50,
        'hashtags': ['pethairremover', 'petowners', 'cleaninghacks'],
        'image': 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=600&fit=crop',
    },
    {
        'name': 'USB Rechargeable Blender Cup',
        'category': 'Kitchen',
        'description': 'Portable personal blender for smoothies and protein shakes on the go',
        'views': 48000000,
        'ads': 356,
        'competition': 'high',
        'retail_price': 34.99,
        'supplier_cost': 11.00,
        'hashtags': ['portableblender', 'smoothie', 'healthylifestyle'],
        'image': 'https://images.unsplash.com/photo-1570197571499-166b36435e9f?w=600&h=600&fit=crop',
    },
    {
        'name': 'RGB LED Strip Lights 50ft',
        'category': 'Home Decor',
        'description': 'Color-changing LED strips with app control and music sync feature',
        'views': 78000000,
        'ads': 489,
        'competition': 'high',
        'retail_price': 19.99,
        'supplier_cost': 5.00,
        'hashtags': ['ledlights', 'roomtransformation', 'aesthetic'],
        'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop',
    },
    {
        'name': 'Electric Heated Lunch Box',
        'category': 'Kitchen',
        'description': 'Portable food warmer with stainless steel container for office meals',
        'views': 21000000,
        'ads': 112,
        'competition': 'medium',
        'retail_price': 39.99,
        'supplier_cost': 12.00,
        'hashtags': ['lunchbox', 'mealprep', 'officelife'],
        'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=600&fit=crop',
    },
    # New trending products
    {
        'name': 'Wireless Charging Desk Pad',
        'category': 'Electronics',
        'description': 'Large desk pad with built-in wireless charging zones for multiple devices',
        'views': 19000000,
        'ads': 87,
        'competition': 'low',
        'retail_price': 59.99,
        'supplier_cost': 18.00,
        'hashtags': ['desksetup', 'wirelesscharging', 'techgadgets'],
        'image': 'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&h=600&fit=crop',
    },
    {
        'name': 'Smart Water Bottle Reminder',
        'category': 'Health & Fitness',
        'description': 'LED water bottle that glows to remind you to stay hydrated',
        'views': 36000000,
        'ads': 156,
        'competition': 'medium',
        'retail_price': 29.99,
        'supplier_cost': 7.50,
        'hashtags': ['hydration', 'wellness', 'smartgadgets'],
        'image': 'https://images.unsplash.com/photo-1523362628745-0c100150b504?w=600&h=600&fit=crop',
    },
    {
        'name': 'Mini Thermal Printer',
        'category': 'Electronics',
        'description': 'Pocket-sized Bluetooth thermal printer for labels, notes, and photos',
        'views': 42000000,
        'ads': 178,
        'competition': 'medium',
        'retail_price': 44.99,
        'supplier_cost': 15.00,
        'hashtags': ['miniprinter', 'aesthetic', 'journaling'],
        'image': 'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=600&h=600&fit=crop',
    },
]

# Amazon trending categories and products
AMAZON_TRENDING_PRODUCTS = [
    {
        'name': 'Weighted Sleep Eye Mask',
        'category': 'Health & Fitness',
        'description': 'Weighted eye mask with cooling gel insert for better sleep',
        'sales_rank': 1250,
        'reviews': 15000,
        'rating': 4.5,
        'retail_price': 24.99,
        'supplier_cost': 5.50,
        'bsr_change': -35,  # Negative = rising
        'image': 'https://images.unsplash.com/photo-1531353826977-0941b4779a1c?w=600&h=600&fit=crop',
    },
    {
        'name': 'Ergonomic Laptop Stand',
        'category': 'Home Office',
        'description': 'Adjustable aluminum laptop stand with phone holder and cable organizer',
        'sales_rank': 890,
        'reviews': 28000,
        'rating': 4.7,
        'retail_price': 39.99,
        'supplier_cost': 12.00,
        'bsr_change': -42,
        'image': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&h=600&fit=crop',
    },
    {
        'name': 'Electric Milk Frother',
        'category': 'Kitchen',
        'description': 'Handheld battery-powered milk frother for coffee and matcha',
        'sales_rank': 567,
        'reviews': 45000,
        'rating': 4.6,
        'retail_price': 12.99,
        'supplier_cost': 2.50,
        'bsr_change': -28,
        'image': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&h=600&fit=crop',
    },
    {
        'name': 'Collapsible Storage Bins Set',
        'category': 'Home Decor',
        'description': 'Set of 6 fabric storage bins with handles for closet organization',
        'sales_rank': 1100,
        'reviews': 22000,
        'rating': 4.4,
        'retail_price': 29.99,
        'supplier_cost': 8.00,
        'bsr_change': -51,
        'image': 'https://images.unsplash.com/photo-1558997519-83ea9252edf8?w=600&h=600&fit=crop',
    },
    {
        'name': 'Ceramic Coating Spray',
        'category': 'Automotive',
        'description': 'DIY ceramic car coating spray with hydrophobic protection',
        'sales_rank': 780,
        'reviews': 18000,
        'rating': 4.3,
        'retail_price': 19.99,
        'supplier_cost': 4.50,
        'bsr_change': -67,
        'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=600&fit=crop',
    },
    {
        'name': 'Yoga Wheel Set',
        'category': 'Health & Fitness',
        'description': '3-piece yoga wheel set for back stretching and flexibility training',
        'sales_rank': 2100,
        'reviews': 9500,
        'rating': 4.6,
        'retail_price': 34.99,
        'supplier_cost': 9.00,
        'bsr_change': -45,
        'image': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&h=600&fit=crop',
    },
    {
        'name': 'Magnetic Spice Jars Set',
        'category': 'Kitchen',
        'description': 'Set of 12 magnetic glass spice jars with stainless steel lids',
        'sales_rank': 1450,
        'reviews': 11000,
        'rating': 4.5,
        'retail_price': 44.99,
        'supplier_cost': 14.00,
        'bsr_change': -38,
        'image': 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600&h=600&fit=crop',
    },
    {
        'name': 'Self-Watering Plant Pots',
        'category': 'Home Decor',
        'description': 'Set of 3 self-watering planters with water level indicator',
        'sales_rank': 980,
        'reviews': 16000,
        'rating': 4.4,
        'retail_price': 27.99,
        'supplier_cost': 7.00,
        'bsr_change': -55,
        'image': 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=600&h=600&fit=crop',
    },
]


class TikTokTrends(SimulatedDataSource):
    """
    TikTok trending products data source.
    
    Live API: TikTok Creative Center (requires business API access)
    Fallback: Curated trending product database
    """
    
    def __init__(self, db):
        config = DataSourceConfig(
            name="tiktok_trends",
            source_type=DataSourceType.TREND,
            api_key=os.environ.get('TIKTOK_API_KEY'),
            api_secret=os.environ.get('TIKTOK_API_SECRET'),
            base_url="https://business-api.tiktok.com/open_api/v1.3",
            rate_limit_per_minute=30,
            cache_ttl_minutes=60,
        )
        super().__init__(db, config)
    
    async def fetch_raw_data(self, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch trending products from TikTok"""
        
        # Try live API if credentials available
        if self.config.api_key:
            try:
                return await self._fetch_live_api(category, limit)
            except Exception as e:
                self.logger.warning(f"TikTok API failed, using fallback: {e}")
        
        # Use curated data with variation
        return self._get_simulated_data(category, limit)
    
    async def _fetch_live_api(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Fetch from TikTok Creative Center API"""
        url = f"{self.config.base_url}/creative/trending_products/"
        headers = {
            'Access-Token': self.config.api_key,
            'Content-Type': 'application/json',
        }
        params = {'page_size': limit, 'region_code': 'GB'}
        if category:
            params['category'] = category
        
        data = await self._make_request(url, headers=headers, params=params)
        return data.get('data', {}).get('products', [])
    
    def _get_simulated_data(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Generate simulated TikTok trending data"""
        products = []
        
        for item in TIKTOK_TRENDING_PRODUCTS:
            if category and item['category'].lower() != category.lower():
                continue
            
            # Add realistic variation
            product = {
                **item,
                'views': self._add_int_variation(item['views'], 0.12),
                'ads': self._add_int_variation(item['ads'], 0.18),
                'engagement_rate': round(random.uniform(2.5, 8.5), 2),
                'view_growth_rate': round(random.uniform(5, 45), 1),
            }
            products.append(product)
            
            if len(products) >= limit:
                break
        
        return products
    
    def normalize_product(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize TikTok data to ViralScout schema"""
        return {
            'product_name': raw_data.get('name', raw_data.get('product_name', '')),
            'category': raw_data.get('category', 'General'),
            'short_description': raw_data.get('description', ''),
            'supplier_cost': raw_data.get('supplier_cost', raw_data.get('cost', 0)),
            'estimated_retail_price': raw_data.get('retail_price', raw_data.get('price', 0)),
            'tiktok_views': raw_data.get('views', raw_data.get('tiktok_views', 0)),
            'ad_count': raw_data.get('ads', raw_data.get('ad_count', 0)),
            'competition_level': raw_data.get('competition', 'medium'),
            'image_url': raw_data.get('image', raw_data.get('image_url')),
            'engagement_rate': raw_data.get('engagement_rate', 0),
            'view_growth_rate': raw_data.get('view_growth_rate', 0),
            'trend_hashtags': raw_data.get('hashtags', []),
        }


class AmazonTrends(SimulatedDataSource):
    """
    Amazon trending products data source.
    
    Live API: Amazon Product Advertising API or SerpAPI
    Fallback: Curated BSR movers data
    """
    
    def __init__(self, db):
        config = DataSourceConfig(
            name="amazon_trends",
            source_type=DataSourceType.TREND,
            api_key=os.environ.get('AMAZON_API_KEY') or os.environ.get('SERPAPI_KEY'),
            base_url="https://serpapi.com/search",
            rate_limit_per_minute=20,
            cache_ttl_minutes=120,
        )
        super().__init__(db, config)
    
    async def fetch_raw_data(self, category: Optional[str] = None, limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch trending products from Amazon"""
        
        if self.config.api_key and 'serpapi' in (self.config.api_key or '').lower():
            try:
                return await self._fetch_serpapi(category, limit)
            except Exception as e:
                self.logger.warning(f"SerpAPI failed, using fallback: {e}")
        
        return self._get_simulated_data(category, limit)
    
    async def _fetch_serpapi(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Fetch from SerpAPI Amazon search"""
        params = {
            'engine': 'amazon',
            'amazon_domain': 'amazon.co.uk',
            'type': 'search',
            'k': category or 'trending products',
            'api_key': self.config.api_key,
        }
        
        data = await self._make_request(self.config.base_url, params=params)
        return data.get('organic_results', [])[:limit]
    
    def _get_simulated_data(self, category: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Generate simulated Amazon trending data"""
        products = []
        
        for item in AMAZON_TRENDING_PRODUCTS:
            if category and item['category'].lower() != category.lower():
                continue
            
            product = {
                **item,
                'sales_rank': self._add_int_variation(item['sales_rank'], 0.2),
                'reviews': self._add_int_variation(item['reviews'], 0.1),
                'bsr_change': self._add_int_variation(item['bsr_change'], 0.25),
            }
            products.append(product)
            
            if len(products) >= limit:
                break
        
        return products
    
    def normalize_product(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Amazon data to ViralScout schema"""
        # Calculate trend signals from BSR
        bsr_change = raw_data.get('bsr_change', 0)
        reviews = raw_data.get('reviews', 0)
        
        # Estimate views from BSR and reviews
        estimated_views = reviews * 500 + abs(bsr_change) * 100000
        
        # Estimate ad count from competition
        estimated_ads = max(50, int(reviews / 100))
        
        return {
            'product_name': raw_data.get('name', ''),
            'category': raw_data.get('category', 'General'),
            'short_description': raw_data.get('description', ''),
            'supplier_cost': raw_data.get('supplier_cost', 0),
            'estimated_retail_price': raw_data.get('retail_price', 0),
            'tiktok_views': estimated_views,
            'ad_count': estimated_ads,
            'competition_level': 'high' if reviews > 20000 else 'medium' if reviews > 5000 else 'low',
            'image_url': raw_data.get('image'),
            'amazon_bsr': raw_data.get('sales_rank'),
            'amazon_bsr_change': bsr_change,
            'amazon_reviews': reviews,
            'amazon_rating': raw_data.get('rating'),
        }
