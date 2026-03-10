"""
Intelligence Layer - Success Prediction Model

Calculates success_probability based on multiple market signals.
Uses a weighted scoring model to predict product launch success.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SuccessOutcome(str, Enum):
    """Predicted success outcome"""
    HIGH_SUCCESS = "high_success"       # >70% probability
    MODERATE_SUCCESS = "moderate_success" # 50-70%
    UNCERTAIN = "uncertain"             # 30-50%
    LIKELY_FAILURE = "likely_failure"   # <30%


@dataclass
class SuccessFactor:
    """Individual factor contributing to success prediction"""
    name: str
    value: Any
    contribution: float  # -1 to +1
    weight: float
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "contribution": round(self.contribution, 2),
            "weight": self.weight,
            "explanation": self.explanation,
        }


@dataclass
class SuccessPrediction:
    """Complete success prediction result"""
    product_id: str
    success_probability: float  # 0-100
    outcome: SuccessOutcome
    outcome_label: str
    factors: List[SuccessFactor] = field(default_factory=list)
    top_positive_factors: List[str] = field(default_factory=list)
    top_negative_factors: List[str] = field(default_factory=list)
    confidence: int = 50
    prediction_explanation: str = ""
    predicted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "success_probability": round(self.success_probability, 1),
            "outcome": self.outcome.value,
            "outcome_label": self.outcome_label,
            "factors": [f.to_dict() for f in self.factors],
            "top_positive_factors": self.top_positive_factors,
            "top_negative_factors": self.top_negative_factors,
            "confidence": self.confidence,
            "prediction_explanation": self.prediction_explanation,
            "predicted_at": self.predicted_at.isoformat(),
        }


class SuccessPredictionModel:
    """
    Predicts product launch success probability.
    
    Factors considered:
    - Trend velocity (is demand growing?)
    - Engagement rate (are people interested?)
    - Supplier demand growth (proven market?)
    - Advertising activity (validated but not saturated?)
    - Competition growth rate (window closing?)
    - Profit margin (sustainable business?)
    
    The model combines these signals into a success_probability score.
    """
    
    # Factor weights (sum to 1.0)
    FACTOR_WEIGHTS = {
        "trend_velocity": 0.20,
        "engagement": 0.15,
        "supplier_demand": 0.15,
        "ad_landscape": 0.15,
        "competition_pressure": 0.15,
        "profit_margin": 0.20,
    }
    
    # Base probability
    BASE_PROBABILITY = 50.0
    
    def __init__(self, db=None):
        self.db = db
    
    def predict_success(self, product: Dict[str, Any]) -> SuccessPrediction:
        """Generate success prediction for a product"""
        product_id = product.get("id", "")
        
        factors = []
        
        # Analyze each factor
        factors.append(self._analyze_trend_velocity(product))
        factors.append(self._analyze_engagement(product))
        factors.append(self._analyze_supplier_demand(product))
        factors.append(self._analyze_ad_landscape(product))
        factors.append(self._analyze_competition_pressure(product))
        factors.append(self._analyze_profit_margin(product))
        
        # Calculate probability
        probability = self._calculate_probability(factors)
        
        # Determine outcome
        outcome, label = self._classify_outcome(probability)
        
        # Identify top factors
        positive_factors = self._get_top_positive_factors(factors)
        negative_factors = self._get_top_negative_factors(factors)
        
        # Calculate confidence
        confidence = self._calculate_confidence(product, factors)
        
        # Generate explanation
        explanation = self._generate_explanation(
            probability, outcome, positive_factors, negative_factors
        )
        
        return SuccessPrediction(
            product_id=product_id,
            success_probability=probability,
            outcome=outcome,
            outcome_label=label,
            factors=factors,
            top_positive_factors=positive_factors,
            top_negative_factors=negative_factors,
            confidence=confidence,
            prediction_explanation=explanation,
        )
    
    def _analyze_trend_velocity(self, product: Dict[str, Any]) -> SuccessFactor:
        """Analyze trend velocity factor"""
        velocity = product.get("trend_velocity", 0)
        trend_score = product.get("trend_score", 50)
        
        # Calculate contribution (-1 to +1)
        if velocity is None:
            contribution = 0
            explanation = "Trend velocity data unavailable"
        elif velocity > 100:
            contribution = 0.9
            explanation = f"Explosive growth (+{velocity:.0f}%) strongly predicts success"
        elif velocity > 50:
            contribution = 0.7
            explanation = f"Strong growth (+{velocity:.0f}%) indicates good momentum"
        elif velocity > 20:
            contribution = 0.4
            explanation = f"Healthy growth (+{velocity:.0f}%) supports success"
        elif velocity > 0:
            contribution = 0.2
            explanation = f"Slight growth (+{velocity:.0f}%) is positive but modest"
        elif velocity > -10:
            contribution = -0.1
            explanation = "Flat trend may limit growth potential"
        else:
            contribution = -0.5
            explanation = f"Declining trend ({velocity:.0f}%) reduces success likelihood"
        
        return SuccessFactor(
            name="Trend Velocity",
            value=velocity,
            contribution=contribution,
            weight=self.FACTOR_WEIGHTS["trend_velocity"],
            explanation=explanation,
        )
    
    def _analyze_engagement(self, product: Dict[str, Any]) -> SuccessFactor:
        """Analyze engagement factor"""
        engagement_rate = product.get("engagement_rate", 0)
        tiktok_views = product.get("tiktok_views", 0)
        
        # Calculate contribution
        if not tiktok_views:
            contribution = 0
            explanation = "Engagement data unavailable"
        else:
            # Views indicate interest
            if tiktok_views > 5000000:
                contribution = 0.8
                explanation = f"Massive visibility ({tiktok_views/1000000:.1f}M views) predicts strong demand"
            elif tiktok_views > 1000000:
                contribution = 0.6
                explanation = f"High visibility ({tiktok_views/1000000:.1f}M views) indicates market interest"
            elif tiktok_views > 100000:
                contribution = 0.3
                explanation = f"Good visibility ({tiktok_views/1000:.0f}K views) shows potential"
            elif tiktok_views > 10000:
                contribution = 0.1
                explanation = f"Moderate visibility ({tiktok_views/1000:.0f}K views)"
            else:
                contribution = -0.2
                explanation = "Limited visibility may indicate niche market"
            
            # Engagement rate bonus
            if engagement_rate and engagement_rate > 5:
                contribution = min(1.0, contribution + 0.2)
                explanation += f" (high engagement rate: {engagement_rate:.1f}%)"
        
        return SuccessFactor(
            name="Engagement",
            value={"views": tiktok_views, "rate": engagement_rate},
            contribution=contribution,
            weight=self.FACTOR_WEIGHTS["engagement"],
            explanation=explanation,
        )
    
    def _analyze_supplier_demand(self, product: Dict[str, Any]) -> SuccessFactor:
        """Analyze supplier demand factor"""
        orders = product.get("supplier_orders", 0)
        
        if not orders:
            contribution = 0
            explanation = "Supplier demand data unavailable"
        elif orders > 10000:
            contribution = 0.8
            explanation = f"Very high supplier demand ({orders:,} orders) validates market"
        elif orders > 5000:
            contribution = 0.6
            explanation = f"Strong supplier demand ({orders:,} orders)"
        elif orders > 1000:
            contribution = 0.3
            explanation = f"Good supplier activity ({orders:,} orders)"
        elif orders > 100:
            contribution = 0.1
            explanation = f"Moderate supplier activity ({orders:,} orders)"
        else:
            contribution = -0.2
            explanation = "Low supplier orders suggest limited market validation"
        
        return SuccessFactor(
            name="Supplier Demand",
            value=orders,
            contribution=contribution,
            weight=self.FACTOR_WEIGHTS["supplier_demand"],
            explanation=explanation,
        )
    
    def _analyze_ad_landscape(self, product: Dict[str, Any]) -> SuccessFactor:
        """Analyze advertising landscape factor"""
        ad_count = product.get("ad_count", 0)
        
        if ad_count is None:
            contribution = 0
            explanation = "Ad activity data unavailable"
        elif ad_count == 0:
            contribution = 0.2
            explanation = "No ads detected - untested market or opportunity"
        elif ad_count < 20:
            contribution = 0.7
            explanation = f"Low competition ({ad_count} ads) - validated but not saturated"
        elif ad_count < 50:
            contribution = 0.4
            explanation = f"Moderate ad activity ({ad_count} ads) - some competition"
        elif ad_count < 100:
            contribution = -0.1
            explanation = f"High ad activity ({ad_count} ads) - competitive market"
        else:
            contribution = -0.5
            explanation = f"Very high ad saturation ({ad_count} ads) - difficult to compete"
        
        return SuccessFactor(
            name="Ad Landscape",
            value=ad_count,
            contribution=contribution,
            weight=self.FACTOR_WEIGHTS["ad_landscape"],
            explanation=explanation,
        )
    
    def _analyze_competition_pressure(self, product: Dict[str, Any]) -> SuccessFactor:
        """Analyze competition pressure factor"""
        competition_level = product.get("competition_level", "medium")
        competitor_count = product.get("competitor_store_count", 0)
        
        # Map competition level
        level_contributions = {
            "low": 0.7,
            "medium": 0.2,
            "high": -0.4,
        }
        contribution = level_contributions.get(competition_level, 0)
        
        # Adjust for competitor count
        if competitor_count:
            if competitor_count < 10:
                contribution = min(1.0, contribution + 0.2)
            elif competitor_count > 100:
                contribution = max(-1.0, contribution - 0.3)
        
        if competition_level == "low":
            explanation = f"Low competition ({competitor_count or 'few'} competitors) favors success"
        elif competition_level == "high":
            explanation = f"High competition ({competitor_count} competitors) increases failure risk"
        else:
            explanation = f"Moderate competition - differentiation will be important"
        
        return SuccessFactor(
            name="Competition Pressure",
            value={"level": competition_level, "count": competitor_count},
            contribution=contribution,
            weight=self.FACTOR_WEIGHTS["competition_pressure"],
            explanation=explanation,
        )
    
    def _analyze_profit_margin(self, product: Dict[str, Any]) -> SuccessFactor:
        """Analyze profit margin factor"""
        supplier_cost = product.get("supplier_cost", 0)
        retail_price = product.get("estimated_retail_price", 0)
        
        if not supplier_cost or not retail_price:
            contribution = 0
            explanation = "Pricing data unavailable"
        else:
            margin = retail_price - supplier_cost
            margin_percent = (margin / retail_price) * 100 if retail_price > 0 else 0
            
            if margin_percent >= 60:
                contribution = 0.9
                explanation = f"Excellent margin ({margin_percent:.0f}%) enables strong profitability"
            elif margin_percent >= 50:
                contribution = 0.7
                explanation = f"Strong margin ({margin_percent:.0f}%) supports sustainable business"
            elif margin_percent >= 40:
                contribution = 0.4
                explanation = f"Good margin ({margin_percent:.0f}%) allows for advertising spend"
            elif margin_percent >= 30:
                contribution = 0.1
                explanation = f"Moderate margin ({margin_percent:.0f}%) - limited advertising budget"
            elif margin_percent >= 20:
                contribution = -0.3
                explanation = f"Tight margin ({margin_percent:.0f}%) - profitability challenging"
            else:
                contribution = -0.7
                explanation = f"Very low margin ({margin_percent:.0f}%) - likely unprofitable"
        
        return SuccessFactor(
            name="Profit Margin",
            value={"cost": supplier_cost, "price": retail_price},
            contribution=contribution,
            weight=self.FACTOR_WEIGHTS["profit_margin"],
            explanation=explanation,
        )
    
    def _calculate_probability(self, factors: List[SuccessFactor]) -> float:
        """Calculate overall success probability from factors"""
        # Start with base probability
        probability = self.BASE_PROBABILITY
        
        # Apply weighted contributions
        for factor in factors:
            # Each factor can shift probability by up to weight * 50
            shift = factor.contribution * factor.weight * 50
            probability += shift
        
        # Clamp to 0-100
        return max(0, min(100, probability))
    
    def _classify_outcome(self, probability: float) -> tuple:
        """Classify probability into outcome category"""
        if probability >= 70:
            return SuccessOutcome.HIGH_SUCCESS, "High Success Likelihood"
        elif probability >= 50:
            return SuccessOutcome.MODERATE_SUCCESS, "Moderate Success Likelihood"
        elif probability >= 30:
            return SuccessOutcome.UNCERTAIN, "Uncertain Outcome"
        else:
            return SuccessOutcome.LIKELY_FAILURE, "Likely Failure"
    
    def _get_top_positive_factors(self, factors: List[SuccessFactor]) -> List[str]:
        """Get top positive contributing factors"""
        positive = [f for f in factors if f.contribution > 0.2]
        positive.sort(key=lambda x: x.contribution * x.weight, reverse=True)
        return [f.explanation for f in positive[:3]]
    
    def _get_top_negative_factors(self, factors: List[SuccessFactor]) -> List[str]:
        """Get top negative contributing factors"""
        negative = [f for f in factors if f.contribution < -0.1]
        negative.sort(key=lambda x: x.contribution * x.weight)
        return [f.explanation for f in negative[:3]]
    
    def _calculate_confidence(self, product: Dict[str, Any], factors: List[SuccessFactor]) -> int:
        """Calculate confidence in prediction"""
        confidence = 50
        
        # Data source quality
        data_source = product.get("data_source", "unknown")
        if data_source == "simulated":
            confidence -= 25
        elif data_source not in ["unknown", "manual"]:
            confidence += 15
        
        # Data availability
        zero_contribution_count = len([f for f in factors if f.contribution == 0])
        confidence -= zero_contribution_count * 8
        
        # Product-level confidence
        product_confidence = product.get("confidence_score", 50)
        confidence = (confidence + product_confidence) / 2
        
        return max(10, min(100, int(confidence)))
    
    def _generate_explanation(
        self,
        probability: float,
        outcome: SuccessOutcome,
        positive_factors: List[str],
        negative_factors: List[str]
    ) -> str:
        """Generate human-readable prediction explanation"""
        explanation = f"Success probability: {probability:.0f}%. "
        
        if outcome == SuccessOutcome.HIGH_SUCCESS:
            explanation += "Strong signals indicate good launch potential. "
        elif outcome == SuccessOutcome.MODERATE_SUCCESS:
            explanation += "Mixed signals - success possible with right execution. "
        elif outcome == SuccessOutcome.UNCERTAIN:
            explanation += "Insufficient positive signals for confident prediction. "
        else:
            explanation += "Multiple risk factors present. "
        
        if positive_factors:
            explanation += f"Strengths: {positive_factors[0]}. "
        
        if negative_factors:
            explanation += f"Concerns: {negative_factors[0]}."
        
        return explanation
