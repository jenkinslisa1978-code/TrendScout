"""
Scoring Engine

Unified scoring pipeline that calculates all product scores:
- trend_score: Viral potential
- margin_score: Profit potential  
- competition_score: Market accessibility
- ad_activity_score: Market validation
- supplier_demand_score: Supply chain signals
- market_score: Combined opportunity score

All scores are 0-100 scale.
"""

import logging
from typing import Dict, Any, Tuple, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Central scoring engine for ViralScout products.
    
    Calculates individual component scores and combined market_score.
    Designed for easy adjustment of weights and thresholds.
    """
    
    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        'trend': 0.25,
        'margin': 0.25,
        'competition': 0.20,
        'ad_activity': 0.15,
        'supplier_demand': 0.15,
    }
    
    # Market opportunity labels
    MARKET_LABELS = {
        90: ('massive', 'Massive Opportunity'),
        75: ('strong', 'Strong Opportunity'),
        60: ('competitive', 'Competitive'),
        0: ('saturated', 'Saturated'),
    }
    
    def __init__(self, db=None):
        self.db = db
    
    def calculate_all_scores(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all scores for a product.
        
        Returns dict with all score fields ready for database update.
        """
        # Calculate individual component scores
        trend_score = self.calculate_trend_score(product)
        margin_score = self.calculate_margin_score(product)
        competition_score = self.calculate_competition_score(product)
        ad_activity_score = self.calculate_ad_activity_score(product)
        supplier_demand_score = self.calculate_supplier_demand_score(product)
        
        # Calculate combined market score
        market_score = self.calculate_market_score(
            trend_score,
            margin_score,
            competition_score,
            ad_activity_score,
            supplier_demand_score
        )
        
        # Get market label
        market_label, market_description = self.get_market_label(market_score)
        
        # Additional derived scores
        early_trend_score, early_trend_label = self.calculate_early_trend_score(product)
        success_probability = self.calculate_success_probability(product, market_score)
        
        return {
            # Component scores
            'trend_score': trend_score,
            'margin_score': margin_score,
            'competition_score': competition_score,
            'ad_activity_score': ad_activity_score,
            'supplier_demand_score': supplier_demand_score,
            
            # Combined market score
            'market_score': market_score,
            'market_label': market_label,
            'market_description': market_description,
            'market_score_breakdown': {
                'trend': trend_score,
                'margin': margin_score,
                'competition': competition_score,
                'ad_activity': ad_activity_score,
                'supplier_demand': supplier_demand_score,
            },
            
            # Derived scores
            'early_trend_score': early_trend_score,
            'early_trend_label': early_trend_label,
            'success_probability': success_probability,
            
            # Metadata
            'scores_updated_at': datetime.now(timezone.utc).isoformat(),
        }
    
    def calculate_trend_score(self, product: Dict[str, Any]) -> int:
        """
        Calculate trend score (0-100) based on viral signals.
        
        Signals:
        - TikTok views (primary indicator)
        - View growth rate
        - Engagement rate
        - Trend stage
        """
        tiktok_views = product.get('tiktok_views', 0)
        view_growth = product.get('view_growth_rate', 0)
        engagement = product.get('engagement_rate', 0)
        trend_stage = product.get('trend_stage', 'rising')
        
        score = 0
        
        # TikTok views (50% of trend score)
        if tiktok_views >= 50000000:
            score += 50
        elif tiktok_views >= 25000000:
            score += 43
        elif tiktok_views >= 10000000:
            score += 36
        elif tiktok_views >= 5000000:
            score += 28
        elif tiktok_views >= 1000000:
            score += 20
        elif tiktok_views >= 100000:
            score += 12
        else:
            score += min(12, int(tiktok_views / 10000))
        
        # View growth rate (25%)
        if view_growth >= 40:
            score += 25
        elif view_growth >= 25:
            score += 20
        elif view_growth >= 15:
            score += 15
        elif view_growth >= 5:
            score += 10
        else:
            score += 5
        
        # Engagement rate (15%)
        if engagement >= 8:
            score += 15
        elif engagement >= 5:
            score += 12
        elif engagement >= 3:
            score += 8
        else:
            score += 4
        
        # Trend stage bonus (10%)
        stage_scores = {'early': 10, 'rising': 8, 'peak': 5, 'saturated': 2}
        score += stage_scores.get(trend_stage, 5)
        
        return min(100, max(0, score))
    
    def calculate_margin_score(self, product: Dict[str, Any]) -> int:
        """
        Calculate margin score (0-100) based on profit potential.
        
        Signals:
        - Absolute margin (GBP)
        - Margin percentage
        - Price point viability
        """
        supplier_cost = product.get('supplier_cost', 0)
        retail_price = product.get('estimated_retail_price', 0)
        
        if retail_price <= 0 or supplier_cost <= 0:
            return 30  # Default for missing data
        
        margin = retail_price - supplier_cost
        margin_percent = (margin / retail_price) * 100
        
        score = 0
        
        # Absolute margin (60%)
        if margin >= 50:
            score += 60
        elif margin >= 35:
            score += 52
        elif margin >= 25:
            score += 44
        elif margin >= 18:
            score += 36
        elif margin >= 12:
            score += 28
        elif margin >= 8:
            score += 20
        else:
            score += max(10, int(margin * 2.5))
        
        # Margin percentage (40%)
        if margin_percent >= 75:
            score += 40
        elif margin_percent >= 60:
            score += 35
        elif margin_percent >= 50:
            score += 28
        elif margin_percent >= 40:
            score += 22
        elif margin_percent >= 30:
            score += 16
        else:
            score += 10
        
        return min(100, max(0, score))
    
    def calculate_competition_score(self, product: Dict[str, Any]) -> int:
        """
        Calculate competition score (0-100). Higher = LESS competition = better.
        
        Signals:
        - Active competitor stores
        - Competition level
        - Market saturation
        - New stores this week
        """
        competitor_stores = product.get('active_competitor_stores', 0)
        competition_level = product.get('competition_level', 'medium')
        saturation = product.get('market_saturation', 50)
        new_stores = product.get('new_competitor_stores_week', 0)
        
        score = 0
        
        # Competitor store count (45%) - INVERSE: fewer stores = higher score
        if competitor_stores == 0:
            score += 38  # No validation
        elif competitor_stores < 15:
            score += 45  # Sweet spot - some validation, low competition
        elif competitor_stores < 35:
            score += 38
        elif competitor_stores < 60:
            score += 28
        elif competitor_stores < 100:
            score += 18
        else:
            score += 8
        
        # Competition level (30%)
        level_scores = {'low': 30, 'medium': 18, 'high': 8}
        score += level_scores.get(competition_level, 15)
        
        # Market saturation (25%) - INVERSE: lower saturation = higher score
        saturation_score = max(0, 25 - int(saturation * 0.25))
        score += saturation_score
        
        # New stores penalty (if many new entrants)
        if new_stores > 15:
            score = max(0, score - 10)
        elif new_stores > 8:
            score = max(0, score - 5)
        
        return min(100, max(0, score))
    
    def calculate_ad_activity_score(self, product: Dict[str, Any]) -> int:
        """
        Calculate ad activity score (0-100).
        
        Moderate ad activity = validated market (good)
        Very high ad activity = saturated market (less good)
        Very low ad activity = unvalidated market (risky)
        
        Sweet spot: 50-150 active ads
        """
        ad_count = product.get('ad_count', 0)
        ad_growth = product.get('recent_ad_growth', 0)
        validation_level = product.get('ad_validation_level', 'unknown')
        
        score = 0
        
        # Ad count - sweet spot scoring (60%)
        if ad_count == 0:
            score += 25  # Unvalidated
        elif ad_count < 30:
            score += 40  # Early stage
        elif ad_count < 75:
            score += 55  # Growing validation
        elif ad_count < 150:
            score += 60  # Sweet spot
        elif ad_count < 250:
            score += 50  # Getting crowded
        elif ad_count < 400:
            score += 35  # High competition
        else:
            score += 20  # Saturated
        
        # Ad growth trend (25%)
        if 10 <= ad_growth <= 30:
            score += 25  # Healthy growth
        elif 5 <= ad_growth < 10:
            score += 20
        elif 30 < ad_growth <= 50:
            score += 18  # Very fast growth
        elif ad_growth > 50:
            score += 12  # Too fast (saturating)
        elif ad_growth < 0:
            score += 8  # Declining
        else:
            score += 15
        
        # Validation level bonus (15%)
        validation_scores = {
            'highly_validated': 15,
            'validated': 12,
            'emerging': 10,
            'early': 8,
            'unvalidated': 5,
        }
        score += validation_scores.get(validation_level, 8)
        
        return min(100, max(0, score))
    
    def calculate_supplier_demand_score(self, product: Dict[str, Any]) -> int:
        """
        Calculate supplier demand score (0-100) based on supply chain signals.
        
        Signals:
        - Supplier order velocity (orders/week)
        - Supplier rating
        - Processing/shipping time
        - Total 30-day orders
        """
        order_velocity = product.get('supplier_order_velocity', 0)
        orders_30d = product.get('supplier_orders_30d', 0)
        supplier_rating = product.get('supplier_rating', 0)
        processing_days = product.get('supplier_processing_days', 5)
        shipping_days = product.get('supplier_shipping_days', 15)
        
        score = 0
        
        # Order velocity (40%)
        if order_velocity >= 3000:
            score += 40
        elif order_velocity >= 1500:
            score += 35
        elif order_velocity >= 800:
            score += 30
        elif order_velocity >= 400:
            score += 24
        elif order_velocity >= 150:
            score += 18
        elif order_velocity >= 50:
            score += 12
        else:
            score += 6
        
        # 30-day orders (25%)
        if orders_30d >= 10000:
            score += 25
        elif orders_30d >= 5000:
            score += 22
        elif orders_30d >= 2000:
            score += 18
        elif orders_30d >= 500:
            score += 12
        else:
            score += 6
        
        # Supplier rating (20%)
        if supplier_rating >= 4.7:
            score += 20
        elif supplier_rating >= 4.5:
            score += 17
        elif supplier_rating >= 4.2:
            score += 13
        elif supplier_rating >= 4.0:
            score += 9
        else:
            score += 5
        
        # Fulfillment speed (15%)
        total_days = processing_days + shipping_days
        if total_days <= 10:
            score += 15
        elif total_days <= 14:
            score += 12
        elif total_days <= 20:
            score += 8
        else:
            score += 4
        
        return min(100, max(0, score))
    
    def calculate_market_score(
        self,
        trend_score: int,
        margin_score: int,
        competition_score: int,
        ad_activity_score: int,
        supplier_demand_score: int
    ) -> int:
        """
        Calculate combined market opportunity score (0-100).
        
        Weighted combination of all component scores.
        """
        market_score = (
            trend_score * self.WEIGHTS['trend'] +
            margin_score * self.WEIGHTS['margin'] +
            competition_score * self.WEIGHTS['competition'] +
            ad_activity_score * self.WEIGHTS['ad_activity'] +
            supplier_demand_score * self.WEIGHTS['supplier_demand']
        )
        
        return min(100, max(0, round(market_score)))
    
    def get_market_label(self, market_score: int) -> Tuple[str, str]:
        """Get market opportunity label and description from score"""
        for threshold, (label, description) in sorted(
            self.MARKET_LABELS.items(), 
            reverse=True
        ):
            if market_score >= threshold:
                return label, description
        return 'saturated', 'Saturated'
    
    def calculate_early_trend_score(self, product: Dict[str, Any]) -> Tuple[int, str]:
        """
        Calculate early trend detection score (0-100).
        
        Identifies products with accelerating momentum.
        """
        view_growth = product.get('view_growth_rate', 0)
        engagement = product.get('engagement_rate', 0)
        order_velocity = product.get('supplier_order_velocity', 0)
        ad_count = product.get('ad_count', 0)
        competition = product.get('competition_level', 'medium')
        trend_stage = product.get('trend_stage', 'rising')
        
        score = 0
        
        # View growth rate (25%)
        if view_growth >= 35:
            score += 25
        elif view_growth >= 20:
            score += 20
        elif view_growth >= 10:
            score += 14
        else:
            score += 7
        
        # Engagement rate (20%)
        if engagement >= 7:
            score += 20
        elif engagement >= 5:
            score += 15
        elif engagement >= 3:
            score += 10
        else:
            score += 5
        
        # Supplier order velocity (20%)
        if order_velocity >= 2000:
            score += 20
        elif order_velocity >= 1000:
            score += 16
        elif order_velocity >= 400:
            score += 12
        else:
            score += 6
        
        # Ad activity - low is good for early trends (20%)
        if ad_count < 50:
            score += 20  # Early opportunity
        elif ad_count < 100:
            score += 15
        elif ad_count < 200:
            score += 10
        else:
            score += 5
        
        # Competition (15%)
        comp_scores = {'low': 15, 'medium': 10, 'high': 5}
        score += comp_scores.get(competition, 8)
        
        # Stage bonus
        if trend_stage == 'early':
            score = min(100, score + 10)
        elif trend_stage == 'rising':
            score = min(100, score + 5)
        
        score = min(100, max(0, score))
        
        # Determine label
        if score >= 85:
            label = 'exploding'
        elif score >= 65:
            label = 'rising'
        elif score >= 45:
            label = 'early_trend'
        else:
            label = 'stable'
        
        return score, label
    
    def calculate_success_probability(
        self, 
        product: Dict[str, Any], 
        market_score: int
    ) -> int:
        """
        Calculate success probability (0-100) based on all signals.
        
        Also considers:
        - Historical success (stores created, exports)
        - Proven winner status
        """
        stores_created = product.get('stores_created', 0)
        exports = product.get('exports_count', 0)
        proven_winner = product.get('proven_winner', False)
        
        # Base from market score
        base_probability = int(market_score * 0.7)
        
        # Bonus for proven success
        if proven_winner:
            base_probability += 15
        
        if stores_created >= 5:
            base_probability += 10
        elif stores_created >= 2:
            base_probability += 5
        
        if exports >= 3:
            base_probability += 5
        
        return min(100, max(0, base_probability))
    
    async def batch_update_scores(self, limit: int = 100) -> Dict[str, int]:
        """
        Batch update scores for all products.
        
        Returns stats on updates.
        """
        if self.db is None:
            raise ValueError("Database connection required for batch updates")
        
        stats = {'updated': 0, 'failed': 0}
        
        cursor = self.db.products.find({}, {"_id": 0})
        products = await cursor.to_list(limit)
        
        for product in products:
            try:
                scores = self.calculate_all_scores(product)
                
                await self.db.products.update_one(
                    {"id": product['id']},
                    {"$set": scores}
                )
                stats['updated'] += 1
                
            except Exception as e:
                logger.error(f"Failed to update scores for {product.get('product_name')}: {e}")
                stats['failed'] += 1
        
        return stats
