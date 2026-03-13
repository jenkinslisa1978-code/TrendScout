"""
Cache utilities and common text helpers.
Uses Redis-backed cache with in-memory fallback.
"""
import re
from common.redis_cache import cache_get as _redis_get, cache_set as _redis_set


def get_cached(key):
    return _redis_get(key)


def set_cached(key, data, ttl=300):
    _redis_set(key, data, ttl)


def slugify(text: str) -> str:
    """Convert product name to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def get_margin_range(margin: float) -> str:
    if margin >= 50:
        return "50%+"
    elif margin >= 40:
        return "40-50%"
    elif margin >= 30:
        return "30-40%"
    elif margin >= 20:
        return "20-30%"
    elif margin >= 10:
        return "10-20%"
    else:
        return "<10%"
