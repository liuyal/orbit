# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# app/cache.py

from cachetools import TTLCache

# ---------------------------------------------------------------------------
# Cache configuration
# ---------------------------------------------------------------------------
# maxsize  – maximum number of distinct cache entries before LRU eviction.
# ttl      – seconds before a cached entry automatically expires.
#
# Cache keys used across the application:
#   "projects:all"              → GET /tm/projects
#   "projects:<project_key>"    → GET /tm/projects/{project_key}
#   "test_cases:all"            → GET /tm/test-cases
#   "test_cases:<project_key>"  → GET /tm/projects/{project_key}/test-cases
# ---------------------------------------------------------------------------

_cache: TTLCache = TTLCache(maxsize=256, ttl=60)


def cache_get(key: str):
    """Return cached value for key, or None if missing / expired."""

    return _cache.get(key)


def cache_set(key: str, value) -> None:
    """Store value in cache under key."""

    _cache[key] = value


def cache_invalidate(*keys: str) -> None:
    """Remove one or more specific keys from the cache."""

    for key in keys:
        _cache.pop(key, None)


def cache_invalidate_prefix(prefix: str) -> None:
    """Remove all cache entries whose key starts with prefix."""

    for key in list(_cache.keys()):
        if key.startswith(prefix):
            _cache.pop(key, None)
