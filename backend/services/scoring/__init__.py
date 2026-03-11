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
    
    # Scoring weights (must sum to 1.0) — exact formula from product spec
    WEIGHTS = {
        'trend': 0.30,
        'margin': 0.25,
        'competition': 0.20,
        'ad_activity': 0.15,
        'supplier_demand': 0.10,
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
        Each component includes transparent reasoning.
        """
        # Calculate individual component scores with reasoning
        trend_score, trend_reasoning = self.calculate_trend_score(product)
        margin_score, margin_reasoning = self.calculate_margin_score(product)
        competition_score, competition_reasoning = self.calculate_competition_score(product)
        ad_activity_score, ad_reasoning = self.calculate_ad_activity_score(product)
        supplier_demand_score, supplier_reasoning = self.calculate_supplier_demand_score(product)
        
        # Calculate launch_score using exact formula
        launch_score = round(
            trend_score * self.WEIGHTS['trend'] +
            margin_score * self.WEIGHTS['margin'] +
            competition_score * self.WEIGHTS['competition'] +
            ad_activity_score * self.WEIGHTS['ad_activity'] +
            supplier_demand_score * self.WEIGHTS['supplier_demand']
        )
        launch_score = min(100, max(0, launch_score))
        
        # Get market label
        market_label, market_description = self.get_market_label(launch_score)
        
        # Additional derived scores
        early_trend_score, early_trend_label = self.calculate_early_trend_score(product)
        success_probability = self.calculate_success_probability(product, launch_score)
        
        # Build transparent score breakdown
        score_breakdown = {
            'trend': {
                'score': trend_score,
                'weight': self.WEIGHTS['trend'],
                'weighted': round(trend_score * self.WEIGHTS['trend'], 1),
                'reasoning': trend_reasoning,
            },
            'margin': {
                'score': margin_score,
                'weight': self.WEIGHTS['margin'],
                'weighted': round(margin_score * self.WEIGHTS['margin'], 1),
                'reasoning': margin_reasoning,
            },
            'competition': {
                'score': competition_score,
                'weight': self.WEIGHTS['competition'],
                'weighted': round(competition_score * self.WEIGHTS['competition'], 1),
                'reasoning': competition_reasoning,
            },
            'ad_activity': {
                'score': ad_activity_score,
                'weight': self.WEIGHTS['ad_activity'],
                'weighted': round(ad_activity_score * self.WEIGHTS['ad_activity'], 1),
                'reasoning': ad_reasoning,
            },
            'supplier_demand': {
                'score': supplier_demand_score,
                'weight': self.WEIGHTS['supplier_demand'],
                'weighted': round(supplier_demand_score * self.WEIGHTS['supplier_demand'], 1),
                'reasoning': supplier_reasoning,
            },
        }
        
        return {
            # Component scores
            'trend_score': trend_score,
            'margin_score': margin_score,
            'competition_score': competition_score,
            'ad_activity_score': ad_activity_score,
            'supplier_demand_score': supplier_demand_score,
            
            # Launch score (PRIMARY metric)
            'launch_score': launch_score,
            'launch_score_breakdown': score_breakdown,
            'market_label': market_label,
            'market_description': market_description,
            
            # Legacy market_score = launch_score
            'market_score': launch_score,
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
    
    def calculate_trend_score(self, product: Dict[str, Any]) -> tuple:
        """
        Calculate trend score (0-100) based on viral signals.
        Returns (score, reasoning).
        """
        tiktok_views = product.get('tiktok_views', 0)
        view_growth = product.get('view_growth_rate', 0)
        trend_velocity = product.get('trend_velocity', 0)
        amazon_bsr = product.get('amazon_bsr_change', 0)
        trend_stage = product.get('trend_stage', '')
        
        score = 0
        reasons = []
        
        # Amazon BSR change (strongest real signal)
        if amazon_bsr and amazon_bsr > 0:
            if amazon_bsr >= 1000:
                score += 40
                reasons.append(f"Explosive Amazon rank movement (+{amazon_bsr}%)")
            elif amazon_bsr >= 300:
                score += 32
                reasons.append(f"Strong Amazon rank surge (+{amazon_bsr}%)")
            elif amazon_bsr >= 100:
                score += 24
                reasons.append(f"Rising Amazon demand (+{amazon_bsr}%)")
            else:
                score += 15
                reasons.append(f"Moderate Amazon movement (+{amazon_bsr}%)")
        else:
            reasons.append("Amazon trend data unavailable")
        
        # Google Trends velocity (real data)
        if trend_velocity and trend_velocity != 0:
            if trend_velocity > 50:
                score += 25
                reasons.append(f"Google Trends surging (+{trend_velocity:.0f}%)")
            elif trend_velocity > 20:
                score += 20
                reasons.append(f"Google Trends rising (+{trend_velocity:.0f}%)")
            elif trend_velocity > 0:
                score += 12
                reasons.append(f"Google Trends stable (+{trend_velocity:.0f}%)")
            elif trend_velocity > -20:
                score += 6
                reasons.append(f"Google Trends flat ({trend_velocity:.0f}%)")
            else:
                score += 2
                reasons.append(f"Google Trends declining ({trend_velocity:.0f}%)")
        
        # TikTok views (if available)
        if tiktok_views and tiktok_views > 0:
            if tiktok_views >= 10000000:
                score += 20
                reasons.append(f"Viral on TikTok ({tiktok_views/1000000:.1f}M views)")
            elif tiktok_views >= 1000000:
                score += 15
                reasons.append(f"Strong TikTok presence ({tiktok_views/1000000:.1f}M views)")
            elif tiktok_views >= 100000:
                score += 10
            else:
                score += 5
        
        # View growth rate
        if view_growth and view_growth > 0:
            score += min(15, int(view_growth / 3))
        
        score = min(100, max(0, score))
        
        if not reasons:
            reasons.append("Trend data unavailable")
        
        return score, ". ".join(reasons)
    
    def calculate_margin_score(self, product: Dict[str, Any]) -> tuple:
        """
        Calculate margin score (0-100) based on profit potential.
        Returns (score, reasoning).
        """
        supplier_cost = product.get('supplier_cost', 0)
        retail_price = product.get('estimated_retail_price', 0)
        
        if not retail_price or retail_price <= 0 or not supplier_cost or supplier_cost <= 0:
            return 0, "Price or cost data unavailable — cannot calculate margin"
        
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
        
        score = min(100, max(0, score))
        reasoning = f"{margin_percent:.0f}% margin (£{margin:.2f} profit on £{retail_price:.2f} retail)"
        
        if margin_percent >= 50:
            reasoning += " — healthy margins"
        elif margin_percent >= 30:
            reasoning += " — acceptable margins"
        else:
            reasoning += " — tight margins, ad costs may erode profit"
        
        return score, reasoning
    
    def calculate_competition_score(self, product: Dict[str, Any]) -> tuple:
        """
        Calculate competition score (0-100). Higher = LESS competition = better.
        Returns (score, reasoning).
        """
        competition_level = product.get('competition_level', 'unknown')
        amazon_reviews = product.get('amazon_reviews', 0)
        
        score = 0
        reasons = []
        
        # Competition level
        if competition_level == 'low':
            score += 45
            reasons.append("Low competition — good entry window")
        elif competition_level == 'medium':
            score += 30
            reasons.append("Moderate competition — differentiation needed")
        elif competition_level == 'high':
            score += 12
            reasons.append("High competition — saturated market")
        else:
            score += 25
            reasons.append("Competition data unavailable")
        
        # Amazon review count as competition proxy
        if amazon_reviews and amazon_reviews > 0:
            if amazon_reviews < 100:
                score += 35
                reasons.append(f"Few reviews ({amazon_reviews}) — new market")
            elif amazon_reviews < 500:
                score += 28
                reasons.append(f"{amazon_reviews} reviews — growing market")
            elif amazon_reviews < 2000:
                score += 18
                reasons.append(f"{amazon_reviews} reviews — established market")
            else:
                score += 8
                reasons.append(f"{amazon_reviews} reviews — very established market")
        else:
            score += 15
        
        # Rating-based quality bar
        rating = product.get('amazon_rating', 0)
        if rating and rating >= 4.5:
            score += 10
            reasons.append(f"High quality bar ({rating} stars)")
        elif rating and rating >= 4.0:
            score += 15
            reasons.append(f"Good quality bar ({rating} stars)")
        elif rating and rating > 0:
            score += 20
            reasons.append(f"Low quality bar ({rating} stars) — room to compete")
        
        score = min(100, max(0, score))
        return score, ". ".join(reasons)
    
    def calculate_ad_activity_score(self, product: Dict[str, Any]) -> tuple:
        """
        Calculate ad activity score (0-100).
        Sweet spot: some ads = validated market, too many = saturated.
        Returns (score, reasoning).
        """
        ad_count = product.get('ad_count', 0)
        
        if not ad_count:
            return 40, "Ad activity data unavailable"
        
        if ad_count < 10:
            score = 55
            reasoning = f"{ad_count} active ads — early opportunity, unvalidated"
        elif ad_count < 30:
            score = 75
            reasoning = f"{ad_count} active ads — validated market, low competition"
        elif ad_count < 75:
            score = 85
            reasoning = f"{ad_count} active ads — sweet spot: proven demand, manageable competition"
        elif ad_count < 150:
            score = 65
            reasoning = f"{ad_count} active ads — getting crowded"
        elif ad_count < 300:
            score = 40
            reasoning = f"{ad_count} active ads — high ad competition, expect costly CPA"
        else:
            score = 20
            reasoning = f"{ad_count} active ads — saturated, very expensive to compete"
        
        return min(100, max(0, score)), reasoning
    
    def calculate_supplier_demand_score(self, product: Dict[str, Any]) -> tuple:
        """
        Calculate supplier demand score (0-100).
        Returns (score, reasoning).
        """
        order_velocity = product.get('supplier_order_velocity', 0)
        orders_30d = product.get('supplier_orders_30d', 0)
        supplier_rating = product.get('supplier_rating', 0)
        processing_days = product.get('supplier_processing_days', 0)
        shipping_days = product.get('supplier_shipping_days', 0)
        supplier_cost = product.get('supplier_cost', 0)
        
        # If we have no supplier data at all, mark as unavailable
        has_data = any([order_velocity, orders_30d, supplier_rating, supplier_cost])
        if not has_data:
            return 0, "Supplier data unavailable"
        
        score = 0
        reasons = []
        
        # Order velocity (40%)
        if order_velocity >= 3000:
            score += 40
            reasons.append(f"Very high demand ({order_velocity} orders/week)")
        elif order_velocity >= 1000:
            score += 32
            reasons.append(f"Strong demand ({order_velocity} orders/week)")
        elif order_velocity >= 400:
            score += 24
        elif order_velocity >= 100:
            score += 16
        elif order_velocity > 0:
            score += 8
        
        # 30-day orders (25%)
        if orders_30d >= 10000:
            score += 25
        elif orders_30d >= 5000:
            score += 20
        elif orders_30d >= 1000:
            score += 15
        elif orders_30d > 0:
            score += 8
        
        # Supplier rating (20%)
        if supplier_rating >= 4.7:
            score += 20
            reasons.append(f"Top-rated supplier ({supplier_rating} stars)")
        elif supplier_rating >= 4.3:
            score += 15
        elif supplier_rating >= 4.0:
            score += 10
        elif supplier_rating > 0:
            score += 5
        
        # Fulfillment speed (15%)
        total_days = (processing_days or 0) + (shipping_days or 0)
        if total_days > 0:
            if total_days <= 10:
                score += 15
                reasons.append(f"Fast fulfillment ({total_days} days)")
            elif total_days <= 14:
                score += 10
            elif total_days <= 21:
                score += 6
            else:
                score += 2
                reasons.append(f"Slow shipping ({total_days} days)")
        
        # If supplier_cost exists, give some base score
        if supplier_cost > 0 and score < 20:
            score = max(score, 20)
            if not reasons:
                reasons.append(f"Supplier found at £{supplier_cost:.2f}")
        
        score = min(100, max(0, score))
        reasoning = ". ".join(reasons) if reasons else "Limited supplier data"
        return score, reasoning
    
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
