"""
Intelligence Layer - Product Validation Engine

Determines whether a product is realistically viable to launch.
Combines multiple signals into clear, actionable recommendations.

Key output:
- LAUNCH OPPORTUNITY: Strong signals, low competition, good margin
- PROMISING BUT MONITOR: Decent signals but needs watching
- HIGH RISK / SATURATED: Too competitive or weak signals

CRITICAL: Never fabricate data. Show confidence and reasoning.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class LaunchRecommendation(str, Enum):
    """Product launch recommendations"""
    LAUNCH_OPPORTUNITY = "launch_opportunity"
    PROMISING_MONITOR = "promising_monitor"
    HIGH_RISK = "high_risk"
    INSUFFICIENT_DATA = "insufficient_data"


class RiskLevel(str, Enum):
    """Risk classification"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    UNKNOWN = "unknown"


class SignalStrength(str, Enum):
    """Signal quality classification"""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    MISSING = "missing"


@dataclass
class ValidationSignal:
    """Individual signal used in validation"""
    name: str
    value: Any
    score: float  # 0-100
    strength: SignalStrength
    weight: float
    reasoning: str
    is_simulated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "score": self.score,
            "strength": self.strength.value,
            "weight": self.weight,
            "reasoning": self.reasoning,
            "is_simulated": self.is_simulated,
        }


@dataclass
class ValidationResult:
    """Complete product validation result"""
    product_id: str
    product_name: str
    recommendation: LaunchRecommendation
    recommendation_label: str
    confidence_score: int  # 0-100
    risk_level: RiskLevel
    overall_score: float  # 0-100
    signals: List[ValidationSignal] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    summary: str = ""
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "recommendation": self.recommendation.value,
            "recommendation_label": self.recommendation_label,
            "confidence_score": self.confidence_score,
            "risk_level": self.risk_level.value,
            "overall_score": round(self.overall_score, 1),
            "signals": [s.to_dict() for s in self.signals],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "action_items": self.action_items,
            "summary": self.summary,
            "validated_at": self.validated_at.isoformat(),
        }


