"""
Data Reliability Layer

Provides circuit-breaking, fallback chains, source tracking,
and confidence tagging for all data sources.

Every data pull produces a SourceResult with:
  - data_confidence: live | estimated | fallback
  - source_method: api | scraper | estimation | hardcoded
  - freshness_ts: when the data was fetched
  - error_log: any error messages from attempts
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class DataConfidence(str, Enum):
    LIVE = "live"
    ESTIMATED = "estimated"
    FALLBACK = "fallback"


class SourceMethod(str, Enum):
    API = "api"
    SCRAPER = "scraper"
    ESTIMATION = "estimation"
    HARDCODED = "hardcoded"


@dataclass
class SourceResult:
    """Result from a single data source attempt."""
    success: bool
    data: Any = None
    confidence: DataConfidence = DataConfidence.FALLBACK
    method: SourceMethod = SourceMethod.HARDCODED
    source_name: str = ""
    fetched_at: str = ""
    error: Optional[str] = None
    latency_ms: float = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "confidence": self.confidence.value,
            "method": self.method.value,
            "source_name": self.source_name,
            "fetched_at": self.fetched_at,
            "error": self.error,
            "latency_ms": round(self.latency_ms, 1),
        }


class CircuitBreaker:
    """
    Per-source circuit breaker.
    CLOSED → OPEN after `failure_threshold` consecutive failures.
    OPEN → HALF_OPEN after `recovery_timeout` seconds.
    HALF_OPEN → CLOSED on success, OPEN on failure.
    """
    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: int = 300):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "closed"  # closed | open | half_open
        self.last_failure_time: Optional[datetime] = None

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if self.last_failure_time and \
               (datetime.now(timezone.utc) - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = "half_open"
                logger.info(f"CircuitBreaker [{self.name}]: open → half_open")
                return True
            return False
        return True  # half_open

    def record_success(self):
        self.failures = 0
        if self.state != "closed":
            logger.info(f"CircuitBreaker [{self.name}]: {self.state} → closed")
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now(timezone.utc)
        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"CircuitBreaker [{self.name}]: → open after {self.failures} failures")


# Global registry of circuit breakers
_breakers: Dict[str, CircuitBreaker] = {}


def get_breaker(name: str) -> CircuitBreaker:
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(name)
    return _breakers[name]


async def execute_with_fallback(
    source_name: str,
    chain: List[Dict[str, Any]],
    db=None,
) -> SourceResult:
    """
    Execute a fallback chain for a data source.

    `chain` is a list of dicts:
      [
        {"label": "scraper", "method": SourceMethod.SCRAPER, "confidence": DataConfidence.LIVE, "fn": async_callable},
        {"label": "estimation", "method": SourceMethod.ESTIMATION, "confidence": DataConfidence.ESTIMATED, "fn": async_callable},
        {"label": "hardcoded", "method": SourceMethod.HARDCODED, "confidence": DataConfidence.FALLBACK, "fn": async_callable},
      ]
    """
    errors = []
    for step in chain:
        label = step["label"]
        breaker = get_breaker(f"{source_name}_{label}")

        if not breaker.can_execute():
            errors.append(f"{label}: circuit open")
            continue

        start = datetime.now(timezone.utc)
        try:
            data = await step["fn"]()
            latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            breaker.record_success()

            if data:
                # Log success
                if db is not None:
                    await _log_pull(db, source_name, label, True, latency)
                return SourceResult(
                    success=True,
                    data=data,
                    confidence=step["confidence"],
                    method=step["method"],
                    source_name=source_name,
                    fetched_at=datetime.now(timezone.utc).isoformat(),
                    latency_ms=latency,
                )
            else:
                errors.append(f"{label}: returned empty data")
        except Exception as e:
            latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            breaker.record_failure()
            err_msg = f"{label}: {str(e)[:200]}"
            errors.append(err_msg)
            logger.warning(f"[{source_name}] {err_msg}")
            if db is not None:
                await _log_pull(db, source_name, label, False, latency, str(e)[:500])

    # All steps failed
    return SourceResult(
        success=False,
        confidence=DataConfidence.FALLBACK,
        method=SourceMethod.HARDCODED,
        source_name=source_name,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        error="; ".join(errors),
    )


async def _log_pull(db, source: str, method: str, success: bool, latency_ms: float, error: str = None):
    """Log every data pull attempt to source_pull_log collection."""
    try:
        await db.source_pull_log.insert_one({
            "source": source,
            "method": method,
            "success": success,
            "latency_ms": round(latency_ms, 1),
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass  # Don't fail on logging


def build_source_signals(signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build source_signals dict for a product.

    signals = {
        "trend": {"value": 75, "confidence": "live", "source": "tiktok_scraper", "updated": "..."},
        "supplier_cost": {"value": 8.50, "confidence": "estimated", "source": "aliexpress_estimation", "updated": "..."},
        ...
    }
    """
    return signals


def compute_product_confidence(source_signals: Dict[str, Any]) -> str:
    """Determine overall product data_confidence from source_signals."""
    confidences = [v.get("confidence", "fallback") for v in source_signals.values() if isinstance(v, dict)]
    if not confidences:
        return "fallback"
    if all(c == "live" for c in confidences):
        return "live"
    if any(c == "live" for c in confidences):
        return "estimated"  # mixed
    if any(c == "estimated" for c in confidences):
        return "estimated"
    return "fallback"
