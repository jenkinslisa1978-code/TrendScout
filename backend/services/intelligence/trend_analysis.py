"""
Intelligence Layer - Trend Analysis

Detects trend velocity and classifies products into trend stages.
Key for identifying early opportunities before market saturation.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class TrendStage(str, Enum):
    """Product trend lifecycle stages"""
    EXPLODING = "exploding"     # >100% growth
    RISING = "rising"          # 20-100% growth
    EARLY_TREND = "early_trend" # 5-20% growth, low competition
    STABLE = "stable"          # -5% to 5% change
    DECLINING = "declining"    # <-5% change


class TrendVelocity(str, Enum):
    """Velocity classification"""
    EXPLOSIVE = "explosive"      # >100%
    FAST = "fast"               # 50-100%
    MODERATE = "moderate"       # 20-50%
    SLOW = "slow"              # 5-20%
    FLAT = "flat"              # -5% to 5%
    NEGATIVE = "negative"      # <-5%


@dataclass
class TrendAnalysisResult:
    """Result of trend analysis for a product"""
    product_id: str
    trend_stage: TrendStage
    trend_velocity: TrendVelocity
    velocity_percent: float
    is_early_opportunity: bool
    days_until_saturation: Optional[int]
    momentum_score: float  # 0-100
    reasoning: List[str]
    confidence: int  # 0-100
    analyzed_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "trend_stage": self.trend_stage.value,
            "trend_velocity": self.trend_velocity.value,
            "velocity_percent": round(self.velocity_percent, 1),
            "is_early_opportunity": self.is_early_opportunity,
            "days_until_saturation": self.days_until_saturation,
            "momentum_score": round(self.momentum_score, 1),
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


class TrendAnalyzer:
    """
    Analyzes trend velocity and predicts trend lifecycle.
    
    Key metrics:
    - Velocity: Rate of change in interest/views
    - Stage: Where product is in lifecycle
    - Early Opportunity: Is this a good time to enter?
    """
    
    def __init__(self, db=None):
        self.db = db
    
    def analyze_trend(self, product: Dict[str, Any]) -> TrendAnalysisResult:
        """Analyze trend for a single product"""
        product_id = product.get("id", "")
        
        # Get velocity data
        velocity_percent = self._calculate_velocity(product)
        velocity_class = self._classify_velocity(velocity_percent)
        
        # Determine trend stage
        trend_stage = self._determine_stage(product, velocity_percent)
        
        # Calculate momentum score
        momentum = self._calculate_momentum(product, velocity_percent)
        
        # Detect early opportunity
        is_early = self._detect_early_opportunity(product, velocity_percent, trend_stage)
        
        # Estimate time to saturation
        days_to_saturation = self._estimate_saturation_timeline(product, velocity_percent)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            velocity_percent, velocity_class, trend_stage, is_early
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(product)
        
        return TrendAnalysisResult(
            product_id=product_id,
            trend_stage=trend_stage,
            trend_velocity=velocity_class,
            velocity_percent=velocity_percent,
            is_early_opportunity=is_early,
            days_until_saturation=days_to_saturation,
            momentum_score=momentum,
            reasoning=reasoning,
            confidence=confidence,
            analyzed_at=datetime.now(timezone.utc),
        )
    
    def _calculate_velocity(self, product: Dict[str, Any]) -> float:
        """
        Calculate trend velocity as percentage change.
        
        Formula: (current - previous) / previous * 100
        """
        # Try to use stored velocity first
        stored_velocity = product.get("trend_velocity")
        if stored_velocity is not None:
            return float(stored_velocity)
        
        # Calculate from historical data if available
        views_current = product.get("tiktok_views", 0)
        views_previous = product.get("tiktok_views_previous", 0)
        
        if views_previous and views_previous > 0:
            velocity = ((views_current - views_previous) / views_previous) * 100
            return velocity
        
        # Fallback: estimate from trend score
        trend_score = product.get("trend_score", 50)
        # Map trend score to approximate velocity
        if trend_score >= 90:
            return 80
        elif trend_score >= 80:
            return 40
        elif trend_score >= 60:
            return 15
        elif trend_score >= 40:
            return 0
        else:
            return -10
    
    def _classify_velocity(self, velocity_percent: float) -> TrendVelocity:
        """Classify velocity into categories"""
        if velocity_percent > 100:
            return TrendVelocity.EXPLOSIVE
        elif velocity_percent > 50:
            return TrendVelocity.FAST
        elif velocity_percent > 20:
            return TrendVelocity.MODERATE
        elif velocity_percent > 5:
            return TrendVelocity.SLOW
        elif velocity_percent >= -5:
            return TrendVelocity.FLAT
        else:
            return TrendVelocity.NEGATIVE
    
    def _determine_stage(self, product: Dict[str, Any], velocity: float) -> TrendStage:
        """Determine product's position in trend lifecycle"""
        # Use stored stage if available and recent
        stored_stage = product.get("trend_stage")
        competition_level = product.get("competition_level", "medium")
        competitor_count = product.get("competitor_store_count", 0)
        
        # Classify based on velocity and competition
        if velocity > 100:
            return TrendStage.EXPLODING
        elif velocity > 20:
            if competition_level == "low" and competitor_count < 20:
                return TrendStage.EARLY_TREND
            else:
                return TrendStage.RISING
        elif velocity > 5:
            if competition_level == "low":
                return TrendStage.EARLY_TREND
            else:
                return TrendStage.RISING
        elif velocity >= -5:
            return TrendStage.STABLE
        else:
            return TrendStage.DECLINING
    
    def _calculate_momentum(self, product: Dict[str, Any], velocity: float) -> float:
        """Calculate momentum score (0-100)"""
        momentum = 50  # Base score
        
        # Velocity contribution (max +/- 30)
        if velocity > 100:
            momentum += 30
        elif velocity > 50:
            momentum += 20
        elif velocity > 20:
            momentum += 10
        elif velocity < -10:
            momentum -= 20
        elif velocity < 0:
            momentum -= 10
        
        # Trend score contribution (max +/- 20)
        trend_score = product.get("trend_score", 50)
        momentum += (trend_score - 50) * 0.4
        
        # Early trend detection bonus
        early_trend_score = product.get("early_trend_score", 0)
        if early_trend_score > 70:
            momentum += 10
        
        return max(0, min(100, momentum))
    
    def _detect_early_opportunity(
        self, 
        product: Dict[str, Any], 
        velocity: float,
        stage: TrendStage
    ) -> bool:
        """Detect if this is an early market opportunity"""
        # Early opportunity criteria:
        # 1. Positive velocity
        # 2. Low competition
        # 3. Not yet saturated
        
        if velocity <= 0:
            return False
        
        competition_level = product.get("competition_level", "medium")
        if competition_level == "high":
            return False
        
        ad_count = product.get("ad_count", 0)
        if ad_count and ad_count > 100:
            return False
        
        competitor_count = product.get("competitor_store_count", 0)
        if competitor_count and competitor_count > 50:
            return False
        
        # Check trend stage
        if stage in [TrendStage.EXPLODING, TrendStage.RISING, TrendStage.EARLY_TREND]:
            return True
        
        return False
    
    def _estimate_saturation_timeline(
        self, 
        product: Dict[str, Any], 
        velocity: float
    ) -> Optional[int]:
        """Estimate days until market becomes saturated"""
        if velocity <= 0:
            return None  # Not growing
        
        competition_level = product.get("competition_level", "medium")
        competitor_count = product.get("competitor_store_count", 0) or 0
        
        # Saturation threshold
        saturation_threshold = 100  # competitors
        
        if competitor_count >= saturation_threshold:
            return 0  # Already saturated
        
        # Estimate growth rate based on velocity
        # Higher velocity = faster saturation
        if velocity > 100:
            daily_growth_rate = 0.15  # 15% daily competitor growth
        elif velocity > 50:
            daily_growth_rate = 0.10
        elif velocity > 20:
            daily_growth_rate = 0.05
        else:
            daily_growth_rate = 0.02
        
        # Calculate days to saturation
        if daily_growth_rate <= 0:
            return None
        
        remaining = saturation_threshold - competitor_count
        days = 0
        current = competitor_count if competitor_count > 0 else 5
        
        while current < saturation_threshold and days < 365:
            current *= (1 + daily_growth_rate)
            days += 1
        
        return days if days < 365 else None
    
    def _generate_reasoning(
        self,
        velocity: float,
        velocity_class: TrendVelocity,
        stage: TrendStage,
        is_early: bool
    ) -> List[str]:
        """Generate human-readable reasoning"""
        reasons = []
        
        # Velocity reasoning
        if velocity_class == TrendVelocity.EXPLOSIVE:
            reasons.append(f"Explosive growth: +{velocity:.0f}% velocity indicates viral momentum")
        elif velocity_class == TrendVelocity.FAST:
            reasons.append(f"Fast growth: +{velocity:.0f}% velocity shows strong upward trend")
        elif velocity_class == TrendVelocity.MODERATE:
            reasons.append(f"Moderate growth: +{velocity:.0f}% velocity is healthy but not explosive")
        elif velocity_class == TrendVelocity.SLOW:
            reasons.append(f"Slow growth: +{velocity:.0f}% velocity indicates gradual interest")
        elif velocity_class == TrendVelocity.FLAT:
            reasons.append("Flat trend: Interest is stable but not growing")
        else:
            reasons.append(f"Declining: {velocity:.0f}% indicates waning interest")
        
        # Stage reasoning
        stage_reasons = {
            TrendStage.EXPLODING: "Product is in explosive growth phase - high demand, time-sensitive opportunity",
            TrendStage.RISING: "Product is rising in popularity - growing market with increasing competition",
            TrendStage.EARLY_TREND: "Early trend detected - potential first-mover advantage",
            TrendStage.STABLE: "Mature/stable market - established demand but limited growth",
            TrendStage.DECLINING: "Declining interest - market may be moving on",
        }
        reasons.append(stage_reasons.get(stage, ""))
        
        # Early opportunity flag
        if is_early:
            reasons.append("🎯 Early opportunity detected - low competition window available")
        
        return [r for r in reasons if r]  # Filter empty
    
    def _calculate_confidence(self, product: Dict[str, Any]) -> int:
        """Calculate confidence in trend analysis"""
        confidence = 50
        
        # Data source quality
        data_source = product.get("data_source", "unknown")
        if data_source == "simulated":
            confidence -= 20
        elif data_source in ["tiktok_api", "amazon_api"]:
            confidence += 20
        
        # Data availability
        if product.get("tiktok_views"):
            confidence += 10
        if product.get("trend_velocity"):
            confidence += 10
        if product.get("early_trend_score"):
            confidence += 5
        
        # Data freshness
        last_updated = product.get("last_updated")
        if last_updated:
            try:
                if isinstance(last_updated, str):
                    updated_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                else:
                    updated_time = last_updated
                
                hours_old = (datetime.now(timezone.utc) - updated_time).total_seconds() / 3600
                if hours_old < 6:
                    confidence += 10
                elif hours_old > 48:
                    confidence -= 15
            except Exception:
                pass
        
        return max(10, min(100, confidence))


