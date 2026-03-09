"""
Early Trend Detection System

Identifies products that are accelerating rapidly before market saturation.
Uses multiple signals to calculate an early_trend_score from 0-100.

Key Signals:
- View velocity (rapid growth rate)
- Engagement ratio (views to ads ratio)
- Ad momentum (increasing ad activity)
- Supplier traction (rising order counts)
- Competition gap (low competition advantage)
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import math


# Thresholds for early trend detection
EARLY_TREND_THRESHOLDS = {
    # View velocity thresholds (views per day estimated)
    'view_velocity': {
        'explosive': 500000,  # 500K+ views/day
        'rapid': 100000,      # 100K+ views/day
        'moderate': 50000,    # 50K+ views/day
        'slow': 10000,        # 10K+ views/day
    },
    # Engagement ratio (views per ad)
    'engagement_ratio': {
        'viral': 100000,      # 100K views per ad
        'high': 50000,        # 50K views per ad
        'moderate': 20000,    # 20K views per ad
        'low': 5000,          # 5K views per ad
    },
    # Ad momentum thresholds
    'ad_momentum': {
        'accelerating': (10, 100),    # 10-100 ads (sweet spot)
        'building': (100, 200),       # 100-200 ads
        'established': (200, 400),    # 200-400 ads
        'saturated': (400, float('inf')),  # 400+ ads
    },
    # Alert threshold
    'early_trend_alert': 75,  # Score >= 75 triggers alert
}


def calculate_view_velocity_score(tiktok_views: int, created_days_ago: int = 30) -> float:
    """
    Calculate view velocity score based on estimated daily view rate.
    
    Args:
        tiktok_views: Total TikTok views
        created_days_ago: Estimated product age in days
        
    Returns:
        Score from 0-100
    """
    if tiktok_views <= 0:
        return 0
    
    # Estimate daily view rate
    days = max(1, created_days_ago)
    daily_views = tiktok_views / days
    
    thresholds = EARLY_TREND_THRESHOLDS['view_velocity']
    
    if daily_views >= thresholds['explosive']:
        return 100
    elif daily_views >= thresholds['rapid']:
        # Scale between 80-100
        return 80 + (daily_views - thresholds['rapid']) / (thresholds['explosive'] - thresholds['rapid']) * 20
    elif daily_views >= thresholds['moderate']:
        # Scale between 60-80
        return 60 + (daily_views - thresholds['moderate']) / (thresholds['rapid'] - thresholds['moderate']) * 20
    elif daily_views >= thresholds['slow']:
        # Scale between 30-60
        return 30 + (daily_views - thresholds['slow']) / (thresholds['moderate'] - thresholds['slow']) * 30
    else:
        # Scale between 0-30
        return min(30, (daily_views / thresholds['slow']) * 30)


def calculate_engagement_ratio_score(tiktok_views: int, ad_count: int) -> float:
    """
    Calculate engagement ratio score (views per ad).
    Higher ratio = less saturated, more organic growth.
    
    Args:
        tiktok_views: Total TikTok views
        ad_count: Number of ads running
        
    Returns:
        Score from 0-100
    """
    if ad_count <= 0:
        # No ads yet = very early stage (could be good or untested)
        if tiktok_views >= 1000000:
            return 90  # High views, no ads = early opportunity
        elif tiktok_views >= 100000:
            return 70
        else:
            return 40  # Low views, no ads = unproven
    
    ratio = tiktok_views / ad_count
    thresholds = EARLY_TREND_THRESHOLDS['engagement_ratio']
    
    if ratio >= thresholds['viral']:
        return 100
    elif ratio >= thresholds['high']:
        return 80 + (ratio - thresholds['high']) / (thresholds['viral'] - thresholds['high']) * 20
    elif ratio >= thresholds['moderate']:
        return 60 + (ratio - thresholds['moderate']) / (thresholds['high'] - thresholds['moderate']) * 20
    elif ratio >= thresholds['low']:
        return 30 + (ratio - thresholds['low']) / (thresholds['moderate'] - thresholds['low']) * 30
    else:
        return min(30, (ratio / thresholds['low']) * 30)


def calculate_ad_momentum_score(ad_count: int) -> float:
    """
    Calculate ad momentum score.
    Sweet spot is 10-100 ads (early movers, not saturated).
    
    Args:
        ad_count: Number of ads running
        
    Returns:
        Score from 0-100
    """
    thresholds = EARLY_TREND_THRESHOLDS['ad_momentum']
    
    if ad_count == 0:
        return 50  # No ads = unknown momentum
    elif thresholds['accelerating'][0] <= ad_count <= thresholds['accelerating'][1]:
        # Sweet spot - high score
        # Peak at ~50 ads
        peak = 50
        distance = abs(ad_count - peak) / peak
        return 100 - (distance * 20)  # 80-100 range
    elif thresholds['building'][0] <= ad_count <= thresholds['building'][1]:
        # Building momentum
        return 70 - ((ad_count - 100) / 100) * 10  # 60-70 range
    elif thresholds['established'][0] <= ad_count <= thresholds['established'][1]:
        # Established - harder to enter
        return 50 - ((ad_count - 200) / 200) * 20  # 30-50 range
    else:
        # Saturated
        return max(10, 30 - ((ad_count - 400) / 400) * 20)


def calculate_supplier_traction_score(supplier_orders: int = 0, supplier_rating: float = 0) -> float:
    """
    Calculate supplier traction score.
    Rising order counts with good ratings indicate validated demand.
    
    Args:
        supplier_orders: Number of supplier orders
        supplier_rating: Supplier rating (0-5)
        
    Returns:
        Score from 0-100
    """
    if supplier_orders <= 0:
        return 40  # Unknown traction
    
    # Order volume score (0-60 points)
    if supplier_orders >= 20000:
        order_score = 60
    elif supplier_orders >= 10000:
        order_score = 50 + (supplier_orders - 10000) / 10000 * 10
    elif supplier_orders >= 5000:
        order_score = 40 + (supplier_orders - 5000) / 5000 * 10
    elif supplier_orders >= 1000:
        order_score = 25 + (supplier_orders - 1000) / 4000 * 15
    else:
        order_score = (supplier_orders / 1000) * 25
    
    # Rating bonus (0-40 points)
    if supplier_rating >= 4.5:
        rating_score = 40
    elif supplier_rating >= 4.0:
        rating_score = 30
    elif supplier_rating >= 3.5:
        rating_score = 20
    elif supplier_rating > 0:
        rating_score = 10
    else:
        rating_score = 15  # Unknown rating
    
    return min(100, order_score + rating_score)


def calculate_competition_gap_score(competition_level: str, trend_stage: str) -> float:
    """
    Calculate competition gap score.
    Low competition + early stage = high opportunity.
    
    Args:
        competition_level: 'low', 'medium', 'high'
        trend_stage: 'early', 'rising', 'peak', 'saturated'
        
    Returns:
        Score from 0-100
    """
    # Base score from competition level
    competition_scores = {
        'low': 100,
        'medium': 60,
        'high': 25,
    }
    base_score = competition_scores.get(competition_level.lower(), 50)
    
    # Modifier from trend stage
    stage_multipliers = {
        'early': 1.0,      # Full score
        'rising': 0.85,    # 85% of score
        'peak': 0.6,       # 60% of score
        'saturated': 0.3,  # 30% of score
    }
    multiplier = stage_multipliers.get(trend_stage.lower(), 0.7)
    
    return base_score * multiplier


def calculate_early_trend_score(product: Dict[str, Any]) -> int:
    """
    Calculate the overall early trend score for a product.
    
    Combines multiple signals with weighted scoring:
    - View Velocity: 25%
    - Engagement Ratio: 25%
    - Ad Momentum: 20%
    - Supplier Traction: 15%
    - Competition Gap: 15%
    
    Args:
        product: Product data dictionary
        
    Returns:
        Early trend score from 0-100
    """
    # Extract product data
    tiktok_views = product.get('tiktok_views', 0) or 0
    ad_count = product.get('ad_count', 0) or 0
    competition_level = product.get('competition_level', 'medium') or 'medium'
    trend_stage = product.get('trend_stage', 'rising') or 'rising'
    supplier_orders = product.get('supplier_orders', 0) or 0
    supplier_rating = product.get('supplier_rating', 0) or 0
    
    # Calculate individual scores
    view_velocity = calculate_view_velocity_score(tiktok_views)
    engagement_ratio = calculate_engagement_ratio_score(tiktok_views, ad_count)
    ad_momentum = calculate_ad_momentum_score(ad_count)
    supplier_traction = calculate_supplier_traction_score(supplier_orders, supplier_rating)
    competition_gap = calculate_competition_gap_score(competition_level, trend_stage)
    
    # Weighted average
    weighted_score = (
        view_velocity * 0.25 +
        engagement_ratio * 0.25 +
        ad_momentum * 0.20 +
        supplier_traction * 0.15 +
        competition_gap * 0.15
    )
    
    # Apply bonuses for exceptional signals
    bonuses = 0
    
    # Bonus: Very high views with low ads (untapped viral)
    if tiktok_views >= 10000000 and ad_count < 50:
        bonuses += 10
    
    # Bonus: Low competition + early stage
    if competition_level == 'low' and trend_stage == 'early':
        bonuses += 8
    
    # Bonus: High engagement + rising stage
    if engagement_ratio >= 70 and trend_stage == 'rising':
        bonuses += 5
    
    # Penalty: Saturated market
    if trend_stage == 'saturated' and competition_level == 'high':
        bonuses -= 15
    
    final_score = min(100, max(0, round(weighted_score + bonuses)))
    
    return final_score


def get_early_trend_label(early_trend_score: int) -> str:
    """
    Get human-readable label for early trend score.
    
    Args:
        early_trend_score: Score from 0-100
        
    Returns:
        Label string
    """
    if early_trend_score >= 90:
        return 'Hot Opportunity'
    elif early_trend_score >= 75:
        return 'Early Mover'
    elif early_trend_score >= 60:
        return 'Rising'
    elif early_trend_score >= 40:
        return 'Monitoring'
    else:
        return 'Saturated'


def get_early_trend_color(early_trend_score: int) -> str:
    """
    Get color class for early trend score badge.
    
    Args:
        early_trend_score: Score from 0-100
        
    Returns:
        Tailwind color class
    """
    if early_trend_score >= 90:
        return 'bg-gradient-to-r from-pink-500 to-rose-500 text-white'
    elif early_trend_score >= 75:
        return 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
    elif early_trend_score >= 60:
        return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    elif early_trend_score >= 40:
        return 'bg-blue-100 text-blue-700 border-blue-200'
    else:
        return 'bg-slate-100 text-slate-600 border-slate-200'


def should_create_early_trend_alert(product: Dict[str, Any]) -> bool:
    """
    Check if product qualifies for an early trend alert.
    
    Args:
        product: Product data dictionary
        
    Returns:
        True if alert should be created
    """
    early_trend_score = product.get('early_trend_score', 0)
    threshold = EARLY_TREND_THRESHOLDS['early_trend_alert']
    
    return early_trend_score >= threshold


def generate_early_trend_alert(product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate an early trend alert for a qualifying product.
    
    Args:
        product: Product data dictionary
        
    Returns:
        Alert dictionary or None
    """
    if not should_create_early_trend_alert(product):
        return None
    
    early_trend_score = product.get('early_trend_score', 0)
    trend_stage = product.get('trend_stage', 'rising')
    competition = product.get('competition_level', 'medium')
    
    # Determine priority based on score
    if early_trend_score >= 90:
        priority = 'critical'
        alert_type = 'hot_opportunity'
        title = f"🔥 Hot Opportunity: {product.get('product_name')}"
    elif early_trend_score >= 80:
        priority = 'high'
        alert_type = 'early_mover'
        title = f"⚡ Early Mover Alert: {product.get('product_name')}"
    else:
        priority = 'medium'
        alert_type = 'early_trend'
        title = f"📈 Early Trend Detected: {product.get('product_name')}"
    
    # Generate insight message
    insights = []
    
    tiktok_views = product.get('tiktok_views', 0)
    ad_count = product.get('ad_count', 0)
    
    if tiktok_views >= 10000000 and ad_count < 100:
        insights.append("High viral potential with low ad saturation")
    elif trend_stage == 'early':
        insights.append("Very early stage - first mover advantage")
    elif competition == 'low':
        insights.append("Low competition market entry window")
    
    if ad_count > 0 and tiktok_views / ad_count > 50000:
        insights.append("Strong organic engagement ratio")
    
    body = f"Early Trend Score: {early_trend_score}/100. "
    if insights:
        body += " ".join(insights)
    else:
        body += f"Product showing strong early trend signals in the {trend_stage} stage."
    
    import uuid
    
    return {
        'id': str(uuid.uuid4()),
        'product_id': product.get('id'),
        'product_name': product.get('product_name'),
        'alert_type': alert_type,
        'priority': priority,
        'title': title,
        'body': body,
        'trend_score': product.get('trend_score', 0),
        'early_trend_score': early_trend_score,
        'opportunity_rating': product.get('opportunity_rating', 'medium'),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'read': False,
        'dismissed': False,
    }


