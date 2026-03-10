"""
Intelligence Layer

Converts raw data into actionable insights for users.
"""

from .product_validation import (
    ProductValidationEngine,
    ValidationResult,
    LaunchRecommendation,
    RiskLevel,
)

from .trend_analysis import (
    TrendAnalyzer,
    TrendAnalysisResult,
    TrendStage,
    TrendVelocity,
)

from .success_prediction import (
    SuccessPredictionModel,
    SuccessPrediction,
    SuccessOutcome,
)

__all__ = [
    "ProductValidationEngine",
    "ValidationResult",
    "LaunchRecommendation",
    "RiskLevel",
    "TrendAnalyzer",
    "TrendAnalysisResult",
    "TrendStage",
    "TrendVelocity",
    "SuccessPredictionModel",
    "SuccessPrediction",
    "SuccessOutcome",
]
