"""
Ad Activity Signals Module

Analyzes advertising activity to estimate market validation and competition.
Tracks ad spend, ad growth, and platform distribution.
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


class AdActivityAnalyzer(SimulatedDataSource):
    """
    Ad activity analysis data source.
    
    Estimates:
    - Total ad count across platforms
    - Ad activity score (0-100)
    - Recent ad growth trend
    - Platform distribution
    - Estimated monthly ad spend
    
    Live sources (future):
    - TikTok Ad Library API
    - Meta Ad Library API
    - Ad intelligence tools
    """
    
    def __init__(self, db):
        config = DataSourceConfig(
            name="ad_activity_signals",
            source_type=DataSourceType.AD_SIGNALS,
            api_key=os.environ.get('TIKTOK_AD_API_KEY'),
            rate_limit_per_minute=20,
            cache_ttl_minutes=240,  # 4 hours
        )
        super().__init__(db, config)
    
    async def fetch_raw_data(self, product_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Fetch ad activity data"""
        
        # Future: Integrate with ad library APIs
        if self.config.api_key:
            try:
                return await self._fetch_ad_library(product_name)
            except Exception as e:
                self.logger.warning(f"Ad Library API failed: {e}")
        
        # Generate estimated data
        return await self._estimate_ad_activity(product_name)
    
    async def _fetch_ad_library(self, product_name: str) -> List[Dict[str, Any]]:
        """Fetch from TikTok/Meta Ad Library"""
        # Implementation for live ad library APIs
        raise NotImplementedError("Ad Library API not configured")
    
    async def _estimate_ad_activity(self, product_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Estimate ad activity based on product signals.
        Uses existing ad_count and trend data to extrapolate activity.
        """
        if product_name:
            product = await self.db.products.find_one(
                {"product_name": {"$regex": product_name, "$options": "i"}},
                {"_id": 0}
            )
            if product:
                return [self._generate_ad_estimate(product)]
            return []
        
        # Process all products
        cursor = self.db.products.find({}, {"_id": 0})
        products = await cursor.to_list(100)
        return [self._generate_ad_estimate(p) for p in products]
    
    def _generate_ad_estimate(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate estimated ad activity based on product signals.
        
        Estimation logic:
        - Base ad count from product
        - Platform distribution based on category
        - Growth rate based on trend stage
        - Ad spend estimation from ad count
        """
        base_ad_count = product.get('ad_count', 0)
        tiktok_views = product.get('tiktok_views', 0)
        trend_stage = product.get('trend_stage', 'rising')
        category = product.get('category', 'General')
        competition = product.get('competition_level', 'medium')
        
        # Estimate total ads with variation
        estimated_ad_count = max(0, self._add_int_variation(base_ad_count, 0.15))
        
        # Platform distribution based on category
        platform_weights = self._get_platform_weights(category)
        platform_distribution = {
            'tiktok': int(estimated_ad_count * platform_weights['tiktok']),
            'facebook': int(estimated_ad_count * platform_weights['facebook']),
            'instagram': int(estimated_ad_count * platform_weights['instagram']),
            'google': int(estimated_ad_count * platform_weights['google']),
        }
        
        # Ad activity score (0-100)
        ad_activity_score = self._calculate_ad_activity_score(
            estimated_ad_count, 
            tiktok_views, 
            competition
        )
        
        # Recent ad growth based on trend stage
        growth_rates = {
            'early': random.uniform(15, 40),      # Growing fast
            'rising': random.uniform(25, 60),     # Very active
            'peak': random.uniform(5, 20),        # Slowing
            'saturated': random.uniform(-10, 10), # Stagnant/declining
        }
        recent_ad_growth = growth_rates.get(trend_stage, 10)
        
        # Estimate monthly ad spend (avg £100-200 per ad per month)
        avg_spend_per_ad = random.randint(80, 200)
        estimated_monthly_spend = estimated_ad_count * avg_spend_per_ad
        
        # Weekly new ads
        new_ads_week = max(0, int(estimated_ad_count * (recent_ad_growth / 100) / 4))
        
        return {
            'product_name': product.get('product_name', ''),
            'product_id': product.get('id', ''),
            'estimated_ad_count': estimated_ad_count,
            'ad_activity_score': ad_activity_score,
            'recent_ad_growth': round(recent_ad_growth, 1),
            'new_ads_this_week': new_ads_week,
            'platform_distribution': platform_distribution,
            'estimated_monthly_ad_spend': estimated_monthly_spend,
            'top_platform': max(platform_distribution, key=platform_distribution.get),
            'ad_validation_level': self._get_validation_level(ad_activity_score),
            'data_source': 'estimated',
        }
    
    def _get_platform_weights(self, category: str) -> Dict[str, float]:
        """Get platform distribution weights based on category"""
        # Category-specific platform preferences
        category_weights = {
            'Beauty': {'tiktok': 0.45, 'facebook': 0.20, 'instagram': 0.30, 'google': 0.05},
            'Fashion': {'tiktok': 0.40, 'facebook': 0.15, 'instagram': 0.40, 'google': 0.05},
            'Electronics': {'tiktok': 0.30, 'facebook': 0.30, 'instagram': 0.15, 'google': 0.25},
            'Home Decor': {'tiktok': 0.35, 'facebook': 0.25, 'instagram': 0.30, 'google': 0.10},
            'Health & Fitness': {'tiktok': 0.40, 'facebook': 0.30, 'instagram': 0.20, 'google': 0.10},
            'Kitchen': {'tiktok': 0.35, 'facebook': 0.35, 'instagram': 0.15, 'google': 0.15},
            'Pet Supplies': {'tiktok': 0.30, 'facebook': 0.40, 'instagram': 0.20, 'google': 0.10},
        }
        
        return category_weights.get(category, {
            'tiktok': 0.35, 'facebook': 0.30, 'instagram': 0.25, 'google': 0.10
        })
    
    def _calculate_ad_activity_score(
        self, 
        ad_count: int, 
        tiktok_views: int, 
        competition: str
    ) -> int:
        """
        Calculate ad activity score (0-100).
        
        Higher score = more active advertising market = validated demand
        But also more competition
        """
        score = 0
        
        # Ad count component (40%)
        if ad_count >= 300:
            score += 40
        elif ad_count >= 150:
            score += 35
        elif ad_count >= 75:
            score += 30
        elif ad_count >= 30:
            score += 20
        elif ad_count >= 10:
            score += 10
        else:
            score += 5
        
        # Market validation from views (30%)
        if tiktok_views >= 50000000:
            score += 30
        elif tiktok_views >= 20000000:
            score += 25
        elif tiktok_views >= 5000000:
            score += 20
        elif tiktok_views >= 1000000:
            score += 15
        else:
            score += 10
        
        # Competition adjustment (30%)
        comp_scores = {'low': 30, 'medium': 20, 'high': 10}
        score += comp_scores.get(competition, 15)
        
        return min(100, max(0, score))
    
    def _get_validation_level(self, ad_score: int) -> str:
        """Get market validation level from ad score"""
        if ad_score >= 80:
            return 'highly_validated'
        elif ad_score >= 60:
            return 'validated'
        elif ad_score >= 40:
            return 'emerging'
        elif ad_score >= 20:
            return 'early'
        return 'unvalidated'
    
    def normalize_product(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize ad activity data for product update"""
        return {
            'ad_count': raw_data.get('estimated_ad_count', 0),
            'ad_activity_score': raw_data.get('ad_activity_score', 0),
            'recent_ad_growth': raw_data.get('recent_ad_growth', 0),
            'new_ads_this_week': raw_data.get('new_ads_this_week', 0),
            'estimated_monthly_ad_spend': raw_data.get('estimated_monthly_ad_spend', 0),
            'ad_platform_distribution': raw_data.get('platform_distribution'),
            'ad_validation_level': raw_data.get('ad_validation_level', 'unknown'),
            'ad_data_source': raw_data.get('data_source', 'estimated'),
        }
    
    async def update_product_ad_activity(self, product_id: str) -> Dict[str, Any]:
        """Update ad activity data for a specific product"""
        product = await self.db.products.find_one({"id": product_id}, {"_id": 0})
        if not product:
            return {'error': 'Product not found'}
        
        ad_data = self._generate_ad_estimate(product)
        normalized = self.normalize_product(ad_data)
        
        await self.db.products.update_one(
            {"id": product_id},
            {"$set": {
                **normalized,
                'ad_activity_last_updated': datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return ad_data
    
    async def batch_update_ad_activity(self, limit: int = 100) -> Dict[str, int]:
        """Batch update ad activity for multiple products"""
        stats = {'updated': 0, 'failed': 0}
        
        cursor = self.db.products.find({}, {"_id": 0, "id": 1, "product_name": 1})
        products = await cursor.to_list(limit)
        
        for product in products:
            try:
                await self.update_product_ad_activity(product['id'])
                stats['updated'] += 1
            except Exception as e:
                self.logger.error(f"Failed to update ad activity for {product.get('product_name')}: {e}")
                stats['failed'] += 1
        
        return stats
