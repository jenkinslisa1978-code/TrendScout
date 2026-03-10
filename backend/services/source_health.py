"""
Source Health Monitoring Service

Tracks the health and status of all data ingestion pipelines.
Provides real-time monitoring and alerts for data source issues.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SourceStatus(str, Enum):
    """Status of a data source"""
    HEALTHY = "healthy"         # Working normally
    DEGRADED = "degraded"       # Working but with issues
    UNAVAILABLE = "unavailable" # Not currently accessible
    DISABLED = "disabled"       # Manually disabled
    ERROR = "error"            # Error state
    UNKNOWN = "unknown"         # Status not determined


class SourceType(str, Enum):
    """Type of data source"""
    TREND = "trend"
    SUPPLIER = "supplier"
    COMPETITOR = "competitor"
    AD_SIGNALS = "ad_signals"


@dataclass
class SourceHealthRecord:
    """Health record for a single data source"""
    source_name: str
    source_type: SourceType
    status: SourceStatus = SourceStatus.UNKNOWN
    is_live: bool = False
    is_enabled: bool = True
    last_run: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_error: Optional[datetime] = None
    last_error_message: Optional[str] = None
    records_ingested_last_run: int = 0
    total_records_ingested: int = 0
    success_rate: float = 0.0
    avg_latency_ms: float = 0.0
    data_freshness_hours: Optional[float] = None
    api_key_configured: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_type": self.source_type.value,
            "status": self.status.value,
            "is_live": self.is_live,
            "is_enabled": self.is_enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_error": self.last_error.isoformat() if self.last_error else None,
            "last_error_message": self.last_error_message,
            "records_ingested_last_run": self.records_ingested_last_run,
            "total_records_ingested": self.total_records_ingested,
            "success_rate": self.success_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "data_freshness_hours": self.data_freshness_hours,
            "api_key_configured": self.api_key_configured,
        }


@dataclass
class PlatformHealthSummary:
    """Overall platform data health summary"""
    overall_status: SourceStatus = SourceStatus.UNKNOWN
    total_sources: int = 0
    healthy_sources: int = 0
    degraded_sources: int = 0
    unavailable_sources: int = 0
    live_sources: int = 0
    simulated_sources: int = 0
    last_data_ingestion: Optional[datetime] = None
    oldest_data_hours: Optional[float] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "total_sources": self.total_sources,
            "healthy_sources": self.healthy_sources,
            "degraded_sources": self.degraded_sources,
            "unavailable_sources": self.unavailable_sources,
            "live_sources": self.live_sources,
            "simulated_sources": self.simulated_sources,
            "last_data_ingestion": self.last_data_ingestion.isoformat() if self.last_data_ingestion else None,
            "oldest_data_hours": self.oldest_data_hours,
            "warnings": self.warnings,
        }


class SourceHealthMonitor:
    """
    Monitors health of all data sources and provides platform-wide health status.
    """
    
    # Define all known data sources
    KNOWN_SOURCES = {
        "tiktok_trends": {
            "type": SourceType.TREND,
            "api_key_env": "TIKTOK_API_KEY",
            "description": "TikTok Creative Center trending products",
        },
        "amazon_trends": {
            "type": SourceType.TREND,
            "api_key_env": "SERPAPI_KEY",
            "description": "Amazon Movers & Shakers BSR tracking",
        },
        "aliexpress_supplier": {
            "type": SourceType.SUPPLIER,
            "api_key_env": "ALIEXPRESS_API_KEY",
            "description": "AliExpress product data and pricing",
        },
        "cj_dropshipping": {
            "type": SourceType.SUPPLIER,
            "api_key_env": "CJ_API_KEY",
            "description": "CJ Dropshipping product feeds",
        },
        "competitor_analysis": {
            "type": SourceType.COMPETITOR,
            "api_key_env": None,  # Uses estimation algorithms
            "description": "Competitor store detection and analysis",
        },
        "ad_signals": {
            "type": SourceType.AD_SIGNALS,
            "api_key_env": None,  # Uses estimation algorithms
            "description": "Advertising activity estimation",
        },
    }
    
    def __init__(self, db):
        self.db = db
        self._health_cache: Dict[str, SourceHealthRecord] = {}
        self._last_check: Optional[datetime] = None
    
    async def get_source_health(self, source_name: str) -> SourceHealthRecord:
        """Get health record for a specific source"""
        if source_name not in self.KNOWN_SOURCES:
            return SourceHealthRecord(
                source_name=source_name,
                source_type=SourceType.TREND,
                status=SourceStatus.UNKNOWN,
            )
        
        source_config = self.KNOWN_SOURCES[source_name]
        
        # Check if API key is configured
        api_key_env = source_config.get("api_key_env")
        api_key_configured = bool(os.environ.get(api_key_env)) if api_key_env else False
        is_live = api_key_configured
        
        # Get job history for this source
        job_history = await self._get_job_history(source_name)
        
        # Calculate metrics from job history
        last_run = None
        last_success = None
        last_error = None
        last_error_message = None
        records_ingested = 0
        success_count = 0
        total_count = 0
        latencies = []
        
        for job in job_history:
            total_count += 1
            job_time = job.get('started_at')
            
            if job_time:
                if isinstance(job_time, str):
                    job_time = datetime.fromisoformat(job_time.replace('Z', '+00:00'))
                
                if not last_run or job_time > last_run:
                    last_run = job_time
                    records_ingested = job.get('products_processed', 0)
            
            if job.get('status') == 'completed':
                success_count += 1
                if job_time and (not last_success or job_time > last_success):
                    last_success = job_time
                
                # Calculate latency
                end_time = job.get('completed_at')
                if end_time and job_time:
                    if isinstance(end_time, str):
                        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    latency = (end_time - job_time).total_seconds() * 1000
                    latencies.append(latency)
            
            elif job.get('status') == 'failed':
                if job_time and (not last_error or job_time > last_error):
                    last_error = job_time
                    last_error_message = job.get('error_message')
        
        # Calculate success rate
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        # Calculate data freshness
        data_freshness_hours = None
        if last_success:
            data_freshness_hours = (datetime.now(timezone.utc) - last_success).total_seconds() / 3600
        
        # Determine status
        status = self._determine_status(
            is_live=is_live,
            last_success=last_success,
            last_error=last_error,
            success_rate=success_rate,
        )
        
        # Get total records from database
        total_records = await self.db.products.count_documents({
            "data_source": source_name
        })
        
        return SourceHealthRecord(
            source_name=source_name,
            source_type=source_config["type"],
            status=status,
            is_live=is_live,
            is_enabled=True,  # Could be made configurable
            last_run=last_run,
            last_success=last_success,
            last_error=last_error,
            last_error_message=last_error_message,
            records_ingested_last_run=records_ingested,
            total_records_ingested=total_records,
            success_rate=success_rate,
            avg_latency_ms=avg_latency,
            data_freshness_hours=data_freshness_hours,
            api_key_configured=api_key_configured,
        )
    
    def _determine_status(
        self,
        is_live: bool,
        last_success: Optional[datetime],
        last_error: Optional[datetime],
        success_rate: float,
    ) -> SourceStatus:
        """Determine source status based on metrics"""
        now = datetime.now(timezone.utc)
        
        # No successful runs ever
        if not last_success:
            if last_error:
                return SourceStatus.ERROR
            return SourceStatus.UNKNOWN
        
        # Check freshness
        hours_since_success = (now - last_success).total_seconds() / 3600
        
        # Recent error after success
        if last_error and last_error > last_success:
            if hours_since_success > 24:
                return SourceStatus.UNAVAILABLE
            return SourceStatus.DEGRADED
        
        # Check success rate
        if success_rate < 50:
            return SourceStatus.DEGRADED
        
        # Check data freshness
        if hours_since_success > 24:
            return SourceStatus.DEGRADED
        
        return SourceStatus.HEALTHY
    
    async def _get_job_history(self, source_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent job history for a source"""
        # Map source names to job types
        job_type_map = {
            "tiktok_trends": "tiktok_import",
            "amazon_trends": "amazon_import",
            "aliexpress_supplier": "supplier_import",
            "cj_dropshipping": "supplier_import",
            "competitor_analysis": "full_pipeline",
            "ad_signals": "full_pipeline",
        }
        
        job_type = job_type_map.get(source_name)
        if not job_type:
            return []
        
        cursor = self.db.automation_logs.find(
            {"job_type": job_type}
        ).sort("started_at", -1).limit(limit)
        
        return await cursor.to_list(limit)
    
    async def get_all_source_health(self) -> Dict[str, SourceHealthRecord]:
        """Get health records for all known sources"""
        health_records = {}
        
        for source_name in self.KNOWN_SOURCES:
            health_records[source_name] = await self.get_source_health(source_name)
        
        self._health_cache = health_records
        self._last_check = datetime.now(timezone.utc)
        
        return health_records
    
    async def get_platform_health(self) -> PlatformHealthSummary:
        """Get overall platform health summary"""
        health_records = await self.get_all_source_health()
        
        summary = PlatformHealthSummary(
            total_sources=len(health_records),
        )
        
        latest_run = None
        oldest_freshness = 0
        
        for source_name, record in health_records.items():
            if record.status == SourceStatus.HEALTHY:
                summary.healthy_sources += 1
            elif record.status == SourceStatus.DEGRADED:
                summary.degraded_sources += 1
            elif record.status in [SourceStatus.UNAVAILABLE, SourceStatus.ERROR]:
                summary.unavailable_sources += 1
            
            if record.is_live:
                summary.live_sources += 1
            else:
                summary.simulated_sources += 1
            
            if record.last_run:
                if not latest_run or record.last_run > latest_run:
                    latest_run = record.last_run
            
            if record.data_freshness_hours is not None:
                if record.data_freshness_hours > oldest_freshness:
                    oldest_freshness = record.data_freshness_hours
        
        summary.last_data_ingestion = latest_run
        summary.oldest_data_hours = oldest_freshness if oldest_freshness > 0 else None
        
        # Determine overall status
        if summary.unavailable_sources > 0:
            summary.overall_status = SourceStatus.DEGRADED
        elif summary.degraded_sources > summary.healthy_sources:
            summary.overall_status = SourceStatus.DEGRADED
        elif summary.healthy_sources > 0:
            summary.overall_status = SourceStatus.HEALTHY
        else:
            summary.overall_status = SourceStatus.UNKNOWN
        
        # Generate warnings
        if summary.live_sources == 0:
            summary.warnings.append("No live data sources configured. All data is simulated.")
        
        if summary.oldest_data_hours and summary.oldest_data_hours > 24:
            summary.warnings.append(f"Some data is stale (oldest: {summary.oldest_data_hours:.1f} hours)")
        
        if summary.unavailable_sources > 0:
            summary.warnings.append(f"{summary.unavailable_sources} data source(s) currently unavailable")
        
        return summary
    
    async def get_source_status_for_ui(self) -> Dict[str, Any]:
        """Get formatted source status for admin UI"""
        health_records = await self.get_all_source_health()
        platform_health = await self.get_platform_health()
        
        sources_list = []
        for source_name, record in health_records.items():
            config = self.KNOWN_SOURCES.get(source_name, {})
            sources_list.append({
                **record.to_dict(),
                "description": config.get("description", ""),
                "api_key_env": config.get("api_key_env"),
                "status_badge": self._get_status_badge(record.status),
            })
        
        return {
            "platform": platform_health.to_dict(),
            "sources": sources_list,
            "last_check": self._last_check.isoformat() if self._last_check else None,
        }
    
    def _get_status_badge(self, status: SourceStatus) -> Dict[str, str]:
        """Get badge styling for status"""
        badges = {
            SourceStatus.HEALTHY: {"color": "green", "text": "Healthy"},
            SourceStatus.DEGRADED: {"color": "yellow", "text": "Degraded"},
            SourceStatus.UNAVAILABLE: {"color": "red", "text": "Unavailable"},
            SourceStatus.ERROR: {"color": "red", "text": "Error"},
            SourceStatus.DISABLED: {"color": "gray", "text": "Disabled"},
            SourceStatus.UNKNOWN: {"color": "gray", "text": "Unknown"},
        }
        return badges.get(status, {"color": "gray", "text": "Unknown"})