class TrendVelocityCalculator:
    """Utility for calculating trend velocity from time series data"""
    
    @staticmethod
    def calculate_from_snapshots(
        snapshots: List[Dict[str, Any]],
        metric_field: str = "views"
    ) -> float:
        """
        Calculate velocity from a series of data snapshots.
        
        Args:
            snapshots: List of {timestamp, metric_field} dicts
            metric_field: Field to calculate velocity for
            
        Returns:
            Velocity as percentage change
        """
        if len(snapshots) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_snapshots = sorted(snapshots, key=lambda x: x.get("timestamp", ""))
        
        first_value = sorted_snapshots[0].get(metric_field, 0)
        last_value = sorted_snapshots[-1].get(metric_field, 0)
        
        if first_value <= 0:
            return 100.0 if last_value > 0 else 0.0
        
        return ((last_value - first_value) / first_value) * 100
    
    @staticmethod
    def calculate_acceleration(velocities: List[float]) -> float:
        """
        Calculate trend acceleration (change in velocity).
        
        Positive acceleration = trend is speeding up
        Negative acceleration = trend is slowing down
        """
        if len(velocities) < 2:
            return 0.0
        
        # Calculate change between consecutive velocities
        changes = []
        for i in range(1, len(velocities)):
            change = velocities[i] - velocities[i-1]
            changes.append(change)
        
        return sum(changes) / len(changes) if changes else 0.0