def get_early_trend_breakdown(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed breakdown of early trend score components.
    
    Args:
        product: Product data dictionary
        
    Returns:
        Breakdown dictionary with individual scores
    """
    tiktok_views = product.get('tiktok_views', 0) or 0
    ad_count = product.get('ad_count', 0) or 0
    competition_level = product.get('competition_level', 'medium') or 'medium'
    trend_stage = product.get('trend_stage', 'rising') or 'rising'
    supplier_orders = product.get('supplier_orders', 0) or 0
    supplier_rating = product.get('supplier_rating', 0) or 0
    
    return {
        'view_velocity': {
            'score': round(calculate_view_velocity_score(tiktok_views)),
            'weight': '25%',
            'description': 'Daily view growth rate',
        },
        'engagement_ratio': {
            'score': round(calculate_engagement_ratio_score(tiktok_views, ad_count)),
            'weight': '25%',
            'description': 'Views per ad ratio',
        },
        'ad_momentum': {
            'score': round(calculate_ad_momentum_score(ad_count)),
            'weight': '20%',
            'description': 'Ad activity sweet spot',
        },
        'supplier_traction': {
            'score': round(calculate_supplier_traction_score(supplier_orders, supplier_rating)),
            'weight': '15%',
            'description': 'Supplier order validation',
        },
        'competition_gap': {
            'score': round(calculate_competition_gap_score(competition_level, trend_stage)),
            'weight': '15%',
            'description': 'Market entry opportunity',
        },
    }
