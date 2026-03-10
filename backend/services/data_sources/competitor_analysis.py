"""
Competitor Analysis Module

Estimates competitor store counts, pricing intelligence, and market saturation.
Designed to be swapped with real data sources (SerpAPI, store detection) later.
"""

import os
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

from .base import (
    BaseDataSource,
    SimulatedDataSource,
    DataSourceConfig,
    DataSourceType,
    DataConfidenceLevel
)


class CompetitorIntelligence(SimulatedDataSource):
    """
    Competitor intelligence data source.
    
    Estimates:
    - Number of stores selling each product
    - Average store prices
    - New stores this week
    - Price distribution
    
    Live sources (future):
    - SerpAPI for Google Shopping results
    - Shopify store detection
    - Direct competitor monitoring
    """
    
    def __init__(self, db):
        config = DataSourceConfig(
            name="competitor_intelligence",
            source_type=DataSourceType.COMPETITOR,
            api_key=os.environ.get('SERPAPI_KEY'),
            base_url="https://serpapi.com/search",
            rate_limit_per_minute=10,
            cache_ttl_minutes=360,  # 6 hours
        )
        super().__init__(db, config)
    
    async def fetch_raw_data(self, product_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Fetch competitor data for products"""
        
        if self.config.api_key:
            try:
                return await self._fetch_serpapi_shopping(product_name)
            except Exception as e:
                self.logger.warning(f"SerpAPI failed: {e}")
        
        # Generate estimated data based on product signals
        return await self._estimate_competitor_data(product_name)
    
    async def _fetch_serpapi_shopping(self, product_name: str) -> List[Dict[str, Any]]:
        """Fetch from SerpAPI Google Shopping"""
        params = {
            'engine': 'google_shopping',
            'google_domain': 'google.co.uk',
            'q': product_name,
            'api_key': self.config.api_key,
        }
        
        data = await self._make_request(self.config.base_url, params=params)
        return self._parse_shopping_results(data)
    
    def _parse_shopping_results(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse Google Shopping results"""
        results = []
        for item in data.get('shopping_results', []):
            results.append({
                'store_name': item.get('source', 'Unknown'),
                'price': self._parse_price(item.get('price', '0')),
                'product_link': item.get('link', ''),
                'has_ads': item.get('sponsored', False),
                'rating': item.get('rating', 0),
                'reviews': item.get('reviews', 0),
            })
        return results
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        try:
            # Remove currency symbols and convert
            cleaned = ''.join(c for c in price_str if c.isdigit() or c == '.')
            return float(cleaned) if cleaned else 0
        except:
            return 0
    
    async def _estimate_competitor_data(self, product_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Estimate competitor data based on product signals.
        This is the simulated fallback when live APIs aren't available.
        """
        # Get product from database if name provided
        if product_name:
            product = await self.db.products.find_one(
                {"product_name": {"$regex": product_name, "$options": "i"}},
                {"_id": 0}
            )
        else:
            # Get all products that need competitor data
            cursor = self.db.products.find({}, {"_id": 0})
            products = await cursor.to_list(100)
            return [self._generate_competitor_estimate(p) for p in products]
        
        if product:
            return [self._generate_competitor_estimate(product)]
        return []
    
    def _generate_competitor_estimate(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate estimated competitor data based on product signals.
        
        Estimation logic:
        - High ad count = more competitors
        - High TikTok views = more market interest = more stores
        - Competition level affects store density
        - Trend stage affects new store rate
        """
        ad_count = product.get('ad_count', 0)
        tiktok_views = product.get('tiktok_views', 0)
        competition_level = product.get('competition_level', 'medium')
        trend_stage = product.get('trend_stage', 'rising')
        retail_price = product.get('estimated_retail_price', 0)
        
        # Base store count from competition level
        base_stores = {
            'low': random.randint(5, 20),
            'medium': random.randint(20, 60),
            'high': random.randint(60, 150),
        }.get(competition_level, 30)
        
        # Adjust based on ad count
        ad_multiplier = 1.0
        if ad_count > 300:
            ad_multiplier = 1.8
        elif ad_count > 150:
            ad_multiplier = 1.4
        elif ad_count > 50:
            ad_multiplier = 1.2
        elif ad_count < 20:
            ad_multiplier = 0.7
        
        # Adjust based on views
        view_multiplier = 1.0
        if tiktok_views > 50000000:
            view_multiplier = 1.5
        elif tiktok_views > 10000000:
            view_multiplier = 1.2
        elif tiktok_views < 1000000:
            view_multiplier = 0.8
        
        estimated_stores = int(base_stores * ad_multiplier * view_multiplier)
        
        # New stores this week based on trend stage
        new_store_rates = {
            'early': random.randint(3, 8),
            'rising': random.randint(5, 15),
            'peak': random.randint(8, 20),
            'saturated': random.randint(1, 5),
        }
        new_stores_week = new_store_rates.get(trend_stage, 5)
        
        # Price distribution
        if retail_price > 0:
            price_variance = retail_price * 0.25
            min_price = max(1, retail_price - price_variance)
            max_price = retail_price + price_variance
            avg_price = retail_price + random.uniform(-5, 10)
        else:
            min_price, max_price, avg_price = 0, 0, 0
        
        # Generate sample competitor stores
        competitor_stores = self._generate_sample_stores(
            estimated_stores, 
            retail_price, 
            competition_level
        )
        
        return {
            'product_name': product.get('product_name', ''),
            'product_id': product.get('id', ''),
            'competitor_store_count': estimated_stores,
            'new_stores_this_week': new_stores_week,
            'average_store_price': round(avg_price, 2),
            'min_price': round(min_price, 2),
            'max_price': round(max_price, 2),
            'price_range': {'min': round(min_price, 2), 'max': round(max_price, 2)},
            'competitor_stores': competitor_stores,
            'market_saturation': self._calculate_saturation(estimated_stores, competition_level),
            'data_source': 'estimated',
            'estimation_confidence': 'medium',
        }
    
    def _generate_sample_stores(
        self, 
        total_stores: int, 
        base_price: float, 
        competition: str
    ) -> List[Dict[str, Any]]:
        """Generate sample competitor store data"""
        store_prefixes = [
            'Quick', 'Best', 'Top', 'Premium', 'Smart', 'Value', 
            'Direct', 'Pro', 'Elite', 'Super', 'Mega', 'Ultra'
        ]
        store_suffixes = [
            'Shop', 'Store', 'Market', 'Deals', 'Hub', 'Zone', 
            'Express', 'Outlet', 'Central', 'Direct', 'Plus', 'Mall'
        ]
        
        num_samples = min(10, total_stores)
        stores = []
        
        for i in range(num_samples):
            price_variance = base_price * random.uniform(-0.25, 0.30)
            store_price = max(1, base_price + price_variance)
            
            # More stores have ads in high competition
            ad_probability = {'low': 0.3, 'medium': 0.5, 'high': 0.7}.get(competition, 0.5)
            has_ads = random.random() < ad_probability
            
            stores.append({
                'id': f'comp_{i}_{random.randint(1000, 9999)}',
                'name': f"{random.choice(store_prefixes)}{random.choice(store_suffixes)}",
                'price': round(store_price, 2),
                'currency': 'GBP',
                'has_active_ads': has_ads,
                'estimated_monthly_sales': random.randint(10, 300) if has_ads else random.randint(5, 80),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'reviews_count': random.randint(10, 500),
                'last_seen': datetime.now(timezone.utc).isoformat(),
            })
        
        # Sort by price
        stores.sort(key=lambda x: x['price'])
        return stores
    
    def _calculate_saturation(self, store_count: int, competition: str) -> int:
        """Calculate market saturation score (0-100)"""
        base_saturation = {
            'low': random.randint(15, 35),
            'medium': random.randint(35, 60),
            'high': random.randint(60, 85),
        }.get(competition, 45)
        
        # Adjust for store count
        if store_count > 100:
            base_saturation = min(95, base_saturation + 20)
        elif store_count > 50:
            base_saturation = min(90, base_saturation + 10)
        elif store_count < 15:
            base_saturation = max(10, base_saturation - 15)
        
        return base_saturation
    
    def normalize_product(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize competitor data to update product record"""
        return {
            'active_competitor_stores': raw_data.get('competitor_store_count', 0),
            'new_competitor_stores_week': raw_data.get('new_stores_this_week', 0),
            'avg_selling_price': raw_data.get('average_store_price', 0),
            'price_range': raw_data.get('price_range'),
            'market_saturation': raw_data.get('market_saturation', 0),
            'competitor_data_source': raw_data.get('data_source', 'estimated'),
            'competitor_confidence': raw_data.get('estimation_confidence', 'low'),
        }
    
    async def update_product_competitors(self, product_id: str) -> Dict[str, Any]:
        """
        Update competitor data for a specific product.
        Returns updated competitor intelligence.
        """
        product = await self.db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            return {'error': 'Product not found'}
        
        competitor_data = self._generate_competitor_estimate(product)
        normalized = self.normalize_product(competitor_data)
        
        # Update product in database
        await self.db.products.update_one(
            {"id": product_id},
            {"$set": {
                **normalized,
                'competitor_last_updated': datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            **competitor_data,
            'normalized_fields': normalized
        }
    
    async def batch_update_competitors(self, limit: int = 100) -> Dict[str, int]:
        """
        Batch update competitor data for multiple products.
        Returns stats on updates.
        """
        stats = {'updated': 0, 'failed': 0}
        
        # Get products that need competitor updates
        cursor = self.db.products.find({}, {"_id": 0, "id": 1, "product_name": 1})
        products = await cursor.to_list(limit)
        
        for product in products:
            try:
                await self.update_product_competitors(product['id'])
                stats['updated'] += 1
            except Exception as e:
                self.logger.error(f"Failed to update competitors for {product.get('product_name')}: {e}")
                stats['failed'] += 1
        
        return stats
