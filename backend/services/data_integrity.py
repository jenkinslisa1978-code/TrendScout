"""
Data Integrity Module

Provides data integrity tracking, signal provenance, and confidence scoring.
Ensures the platform NEVER presents simulated data as real insights.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field


class SignalOrigin(str, Enum):
    """Origin classification for each data signal"""
    LIVE_API = "live_api"           # Real data from verified API
    SCRAPED = "scraped"             # Scraped from public source
    ESTIMATED = "estimated"         # Calculated/derived from other signals
    SIMULATED = "simulated"         # Generated/synthetic data
    USER_INPUT = "user_input"       # Manually entered by user
    UNKNOWN = "unknown"             # Origin cannot be determined


class DataFreshness(str, Enum):
    """How fresh/stale the data is"""
    REAL_TIME = "real_time"         # < 1 minute old
    FRESH = "fresh"                 # < 1 hour old
    RECENT = "recent"               # < 24 hours old
    STALE = "stale"                 # > 24 hours old
    UNKNOWN = "unknown"             # Timestamp not available


class ConfidenceLevel(str, Enum):
    """Human-readable confidence classification"""
    HIGH = "high"           # 80-100: Live API with multiple sources
    MEDIUM = "medium"       # 50-79: Single live source or good estimation
    LOW = "low"            # 25-49: Estimation with limited signals
    VERY_LOW = "very_low"   # 0-24: Simulated or highly uncertain
    UNKNOWN = "unknown"     # No confidence data available


@dataclass
class SignalMetadata:
    """Metadata for individual data signals"""
    value: Any
    origin: SignalOrigin
    source_name: str
    timestamp: Optional[datetime] = None
    confidence: int = 0  # 0-100
    is_simulated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "origin": self.origin.value,
            "source_name": self.source_name,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "confidence": self.confidence,
            "is_simulated": self.is_simulated,
        }


@dataclass
class ProductDataIntegrity:
    """Complete data integrity record for a product"""
    product_id: str
    overall_confidence: int = 0
    overall_confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    data_freshness: DataFreshness = DataFreshness.UNKNOWN
    last_updated: Optional[datetime] = None
    sources_count: int = 0
    live_sources_count: int = 0
    simulated_signals_count: int = 0
    total_signals_count: int = 0
    
    # Signal-level metadata
    signals: Dict[str, SignalMetadata] = field(default_factory=dict)
    
    # Source health
    source_health: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "overall_confidence": self.overall_confidence,
            "overall_confidence_level": self.overall_confidence_level.value,
            "data_freshness": self.data_freshness.value,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "sources_count": self.sources_count,
            "live_sources_count": self.live_sources_count,
            "simulated_signals_count": self.simulated_signals_count,
            "total_signals_count": self.total_signals_count,
            "signals": {k: v.to_dict() for k, v in self.signals.items()},
            "source_health": self.source_health,
        }


class DataIntegrityService:
    """
    Service for managing data integrity across the platform.
    
    Key principles:
    1. NEVER fabricate data - if unavailable, show null/unknown
    2. Always track signal origin and confidence
    3. Clearly label estimated vs measured values
    4. Provide data freshness information
    """
    
    # Define which fields are critical for decision making
    CRITICAL_FIELDS = [
        'supplier_cost',
        'estimated_retail_price', 
        'tiktok_views',
        'ad_count',
        'competitor_store_count',
    ]
    
    # Fields that are always estimated/calculated
    CALCULATED_FIELDS = [
        'trend_score',
        'margin_score',
        'competition_score',
        'market_score',
        'success_probability',
        'early_trend_score',
        'win_score',
    ]
    
    def __init__(self, db):
        self.db = db
    
    def calculate_confidence_score(self, product: Dict[str, Any]) -> int:
        """
        Calculate overall confidence score (0-100) based on:
        - Data completeness
        - Source reliability  
        - Data freshness
        - Signal consistency
        """
        score = 0
        weights = {
            'completeness': 30,
            'source_quality': 40,
            'freshness': 20,
            'consistency': 10,
        }
        
        # Completeness: Do we have the critical fields?
        completeness_score = self._calculate_completeness(product)
        score += (completeness_score / 100) * weights['completeness']
        
        # Source quality: Live API vs simulated
        source_score = self._calculate_source_quality(product)
        score += (source_score / 100) * weights['source_quality']
        
        # Freshness: How old is the data?
        freshness_score = self._calculate_freshness_score(product)
        score += (freshness_score / 100) * weights['freshness']
        
        # Consistency: Do signals agree with each other?
        consistency_score = self._calculate_consistency(product)
        score += (consistency_score / 100) * weights['consistency']
        
        return min(100, int(score))
    
    def _calculate_completeness(self, product: Dict[str, Any]) -> int:
        """Score based on how many critical fields have real values"""
        total_fields = len(self.CRITICAL_FIELDS)
        filled_fields = 0
        
        for field_name in self.CRITICAL_FIELDS:
            value = product.get(field_name)
            if value is not None and value != 0 and value != '':
                filled_fields += 1
        
        return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
    
    def _calculate_source_quality(self, product: Dict[str, Any]) -> int:
        """Score based on data source reliability"""
        data_source = product.get('data_source', 'unknown')
        data_source_type = product.get('data_source_type', 'unknown')
        
        # Check if using live API
        is_live = data_source not in ['simulated', 'manual', 'unknown']
        is_simulated = data_source == 'simulated' or 'simulated' in data_source_type
        
        if is_live:
            return 100
        elif is_simulated:
            return 20
        else:
            return 50
    
    def _calculate_freshness_score(self, product: Dict[str, Any]) -> int:
        """Score based on data age"""
        last_updated = product.get('last_updated')
        
        if not last_updated:
            return 0
        
        try:
            if isinstance(last_updated, str):
                updated_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            else:
                updated_time = last_updated
            
            age_hours = (datetime.now(timezone.utc) - updated_time).total_seconds() / 3600
            
            if age_hours < 1:
                return 100
            elif age_hours < 6:
                return 80
            elif age_hours < 24:
                return 60
            elif age_hours < 72:
                return 40
            else:
                return 20
        except Exception:
            return 0
    
    def _calculate_consistency(self, product: Dict[str, Any]) -> int:
        """Score based on signal consistency (do the numbers make sense?)"""
        score = 100
        
        # Check margin consistency
        supplier_cost = product.get('supplier_cost', 0)
        retail_price = product.get('estimated_retail_price', 0)
        
        if supplier_cost > 0 and retail_price > 0:
            if retail_price < supplier_cost:
                score -= 30  # Retail less than cost doesn't make sense
        
        # Check competition vs ad count consistency
        ad_count = product.get('ad_count', 0)
        competition = product.get('competition_level', 'medium')
        
        if ad_count > 300 and competition == 'low':
            score -= 20  # High ads but low competition is inconsistent
        
        return max(0, score)
    
    def get_confidence_level(self, confidence_score: int) -> ConfidenceLevel:
        """Convert numeric confidence to human-readable level"""
        if confidence_score >= 80:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 50:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 25:
            return ConfidenceLevel.LOW
        elif confidence_score > 0:
            return ConfidenceLevel.VERY_LOW
        else:
            return ConfidenceLevel.UNKNOWN
    
    def get_data_freshness(self, product: Dict[str, Any]) -> DataFreshness:
        """Determine data freshness category"""
        last_updated = product.get('last_updated')
        
        if not last_updated:
            return DataFreshness.UNKNOWN
        
        try:
            if isinstance(last_updated, str):
                updated_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            else:
                updated_time = last_updated
            
            age_hours = (datetime.now(timezone.utc) - updated_time).total_seconds() / 3600
            
            if age_hours < 1/60:  # < 1 minute
                return DataFreshness.REAL_TIME
            elif age_hours < 1:
                return DataFreshness.FRESH
            elif age_hours < 24:
                return DataFreshness.RECENT
            else:
                return DataFreshness.STALE
        except Exception:
            return DataFreshness.UNKNOWN
    
    def is_signal_simulated(self, product: Dict[str, Any], field_name: str) -> bool:
        """Check if a specific signal is simulated"""
        data_source = product.get('data_source', 'unknown')
        
        # All signals from simulated source are simulated
        if data_source == 'simulated':
            return True
        
        # Check field-specific metadata if available
        signal_metadata = product.get('signal_metadata', {})
        if field_name in signal_metadata:
            return signal_metadata[field_name].get('is_simulated', False)
        
        return False
    
    def get_signal_origin(self, product: Dict[str, Any], field_name: str) -> SignalOrigin:
        """Get the origin of a specific signal"""
        data_source = product.get('data_source', 'unknown')
        
        # Calculated fields are always estimated
        if field_name in self.CALCULATED_FIELDS:
            return SignalOrigin.ESTIMATED
        
        # Check data source
        if data_source == 'simulated':
            return SignalOrigin.SIMULATED
        elif data_source == 'manual':
            return SignalOrigin.USER_INPUT
        elif data_source in ['tiktok_api', 'aliexpress_api', 'amazon_api']:
            return SignalOrigin.LIVE_API
        elif data_source in ['tiktok_scrape', 'aliexpress_scrape']:
            return SignalOrigin.SCRAPED
        else:
            return SignalOrigin.UNKNOWN
    
    def build_product_integrity(self, product: Dict[str, Any]) -> ProductDataIntegrity:
        """Build complete data integrity record for a product"""
        confidence = self.calculate_confidence_score(product)
        
        integrity = ProductDataIntegrity(
            product_id=product.get('id', ''),
            overall_confidence=confidence,
            overall_confidence_level=self.get_confidence_level(confidence),
            data_freshness=self.get_data_freshness(product),
            last_updated=datetime.now(timezone.utc),
        )
        
        # Analyze each signal
        all_fields = list(product.keys())
        sources = set()
        simulated_count = 0
        
        for field_name in all_fields:
            if field_name.startswith('_') or field_name in ['id', 'created_at', 'updated_at']:
                continue
            
            origin = self.get_signal_origin(product, field_name)
            is_simulated = origin == SignalOrigin.SIMULATED
            
            if is_simulated:
                simulated_count += 1
            
            data_source = product.get('data_source', 'unknown')
            sources.add(data_source)
            
            integrity.signals[field_name] = SignalMetadata(
                value=product.get(field_name),
                origin=origin,
                source_name=data_source,
                timestamp=datetime.now(timezone.utc),
                confidence=confidence if not is_simulated else 20,
                is_simulated=is_simulated,
            )
        
        integrity.sources_count = len(sources)
        integrity.live_sources_count = len([s for s in sources if s not in ['simulated', 'manual', 'unknown']])
        integrity.simulated_signals_count = simulated_count
        integrity.total_signals_count = len(integrity.signals)
        
        return integrity
    
    def format_for_ui(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format product data for UI display with integrity information.
        Ensures simulated/estimated data is clearly labeled.
        """
        integrity = self.build_product_integrity(product)
        data_source = product.get('data_source', 'unknown')
        is_simulated = data_source == 'simulated'
        
        return {
            **product,
            # Data integrity metadata
            'data_integrity': {
                'confidence_score': integrity.overall_confidence,
                'confidence_level': integrity.overall_confidence_level.value,
                'data_freshness': integrity.data_freshness.value,
                'is_simulated': is_simulated,
                'simulated_signals_count': integrity.simulated_signals_count,
                'total_signals_count': integrity.total_signals_count,
                'sources_count': integrity.sources_count,
                'live_sources_count': integrity.live_sources_count,
            },
            # Field-level warnings
            'warnings': self._generate_warnings(product, integrity),
            # Display hints for UI
            'display_hints': self._generate_display_hints(product, integrity),
        }
    
    def _generate_warnings(self, product: Dict[str, Any], integrity: ProductDataIntegrity) -> List[str]:
        """Generate warnings for low confidence or simulated data"""
        warnings = []
        
        if integrity.overall_confidence < 50:
            warnings.append("Low confidence data - limited signals available")
        
        if integrity.simulated_signals_count > 0:
            warnings.append(f"{integrity.simulated_signals_count} signals are simulated/estimated")
        
        if integrity.data_freshness == DataFreshness.STALE:
            warnings.append("Data may be outdated - last update over 24 hours ago")
        
        if integrity.live_sources_count == 0:
            warnings.append("Values based on market analysis and trend modelling. Connect live APIs for real-time data.")
        
        return warnings
    
    def _generate_display_hints(self, product: Dict[str, Any], integrity: ProductDataIntegrity) -> Dict[str, Any]:
        """Generate display hints for UI rendering"""
        hints = {}
        
        for field_name, signal in integrity.signals.items():
            if signal.is_simulated:
                hints[field_name] = {
                    'label': 'Simulated',
                    'tooltip': 'This value is simulated. Real data not available.',
                    'css_class': 'data-simulated',
                }
            elif signal.origin == SignalOrigin.ESTIMATED:
                hints[field_name] = {
                    'label': 'Estimated',
                    'tooltip': 'This value is calculated from other signals.',
                    'css_class': 'data-estimated',
                }
            elif signal.confidence < 50:
                hints[field_name] = {
                    'label': 'Low Confidence',
                    'tooltip': f'Confidence: {signal.confidence}%',
                    'css_class': 'data-low-confidence',
                }
        
        return hints


def get_null_safe_value(value: Any, fallback: str = "Unknown") -> Any:
    """Return fallback for null/zero values"""
    if value is None or value == 0 or value == '':
        return fallback
    return value


def format_with_confidence(value: Any, confidence: int, is_simulated: bool = False) -> Dict[str, Any]:
    """Format a value with its confidence metadata"""
    return {
        'value': value,
        'display_value': get_null_safe_value(value),
        'confidence': confidence,
        'is_simulated': is_simulated,
        'label': 'Simulated' if is_simulated else ('Low Confidence' if confidence < 50 else None),
    }
