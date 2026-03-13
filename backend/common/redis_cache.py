"""
Redis-backed cache with automatic fallback to in-memory.
Provides TTL-based caching for API responses and rate limiting.
"""
import json
import time
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

_redis_client = None
_fallback_store = {}  # In-memory fallback
_REDIS_AVAILABLE = False


def _get_redis():
    """Lazy-init Redis connection."""
    global _redis_client, _REDIS_AVAILABLE
    if _redis_client is not None:
        return _redis_client

    try:
        import redis
        url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        _redis_client.ping()
        _REDIS_AVAILABLE = True
        logger.info("Redis cache connected")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}), using in-memory fallback")
        _REDIS_AVAILABLE = False
        _redis_client = None
        return None


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache (Redis or fallback)."""
    r = _get_redis()
    if r:
        try:
            raw = r.get(f"ts:{key}")
            if raw:
                return json.loads(raw)
        except Exception:
            pass

    # Fallback
    entry = _fallback_store.get(key)
    if entry and (time.time() - entry["ts"]) < entry.get("ttl", 300):
        return entry["data"]
    return None


def cache_set(key: str, data: Any, ttl: int = 300):
    """Set value in cache with TTL (seconds)."""
    r = _get_redis()
    if r:
        try:
            r.setex(f"ts:{key}", ttl, json.dumps(data, default=str))
            return
        except Exception:
            pass

    # Fallback
    _fallback_store[key] = {"data": data, "ts": time.time(), "ttl": ttl}


def cache_delete(key: str):
    """Delete a key from cache."""
    r = _get_redis()
    if r:
        try:
            r.delete(f"ts:{key}")
        except Exception:
            pass
    _fallback_store.pop(key, None)


def cache_incr(key: str, ttl: int = 60) -> int:
    """Atomic increment for rate limiting. Returns new count."""
    r = _get_redis()
    if r:
        try:
            pipe = r.pipeline()
            pipe.incr(f"rl:{key}")
            pipe.expire(f"rl:{key}", ttl)
            results = pipe.execute()
            return results[0]
        except Exception:
            pass

    # Fallback
    entry = _fallback_store.get(f"rl:{key}")
    now = time.time()
    if not entry or (now - entry["ts"]) >= ttl:
        _fallback_store[f"rl:{key}"] = {"count": 1, "ts": now, "ttl": ttl}
        return 1
    entry["count"] += 1
    return entry["count"]


def cache_get_ttl(key: str) -> int:
    """Get remaining TTL for a key."""
    r = _get_redis()
    if r:
        try:
            return max(0, r.ttl(f"rl:{key}"))
        except Exception:
            pass

    entry = _fallback_store.get(f"rl:{key}")
    if entry:
        elapsed = time.time() - entry["ts"]
        return max(0, int(entry.get("ttl", 60) - elapsed))
    return 0


def is_redis_available() -> bool:
    """Check if Redis is connected."""
    _get_redis()
    return _REDIS_AVAILABLE
