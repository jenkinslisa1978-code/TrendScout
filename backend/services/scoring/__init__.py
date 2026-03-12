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
    
    # Scoring weights (must sum to 1.0) — from user specification
    WEIGHTS = {
        'trend': 0.25,
        'margin': 0.20,
        'competition': 0.15,
        'ad_activity': 0.15,
        'supplier_demand': 0.10,
        'search_growth': 0.10,
        'order_velocity': 0.05,
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
        Calculate all 7 scores for a product.
        Returns dict with all score fields ready for database update.
        """
        trend_score, trend_reasoning = self.calculate_trend_score(product)
        margin_score, margin_reasoning = self.calculate_margin_score(product)
        competition_score, competition_reasoning = self.calculate_competition_score(product)
        ad_activity_score, ad_reasoning = self.calculate_ad_activity_score(product)
        supplier_demand_score, supplier_reasoning = self.calculate_supplier_demand_score(product)
        search_growth_score, search_reasoning = self.calculate_search_growth_score(product)
        order_velocity_score, order_reasoning = self.calculate_order_velocity_score(product)
        
        # Calculate launch_score using 7-signal formula
        launch_score = round(
            trend_score * self.WEIGHTS['trend'] +
            margin_score * self.WEIGHTS['margin'] +
            competition_score * self.WEIGHTS['competition'] +
            ad_activity_score * self.WEIGHTS['ad_activity'] +
            supplier_demand_score * self.WEIGHTS['supplier_demand'] +
            search_growth_score * self.WEIGHTS['search_growth'] +
            order_velocity_score * self.WEIGHTS['order_velocity']
        )
        launch_score = min(100, max(0, launch_score))
        
        market_label, market_description = self.get_market_label(launch_score)
        
        early_trend_score, early_trend_label = self.calculate_early_trend_score(product)
        trend_stage = self.classify_trend_stage(product, trend_score, early_trend_score)
        success_probability = self.calculate_success_probability(product, launch_score)
        
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
            'search_growth': {
                'score': search_growth_score,
                'weight': self.WEIGHTS['search_growth'],
                'weighted': round(search_growth_score * self.WEIGHTS['search_growth'], 1),
                'reasoning': search_reasoning,
            },
            'order_velocity': {
                'score': order_velocity_score,
                'weight': self.WEIGHTS['order_velocity'],
                'weighted': round(order_velocity_score * self.WEIGHTS['order_velocity'], 1),
                'reasoning': order_reasoning,
            },
        }
        
        return {
            'trend_score': trend_score,
            'margin_score': margin_score,
            'competition_score': competition_score,
            'ad_activity_score': ad_activity_score,
            'supplier_demand_score': supplier_demand_score,
            'search_growth_score': search_growth_score,
            'order_velocity_score': order_velocity_score,
            
            'launch_score': launch_score,
            'launch_score_breakdown': score_breakdown,
            'market_label': market_label,
            'market_description': market_description,
            
            'market_score': launch_score,
            'market_score_breakdown': {
                'trend': trend_score,
                'margin': margin_score,
                'competition': competition_score,
                'ad_activity': ad_activity_score,
                'supplier_demand': supplier_demand_score,
                'search_growth': search_growth_score,
                'order_velocity': order_velocity_score,
            },
            
            'early_trend_score': early_trend_score,
            'early_trend_label': early_trend_label,
            'trend_stage': trend_stage,
            'success_probability': success_probability,
            
            'scores_updated_at': datetime.now(timezone.utc).isoformat(),
            'scoring_metadata': self._build_scoring_metadata(product),
        }
    
    def _build_scoring_metadata(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build scoring_metadata.source_breakdown documenting which signals
        are real, estimated, or fallback for this product.
        """
        ss = product.get("source_signals", {})
        dc = product.get("data_confidence", "fallback")

        def _signal_info(signal_key: str, field_key: str, fallback_label: str) -> Dict[str, Any]:
            if signal_key in ss and isinstance(ss[signal_key], dict):
                return {
                    "confidence": ss[signal_key].get("confidence", "fallback"),
                    "source": ss[signal_key].get("source", "unknown"),
                    "updated": ss[signal_key].get("updated"),
                }
            # Check if field has a non-zero value from Amazon/Google (real)
            val = product.get(field_key, 0)
            if val and val != 0:
                return {"confidence": "estimated", "source": fallback_label, "updated": product.get("scores_updated_at")}
            return {"confidence": "fallback", "source": "none", "updated": None}

        return {
            "product_data_confidence": dc,
            "source_breakdown": {
                "trend": _signal_info("tiktok_trend", "tiktok_views", "amazon_bsr"),
                "supplier_cost": _signal_info("supplier_cost", "supplier_cost", "amazon_scraper"),
                "order_velocity": _signal_info("order_velocity", "orders_30d", "estimation"),
                "ad_activity": _signal_info("ad_activity", "ad_count", "estimation"),
                "meta_ads": _signal_info("meta_ads", "meta_active_ads", "estimation"),
                "cj_supplier": _signal_info("cj_supplier", "cj_price", "estimation"),
                "search_growth": {
                    "confidence": "live" if product.get("trend_velocity") else "fallback",
                    "source": "google_trends" if product.get("trend_velocity") else "none",
                    "updated": product.get("scores_updated_at"),
                },
                "competition": {
                    "confidence": "live" if product.get("amazon_reviews") else "estimated",
                    "source": "amazon_scraper" if product.get("amazon_reviews") else "estimation",
                    "updated": product.get("scores_updated_at"),
                },
                "margin": {
                    "confidence": "live" if (product.get("supplier_cost", 0) > 0 and product.get("estimated_retail_price", 0) > 0) else "fallback",
                    "source": "price_data" if product.get("supplier_cost", 0) > 0 else "none",
                    "updated": product.get("scores_updated_at"),
                },
            },
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
        Uses real data from AliExpress/CJ when available, estimation otherwise.
        Returns (score, reasoning).
        """
        order_velocity = product.get('supplier_order_velocity', 0)
        orders_30d = product.get('orders_30d', 0) or product.get('supplier_orders_30d', 0)
        supplier_rating = product.get('ae_rating', 0) or product.get('supplier_rating', 0)
        processing_days = product.get('ae_processing_days', 0) or product.get('cj_processing_days', 0) or product.get('supplier_processing_days', 0)
        shipping_days = product.get('ae_shipping_days', 0) or product.get('cj_shipping_days', 0) or product.get('supplier_shipping_days', 0)
        supplier_cost = product.get('supplier_cost', 0)
        cj_availability = product.get('cj_availability', '')

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
    
    def calculate_search_growth_score(self, product: Dict[str, Any]) -> tuple:
        """
        Calculate search growth score (0-100) based on Google Trends velocity
        and keyword search interest data.
        """
        trend_velocity = product.get('trend_velocity', 0)
        google_interest = product.get('google_trends_interest', 0)
        search_volume_change = product.get('search_volume_change', 0)
        
        score = 0
        reasons = []
        
        # Google Trends velocity (primary signal, 50%)
        if trend_velocity and trend_velocity != 0:
            if trend_velocity > 80:
                score += 50
                reasons.append(f"Surging search interest (+{trend_velocity:.0f}%)")
            elif trend_velocity > 40:
                score += 40
                reasons.append(f"Strong search growth (+{trend_velocity:.0f}%)")
            elif trend_velocity > 15:
                score += 30
                reasons.append(f"Rising search interest (+{trend_velocity:.0f}%)")
            elif trend_velocity > 0:
                score += 20
                reasons.append(f"Modest search growth (+{trend_velocity:.0f}%)")
            elif trend_velocity > -15:
                score += 10
                reasons.append(f"Stable search interest ({trend_velocity:.0f}%)")
            else:
                score += 5
                reasons.append(f"Declining search interest ({trend_velocity:.0f}%)")
        
        # Google Trends absolute interest (30%)
        if google_interest and google_interest > 0:
            if google_interest >= 80:
                score += 30
            elif google_interest >= 50:
                score += 22
            elif google_interest >= 25:
                score += 15
            else:
                score += 8
        
        # Search volume change (20%)
        if search_volume_change and search_volume_change > 0:
            score += min(20, int(search_volume_change / 5))
        
        score = min(100, max(0, score))
        reasoning = ". ".join(reasons) if reasons else "Search data limited"
        return score, reasoning

    def calculate_order_velocity_score(self, product: Dict[str, Any]) -> tuple:
        """
        Calculate order velocity score (0-100) based on supplier order
        rates and momentum.
        """
        order_velocity = product.get('supplier_order_velocity', 0)
        orders_30d = product.get('supplier_orders_30d', 0)
        order_growth = product.get('order_growth_rate', 0)
        
        score = 0
        reasons = []
        
        # Weekly order velocity (50%)
        if order_velocity and order_velocity > 0:
            if order_velocity >= 5000:
                score += 50
                reasons.append(f"Explosive order velocity ({order_velocity}/week)")
            elif order_velocity >= 2000:
                score += 40
                reasons.append(f"Very high orders ({order_velocity}/week)")
            elif order_velocity >= 800:
                score += 30
                reasons.append(f"Strong order velocity ({order_velocity}/week)")
            elif order_velocity >= 300:
                score += 20
                reasons.append(f"Moderate orders ({order_velocity}/week)")
            elif order_velocity >= 50:
                score += 12
            else:
                score += 5
        
        # 30-day total orders (30%)
        if orders_30d and orders_30d > 0:
            if orders_30d >= 20000:
                score += 30
            elif orders_30d >= 8000:
                score += 22
            elif orders_30d >= 3000:
                score += 15
            elif orders_30d >= 500:
                score += 8
            else:
                score += 4
        
        # Order growth rate (20%)
        if order_growth and order_growth > 0:
            score += min(20, int(order_growth / 4))
        
        score = min(100, max(0, score))
        reasoning = ". ".join(reasons) if reasons else "Order data limited"
        return score, reasoning

    def classify_trend_stage(self, product: Dict[str, Any], trend_score: int, early_trend_score: int) -> str:
        """
        Classify product into: Exploding, Emerging, Rising, Stable, Declining
        """
        trend_velocity = product.get('trend_velocity', 0) or 0
        view_growth = product.get('view_growth_rate', 0) or 0
        
        combined = (trend_score * 0.4) + (early_trend_score * 0.3) + min(100, max(0, trend_velocity + 50)) * 0.3
        
        if combined >= 75 or (trend_velocity > 60 and trend_score >= 70):
            return "Exploding"
        elif combined >= 55 or (trend_velocity > 25 and trend_score >= 50):
            return "Emerging"
        elif combined >= 40 or trend_velocity > 5:
            return "Rising"
        elif trend_velocity >= -15:
            return "Stable"
        else:
            return "Declining"

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
