"""
Data Sources Package

Modular data ingestion architecture for ViralScout.
Supports multiple data sources with unified interface.

Data Source Types:
- trend_sources: TikTok, Amazon trending products
- supplier_data: AliExpress, CJ Dropshipping feeds
- competitor_analysis: Store detection, pricing intelligence
- ad_signals: Ad activity and spend estimation

Each source implements the BaseDataSource interface for:
- Consistent data normalization
- Unified error handling
- Rate limiting and caching
- Data freshness tracking
"""

from .base import BaseDataSource, DataSourceConfig, DataSourceResult
from .trend_sources import TikTokTrends, AmazonTrends
from .supplier_data import AliExpressProducts, CJDropshippingProducts
from .competitor_analysis import CompetitorIntelligence
from .ad_signals import AdActivityAnalyzer

__all__ = [
    'BaseDataSource',
    'DataSourceConfig', 
    'DataSourceResult',
    'TikTokTrends',
    'AmazonTrends',
    'AliExpressProducts',
    'CJDropshippingProducts',
    'CompetitorIntelligence',
    'AdActivityAnalyzer',
]
