"""
Cache utilities and common text helpers.
"""
import re
import time as _time

_public_cache = {}
_CACHE_TTL = 300  # 5 minutes


def get_cached(key):
    entry = _public_cache.get(key)
    if entry and (_time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["data"]
    return None


def set_cached(key, data):
    _public_cache[key] = {"data": data, "ts": _time.time()}


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