class ProductValidationEngine:
    """
    Determines whether a product is viable to launch.
    
    Combines signals:
    - Trend velocity (is it growing?)
    - Profit margin (can you make money?)
    - Competition level (is market saturated?)
    - Advertising activity (how hard to compete?)
    - Supplier demand (is supply reliable?)
    - Engagement signals (social proof)
    
    Outputs actionable recommendation with reasoning.
    """
    
    # Signal weights (must sum to 1.0)
    SIGNAL_WEIGHTS = {
        "trend_velocity": 0.20,      # Growing trend = opportunity
        "profit_margin": 0.25,       # Must be profitable
        "competition": 0.20,         # Lower is better
        "ad_activity": 0.10,         # Advertising landscape
        "supplier_demand": 0.10,     # Supply reliability
        "engagement": 0.15,          # Social proof
    }
    
    # Thresholds for recommendations
    LAUNCH_THRESHOLD = 70           # Score >= 70 = Launch Opportunity
    PROMISING_THRESHOLD = 50        # Score >= 50 = Promising
    MIN_CONFIDENCE = 40             # Need at least 40% confidence
    
    def __init__(self, db=None):
        self.db = db
    
    def validate_product(self, product: Dict[str, Any]) -> ValidationResult:
        """
        Validate a product and return launch recommendation.
        
        Args:
            product: Product data from database
            
        Returns:
            ValidationResult with recommendation and reasoning
        """
        product_id = product.get("id", "")
        product_name = product.get("product_name", "Unknown")
        
        # Analyze each signal
        signals = []
        
        # 1. Trend Velocity Signal
        trend_signal = self._analyze_trend_velocity(product)
        signals.append(trend_signal)
        
        # 2. Profit Margin Signal
        margin_signal = self._analyze_profit_margin(product)
        signals.append(margin_signal)
        
        # 3. Competition Signal
        competition_signal = self._analyze_competition(product)
        signals.append(competition_signal)
        
        # 4. Ad Activity Signal
        ad_signal = self._analyze_ad_activity(product)
        signals.append(ad_signal)
        
        # 5. Supplier Demand Signal
        supplier_signal = self._analyze_supplier_demand(product)
        signals.append(supplier_signal)
        
        # 6. Engagement Signal
        engagement_signal = self._analyze_engagement(product)
        signals.append(engagement_signal)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(signals)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(product, signals)
        
        # Determine recommendation
        recommendation, label = self._determine_recommendation(
            overall_score, confidence, signals
        )
        
        # Determine risk level
        risk_level = self._assess_risk(signals, confidence)
        
        # Generate insights
        strengths = self._identify_strengths(signals)
        weaknesses = self._identify_weaknesses(signals)
        action_items = self._generate_action_items(recommendation, signals, weaknesses)
        
        # Generate summary
        summary = self._generate_summary(
            product_name, recommendation, overall_score, confidence, strengths, weaknesses
        )
        
        return ValidationResult(
            product_id=product_id,
            product_name=product_name,
            recommendation=recommendation,
            recommendation_label=label,
            confidence_score=confidence,
            risk_level=risk_level,
            overall_score=overall_score,
            signals=signals,
            strengths=strengths,
            weaknesses=weaknesses,
            action_items=action_items,
            summary=summary,
        )
    
    def _analyze_trend_velocity(self, product: Dict[str, Any]) -> ValidationSignal:
        """Analyze trend velocity - is the product growing?"""
        trend_score = product.get("trend_score", 0)
        trend_stage = product.get("trend_stage", "unknown")
        trend_velocity = product.get("trend_velocity", 0)
        early_trend_score = product.get("early_trend_score", 0)
        
        # Calculate signal score
        score = 0
        reasoning_parts = []
        
        if trend_velocity is None or trend_velocity == 0:
            score = 30
            strength = SignalStrength.MISSING
            reasoning_parts.append("Trend velocity data unavailable")
        else:
            # Velocity-based scoring
            if trend_velocity > 100:  # Exploding
                score = 95
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Exploding trend (+{trend_velocity:.0f}% growth)")
            elif trend_velocity > 50:  # Rising fast
                score = 85
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Rising fast (+{trend_velocity:.0f}% growth)")
            elif trend_velocity > 20:  # Rising
                score = 75
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Rising trend (+{trend_velocity:.0f}% growth)")
            elif trend_velocity > 0:  # Slight growth
                score = 60
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Slight growth (+{trend_velocity:.0f}%)")
            elif trend_velocity > -10:  # Stable
                score = 45
                strength = SignalStrength.WEAK
                reasoning_parts.append("Stable trend, minimal growth")
            else:  # Declining
                score = 20
                strength = SignalStrength.WEAK
                reasoning_parts.append(f"Declining trend ({trend_velocity:.0f}%)")
        
        # Adjust for trend stage
        stage_adjustments = {
            "early": 10,     # Early = bonus
            "rising": 5,     # Rising = small bonus
            "peak": -5,      # Peak = slight penalty
            "saturated": -15 # Saturated = penalty
        }
        adjustment = stage_adjustments.get(trend_stage, 0)
        score = min(100, max(0, score + adjustment))
        
        if trend_stage in stage_adjustments:
            reasoning_parts.append(f"Trend stage: {trend_stage}")
        
        # Early trend detection bonus
        if early_trend_score and early_trend_score > 70:
            score = min(100, score + 10)
            reasoning_parts.append("Early trend detection signal positive")
        
        is_simulated = product.get("data_source") == "simulated"
        
        return ValidationSignal(
            name="Trend Velocity",
            value=trend_velocity,
            score=score,
            strength=strength if 'strength' in dir() else SignalStrength.MODERATE,
            weight=self.SIGNAL_WEIGHTS["trend_velocity"],
            reasoning=". ".join(reasoning_parts),
            is_simulated=is_simulated,
        )
    
    def _analyze_profit_margin(self, product: Dict[str, Any]) -> ValidationSignal:
        """Analyze profit margin - can you make money?"""
        supplier_cost = product.get("supplier_cost", 0)
        retail_price = product.get("estimated_retail_price", 0)
        margin_score = product.get("margin_score", 0)
        
        score = 0
        reasoning_parts = []
        strength = SignalStrength.MISSING
        
        if not supplier_cost or not retail_price:
            score = 30
            strength = SignalStrength.MISSING
            reasoning_parts.append("Price data unavailable - cannot calculate margin")
        else:
            # Calculate actual margin
            margin = retail_price - supplier_cost
            margin_percent = (margin / retail_price) * 100 if retail_price > 0 else 0
            
            if margin_percent >= 60:
                score = 95
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Excellent margin: {margin_percent:.0f}% (£{margin:.2f} profit)")
            elif margin_percent >= 50:
                score = 85
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Strong margin: {margin_percent:.0f}% (£{margin:.2f} profit)")
            elif margin_percent >= 40:
                score = 75
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Good margin: {margin_percent:.0f}% (£{margin:.2f} profit)")
            elif margin_percent >= 30:
                score = 60
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Acceptable margin: {margin_percent:.0f}% (£{margin:.2f} profit)")
            elif margin_percent >= 20:
                score = 40
                strength = SignalStrength.WEAK
                reasoning_parts.append(f"Low margin: {margin_percent:.0f}% - advertising costs may erode profits")
            else:
                score = 15
                strength = SignalStrength.WEAK
                reasoning_parts.append(f"Very low margin: {margin_percent:.0f}% - difficult to profit")
            
            # Add context about pricing
            if retail_price > 50:
                reasoning_parts.append("Higher price point may limit audience")
            elif retail_price < 15:
                reasoning_parts.append("Low price point good for impulse purchases")
        
        is_simulated = product.get("data_source") == "simulated"
        
        return ValidationSignal(
            name="Profit Margin",
            value={"supplier_cost": supplier_cost, "retail_price": retail_price},
            score=score,
            strength=strength,
            weight=self.SIGNAL_WEIGHTS["profit_margin"],
            reasoning=". ".join(reasoning_parts),
            is_simulated=is_simulated,
        )
    
    def _analyze_competition(self, product: Dict[str, Any]) -> ValidationSignal:
        """Analyze competition level - is market saturated?"""
        competition_level = product.get("competition_level", "unknown")
        competition_score = product.get("competition_score", 50)
        competitor_count = product.get("competitor_store_count", 0)
        market_label = product.get("market_label", "unknown")
        
        score = 0
        reasoning_parts = []
        strength = SignalStrength.MODERATE
        
        # Lower competition = higher score (inverted)
        if competition_level == "low":
            score = 90
            strength = SignalStrength.STRONG
            reasoning_parts.append("Low competition - good market entry opportunity")
        elif competition_level == "medium":
            score = 65
            strength = SignalStrength.MODERATE
            reasoning_parts.append("Moderate competition - differentiation needed")
        elif competition_level == "high":
            score = 35
            strength = SignalStrength.WEAK
            reasoning_parts.append("High competition - saturated market")
        else:
            score = 50
            strength = SignalStrength.MISSING
            reasoning_parts.append("Competition data unavailable")
        
        # Adjust for competitor count
        if competitor_count:
            if competitor_count < 10:
                score = min(100, score + 10)
                reasoning_parts.append(f"Only {competitor_count} competitors detected")
            elif competitor_count > 100:
                score = max(0, score - 15)
                reasoning_parts.append(f"{competitor_count} competitors - crowded market")
        
        # Market label context
        if market_label == "Massive Opportunity":
            score = min(100, score + 10)
            reasoning_parts.append("Market shows massive opportunity")
        elif market_label == "Saturated":
            score = max(0, score - 10)
            reasoning_parts.append("Market labeled as saturated")
        
        is_simulated = product.get("data_source") == "simulated"
        
        return ValidationSignal(
            name="Competition Level",
            value={"level": competition_level, "competitors": competitor_count},
            score=score,
            strength=strength,
            weight=self.SIGNAL_WEIGHTS["competition"],
            reasoning=". ".join(reasoning_parts),
            is_simulated=is_simulated,
        )
    
    def _analyze_ad_activity(self, product: Dict[str, Any]) -> ValidationSignal:
        """Analyze advertising activity - how hard to compete?"""
        ad_count = product.get("ad_count", 0)
        ad_activity_score = product.get("ad_activity_score", 50)
        
        score = 0
        reasoning_parts = []
        strength = SignalStrength.MODERATE
        
        if ad_count is None:
            score = 50
            strength = SignalStrength.MISSING
            reasoning_parts.append("Ad activity data unavailable")
        else:
            # Some ads = validated market, too many = competitive
            if ad_count == 0:
                score = 60
                strength = SignalStrength.MODERATE
                reasoning_parts.append("No ads detected - unvalidated market or opportunity")
            elif ad_count < 20:
                score = 85
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Low ad competition ({ad_count} ads) - validated but not saturated")
            elif ad_count < 50:
                score = 70
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Moderate ad activity ({ad_count} ads)")
            elif ad_count < 100:
                score = 50
                strength = SignalStrength.WEAK
                reasoning_parts.append(f"High ad competition ({ad_count} ads) - expect advertising costs")
            else:
                score = 25
                strength = SignalStrength.WEAK
                reasoning_parts.append(f"Very high ad saturation ({ad_count} ads) - expensive to compete")
        
        is_simulated = product.get("data_source") == "simulated"
        
        return ValidationSignal(
            name="Ad Activity",
            value=ad_count,
            score=score,
            strength=strength,
            weight=self.SIGNAL_WEIGHTS["ad_activity"],
            reasoning=". ".join(reasoning_parts),
            is_simulated=is_simulated,
        )
    
    def _analyze_supplier_demand(self, product: Dict[str, Any]) -> ValidationSignal:
        """Analyze supplier demand - is supply reliable?"""
        supplier_orders = product.get("supplier_orders", 0)
        supplier_demand_score = product.get("supplier_demand_score", 50)
        
        score = 0
        reasoning_parts = []
        strength = SignalStrength.MODERATE
        
        if not supplier_orders:
            score = 40
            strength = SignalStrength.MISSING
            reasoning_parts.append("Supplier demand data unavailable")
        else:
            if supplier_orders > 10000:
                score = 95
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Very high supplier orders ({supplier_orders:,}) - proven demand")
            elif supplier_orders > 5000:
                score = 85
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Strong supplier demand ({supplier_orders:,} orders)")
            elif supplier_orders > 1000:
                score = 70
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Good supplier activity ({supplier_orders:,} orders)")
            elif supplier_orders > 100:
                score = 55
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Moderate supplier activity ({supplier_orders:,} orders)")
            else:
                score = 35
                strength = SignalStrength.WEAK
                reasoning_parts.append(f"Low supplier orders ({supplier_orders}) - limited validation")
        
        is_simulated = product.get("data_source") == "simulated"
        
        return ValidationSignal(
            name="Supplier Demand",
            value=supplier_orders,
            score=score,
            strength=strength,
            weight=self.SIGNAL_WEIGHTS["supplier_demand"],
            reasoning=". ".join(reasoning_parts),
            is_simulated=is_simulated,
        )
    
    def _analyze_engagement(self, product: Dict[str, Any]) -> ValidationSignal:
        """Analyze engagement signals - social proof"""
        tiktok_views = product.get("tiktok_views", 0)
        engagement_rate = product.get("engagement_rate", 0)
        
        score = 0
        reasoning_parts = []
        strength = SignalStrength.MODERATE
        
        if not tiktok_views:
            score = 40
            strength = SignalStrength.MISSING
            reasoning_parts.append("Social engagement data unavailable")
        else:
            if tiktok_views > 10000000:  # 10M+
                score = 95
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Viral content ({tiktok_views/1000000:.1f}M views)")
            elif tiktok_views > 1000000:  # 1M+
                score = 85
                strength = SignalStrength.STRONG
                reasoning_parts.append(f"Strong social proof ({tiktok_views/1000000:.1f}M views)")
            elif tiktok_views > 100000:  # 100K+
                score = 70
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Good engagement ({tiktok_views/1000:.0f}K views)")
            elif tiktok_views > 10000:  # 10K+
                score = 55
                strength = SignalStrength.MODERATE
                reasoning_parts.append(f"Moderate visibility ({tiktok_views/1000:.0f}K views)")
            else:
                score = 35
                strength = SignalStrength.WEAK
                reasoning_parts.append(f"Limited social proof ({tiktok_views:,} views)")
        
        # Engagement rate bonus
        if engagement_rate and engagement_rate > 5:
            score = min(100, score + 10)
            reasoning_parts.append(f"High engagement rate ({engagement_rate:.1f}%)")
        
        is_simulated = product.get("data_source") == "simulated"
        
        return ValidationSignal(
            name="Social Engagement",
            value={"views": tiktok_views, "engagement_rate": engagement_rate},
            score=score,
            strength=strength,
            weight=self.SIGNAL_WEIGHTS["engagement"],
            reasoning=". ".join(reasoning_parts),
            is_simulated=is_simulated,
        )
    
    def _calculate_overall_score(self, signals: List[ValidationSignal]) -> float:
        """Calculate weighted overall score from all signals"""
        total_score = 0
        total_weight = 0
        
        for signal in signals:
            total_score += signal.score * signal.weight
            total_weight += signal.weight
        
        return (total_score / total_weight) if total_weight > 0 else 0
    
    def _calculate_confidence(self, product: Dict[str, Any], signals: List[ValidationSignal]) -> int:
        """Calculate confidence in the validation based on data quality"""
        # Start with base confidence
        confidence = 50
        
        # Data source quality
        data_source = product.get("data_source", "unknown")
        if data_source == "simulated":
            confidence -= 20
        elif data_source in ["aliexpress_api", "tiktok_api"]:
            confidence += 20
        
        # Signal completeness
        missing_count = len([s for s in signals if s.strength == SignalStrength.MISSING])
        confidence -= missing_count * 8
        
        # Strong signals boost confidence
        strong_count = len([s for s in signals if s.strength == SignalStrength.STRONG])
        confidence += strong_count * 5
        
        # Data freshness
        last_updated = product.get("last_updated")
        if last_updated:
            # Recent data = higher confidence
            try:
                from datetime import datetime, timezone
                if isinstance(last_updated, str):
                    updated_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                else:
                    updated_time = last_updated
                
                hours_old = (datetime.now(timezone.utc) - updated_time).total_seconds() / 3600
                if hours_old < 6:
                    confidence += 10
                elif hours_old > 48:
                    confidence -= 10
            except Exception:
                pass
        
        return max(10, min(100, confidence))
    
    def _determine_recommendation(
        self, 
        overall_score: float, 
        confidence: int,
        signals: List[ValidationSignal]
    ) -> Tuple[LaunchRecommendation, str]:
        """Determine the final recommendation based on score and confidence"""
        
        # Check for insufficient data
        if confidence < self.MIN_CONFIDENCE:
            return (
                LaunchRecommendation.INSUFFICIENT_DATA,
                "Insufficient Data - Cannot Validate"
            )
        
        # Check for critical weak signals
        critical_weak = False
        for signal in signals:
            if signal.name == "Profit Margin" and signal.score < 30:
                critical_weak = True  # Can't launch without margin
        
        if critical_weak and overall_score >= self.LAUNCH_THRESHOLD:
            return (
                LaunchRecommendation.PROMISING_MONITOR,
                "Promising - Fix Margin Issues"
            )
        
        # Score-based recommendation
        if overall_score >= self.LAUNCH_THRESHOLD:
            return (
                LaunchRecommendation.LAUNCH_OPPORTUNITY,
                "🚀 Launch Opportunity"
            )
        elif overall_score >= self.PROMISING_THRESHOLD:
            return (
                LaunchRecommendation.PROMISING_MONITOR,
                "👀 Promising - Monitor Closely"
            )
        else:
            return (
                LaunchRecommendation.HIGH_RISK,
                "⚠️ High Risk / Saturated"
            )
    
    def _assess_risk(self, signals: List[ValidationSignal], confidence: int) -> RiskLevel:
        """Assess overall risk level"""
        weak_count = len([s for s in signals if s.strength == SignalStrength.WEAK])
        missing_count = len([s for s in signals if s.strength == SignalStrength.MISSING])
        
        # Find specific risk signals
        competition_signal = next((s for s in signals if s.name == "Competition Level"), None)
        margin_signal = next((s for s in signals if s.name == "Profit Margin"), None)
        
        risk_score = 0
        
        # Weak signals increase risk
        risk_score += weak_count * 15
        risk_score += missing_count * 10
        
        # Low confidence = higher risk
        if confidence < 50:
            risk_score += 20
        
        # Specific high-risk conditions
        if competition_signal and competition_signal.score < 40:
            risk_score += 20
        if margin_signal and margin_signal.score < 40:
            risk_score += 25
        
        # Classify risk
        if risk_score >= 60:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 40:
            return RiskLevel.HIGH
        elif risk_score >= 20:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _identify_strengths(self, signals: List[ValidationSignal]) -> List[str]:
        """Identify product strengths from signals"""
        strengths = []
        
        for signal in signals:
            if signal.strength == SignalStrength.STRONG:
                if signal.name == "Trend Velocity":
                    strengths.append("Strong upward trend momentum")
                elif signal.name == "Profit Margin":
                    strengths.append("Healthy profit margins")
                elif signal.name == "Competition Level":
                    strengths.append("Low competition in market")
                elif signal.name == "Ad Activity":
                    strengths.append("Validated market without ad saturation")
                elif signal.name == "Supplier Demand":
                    strengths.append("Proven supplier demand")
                elif signal.name == "Social Engagement":
                    strengths.append("Strong social proof and engagement")
        
        return strengths
    
    def _identify_weaknesses(self, signals: List[ValidationSignal]) -> List[str]:
        """Identify product weaknesses from signals"""
        weaknesses = []
        
        for signal in signals:
            if signal.strength == SignalStrength.WEAK:
                if signal.name == "Trend Velocity":
                    weaknesses.append("Declining or stagnant trend")
                elif signal.name == "Profit Margin":
                    weaknesses.append("Low profit margins - may struggle to profit")
                elif signal.name == "Competition Level":
                    weaknesses.append("High competition / saturated market")
                elif signal.name == "Ad Activity":
                    weaknesses.append("Heavy ad competition - expensive to compete")
                elif signal.name == "Supplier Demand":
                    weaknesses.append("Limited supplier validation")
                elif signal.name == "Social Engagement":
                    weaknesses.append("Limited social proof")
            elif signal.strength == SignalStrength.MISSING:
                weaknesses.append(f"Missing data: {signal.name}")
        
        return weaknesses
    
    def _generate_action_items(
        self, 
        recommendation: LaunchRecommendation,
        signals: List[ValidationSignal],
        weaknesses: List[str]
    ) -> List[str]:
        """Generate actionable next steps"""
        actions = []
        
        if recommendation == LaunchRecommendation.LAUNCH_OPPORTUNITY:
            actions.append("Create store and product listings")
            actions.append("Prepare advertising creatives")
            actions.append("Set up supplier relationship")
            actions.append("Monitor competitor pricing")
        
        elif recommendation == LaunchRecommendation.PROMISING_MONITOR:
            actions.append("Add to watchlist for continued monitoring")
            
            # Address specific weaknesses
            margin_signal = next((s for s in signals if s.name == "Profit Margin"), None)
            if margin_signal and margin_signal.score < 50:
                actions.append("Research alternative suppliers for better pricing")
            
            competition_signal = next((s for s in signals if s.name == "Competition Level"), None)
            if competition_signal and competition_signal.score < 50:
                actions.append("Identify unique angle to differentiate")
            
            actions.append("Wait for trend confirmation before investing")
        
        elif recommendation == LaunchRecommendation.HIGH_RISK:
            actions.append("Consider alternative products")
            actions.append("If proceeding, start with minimal investment")
            actions.append("Focus on unique positioning if entering this market")
        
        elif recommendation == LaunchRecommendation.INSUFFICIENT_DATA:
            actions.append("Gather more market research")
            actions.append("Wait for additional data signals")
            actions.append("Check alternative data sources")
        
        return actions
    
    def _generate_summary(
        self,
        product_name: str,
        recommendation: LaunchRecommendation,
        score: float,
        confidence: int,
        strengths: List[str],
        weaknesses: List[str]
    ) -> str:
        """Generate human-readable summary"""
        if recommendation == LaunchRecommendation.LAUNCH_OPPORTUNITY:
            summary = f"{product_name} shows strong launch potential with a score of {score:.0f}/100. "
            if strengths:
                summary += f"Key strengths: {', '.join(strengths[:2])}. "
            summary += "Consider moving forward with store creation."
        
        elif recommendation == LaunchRecommendation.PROMISING_MONITOR:
            summary = f"{product_name} shows promise (score: {score:.0f}/100) but has areas of concern. "
            if weaknesses:
                summary += f"Watch for: {', '.join(weaknesses[:2])}. "
            summary += "Monitor trends before committing resources."
        
        elif recommendation == LaunchRecommendation.HIGH_RISK:
            summary = f"{product_name} presents high risk (score: {score:.0f}/100). "
            if weaknesses:
                summary += f"Concerns: {', '.join(weaknesses[:2])}. "
            summary += "Consider alternative products unless you have a unique advantage."
        
        else:
            summary = f"Insufficient data to validate {product_name}. "
            summary += f"Confidence: {confidence}%. "
            summary += "More market signals needed for accurate assessment."
        
        return summary
